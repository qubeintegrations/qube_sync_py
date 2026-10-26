"""SyncStatus: where one of your records stands with QuickBooks, derived from the kit's rows.

The README's "Sync status" says how run and link are weighed; nothing is stored for it.
"""
from typing import Any, Optional

from ._store import QUICKBOOKS_RECORD, RUN, current_store

__all__ = ["SyncStatus", "STATUSES"]

STATUSES = ("not_sent", "sending", "needs_answer", "in_quickbooks", "done", "failed", "cancelled")


class SyncStatus(object):
    """record's status on one connection for one operation: status (one of STATUSES), run (the
    latest run there, or None) and link (its newest QuickBooks link there, or None)."""

    STATUSES = STATUSES

    def __init__(self, status, run=None, link=None):
        # type: (str, Any, Any) -> None
        self.status = status
        self.run = run
        self.link = link

    @classmethod
    def of(cls, connection, record, operation):
        # type: (Any, Any, str) -> SyncStatus
        """record's status on connection for operation (its slug)."""
        store = connection._kit_store
        type_name, id = store.key_for(record)
        mine = {"connection_id": connection.id, "record_type": type_name, "record_id": id}
        run = store.first(RUN, order=["-created_at", "-id"], operation=str(operation), **mine)
        link = store.first(QUICKBOOKS_RECORD, order=["-updated_at", "-id"], **mine)
        return cls(_status_of(store, run, link), run, link)

    @classmethod
    def latest(cls, record, operation):
        # type: (Any, str) -> SyncStatus
        """record's status on the connection its latest run of operation went out on, or
        not_sent when it has none."""
        run = current_store().model(RUN).latest_for(record, operation)
        if run is None:
            return cls("not_sent")
        return cls.of(run.connection, record, operation)

    @property
    def qb_id(self):
        # type: () -> Optional[str]
        return self.link.qb_id if self.link is not None else None

    @property
    def error(self):
        # type: () -> Any
        """A failed run's error, as its event carried it."""
        return self.run.error if self.status == "failed" else None

    @property
    def unconfirmed(self):
        # type: () -> bool
        """A start QuBe Sync hasn't confirmed for a minute: run.retry_start() sends it again."""
        return self.status == "sending" and self.run.unconfirmed()

    @property
    def retry(self):
        # type: () -> bool
        """Starting again makes sense: it failed or was cancelled, and isn't in QuickBooks."""
        return self.status in ("failed", "cancelled") and self.link is None

    @property
    def summary_text(self):
        # type: () -> Optional[str]
        if self.status == "not_sent":
            return None
        if self._linked_without_completed_run():
            return "In QuickBooks"
        return self.run.summary_text

    def _linked_without_completed_run(self):
        # type: () -> bool
        return self.status == "in_quickbooks" and (self.run is None or self.run.state != "completed")

    def __str__(self):
        return self.status

    def __repr__(self):
        return "<SyncStatus %s qb_id=%r>" % (self.status, self.qb_id)


def _status_of(store, run, link):
    # type: (Any, Any, Any) -> str
    if run is not None and not run.ended():
        return "needs_answer" if run.state == "awaiting_input" else "sending"
    if _stopped_since_link(store, run, link):
        return "cancelled" if run.cancelled() else "failed"
    if link is not None:
        return "in_quickbooks"
    if run is not None and run.state == "completed":
        return "done"
    return "not_sent"


# The latest run failed or was cancelled, and the link (if any) is no newer than its end.
def _stopped_since_link(store, run, link):
    # type: (Any, Any, Any) -> bool
    if run is None or not (run.failed() or run.cancelled()):
        return False
    if link is None:
        return True
    return store.utc(link.updated_at) <= store.utc(run.ended_at or run.updated_at)
