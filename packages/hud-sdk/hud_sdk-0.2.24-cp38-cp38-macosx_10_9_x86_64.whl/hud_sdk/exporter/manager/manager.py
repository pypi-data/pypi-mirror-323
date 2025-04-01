import asyncio
import mmap
import multiprocessing
import os
import queue
import tempfile
import time
from functools import wraps
from multiprocessing.managers import BaseManager, BaseProxy
from threading import Event, Lock, get_ident
from typing import (
    TYPE_CHECKING,
    Any,
    BinaryIO,
    Callable,
    Coroutine,
    Dict,
    List,  # noqa: F401
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
    cast,
    overload,
)

if TYPE_CHECKING:
    from typing import TypedDict

    class RemoteConfig(TypedDict):
        config: Dict[str, int]
        is_throttled: bool
        id: str


import uuid

from ...process_utils import get_current_pid
from .errors import ManagerException


class QueueRequest:
    def __init__(self, owner_id: int, queue_name: Optional[str] = None) -> None:
        self.owner_id = owner_id
        self.queue_name = queue_name
        self.result_event = Event()
        self.timeout_event = Event()
        self.result_lock = Lock()
        self.result = None  # type: Optional[str]

    def get_queue(self, timeout: float) -> Optional[str]:
        got_it = self.result_event.wait(timeout if timeout > 0 else None)
        with self.result_lock:
            if not got_it:
                self.timeout_event.set()
                # We need to check again after the timeout event is set, as the request might have been fulfilled
                got_it = self.result_event.is_set()
                if not got_it:
                    return None
            return self.result

    def fulfill(self, queue_name: str) -> bool:
        with self.result_lock:
            if not self.timeout_event.is_set():
                self.result = queue_name
                self.result_event.set()
                return True
            return False


class Broker:
    def __init__(self) -> None:
        self._available_queues = []  # type: List[str]
        self._requests = queue.Queue()  # type: queue.Queue[QueueRequest]
        # Missed requests are requests for specific queues that were not available when requested.
        # They will be prioritized over general requests when a queue is released.
        self._missed_requests = queue.Queue()  # type: queue.Queue[QueueRequest]
        self._lock = Lock()
        self._owned_queues = {}  # type: Dict[str, Tuple[int, float]]

    def register_queue(self, queue_name: str) -> None:
        with self._lock:
            self._available_queues.append(queue_name)

    def deregister_queue(self, queue_name: str) -> None:
        with self._lock:
            if queue_name in self._owned_queues:
                del self._owned_queues[queue_name]
            if queue_name in self._available_queues:
                self._available_queues.remove(queue_name)

    def request_queue(
        self,
        owner_id: int,
        queue_name: Optional[str] = None,
        timeout: float = 0.0,
    ) -> Optional[str]:
        with self._lock:
            if queue_name:
                if queue_name in self._available_queues:
                    self._owned_queues[queue_name] = (owner_id, time.time())
                    self._available_queues.remove(queue_name)
                    return queue_name
            else:
                if self._available_queues:
                    queue_name = self._available_queues.pop(0)
                    self._owned_queues[queue_name] = (owner_id, time.time())
                    return queue_name
            queue_request = QueueRequest(owner_id, queue_name)
            self._requests.put(queue_request)

        return queue_request.get_queue(timeout)

    def release_queue(self, qname: str) -> None:
        with self._lock:
            if qname not in self._owned_queues:
                return
            del self._owned_queues[qname]

            tmp_requests = queue.Queue()  # type: queue.Queue[QueueRequest]
            while not self._missed_requests.empty():
                queue_request = self._missed_requests.get_nowait()
                if queue_request.queue_name == qname:
                    if queue_request.fulfill(qname):
                        self._owned_queues[qname] = (
                            queue_request.owner_id,
                            time.time(),
                        )
                        return
                    continue
                tmp_requests.put(queue_request)

            self._missed_requests = tmp_requests

            while not self._requests.empty():
                queue_request = self._requests.get_nowait()
                if queue_request.queue_name is None:
                    if queue_request.fulfill(qname):
                        self._owned_queues[qname] = (
                            queue_request.owner_id,
                            time.time(),
                        )
                        return
                    continue
                if queue_request.queue_name == qname:
                    if queue_request.fulfill(qname):
                        self._owned_queues[qname] = (
                            queue_request.owner_id,
                            time.time(),
                        )
                        return
                    continue
                else:
                    self._missed_requests.put(queue_request)
                    continue

            self._available_queues.append(qname)
            return

    def get_owned_queues(self) -> Dict[str, Tuple[int, float]]:
        with self._lock:
            return self._owned_queues


