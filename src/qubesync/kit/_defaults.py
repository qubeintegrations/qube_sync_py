"""What the kit does when your app hasn't said: the client made from the settings, the
in-process queue, and the two dedupe stores."""
import logging
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, Callable, Dict, List, Optional

log = logging.getLogger("qubesync.kit")

__all__ = ["client", "InProcessQueue", "DatabaseDedupe", "CacheDedupe", "default_queue"]

_lock = threading.Lock()


def client():
    # type: () -> Any
    """QuBe Sync's API, through the library's Client, made once from the api_key and base_url
    settings (QUBE_API_KEY and QUBE_URL): create_connection, start_run, answer, search,
    get_run, cancel_run, queue and the rest. A non-2xx answer raises qubesync.APIError
    (status, code, message, body). A retried call is logged."""
    from ._settings import settings

    config = settings()
    if config.is_set("client"):
        return config.client
    with _lock:
        if config._client is None:
            from ..v2 import Client

            config._client = Client(config.api_key, base_url=config.base_url, on_retry=log_retry)
        return config._client


def log_retry(retry):
    # type: (Dict[str, Any]) -> None
    """A call QuBe Sync didn't answer, sent again (safe calls only, within 60 seconds)."""
    why = retry.get("status") or (retry.get("error") and type(retry["error"]).__name__)
    log.warning(
        "QuBe Sync: retrying %s %s (%s) in %.1f s", retry.get("method"), retry.get("url"), why, retry.get("delay", 0)
    )


class InProcessQueue(object):
    """The enqueue setting's default: runs each delivery on one worker thread in this process,
    in the order they came, and runs one whose work raised again later (qubesync.kit's job,
    job_attempts times in all).

    Point enqueue at a durable queue before production: a restart loses what this hasn't run,
    and QuBe Sync had its 2xx when the delivery was handed on, so it won't send it again. With
    Celery, make a task that calls qubesync.kit.run(kind, id, body) and set
    enqueue=lambda d: run_task.delay(d["kind"], d["id"], d["body"]).
    """

    def __init__(self):
        # type: () -> None
        self._executor = None  # type: Optional[ThreadPoolExecutor]
        self._timers = []  # type: List[threading.Timer]
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
            return self._executor.submit(fn, *args)

    def later(self, delay, fn, *args):
        # type: (float, Callable[..., Any], *Any) -> None
        """Submits fn after delay seconds, on a timer that dies with the process."""
        if delay <= 0:
            self.submit(fn, *args)
            return
        timer = threading.Timer(delay, self.submit, args=(fn,) + args)
        timer.daemon = True
        with self._lock:
            self._timers = [t for t in self._timers if t.is_alive()] + [timer]
        timer.start()

    def shutdown(self, wait=True):
        # type: (bool) -> None
        with self._lock:
            for timer in self._timers:
                timer.cancel()
            self._timers = []
            executor, self._executor = self._executor, None
        if executor is not None:
            executor.shutdown(wait=wait)


class DatabaseDedupe(object):
    """The default dedupe setting: the notification delivery ids each run has taken, in
    qube_notifications. once runs inside the run row's lock and transaction (Operation.handle),
    so the row and the handler's writes commit together: a redelivery finds the row and is
    skipped, and a handler that raised rolls its row back with it, so the retry runs it
    again."""

    def once(self, run, delivery_id, fn):
        # type: (Any, Any, Callable[[], Any]) -> bool
        """Runs fn unless run has taken delivery_id already."""
        from ._store import NOTIFICATION

        store = run._kit_store
        delivery_id = "" if delivery_id is None else str(delivery_id)
        # Under the run row's lock no other worker inserts for this run, so this check is
        # enough; the savepoint keeps a unique violation from a lock-free caller from aborting
        # a PostgreSQL transaction.
        if store.exists(NOTIFICATION, run_id=run.id, delivery_id=delivery_id):
            return False
        try:
            with store.atomic(savepoint=True):
                store.save(store.new(NOTIFICATION, run_id=run.id, delivery_id=delivery_id))
        except store.integrity_errors:
            return False
        fn()
        return True


class CacheDedupe(object):
    """A dedupe setting for an app that would rather not use the kit's table (DatabaseDedupe,
    the default): the notification delivery ids already taken, in a cache, for a day. cache
    answers get(key) and set(key, value, timeout=seconds), as Django's cache and
    Flask-Caching's do. It needs a cache your workers share (Redis, Memcached, the database
    cache): with a per-process one (local memory) a retry that reaches another worker isn't
    caught. It isn't transactional: the id is remembered after the handler commits, so a crash
    between the two runs the handler again on the redelivery.

        qubesync.kit.configure(dedupe=qubesync.kit.CacheDedupe(django.core.cache.cache))
    """

    DAY = 24 * 60 * 60

    def __init__(self, cache, expires_in=DAY):
        # type: (Any, int) -> None
        self.cache = cache
        self.expires_in = expires_in

    def seen(self, key):
        # type: (str) -> bool
        return self.cache.get(key) is not None

    def remember(self, key):
        # type: (str) -> None
        self.cache.set(key, True, timeout=self.expires_in)


_queue = InProcessQueue()


def default_queue():
    # type: () -> InProcessQueue
    return _queue


def _reset_defaults():
    # type: () -> None
    global _queue
    _queue.shutdown(wait=True)
    _queue = InProcessQueue()
