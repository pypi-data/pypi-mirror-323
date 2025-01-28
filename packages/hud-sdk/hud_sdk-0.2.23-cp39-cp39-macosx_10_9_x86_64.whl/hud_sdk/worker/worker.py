import contextlib
import json
import os
import random
import signal
import subprocess
import threading
import time
from functools import wraps
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    TypeVar,
    Union,
)
from uuid import uuid4

from .. import globals
from .._internal import worker_queue
from ..collectors import PerformanceMonitor, get_loaded_modules, runtime_info
from ..config import config
from ..declarations import Declaration, DeclarationsAggregator
from ..endpoint_manager import EndpointsDeclarationsAggregator
from ..exporter.manager.client import Manager, get_manager  # noqa: F401
from ..exporter.manager.errors import ManagerException
from ..exporter.manager.manager import BrokerProxy  # noqa: F401
from ..exporter.queue import BaseInfoStructure, BufferBackedCyclicQueue
from ..forkable import after_fork_in_child
from ..hook import set_hook
from ..invocations_handler import InvocationsHandler
from ..kafka_declaration_manager import KafkaDeclarationsAggregator
from ..logging import internal_logger, send_logs_handler, user_logger
from ..native import get_hud_running_mode
from ..process_utils import get_current_pid, is_alive
from ..run_mode import disable_hud, get_hud_enable, should_run_hud, valid_hud_enable
from ..schemas.events import EndpointDeclaration, KafkaDeclaration
from ..user_options import UserOptions, init_user_options
from ..users_logs import UsersLogs
from ..utils import (
    dump_logs_sync,
    find_python_binary,
    get_shared_state_file_name,
    suppress_exceptions_sync,
)
from ..workload_metadata import get_cpu_limit

if TYPE_CHECKING:
    from collections import deque

    from ..exporter.manager.manager import SharedMemory  # noqa: F401


worker_thread = None  # type: Optional[threading.Thread]
unique_id = None  # type: Optional[str]


def should_run_worker() -> bool:
    return bool(
        get_hud_running_mode()
        and worker_thread
        and not should_finalize_worker(worker_thread)
    )


def should_finalize_worker(worker_thread: threading.Thread) -> bool:
    for thread in threading.enumerate():
        if thread == worker_thread:
            continue
        if (
            not thread.daemon
            and thread.is_alive()
            and thread.name != "pydevd.CheckAliveThread"
        ):
            return False
    internal_logger.info("All threads are done, finalizing worker")
    return True


T = TypeVar("T")


def disable_on_manager_exception(func: Callable[..., T]) -> Callable[..., T]:

    @wraps(func)
    def sync_wrapper(self: Any, *args: Any, **kwargs: Any) -> T:
        try:
            return func(self, *args, **kwargs)
        except ManagerException:
            internal_logger.critical(
                "Disabling Hud due to exception in manager function",
                exc_info=True,
                data={"function": getattr(func, "__name__", None)},
            )
            user_logger.log(*UsersLogs.HUD_FAILED_TO_COMMUNICATE_WITH_MANAGER)
            disable_hud(
                should_dump_logs=False,
                should_clear=False,
                session_id=self.session_id,
            )
            raise

    return sync_wrapper


class QueueInfo:
    def __init__(
        self,
        shared_memory: "SharedMemory",
        queue: BufferBackedCyclicQueue[BaseInfoStructure],
    ) -> None:
        self.shared_memory = shared_memory
        self.queue = queue


class Task:
    def __init__(
        self,
        func: Callable[[], Any],
        interval_factory: Callable[[], float],
        initial_time: float,
    ) -> None:
        self.interval_factory = interval_factory
        interval = interval_factory()
        self.func = func
        self.last_run = initial_time + random.randint(0, int(interval)) - interval

    def run(self, time: float) -> bool:
        interval = self.interval_factory()
        if time - self.last_run >= interval:
            self.last_run = time
            self.func()
            return True
        return False


exporter_pid = None
manager_port = None