class OwnedLock:
    """
    This class implements a lock, with the addition of an owner field.
    """

    def __init__(self) -> None:
        self._block = Lock()
        self._owner = None  # type: Union[int, Tuple[int, int], None]
        self._lock_time = 0.0

    def _at_fork_reinit(self) -> None:
        self._block._at_fork_reinit()  # type: ignore[attr-defined]
        self._owner = None
        self._lock_time = 0.0

    def acquire(
        self,
        blocking: bool = True,
        timeout: int = -1,
        *,
        ident: Optional[Tuple[int, int]] = None,
    ) -> bool:
        """Acquire a lock, blocking or non-blocking."""
        rc = self._block.acquire(blocking, timeout)
        if rc:
            if ident:
                me = ident  # type: Union[int, Tuple[int, int]]
            else:
                me = get_ident()
            self._owner = me
            self._lock_time = time.time()
        return rc

    def release(self, *, ident: Optional[Tuple[int, int]] = None) -> None:
        """Release a lock."""
        if ident:
            me = ident  # type: Union[int, Tuple[int, int]]
        else:
            me = get_ident()
        if self._owner != me:
            raise RuntimeError("cannot release un-acquired lock")
        self._lock_time = 0.0
        self._owner = None
        self._block.release()

    def get_owner_and_locktime(
        self,
    ) -> Optional[Tuple[Union[int, Tuple[int, int]], float]]:
        if self._owner is None:
            return None
        return self._owner, self._lock_time


T = TypeVar("T")
G = TypeVar("G")
ValType = TypeVar("ValType")

AsyncFuncType = TypeVar("AsyncFuncType", bound=Callable[..., Coroutine[Any, Any, T]])
FuncType = TypeVar("FuncType", bound=Callable[..., Any])


@overload
def wrap_in_manager_exception(
    func: AsyncFuncType,
) -> AsyncFuncType: ...


@overload
def wrap_in_manager_exception(func: FuncType) -> FuncType: ...


def wrap_in_manager_exception(
    func: Union[FuncType, Callable[..., Coroutine[Any, Any, T]], Callable[..., T]]
) -> Callable[..., Any]:
    if asyncio.iscoroutinefunction(func):

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return await func(*args, **kwargs)  # type: ignore[no-any-return]
            except AttributeError:
                # Used for hasattr checks
                raise
            except Exception as e:
                raise ManagerException("Exception in manager call") from e

    else:

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)  # type: ignore[return-value]
            except AttributeError:
                # Used for hasattr checks
                raise
            except Exception as e:
                raise ManagerException("Exception in manager call") from e

    return wrapper


