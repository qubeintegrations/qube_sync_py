"""The job: each verified webhook, after the response."""
import logging
import random
from typing import Any, Callable, Dict, Optional

from .. import webhooks
from ._defaults import default_queue
from ._errors import UnknownOperation
from ._settings import settings
from ._store import CONNECTION, RUN, current_store

log = logging.getLogger("qubesync.kit")

__all__ = ["run", "perform", "enqueue_in_process", "retry_delay"]

RUN_KIND = "run"
CONNECTION_KIND = "connection"


def run(kind, id, body):
    # type: (str, Any, Any) -> None
    """Runs one verified delivery. kind is "run" (QUBE_WEBHOOK_URL/runs/<id>): the run's
    operation finds its record and handles the event (Operation.handle); or "connection"
    (QUBE_WEBHOOK_URL/connections/<id>): your connection_events class handles it for that
    connection. The default queue calls it; so does your own queue's worker when the enqueue
    setting hands deliveries elsewhere.

    body is the delivery's raw body, which the webhook route verified: parsed into its typed
    event here, and not verified again, since a job can run after its timestamp's 5 minutes are
    up.

    It raises when it can't do the work (a handler of yours raised, the database is down, the
    run's operation was taken out of operations, or a connection's event came before the
    connection's id was saved: NotReady), for your queue to retry. A run, connection or record
    that isn't there is dropped with a warning instead: the route answered 404 unless the row
    existed, and your app saves a record before its run's row, so by the time a job runs, a
    missing one was deleted, and retrying would never succeed.
    """
    event = webhooks.parse(body)
    kind = str(kind)
    if kind == RUN_KIND:
        _run_event(id, event)
    elif kind == CONNECTION_KIND:
        _connection_event(id, event)
    else:
        raise ValueError("QuBe Sync: a delivery is for a run or a connection, not %r" % (kind,))


def _run_event(id, event):
    # type: (Any, Any) -> None
    store = current_store()
    found = store.get(RUN, id)
    if found is None:
        return _dropped("run %s isn't there" % id, event)

    operation = settings().operation_class(found.operation)
    if operation is None:
        # Putting it back in operations and retrying does work.
        raise UnknownOperation("QuBe Sync: no operation has the slug %r" % (found.operation,))

    record = _find_run_record(store, operation, found)
    if record is None:
        return _dropped("run %s's %s %s isn't there" % (found.id, found.record_type, found.record_id), event)

    operation(record, found).handle(event)


def _connection_event(id, event):
    # type: (Any, Any) -> None
    store = current_store()
    found = store.get(CONNECTION, id)
    if found is None:
        return _dropped("connection %s isn't there" % id, event)

    settings().connection_events_class()(found).handle(event)


def _find_run_record(store, operation, found):
    # type: (Any, Any, Any) -> Any
    try:
        return operation.record_for(found)
    except store.not_found_errors:  # a find_record written with get() (DoesNotExist, NoResultFound)
        return None


def _dropped(why, event):
    # type: (str, Any) -> None
    log.warning(
        "QuBe Sync: dropped %s: %s (deleted since, so it can't be applied)", event.event or event.type, why
    )


def retry_delay(attempt):
    # type: (int) -> float
    """Seconds before the default queue runs a delivery again after its attempt-th try
    raised: a wait that grows with each, as ActiveJob's polynomially_longer does (3 s, 18 s,
    83 s, 258 s ... about four hours over ten attempts)."""
    return attempt ** 4 + 2 + random.uniform(0, 0.15) * attempt ** 4


def perform(delivery, attempt=1, wrap=None):
    # type: (Dict[str, Any], int, Optional[Callable[[Callable[[], None]], None]]) -> None
    """One attempt at a delivery on the default queue: run, and when it raises, again after
    retry_delay, job_attempts times in all. When the attempts run out it logs an error ("QuBe
    Sync: gave up on a webhook ..."). wrap runs the attempt inside what the adapter needs (a
    Flask app context)."""
    kind, id, body = delivery["kind"], delivery["id"], delivery["body"]
    try:
        if wrap is None:
            run(kind, id, body)
        else:
            wrap(lambda: run(kind, id, body))
    except Exception as error:
        attempts = settings().job_attempts
        if attempt >= attempts:
            log.error(
                "QuBe Sync: gave up on a webhook for %s %s after %d attempts: %s: %s",
                kind,
                id,
                attempts,
                type(error).__name__,
                error,
                exc_info=True,
            )
            return
        delay = retry_delay(attempt)
        log.warning(
            "QuBe Sync: a webhook for %s %s raised %s; trying again in %.0f s (attempt %d of %d)",
            kind,
            id,
            type(error).__name__,
            delay,
            attempt + 1,
            attempts,
        )
        default_queue().later(delay, perform, delivery, attempt + 1, wrap)
    finally:
        _cleanup()


def _cleanup():
    # type: () -> None
    try:
        current_store().cleanup()
    except Exception:  # nothing to give back, or no store set up yet
        pass


def enqueue_in_process(delivery, wrap=None):
    # type: (Dict[str, Any], Optional[Callable[[Callable[[], None]], None]]) -> None
    """The enqueue setting's default: perform on the in-process queue, after the response."""
    default_queue().submit(perform, delivery, 1, wrap)