class Worker:

    def __init__(
        self,
        initialization_event: threading.Event,
        user_options: UserOptions,
    ) -> None:
        self.user_options = user_options
        self.declarations = DeclarationsAggregator()
        self.endpoints_declarations = EndpointsDeclarationsAggregator()
        self.kafka_declarations = KafkaDeclarationsAggregator()
        self.invocations_handler = InvocationsHandler()
        self.performance_monitor = PerformanceMonitor("worker", get_cpu_limit())
        self.manager = None  # type: Optional[Manager]
        self.tasks = []  # type: List[Task]
        self.manager_pid = None  # type: Optional[int]
        self.session_id = None  # type: Optional[str]
        self.initialization_event = initialization_event
        self.did_dump_metrics = False
        self.broker = None  # type: Optional[BrokerProxy]
        self._queues = {}  # type: Dict[str, QueueInfo]
        self.remote_config_id = None  # type: Optional[str]

    def cleanup(self) -> None:
        with contextlib.suppress(Exception):
            self.close_shared_memories(should_delete=False)

    def _start_exporter(self) -> bool:
        # Make sure to log to the user every False flow!
        try:
            if not exporter_pid:
                executable = find_python_binary()
                if not executable:
                    internal_logger.error("Python executable not found")
                    if is_main_process:
                        user_logger.log(*UsersLogs.HUD_PYTHON_EXECUTABLE_NOT_FOUND)
                    return False
                if not self.run_exporter(executable):
                    if is_main_process:
                        user_logger.log(*UsersLogs.HUD_RUN_EXPORTER_FAILED)
                    return False
            return True
        finally:
            self.initialization_event.set()

    def _open_shared_memories(self) -> None:
        if not self.manager:
            internal_logger.error("Manager is not set")
            return

        for name, shared_memory in self.manager.get_shared_memories().items():
            shared_memory.open()
            queue = BufferBackedCyclicQueue(
                shared_memory.mmap_obj,
                BaseInfoStructure,
                shared_memory.mmap_obj.size(),
            )
            self._queues[name] = QueueInfo(shared_memory, queue)

    def _setup(self) -> bool:
        # Make sure to log to the user every False flow!
        internal_logger.info("Starting worker")
        try:
            if not self._start_exporter():
                # All the False flows are logged in the function
                internal_logger.error("Failed to start exporter")
                return False
        except Exception:
            user_logger.log(*UsersLogs.HUD_RUN_EXPORTER_FAILED)
            internal_logger.exception("Failed to start exporter")
            return False

        try:
            if not self.connect():
                internal_logger.error("Failed to connect to manager")
                user_logger.log(*UsersLogs.HUD_FAILED_TO_CONNECT_TO_MANAGER)
                return False
        except Exception:
            internal_logger.exception("Failed to connect to manager")
            user_logger.log(*UsersLogs.HUD_FAILED_TO_CONNECT_TO_MANAGER)
            return False

        try:
            if not self.manager:
                internal_logger.error("Manager is not set")
                user_logger.log(*UsersLogs.HUD_NO_MANAGER)
                return False
        except Exception:
            internal_logger.exception("Manager is not set")
            user_logger.log(*UsersLogs.HUD_NO_MANAGER)
            return False

        try:
            self.manager.register_process(os.getpid())
            self.manager_pid = self.manager.manager_pid
        except Exception:
            user_logger.log(*UsersLogs.HUD_FAILED_TO_REGISTER_PROCESSES)
            internal_logger.exception("Failed to register process")
            return False

        self.session_id = self.manager.session_id
        self.broker = self.manager.broker

        try:
            self._open_shared_memories()
        except Exception:
            user_logger.log(*UsersLogs.HUD_FAILED_TO_OPEN_SHARED_MEMORIES)
            internal_logger.exception("Failed to open shared memories")
            return False

        self._update_configuration()

        try:
            self.register_tasks()
        except Exception:
            user_logger.log(*UsersLogs.HUD_FAILED_TO_REGISTER_TASKS)
            internal_logger.exception("Failed to register tasks")
            return False

        internal_logger.info("Worker started")
        try:
            self._send_runtime()  # We need to send the runtime only once
        except Exception:
            user_logger.log(*UsersLogs.HUD_FAILED_TO_COMMUNICATE_WITH_MANAGER)
            internal_logger.exception("Failed to send runtime")
            return False

        if is_main_process and get_hud_running_mode() and self.session_id:
            # We don't want to log success if we got disabled
            user_logger.log(*UsersLogs.HUD_INITIALIZED_SUCCESSFULLY)

        return True

    def run(self) -> None:
        with internal_logger.stage_context("setup"):
            setup_success = self._setup()

        if not setup_success:
            return

        with internal_logger.stage_context("loop"):
            while True:
                if not should_run_worker():
                    with internal_logger.stage_context("finalize"):
                        self._finalize()
                        break
                waketime = time.time()
                for task in self.tasks:
                    if not get_hud_running_mode():
                        break
                    if task.run(waketime):
                        time.sleep(0.01)
                time.sleep(1)

    def run_exporter(self, executable: str) -> bool:
        try:
            global unique_id
            unique_id = str(uuid4())[:8]
            env = os.environ.copy()
            if "ddtrace" in env.get("PYTHONPATH", ""):
                # When running with ddtrace-run, gevent is imported in the exporter process, which causes it to never exit
                python_path_parts = env["PYTHONPATH"].split(os.path.pathsep)
                python_path_parts = [
                    part for part in python_path_parts if "ddtrace" not in part
                ]
                env["PYTHONPATH"] = os.path.pathsep.join(python_path_parts)
                internal_logger.info("Removed ddtrace from PYTHONPATH")
            networkprocess = subprocess.Popen(
                [executable, "-m", "hud_sdk.exporter", unique_id],
                start_new_session=True,
                env=env,
            )
            time.sleep(0.4)
            if networkprocess.poll() is not None:
                internal_logger.error("Failed to run exporter, process exited")
                return False
            global exporter_pid
            exporter_pid = networkprocess.pid
            internal_logger.info("Exporter pid: {}".format(exporter_pid))
            return True
        except Exception:
            internal_logger.exception("Failed to run exporter")
            return False

    def connect(self) -> bool:
        manager_port = self.get_manager_port()
        if not manager_port:
            internal_logger.error("Manager port not found")
            return False
        self.manager = get_manager(("localhost", manager_port), config.manager_password)
        self.manager.connect()
        if (
            is_main_process
            and self.user_options.key
            and self.user_options.service
            and self.user_options.tags is not None
        ):
            self.manager.register_service(
                self.user_options.key, self.user_options.service, self.user_options.tags
            )
            internal_logger.info("Registered service to manager")
        if not self.manager.fully_initialized.wait(
            config.manager_initialization_timeout
        ):
            internal_logger.error("Manager initialization timeout")
            return False
        internal_logger.info("Connected to manager")
        return True

    def get_manager_port(self) -> Optional[int]:
        if manager_port:
            return manager_port
        if not exporter_pid or not unique_id:
            internal_logger.critical(
                "Exporter pid or unique_id are not set",
                data={
                    "exporter_pid": exporter_pid,
                    "unique_id": unique_id,
                },
            )
            return None
        seconds = 0
        file_name = get_shared_state_file_name(str(exporter_pid), unique_id)
        while seconds < config.wait_for_manager_port_timeout:
            if not get_hud_running_mode():
                internal_logger.warning("HUD is not enabled, stopping worker")
                return None
            if not should_run_worker() and seconds > config.min_time_for_manager_port:
                # We want give grace period to the exporter to start if the main thread has finished
                internal_logger.warning(
                    "Worker stopped before getting manager port",
                    data={"seconds": seconds},
                )
                return None
            if not is_alive(exporter_pid):
                internal_logger.error(
                    "Exporter process is not running while getting manager port"
                )
                return None
            try:
                with open(file_name, "r") as f:
                    result = f.read()
                    internal_logger.info("Got manager port", data={"port": result})
                    return int(result)
            except FileNotFoundError:
                time.sleep(1)
                seconds += 1
        return None

    @suppress_exceptions_sync(default_return_factory=lambda: None)
    @disable_on_manager_exception
    def _check_queues(self) -> None:
        if not self.manager:
            internal_logger.error("Manager is not set")
            return

        current_shared_memories = list(self._queues.keys())
        shared_memories = []
        try:
            shared_memories = list(self.manager.get_shared_memory_names())
        except Exception:
            internal_logger.exception("Failed to get shared memories")
            pass

        for shared_memory_name in shared_memories:
            if shared_memory_name not in current_shared_memories:
                self._register_new_queue(shared_memory_name)

        for shared_memory_name in current_shared_memories:
            if shared_memory_name not in shared_memories:
                internal_logger.info(
                    "Removing shared memory", data={"name": shared_memory_name}
                )
                queue_info = self._queues.pop(shared_memory_name, None)
                if queue_info is not None:
                    queue_info.shared_memory.close()

    def _register_new_queue(self, queue_name: str) -> None:
        if not self.manager:
            internal_logger.error("Manager is not set")
            return
        shared_memory = self.manager.get_shared_memory(queue_name)
        if shared_memory:
            shared_memory.open()
            queue = BufferBackedCyclicQueue(
                shared_memory.mmap_obj,
                BaseInfoStructure,
                shared_memory.mmap_obj.size(),
            )
            self._queues[queue_name] = QueueInfo(shared_memory, queue)

    def write(self, events: Union[Dict[Any, Any], List[Any]], event_type: str) -> None:
        try:
            if event_type != "Logs":
                internal_logger.info(
                    "Writing events to queue", data={"type": event_type}
                )
            if not self.broker:
                internal_logger.error("Broker is not set")
                return

            data = json.dumps([events, event_type]).encode()
            queue_name = self.broker.request_queue(get_current_pid(), timeout=8)
            if not queue_name:
                internal_logger.error("Failed to get queue name")
                return

            if queue_name not in self._queues:
                self._register_new_queue(queue_name)

            try:
                self._queues[queue_name].queue.push(data)
            finally:
                self.broker.release_queue(queue_name)
        except Exception:
            internal_logger.exception("Failed to write events to queue")
            raise

    def register_tasks(self) -> None:
        current_time = time.time()
        self.tasks.append(
            Task(
                lambda: self.process_queue(worker_queue),
                lambda: config.process_queue_flush_interval,
                current_time,
            )
        )
        self.tasks.append(
            Task(
                self._set_session_id,
                lambda: config.session_id_refresh_interval,
                current_time,
            )
        )
        self.tasks.append(
            Task(
                self._dump_declarations,
                lambda: config.declarations_flush_interval,
                current_time,
            )
        )
        self.tasks.append(
            Task(
                self._dump_endpoint_declarations,
                lambda: config.declarations_flush_interval,
                current_time,
            )
        )
        self.tasks.append(
            Task(
                self._dump_kafka_declarations,
                lambda: config.declarations_flush_interval,
                current_time,
            )
        )
        self.tasks.append(
            Task(
                self._dump_invocations,
                lambda: config.invocations_flush_interval,
                current_time,
            )
        )
        self.tasks.append(
            Task(
                self._dump_flow_metrics,
                lambda: config.flow_metrics_flush_interval,
                current_time,
            )
        )
        self.tasks.append(
            Task(self._dump_logs, lambda: config.logs_flush_interval, current_time)
        )
        self.tasks.append(
            Task(
                self._send_performance,
                lambda: config.performance_report_interval,
                current_time,
            )
        )
        self.tasks.append(
            Task(
                self._send_loaded_modules,
                lambda: config.modules_report_interval,
                current_time,
            )
        )
        self.tasks.append(
            Task(
                self._check_exporter,
                lambda: config.exporter_is_up_check_interval,
                current_time,
            )
        )
        self.tasks.append(
            Task(
                self._check_queues,
                lambda: config.worker_check_queues_interval,
                current_time,
            )
        )
        self.tasks.append(
            Task(
                self._update_configuration,
                lambda: config.worker_configuration_update_check_interval,
                current_time,
            )
        )

    @suppress_exceptions_sync(default_return_factory=lambda: None)
    @disable_on_manager_exception
    def _update_configuration(self) -> None:
        if not self.manager:
            internal_logger.error("Manager is not set")
            return
        configuration = self.manager.updated_config
        if not configuration:
            return

        if configuration["id"] == self.remote_config_id:
            return
        internal_logger.info("Updating configuration", data=configuration)
        self.remote_config_id = configuration["id"]
        for key, value in configuration["config"].items():
            if key in config.updatable_configuration_keys:
                setattr(config, key, value)
            else:
                internal_logger.warning(
                    "Non updatable configuration key", data={"key": key}
                )
        if configuration["is_throttled"]:
            internal_logger.info("Throttling HUD")
            disable_hud(should_dump_logs=False, should_clear=False)

    @suppress_exceptions_sync(default_return_factory=lambda: None)
    @disable_on_manager_exception
    def process_queue(self, queue: "deque[Any]") -> None:
        qsize = len(queue)
        if not qsize:
            return
        if hasattr(queue, "maxlen") and queue.maxlen == qsize:
            internal_logger.warning("Event queue is full")
        try:
            for item in iter(queue.popleft, None):
                if isinstance(item, Declaration):
                    self.declarations.add_declaration(item)
                elif isinstance(item, EndpointDeclaration):
                    self.endpoints_declarations.add_declaration(item)
                elif isinstance(item, KafkaDeclaration):
                    self.kafka_declarations.add_declaration(item)
                else:
                    internal_logger.warning("Invalid item type: {}".format(type(item)))
                qsize -= 1
                if qsize == 0:
                    break
        except IndexError:
            pass

    def _set_session_id(self) -> None:
        if self.session_id:
            return
        if not self.manager:
            internal_logger.error("Manager is not set")
            return
        try:
            session_id = self.session_id = self.manager.session_id
        except Exception:
            internal_logger.exception("Failed to get session id")
            raise
        if session_id:
            internal_logger.info("Session id set", data={"session_id": self.session_id})
            if is_main_process:
                user_logger.log(*UsersLogs.HUD_INITIALIZED_SUCCESSFULLY)

    def _finalize(self) -> None:
        if not get_hud_running_mode():
            internal_logger.info("HUD is not enabled, skipping finalization")
            return
        internal_logger.info("Finalizing worker")
        self.process_queue(worker_queue)
        self._dump_declarations()
        self._dump_endpoint_declarations()
        self._dump_kafka_declarations()
        self._dump_invocations()
        self._dump_flow_metrics()
        dump_logs_sync(self.session_id)

    @suppress_exceptions_sync(default_return_factory=lambda: None)
    @disable_on_manager_exception
    def _dump_declarations(self) -> None:
        latest_declarations = self.declarations.get_and_clear_declarations()
        if latest_declarations:
            declarations = [
                declaration.to_json_data() for declaration in latest_declarations
            ]
            self.write(declarations, latest_declarations[0].get_type())

    @suppress_exceptions_sync(default_return_factory=lambda: None)
    @disable_on_manager_exception
    def _dump_endpoint_declarations(self) -> None:
        latest_declarations = self.endpoints_declarations.get_and_clear_declarations()
        if latest_declarations:
            declarations = [
                declaration.to_json_data() for declaration in latest_declarations
            ]
            self.write(declarations, latest_declarations[0].get_type())

    @suppress_exceptions_sync(default_return_factory=lambda: None)
    @disable_on_manager_exception
    def _dump_kafka_declarations(self) -> None:
        latest_declarations = self.kafka_declarations.get_and_clear_declarations()
        if latest_declarations:
            declarations = [
                declaration.to_json_data() for declaration in latest_declarations
            ]
            self.write(declarations, latest_declarations[0].get_type())

    @suppress_exceptions_sync(default_return_factory=lambda: None)
    @disable_on_manager_exception
    def _dump_invocations(self) -> None:
        invocations = self.invocations_handler.get_and_clear_invocations()
        if invocations:
            invocations_to_send = [
                invocation.to_json_data() for invocation in invocations
            ]
            self.write(invocations_to_send, invocations[0].get_type())
            if not self.did_dump_metrics and self.session_id:
                if is_main_process:
                    user_logger.log(*UsersLogs.HUD_FIRST_METRICS_COLLECTED)
                    self.did_dump_metrics = True

    @suppress_exceptions_sync(default_return_factory=lambda: None)
    @disable_on_manager_exception
    def _dump_flow_metrics(self) -> None:
        if not globals.metrics_aggregator:
            internal_logger.error("Metrics aggregator is not initialized")
            return
        metrics_by_type = globals.metrics_aggregator.get_and_clear_metrics()
        for metrics in metrics_by_type.values():
            if metrics:
                self.write(
                    [metric.to_json_data() for metric in metrics], metrics[0].get_type()
                )

    @suppress_exceptions_sync(default_return_factory=lambda: None)
    @disable_on_manager_exception
    def _dump_logs(self) -> None:
        logs = send_logs_handler.get_and_clear_logs()
        if logs.logs:
            try:
                self.write(logs.to_json_data(), "Logs")
            except Exception:
                internal_logger.exception(
                    "Failed to write logs to the queue, will try to dump them"
                )
                new_logs = (
                    send_logs_handler.get_and_clear_logs()
                )  # For getting the logs of the exception, and not making it in the next run
                logs.logs.extend(new_logs.logs)
                dump_logs_sync(self.session_id)
                raise

    @suppress_exceptions_sync(default_return_factory=lambda: None)
    @disable_on_manager_exception
    def _send_loaded_modules(self) -> None:
        modules = get_loaded_modules()
        self.write(modules.to_json_data(), modules.get_type())

    @suppress_exceptions_sync(default_return_factory=lambda: None)
    @disable_on_manager_exception
    def _send_performance(self) -> None:
        performance = self.performance_monitor.monitor_process()
        if config.log_performance:
            internal_logger.info("performance data", data=performance.to_json_data())
        self.write(performance.to_json_data(), performance.get_type())

    def _send_runtime(self) -> None:
        runtime = runtime_info()
        if config.log_runtime:
            internal_logger.info("Worker Runtime data", data=runtime.to_json_data())
        self.write(runtime.to_json_data(), runtime.get_type())

    @suppress_exceptions_sync(default_return_factory=lambda: None)
    @disable_on_manager_exception
    def _check_exporter(self) -> None:
        if not exporter_pid or not is_alive(exporter_pid):
            internal_logger.error("Exporter is not running, shutting down")
            self.close_shared_memories(should_delete=True)
            self.kill_manager_gracefully()

            disable_hud(
                should_dump_logs=True,
                session_id=self.session_id,
            )

    def kill_manager_gracefully(self) -> None:
        if self.manager and self.manager_pid and is_alive(self.manager_pid):
            try:
                internal_logger.info("Sending SIGTERM to manager process")
                os.kill(self.manager_pid, signal.SIGTERM)

                timeout = 5
                poll_interval = 0.5

                start_time = time.time()
                while time.time() - start_time < timeout:
                    if not is_alive(self.manager_pid):
                        internal_logger.info("Manager process exited")
                        return
                    time.sleep(poll_interval)

                internal_logger.warning(
                    "Manager process did not exit, sending SIGKILL."
                )
                os.kill(self.manager_pid, signal.SIGKILL)

            except Exception:
                internal_logger.exception("Error terminating manager process")

    def close_shared_memories(self, should_delete: bool) -> None:
        for queue_info in self._queues.values():
            try:
                queue_info.shared_memory.close()
                if should_delete:
                    if os.path.exists(queue_info.shared_memory.file_name):
                        os.remove(queue_info.shared_memory.file_name)
            except Exception:
                if os.path.exists(queue_info.shared_memory.file_name):
                    internal_logger.exception("Failed to close shared memory")
        self._queues.clear()


