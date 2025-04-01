import asyncio
import contextlib
import json
import os
import signal
import time
import uuid
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Union  # noqa: F401

import psutil  # noqa: F401

from ..client import (
    AsyncHandlerReturnType,  # noqa: F401
    Client,  # noqa: F401
    HudThrottledException,
    SyncHandlerReturnType,  # noqa: F401
    get_client,
)  # noqa: F401
from ..collectors.modules import get_installed_packages
from ..collectors.performance import PerformanceMonitor
from ..collectors.runtime import runtime_info
from ..config import config
from ..logging import internal_logger, send_logs_handler
from ..native import get_hud_running_mode
from ..process_utils import is_alive
from ..schemas import events
from ..schemas.events import WorkloadData
from ..user_options import init_user_options
from ..utils import (
    AtomicFileWriter,
    TemporaryFile,
    get_shared_state_file_name,
    suppress_exceptions_async,
    suppress_exceptions_sync,
)
from ..workload_metadata import get_cpu_limit, get_workload_metadata
from .manager.server import Manager, get_manager  # noqa: F401
from .queue import BaseInfoStructure, BufferBackedCyclicQueue
from .task_manager import TaskManager

if TYPE_CHECKING:
    from .manager.manager import AcquirerProxy, BrokerProxy, SharedMemory  # noqa: F401


class QueueInfo:
    def __init__(
        self,
        queue: BufferBackedCyclicQueue[BaseInfoStructure],
        shared_memory: "SharedMemory",
    ):
        self.queue = queue
        self.shared_memory = shared_memory
        self._process_task = None  # type: Optional[asyncio.Task[None]]

    @property
    def process_task(self) -> Optional["asyncio.Task[None]"]:
        return self._process_task

    @process_task.setter
    def process_task(self, task: Optional["asyncio.Task[None]"]) -> None:
        self._process_task = task