class BrokerProxy(BaseProxy):
    _exposed_ = (
        "request_queue",
        "release_queue",
        "register_queue",
        "get_owned_queues",
        "deregister_queue",
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    @wrap_in_manager_exception
    def request_queue(
        self, owner_id: int, queue_name: Optional[str] = None, timeout: float = 0.0
    ) -> Optional[str]:
        return self._callmethod("request_queue", (owner_id, queue_name, timeout))  # type: ignore[func-returns-value,no-any-return]

    @wrap_in_manager_exception
    def release_queue(self, qname: str) -> None:
        return self._callmethod("release_queue", (qname,))

    @wrap_in_manager_exception
    def register_queue(self, queue_name: str) -> None:
        return self._callmethod("register_queue", (queue_name,))

    @wrap_in_manager_exception
    def get_owned_queues(self) -> Dict[str, Tuple[int, float]]:
        return self._callmethod("get_owned_queues")  # type: ignore[func-returns-value,no-any-return]

    @wrap_in_manager_exception
    def deregister_queue(self, queue_name: str) -> None:
        return self._callmethod("deregister_queue", (queue_name,))


# These proxy classes are defined, but not exported in multiprocessing.managers. We modify them.
class AcquirerProxy(BaseProxy):
    _exposed_ = ("acquire", "release", "get_owner_and_locktime")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.ident = (get_current_pid(), get_ident())

    @wrap_in_manager_exception
    def acquire(self, blocking: bool = True, timeout: Optional[int] = None) -> bool:
        args = (blocking,) if timeout is None else (blocking, timeout)
        return self._callmethod("acquire", args, kwds={"ident": self.ident})  # type: ignore[func-returns-value, no-any-return]

    @wrap_in_manager_exception
    async def async_acquire(
        self, blocking: bool = True, timeout: Optional[int] = None
    ) -> bool:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.acquire, blocking, timeout)

    @wrap_in_manager_exception
    def release(self) -> None:
        return self._callmethod("release", kwds={"ident": self.ident})

    @wrap_in_manager_exception
    async def async_release(self) -> None:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.release)

    @wrap_in_manager_exception
    def get_owner_and_locktime(
        self,
    ) -> Optional[Tuple[Union[int, Tuple[int, int]], float]]:
        return self._callmethod("get_owner_and_locktime")  # type: ignore[func-returns-value,no-any-return]

    @wrap_in_manager_exception
    async def async_get_owner_and_locktime(
        self,
    ) -> Optional[Tuple[Union[int, Tuple[int, int]], float]]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.get_owner_and_locktime)

    @wrap_in_manager_exception
    def __enter__(self) -> bool:
        return self.acquire()

    @wrap_in_manager_exception
    async def __aenter__(self) -> bool:
        return await self.async_acquire()

    @wrap_in_manager_exception
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        return self.release()

    @wrap_in_manager_exception
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.async_release()


class NamespaceProxy(BaseProxy):
    _exposed_ = ("__getattribute__", "__setattr__", "__delattr__")

    @wrap_in_manager_exception
    def __getattr__(self, key: str) -> Any:
        if key[0] == "_":
            return object.__getattribute__(self, key)
        callmethod = object.__getattribute__(self, "_callmethod")
        return callmethod("__getattribute__", (key,))

    @wrap_in_manager_exception
    def __setattr__(self, key: str, value: Any) -> None:
        if key[0] == "_":
            return object.__setattr__(self, key, value)
        callmethod = object.__getattribute__(self, "_callmethod")
        return callmethod("__setattr__", (key, value))  # type: ignore[no-any-return]

    @wrap_in_manager_exception
    def __delattr__(self, key: str) -> None:
        if key[0] == "_":
            return object.__delattr__(self, key)
        callmethod = object.__getattribute__(self, "_callmethod")
        return callmethod("__delattr__", (key,))  # type: ignore[no-any-return]


class EventProxy(BaseProxy):
    _exposed_ = ("is_set", "set", "clear", "wait")

    @wrap_in_manager_exception
    def is_set(self) -> bool:
        return self._callmethod("is_set")  # type: ignore[func-returns-value,no-any-return]

    @wrap_in_manager_exception
    def set(self) -> None:
        return self._callmethod("set")

    @wrap_in_manager_exception
    def clear(self) -> None:
        return self._callmethod("clear")

    @wrap_in_manager_exception
    def wait(self, timeout: Optional[float] = None) -> bool:
        return self._callmethod("wait", (timeout,))  # type: ignore[func-returns-value,no-any-return]


