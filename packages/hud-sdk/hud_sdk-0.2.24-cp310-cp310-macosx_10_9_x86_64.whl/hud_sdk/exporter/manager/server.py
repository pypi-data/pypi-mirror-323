__all__ = ["get_manager", "Manager"]

import os
import threading

from .manager import (
    AcquirerProxy,
    Broker,
    BrokerProxy,
    EventProxy,
    Manager,
    NamespaceProxy,
    OwnedLock,
    get_manager,
)

namespace_lock = OwnedLock()


def get_namespace_lock() -> OwnedLock:
    return namespace_lock


Manager.register(
    "_get_namespace_lock", callable=get_namespace_lock, proxytype=AcquirerProxy
)


class Namespace:
    pass


ns = Namespace()


def get_ns() -> object:
    return ns


Manager.register("_get_ns", callable=get_ns, proxytype=NamespaceProxy)

Manager.register("_get_manager_pid", callable=os.getpid)


fully_initialized_event = threading.Event()


def _get_fully_initialized_event() -> threading.Event:
    return fully_initialized_event


Manager.register(
    "_get_fully_initialized_event",
    callable=_get_fully_initialized_event,
    proxytype=EventProxy,
)

service_registered_event = threading.Event()


def _get_service_registered_event() -> threading.Event:
    return service_registered_event


Manager.register(
    "_get_service_registered_event",
    callable=_get_service_registered_event,
    proxytype=EventProxy,
)


broker = Broker()


def _get_broker() -> Broker:
    return broker


Manager.register("_get_broker", callable=_get_broker, proxytype=BrokerProxy)