registered_after_fork = False
is_main_process = True


def init_hud_thread_in_fork(
    key: Optional[str] = None,
    service: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
) -> None:
    global is_main_process
    is_main_process = False
    global worker_thread
    worker_thread = None
    init_hud_thread(key, service, tags)


def init_hud_thread(
    key: Optional[str] = None,
    service: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
) -> None:
    internal_logger.set_component("main")

    start_time = time.time()

    global registered_after_fork
    if config.run_after_fork and not registered_after_fork:
        registered_after_fork = True
        after_fork_in_child.register_callback(
            lambda: init_hud_thread_in_fork(key, service, tags)
        )

    user_logger.set_is_main_process(is_main_process)

    set_hook()  # Ensure the hook is set before starting the worker thread

    global worker_thread
    if worker_thread is not None and worker_thread.is_alive():
        internal_logger.info("Worker thread is already running")
        return

    if not should_run_hud():
        if is_main_process:
            hud_enable = get_hud_enable()
            if not hud_enable:
                user_logger.log(*UsersLogs.HUD_ENABLE_NOT_SET)
            elif not valid_hud_enable(hud_enable):
                user_logger.log(*UsersLogs.HUD_ENABLE_INVALID)
        disable_hud(should_dump_logs=False)
        return

    user_options = init_user_options(key, service, tags, is_main_process)

    if (
        user_options.key is None
        or user_options.service is None
        or user_options.tags is None
    ):
        disable_hud(
            should_dump_logs=False,
            should_clear=True,
        )
        return

    # The main thread must block, at least until the `exporter_pid` global is populated.

    ready_event = threading.Event()

    def target() -> None:
        worker = Worker(ready_event, user_options)
        try:
            worker.run()
        except Exception:
            user_logger.log(
                *UsersLogs.HUD_EXCEPTION_IN_WORKER,
            )
            internal_logger.exception("Exception in worker thread target")
        finally:
            with internal_logger.stage_context("cleanup"):
                worker.cleanup()
                with contextlib.suppress(Exception):
                    if worker.manager and not get_hud_running_mode():
                        worker.manager.deregister_process(os.getpid())

                disable_hud(
                    should_dump_logs=True,
                    session_id=worker.session_id,
                )

    worker_thread = threading.Thread(target=target)
    worker_thread.start()
    if not ready_event.wait(config.exporter_start_timeout):
        internal_logger.error("Exporter startup timeout")
        user_logger.log(
            *UsersLogs.HUD_EXPORTER_STARTUP_TIMEOUT,
        )
        disable_hud(should_dump_logs=True)
    internal_logger.info("HUD initialized", data={"duration": time.time() - start_time})