class SharedMemory:
    def __init__(self, mmap_obj: mmap.mmap, file_obj: BinaryIO, file_name: str) -> None:
        self.mmap_obj = mmap_obj
        self.file_obj = file_obj
        self.file_name = file_name

    def close(self) -> None:
        self.mmap_obj.close()
        self.file_obj.close()

    def open(self) -> str:
        return self.file_name


class Manager(BaseManager):
    _cached_shared_memory_size: int
    _cached_exporter_pid: int
    _cached_manager_pid: int
    _cached_config: "dict[str, int]"

    @wrap_in_manager_exception
    def init_manager(self) -> None:
        with self.namespace_lock:
            self.namespace.connected_processes = set()
            self.namespace.key = None
            self.namespace.service = None
            self.namespace.tags = {}

    @property
    @wrap_in_manager_exception
    def namespace_lock(self) -> AcquirerProxy:
        return self._get_namespace_lock()

    @property
    @wrap_in_manager_exception
    def namespace(self) -> NamespaceProxy:
        return self._get_ns()

    @property
    @wrap_in_manager_exception
    def shared_memory_size(self) -> int:
        if not hasattr(self, "_cached_shared_memory_size"):
            self._cached_shared_memory_size = cast(
                int, self.namespace.shared_memory_size
            )
        return self._cached_shared_memory_size

    @shared_memory_size.setter
    @wrap_in_manager_exception
    def shared_memory_size(self, size: int) -> None:
        self.namespace.shared_memory_size = size

    @wrap_in_manager_exception
    def create_shared_memory(self, name: str) -> SharedMemory:
        filename = os.path.join(tempfile.gettempdir(), "hud_{}".format(name))
        with open(filename, "wb") as file:
            file.truncate(self.shared_memory_size)
            file.flush()
        shared_memory_file = open(filename, "r+b")  # type: BinaryIO
        mm = mmap.mmap(shared_memory_file.fileno(), self.namespace.shared_memory_size)
        with self.namespace_lock:
            shared_memory_names = getattr(self.namespace, "shared_memory_names", [])
            shared_memory_names.append(filename)
            self.namespace.shared_memory_names = shared_memory_names
        self.broker.register_queue(filename)
        return SharedMemory(mm, shared_memory_file, filename)

    @wrap_in_manager_exception
    def delete_shared_memory(self, name: str) -> None:
        with self.namespace_lock:
            shared_memory_names = getattr(self.namespace, "shared_memory_names", [])
            if name in shared_memory_names:
                shared_memory_names.remove(name)
                self.namespace.shared_memory_names = shared_memory_names
                self.broker.deregister_queue(name)
                if os.path.exists(name):
                    os.remove(name)

    @wrap_in_manager_exception
    def get_shared_memories(self) -> Dict[str, SharedMemory]:
        shared_memory_names = getattr(self.namespace, "shared_memory_names", [])
        shared_memory_files = {}
        for name in shared_memory_names:
            shared_memory_file = open(name, "r+b")
            mm = mmap.mmap(shared_memory_file.fileno(), self.shared_memory_size)
            shared_memory_files[name] = SharedMemory(mm, shared_memory_file, name)
        return shared_memory_files

    @wrap_in_manager_exception
    def get_shared_memory(self, name: str) -> Optional[SharedMemory]:
        shared_memory_names = getattr(self.namespace, "shared_memory_names", [])
        if name in shared_memory_names:
            shared_memory_file = open(name, "r+b")
            mm = mmap.mmap(shared_memory_file.fileno(), self.shared_memory_size)
            return SharedMemory(mm, shared_memory_file, name)
        return None

    @wrap_in_manager_exception
    def get_shared_memory_names(self) -> List[str]:
        return getattr(self.namespace, "shared_memory_names", [])

    @wrap_in_manager_exception
    def get_connected_processes(self) -> Set[int]:
        return cast(Set[int], self.namespace.connected_processes)

    @property
    @wrap_in_manager_exception
    def exporter_pid(self) -> int:
        if not hasattr(self, "_cached_exporter_pid"):
            with self.namespace_lock:
                self._cached_exporter_pid = cast(int, self.namespace.exporter_pid)
        return self._cached_exporter_pid

    @exporter_pid.setter
    @wrap_in_manager_exception
    def exporter_pid(self, pid: int) -> None:
        with self.namespace_lock:
            self.namespace.exporter_pid = pid

    @wrap_in_manager_exception
    def register_process(self, pid: int) -> None:
        with self.namespace_lock:
            processes = self.namespace.connected_processes
            processes.add(pid)
            self.namespace.connected_processes = processes

    @wrap_in_manager_exception
    def deregister_process(self, pid: int) -> None:
        with self.namespace_lock:
            processes = self.namespace.connected_processes
            processes.discard(pid)
            self.namespace.connected_processes = processes

    @wrap_in_manager_exception
    def register_service(self, key: str, service: str, tags: Dict[str, str]) -> None:
        with self.namespace_lock:
            self.namespace.key = key
            self.namespace.service = service
            self.namespace.tags = tags
        self.service_registered.set()

    @wrap_in_manager_exception
    def get_service(self) -> Tuple[str, str, Dict[str, str]]:
        with self.namespace_lock:
            return self.namespace.key, self.namespace.service, self.namespace.tags

    @property
    @wrap_in_manager_exception
    def manager_pid(self) -> int:
        if not hasattr(self, "_cached_manager_pid"):
            self._cached_manager_pid = cast(int, self._get_manager_pid()._getvalue())
        return self._cached_manager_pid

    @property
    @wrap_in_manager_exception
    def session_id(self) -> Optional[str]:
        return getattr(self.namespace, "session_id", None)

    @session_id.setter
    @wrap_in_manager_exception
    def session_id(self, session_id: str) -> None:
        with self.namespace_lock:
            self.namespace.session_id = session_id

    @property
    @wrap_in_manager_exception
    def fully_initialized(self) -> EventProxy:
        return self._get_fully_initialized_event()

    @property
    @wrap_in_manager_exception
    def service_registered(self) -> EventProxy:
        return self._get_service_registered_event()

    @property
    @wrap_in_manager_exception
    def broker(self) -> BrokerProxy:
        return self._get_broker()

    @property
    @wrap_in_manager_exception
    def updated_config(self) -> "Optional[RemoteConfig]":
        return getattr(self.namespace, "remote_config", None)

    @wrap_in_manager_exception
    def set_updated_config(
        self, config: "Optional[dict[str, int]]" = None, is_throttled: bool = False
    ) -> None:
        cached_config = getattr(self, "_cached_config", {})
        cached_throttled = getattr(self, "_cached_throttled", False)

        new_config = config if config is not None else cached_config

        if new_config != cached_config or is_throttled != cached_throttled:
            self.namespace.remote_config = {
                "config": new_config,
                "is_throttled": is_throttled,
                "id": str(uuid.uuid4()),
            }
            self._cached_config = new_config
            self._cached_throttled = is_throttled

    def _get_namespace_lock(self) -> AcquirerProxy:
        raise NotImplementedError

    def _get_ns(self) -> NamespaceProxy:
        raise NotImplementedError

    def _get_manager_pid(self) -> BaseProxy:
        raise NotImplementedError

    def _get_fully_initialized_event(self) -> EventProxy:
        raise NotImplementedError

    def _get_service_registered_event(self) -> EventProxy:
        raise NotImplementedError

    def _get_broker(self) -> BrokerProxy:
        raise NotImplementedError


def get_manager(address: Any = None, authkey: Any = None) -> Manager:
    return Manager(address, authkey, ctx=multiprocessing.get_context("spawn"))