class Exporter:
    def __init__(
        self,
        unique_id: str,
        loop: asyncio.AbstractEventLoop,
        shared_memory_size: int = config.exporter_shared_memory_size,
    ):
        self.unique_id = unique_id
        self.shared_memory_size = shared_memory_size
        self.client = (
            None
        )  # type: Optional[Client[AsyncHandlerReturnType] | Client[SyncHandlerReturnType]]

        self.task_manager = TaskManager()
        self.pod_cpu_limit = get_cpu_limit()
        self.perf_monitor = PerformanceMonitor("exporter", self.pod_cpu_limit)
        self.manager = None  # type: Optional[Manager]
        self._queues = {}  # type: Dict[str, QueueInfo]
        self._connected_processes = set()  # type: Set[int]
        self._connected_processes_first_run = True
        self._broker = None  # type: Optional[BrokerProxy]
        self._manager_pid = None  # type: Optional[int]
        self.loop = loop
        loop.set_exception_handler(exception_handler)
        loop.add_signal_handler(
            signal.SIGTERM, lambda: asyncio.create_task(self.handle_exit())
        )
        loop.add_signal_handler(
            signal.SIGINT, lambda: asyncio.create_task(self.handle_exit())
        )

    async def handle_exit(self) -> None:
        internal_logger.info("Received termination signal, stopping exporter")
        self.stop_tasks()

    @suppress_exceptions_async(default_return_factory=lambda: None)
    async def _get_remote_config(self) -> None:
        remote_config = {}
        if self.client:
            if self.client.is_async:
                remote_config = await self.client.get_remote_config()
            else:
                remote_config = self.client.get_remote_config()  # type: ignore[assignment]

        if not remote_config:
            return

        internal_logger.debug("Received remote configuration", data=remote_config)

        if self.manager:
            await self.loop.run_in_executor(
                None, self.manager.set_updated_config, remote_config
            )

    async def send_event(self, event: events.Event) -> None:
        if self.client:
            if self.client.is_async:
                await self.client.send_event(event)
            else:
                self.client.send_event(event)

    async def send_json(self, data: Any, request_type: str) -> None:
        if self.client:
            handler = self.client.handler_from_json(data, request_type)
            if self.client.is_async:
                await handler(data, request_type)
            else:
                handler(data, request_type)

    @suppress_exceptions_async(default_return_factory=lambda: None)
    async def _log_runtime(self) -> None:
        runtime = runtime_info()
        internal_logger.info("Exporter Runtime data", data=runtime.to_json_data())

    @suppress_exceptions_async(default_return_factory=lambda: None)
    async def _send_installed_packages(self) -> None:
        packages = await self.loop.run_in_executor(None, get_installed_packages)
        await self.send_event(packages)

    @suppress_exceptions_async(default_return_factory=lambda: None)
    async def _send_workload_data(self, workload_metadata: WorkloadData) -> None:
        await self.send_event(workload_metadata)

    @suppress_exceptions_async(default_return_factory=lambda: None)
    async def _process_housekeeping(self) -> None:
        if not self.manager:
            return

        current_connected_processes = await self.loop.run_in_executor(
            None, self.manager.get_connected_processes
        )
        current_connected_processes = current_connected_processes.copy()
        if current_connected_processes != self._connected_processes:
            self._connected_processes = current_connected_processes
            internal_logger.info(
                "Connected processes updated",
                data={"connected_processes": current_connected_processes},
            )

        if self.manager and not current_connected_processes:
            if self._connected_processes_first_run:
                internal_logger.error("Manager never got any connected processes")
            else:
                internal_logger.info("No connected processes, Shutting down")
            self.stop_tasks()
        elif self.manager:
            for process in current_connected_processes:
                if not is_alive(process):
                    internal_logger.info(
                        "Process {} has exited, Deregistering".format(process)
                    )
                    await self.loop.run_in_executor(
                        None, self.manager.deregister_process, process
                    )

        self._connected_processes_first_run = False

    async def _create_queue(self) -> str:
        if not self.manager:
            raise RuntimeError("Manager is not initialized")

        name = str(uuid.uuid4())
        shared_memory = await self.loop.run_in_executor(
            None, self.manager.create_shared_memory, name
        )
        shared_memory.open()

        queue = BufferBackedCyclicQueue(
            shared_memory.mmap_obj,
            BaseInfoStructure,
            shared_memory.mmap_obj.size(),
        )

        self._queues[shared_memory.file_name] = QueueInfo(queue, shared_memory)
        internal_logger.info(
            "Created new queue",
            data={"queue_name": name, "shared_memory_name": shared_memory.file_name},
        )

        return shared_memory.file_name

    async def _remove_queue(self, queue_name: str) -> None:
        queue_info = self._queues.get(queue_name)
        if not queue_info:
            internal_logger.warning(
                "Attempted to remove non-existent queue",
                data={"queue_name": queue_name},
            )
            return

        if not self.manager:
            internal_logger.critical("Manager is not initialized")
            return

        try:
            await self.loop.run_in_executor(
                None, self.manager.delete_shared_memory, queue_name
            )
            queue_info.shared_memory.close()

            internal_logger.info(
                "Removed queue and its shared memory",
                data={
                    "queue_name": queue_name,
                    "shared_memory_name": queue_info.shared_memory.file_name,
                },
            )
        except Exception as e:
            internal_logger.exception(
                "Failed to remove queue resources",
                data={"queue_name": queue_name, "error": str(e)},
            )

        if queue_info.process_task:
            queue_info.process_task.cancel()

        del self._queues[queue_name]

    @suppress_exceptions_sync(default_return_factory=lambda: None)
    def _check_manager_lock(self) -> None:
        if self.manager:
            self._check_lock(self.manager.namespace_lock, "Namespace lock")

    def _check_lock(self, lock: "AcquirerProxy", lock_name: str) -> None:
        owner_info = lock.get_owner_and_locktime()
        if not owner_info:
            return
        owner, lock_time = owner_info
        current_time = time.time()
        elapsed_time = current_time - lock_time

        if isinstance(owner, int):
            internal_logger.critical(
                "Lock has been held by local thread, without process info",
                data={"lock_name": lock_name, "lock_time": lock_time},
            )
            self.stop_tasks()
        elif not is_alive(owner[0]):
            internal_logger.critical(
                "Lock has been held by process which has exited",
                data={"lock_name": lock_name, "owner": owner[0]},
            )
            self.stop_tasks()
        elif elapsed_time > config.manager_lock_critical_threshold:
            internal_logger.critical(
                "Lock has been held by process longer than critical threshold",
                data={
                    "lock_name": lock_name,
                    "owner": owner[0],
                    "critical_threshold": config.manager_lock_critical_threshold,
                },
            )
            self.stop_tasks()
        elif elapsed_time > config.manager_lock_warning_threshold:
            internal_logger.warning(
                "Lock has been held by process longer than warning threshold",
                data={
                    "lock_name": lock_name,
                    "owner": owner[0],
                    "warning_threshold": config.manager_lock_warning_threshold,
                },
            )

    @suppress_exceptions_async(default_return_factory=lambda: None)
    async def _check_leaked_queues(self) -> None:
        if not self._broker:
            return
        owned_queues = await self.loop.run_in_executor(
            None, self._broker.get_owned_queues
        )
        for queue_name, data in owned_queues.items():
            owner, lock_time = data
            current_time = time.time()
            elapsed_time = current_time - lock_time

            if not is_alive(owner):
                internal_logger.critical(
                    "Queue has been held by process which has exited",
                    data={"queue_name": queue_name, "owner": owner},
                )
                await self.handle_leaked_queue(queue_name)
            elif elapsed_time > config.manager_lock_critical_threshold:
                internal_logger.critical(
                    "Queue has been held by process longer than critical threshold",
                    data={
                        "queue_name": queue_name,
                        "owner": owner,
                        "critical_threshold": config.manager_lock_critical_threshold,
                    },
                )
                await self.handle_leaked_queue(queue_name)
            elif elapsed_time > config.manager_lock_warning_threshold:
                internal_logger.warning(
                    "Queue has been held by process longer than warning threshold",
                    data={
                        "queue_name": queue_name,
                        "owner": owner,
                        "warning_threshold": config.manager_lock_warning_threshold,
                    },
                )

    @suppress_exceptions_async(default_return_factory=lambda: None)
    async def handle_leaked_queue(self, queue_name: str) -> None:
        internal_logger.info(
            "Handling leaked queue",
            data={"queue_name": queue_name},
        )

        await self._remove_queue(queue_name)

        new_queue_name = await self._create_queue()

        task = self.task_manager.register_periodic_task(
            self.queue_processor,
            config.exporter_queue_process_interval,
            new_queue_name,
            callback=self.queue_processor,
        )
        self._queues[new_queue_name].process_task = task

        internal_logger.info(
            "Replaced corrupted queue with new queue",
            data={"old_queue": queue_name, "new_queue": new_queue_name},
        )

    @suppress_exceptions_sync(default_return_factory=lambda: None)
    def _check_exporter_disabled(self) -> None:
        if not get_hud_running_mode():
            internal_logger.critical("HUD is disabled, stopping exporter")
            self.stop_tasks()

    @suppress_exceptions_async(default_return_factory=lambda: None)
    async def queue_processor(self, queue_name: str) -> None:
        if not self._broker:
            return

        result_queue_name = await self.loop.run_in_executor(
            None, self._broker.request_queue, os.getpid(), queue_name, 8
        )
        if not result_queue_name:
            return

        try:
            utilization = self._queues[result_queue_name].queue.get_utilization()
            if utilization > config.shared_memory_utilization_warning_threshold:
                internal_logger.warning(
                    "Queue utilization is", data={"utilization": utilization}
                )
            if utilization > config.shared_memory_utilization_critical_threshold:
                internal_logger.critical(
                    "Queue utilization is", data={"utilization": utilization}
                )

            while True:
                data = self._queues[result_queue_name].queue.popleft()
                if not data:
                    break
                else:
                    try:
                        data, request_type = json.loads(data)
                    except Exception:
                        internal_logger.exception(
                            "Failed to load data from queue. Queue state may be corrupted"
                        )
                        self.task_manager.register_task(
                            self.handle_leaked_queue, result_queue_name
                        )
                        return

                    self.task_manager.register_task(self.send_json, data, request_type)
        finally:
            await self.loop.run_in_executor(
                None, self._broker.release_queue, result_queue_name
            )

    @suppress_exceptions_async(default_return_factory=lambda: None)
    async def _check_manager(self) -> None:
        if not self._manager_pid:
            internal_logger.critical("Manager pid is not initialized")
            self.stop_tasks()
            return
        if not is_alive(self._manager_pid):
            internal_logger.critical("Manager process has exited")
            self.stop_tasks()

    @suppress_exceptions_async(default_return_factory=lambda: None)
    async def _dump_logs(self) -> None:
        logs = send_logs_handler.get_and_clear_logs()
        if logs:
            await self.send_json(logs.to_json_data(), "Logs")

    @suppress_exceptions_async(default_return_factory=lambda: None)
    async def _send_performance(self) -> None:
        performance = self.perf_monitor.monitor_process()
        if config.log_performance:
            internal_logger.info("performance data", data=performance.to_json_data())
        if self.client:
            await self.client.send_event(performance)

    def stop_tasks(self) -> None:
        self.task_manager.stop_running_tasks()

    @suppress_exceptions_sync(default_return_factory=lambda: None)
    def _check_existence_of_multiple_exporters(self) -> None:
        for ps in psutil.process_iter():
            try:
                if "hud_sdk.exporter" in ps.cmdline() and ps.pid != os.getpid():
                    internal_logger.warning(
                        "Multiple exporters detected. Another exporter found",
                        data={"pid": ps.pid},
                    )
            except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied):
                pass

    @suppress_exceptions_async(default_return_factory=lambda: None)
    async def _initialize_workload_metadata(self) -> None:
        workload_metadata = await get_workload_metadata(self.pod_cpu_limit)
        await self._send_workload_data(workload_metadata)
        self.task_manager.register_periodic_task(
            self._send_workload_data,
            config.workload_data_flush_interval,
            workload_metadata,
        )

    async def cleanup(self) -> None:
        with internal_logger.stage_context("cleanup"):
            internal_logger.info("Cleaning up exporter")

            for queue_name in list(self._queues.keys()):
                await self._remove_queue(queue_name)
            self._queues.clear()

            await self._dump_logs()
            # Logs after this point will not be sent to the server

            if self.client:
                if self.client.is_async:
                    await self.client.close()
                else:
                    self.client.close()
                self.client = None

            if self.manager:
                with contextlib.suppress(Exception):
                    self.manager.shutdown()
                self.manager = None

    async def throttle(self) -> None:
        internal_logger.info(
            "SDK has been throttled",
        )
        if not self.manager:
            return

        self.manager.set_updated_config(is_throttled=True)

        self.loop.call_later(
            config.exporter_process_registry_warmup_period,
            lambda: self.task_manager.register_periodic_task(
                self._process_housekeeping,
                config.exporter_process_registry_update_interval,
            ),
        )

        # The process_houskeeping task will stop the tasks once there are no connected processes
        await self.task_manager.wait_for_tasks()

    async def run(self) -> None:
        with contextlib.ExitStack() as stack:
            manager = stack.enter_context(
                get_manager(("localhost", 0), config.manager_password)
            )
            stack.enter_context(internal_logger.stage_context("setup"))

            file_name = get_shared_state_file_name(str(os.getpid()), self.unique_id)
            with AtomicFileWriter(file_name) as f:
                f.write(str(manager.address[1]))
            stack.enter_context(TemporaryFile(file_name))

            if config.testing_output_directory:
                with open(
                    os.path.join(config.testing_output_directory, "exporter_pid.txt"),
                    "w",
                ) as f:
                    print(os.getpid(), file=f)

                with open(
                    os.path.join(
                        config.testing_output_directory, "exporter_pid_written"
                    ),
                    "w",
                ) as f:
                    pass

            self.manager = manager
            manager.init_manager()
            manager.exporter_pid = os.getpid()
            manager.shared_memory_size = self.shared_memory_size
            self._broker = manager.broker
            self._manager_pid = manager.manager_pid

            if not self.manager.service_registered.wait(
                timeout=config.exporter_service_registered_timeout
            ):
                internal_logger.critical("Manager did not register service")
                await self.cleanup()
                return

            init_user_options(*self.manager.get_service(), False)

            await self._create_queue()
            manager.fully_initialized.set()
            for _ in range(config.num_of_worker_exporter_queues - 1):
                await self._create_queue()

            try:
                self.client = get_client(is_async=True)
                try:
                    if self.client.is_async:
                        await self.client.init_session()
                    else:
                        self.client.init_session()
                except HudThrottledException:
                    await self.throttle()
                    await self.cleanup()
                    return

            except Exception:
                internal_logger.exception("Failed to initialize client")
                await self.cleanup()
                return

            if self.client.session_id:
                manager.session_id = self.client.session_id
            else:
                internal_logger.warning("Client did not return a session id")

            internal_logger.info("Manager process fully initialized")

            self.task_manager.register_periodic_task(
                self._check_manager, config.exporter_manager_check_interval
            )
            for queue_name in self._queues.keys():
                task = self.task_manager.register_periodic_task(
                    self.queue_processor,
                    config.exporter_queue_process_interval,
                    queue_name,
                    callback=self.queue_processor,
                )
                self._queues[queue_name].process_task = task
            self._check_existence_of_multiple_exporters()
            self.task_manager.register_periodic_task(
                self._check_leaked_queues, config.manager_leaked_queue_check_interval
            )
            task_manager = self.task_manager
            self.loop.call_later(
                config.exporter_process_registry_warmup_period,
                lambda: task_manager.register_periodic_task(
                    self._process_housekeeping,
                    config.exporter_process_registry_update_interval,
                ),
            )

            self.task_manager.register_task(self._initialize_workload_metadata)
            self.task_manager.register_task(
                self._log_runtime
            )  # We don't need to send runtime info periodically
            self.task_manager.register_task(
                self._send_installed_packages
            )  # We don't need to send installed packages periodically
            self.task_manager.register_periodic_task(
                self._check_manager_lock, config.manager_lock_owner_check_interval
            )

            self.task_manager.register_periodic_task(
                self._check_exporter_disabled, config.exporter_disabled_check_interval
            )
            self.task_manager.register_periodic_task(
                self._dump_logs, config.logs_flush_interval
            )
            self.task_manager.register_periodic_task(
                self._send_performance, config.performance_report_interval
            )
            self.task_manager.register_periodic_task(
                self._get_remote_config,
                config.exporter_configuration_update_check_interval,
            )

            await self._get_remote_config()
            try:
                with internal_logger.stage_context("loop"):
                    await self.task_manager.wait_for_tasks()
                    internal_logger.info("Loop has exited gracefully")
            except Exception:
                internal_logger.exception("Exception in worker loop")
            finally:
                try:
                    await self.cleanup()
                except Exception:
                    pass


def exception_handler(loop: asyncio.AbstractEventLoop, context: Dict[str, Any]) -> None:
    exc = context.get("exception")  # This could be None
    message = context.get("message", "No error message")

    if exc:
        internal_logger.error(
            "Exception in exporter loop",
            data={"message": message},
            exc_info=(type(exc), exc, exc.__traceback__),
        )
    else:
        internal_logger.error(
            "Exception in exporter loop with no exception object",
            data={"message": message},
        )
