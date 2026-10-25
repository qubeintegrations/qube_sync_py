"""The job: each verified webhook, after the response."""
from typing import Any

from .. import webhooks
from ._settings import settings

__all__ = ["run", "operation_class"]

CONNECTION = "connection"


def operation_class(slug):
    # type: (str) -> Any
    """The class a webhook URL's slug names: an operation from the operations setting, or the
    connection class for "connection" (not an operation: it takes the connection's own events
    the same way). A fixed list, so a class is never looked up from the URL itself: None for
    any other slug. Raises NotConfigured when the setting it needs isn't set."""
    if slug == CONNECTION:
        return settings().connection_class()
    return settings().operation(slug)


def run(operation, record_id, body):
    # type: (str, str, str) -> None
    """One job: the operation its URL names finds its record and handles the event
    (Operation.handle), or, for a connection's own events, the connection class finds the
    account. body is the delivery's raw body, which the webhook route verified: parsed into
    its typed event here, and not verified again, since a job can run after its timestamp's 5
    minutes are up.

    The enqueue setting's queue calls this. QuBe Sync had its 2xx when the event was handed
    on, so it won't send it again: a job that raises is your queue's to retry.

    A workflow that sends notifications (pull_changes's pages) waits for each one's 2xx before
    it sends the next. The endpoint answers at once, so they come as fast as it answers, not
    after each is saved: see each operation's notification handler.
    """
    cls = operation_class(operation)
    if cls is None:
        raise LookupError("qubesync.kit.run: no operation has the slug %r" % (operation,))
    event = webhooks.parse(body)
    record = cls.find_record(record_id)
    if record is None:
        raise LookupError("qubesync.kit.run: %s.find_record(%r) found nothing" % (cls.__name__, record_id))
    cls(record).handle(event)
