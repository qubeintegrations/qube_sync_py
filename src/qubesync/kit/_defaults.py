"""What the kit does when your app hasn't said: the client made from the settings, the
in-process queue and the in-memory dedupe store."""
import logging
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, Callable, Dict, Optional, Set

log = logging.getLogger("qubesync.kit")

__all__ = ["client", "InProcessQueue", "MemoryDedupe", "in_process_enqueue", "memory_dedupe"]

_lock = threading.Lock()


def client():
    # type: () -> Any
    """QuBe Sync's API, through the library's Client, made once from the api_key and base_url
    settings (QUBE_API_KEY and QUBE_URL): create_connection, start_run, answer, search,
    get_run, cancel_run, queue and the rest. A retried call is logged."""
    from ._settings import settings

    config = settings()
    if config.is_set("client"):
        return config.client
    with _lock:
        if config._client is None:
            from ..v2 import Client

            config._client = Client(config.api_key, base_url=config.base_url, on_retry=_log_retry)
        return config._client


def _log_retry(retry):
    # type: (Dict[str, Any]) -> None
    """A call QuBe Sync didn't answer, sent again (safe calls only, within 60 seconds)."""
    why = retry["status"] or retry["error"]
    method, url, delay = retry["method"], retry["url"], retry["delay"]
    log.warning("QuBe Sync: retrying %s %s (%s) in %.1f s", method, url, why, delay)


class InProcessQueue(object):
    """The enqueue setting's default: runs jobs on one worker thread in this process, in the
    order they came, and logs a job that fails.

    Point enqueue at a durable queue before production: a restart loses what this hasn't run,
    and QuBe Sync had its 2xx when the event was handed on, so it won't send it again. With
    Celery, make a task that calls qubesync.kit.run(operation, record_id, body) and set
    enqueue=lambda *job: run_task.delay(*job); with RQ, enqueue=lambda *job:
    queue.enqueue(qubesync.kit.run, *job).
    """

    def __init__(self):
        # type: () -> None
        self._executor = None  # type: Optional[ThreadPoolExecutor]
        self._warned = False
        self._lock = threading.Lock()

    def submit(self, fn, *args):
        # type: (Callable[..., Any], *Any) -> Future
        with self._lock:
            if not self._warned:
                self._warned = True
                log.warning(
                    "QuBe Sync: webhooks run on a thread in this process (the enqueue setting's "
                    "default), so a restart loses what hasn't run: set enqueue to a durable queue "
                    "before production."
                )
            if self._executor is None:
                self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="qubesync")
            return self._executor.submit(_logged, fn, *args)

    def shutdown(self, wait=True):
        # type: (bool) -> None
        with self._lock:
            if self._executor is not None:
                self._executor.shutdown(wait=wait)
                self._executor = None


def _logged(fn, *args):
    # type: (Callable[..., Any], *Any) -> None
    try:
        fn(*args)
    except Exception:
        log.exception("QuBe Sync: a webhook job failed")


class MemoryDedupe(object):
    """The dedupe setting's default: the delivery ids already taken, in this process's memory.
    Keep them in your database (or a shared cache) instead, so a retry that reaches another
    worker, or comes after a restart, is still caught: any object with seen(key) and
    remember(key) will do."""

    def __init__(self):
        # type: () -> None
        self._keys = set()  # type: Set[str]
        self._lock = threading.Lock()
        self._warned = False

    def seen(self, key):
        # type: (str) -> bool
        with self._lock:
            if not self._warned:
                self._warned = True
                log.warning(
                    "QuBe Sync: notification delivery ids are kept in memory (the dedupe setting's "
                    "default), so a retry after a restart, or on another worker, is taken again: "
                    "set dedupe to a store in your database or cache."
                )
            return key in self._keys

    def remember(self, key):
        # type: (str) -> None
        with self._lock:
            self._keys.add(key)


_queue = InProcessQueue()
_dedupe = MemoryDedupe()


def default_queue():
    # type: () -> InProcessQueue
    return _queue


def in_process_enqueue(operation, record_id, body):
    # type: (str, str, str) -> None
    """The enqueue setting's default: qubesync.kit.run on the in-process queue."""
    from ._job import run

    _queue.submit(run, operation, record_id, body)


def memory_dedupe():
    # type: () -> MemoryDedupe
    return _dedupe


def _reset_defaults():
    # type: () -> None
    global _queue, _dedupe
    _queue.shutdown(wait=True)
    _queue = InProcessQueue()
    _dedupe = MemoryDedupe()
