"""ConnectionEvents, the base of your class for a connection's own events."""
import logging
from typing import Any, Optional

from ._errors import NotReady

log = logging.getLogger("qubesync.kit")

__all__ = ["ConnectionEvents"]


class ConnectionEvents(object):
    """A connection's own events, which QuBe Sync POSTs to the connection's webhook URL,
    QUBE_WEBHOOK_URL/connections/<connection id>, set when onboarding makes it. The job applies
    each to the connection row (status, stall_reason, revision) and then hands it to your class
    (a subclass of this, named by the connection_events setting), which sees the connection and
    its owner:

        connection.connected        the Web Connector checked in: QuickBooks is connected
        connection.setup_cancelled  they chose "Cancel setup" on the setup page
        connection.stalled          requests are stuck; see stall_reason
        connection.resumed          after a stall, they're being taken again

    The setup ends on the QuickBooks computer, which usually isn't signed in to your app, so
    nothing comes back to it there: connection.connected, signed by QuBe Sync, is how your app
    knows. connection.status already says so when your handler runs.
    """

    # The status each event leaves the connection in.
    STATUS = {
        "connection.connected": "connected",
        "connection.setup_cancelled": "setup_cancelled",
        "connection.stalled": "stalled",
        "connection.resumed": "connected",
    }

    def __init__(self, connection):
        # type: (Any) -> None
        self.connection = connection

    @property
    def owner(self):
        # type: () -> Any
        """The account (or whatever your app's customer is) that connected it."""
        return self.connection.owner

    def handle(self, event):
        # type: (Any) -> None
        """One of the connection's webhooks, from the job, as qubesync.webhooks parsed it (a
        ConnectionEvent). Deliveries come at least once and, from a queue with more than one
        worker, in any order:

        - an event whose connection isn't this row's qube_id (a signed body posted to another
          connection's URL) is logged and skipped;
        - any other is applied only when its revision is newer than the last one applied, so a
          retried connection.stalled that comes after its connection.resumed is skipped.

        It holds the connection row's lock while it does, so two workers never apply its events
        at once, and what your handler writes is saved with the revision or not at all.

        A row with no qube_id yet can't be checked: its id is adopted from QuBe Sync when one of
        the app's connections there has this row's webhook URL (a create that landed but whose
        id wasn't saved yet), and otherwise NotReady is raised, so the queue retries it.
        """
        if not self.connection.qube_id:
            self.connection.adopt_qube_connection()
            if not self.connection.qube_id:
                raise NotReady(
                    "QuBe Sync: connection %s has no qube_id yet; %s waits for it" % (self.connection.id, event.event)
                )

        store = self.connection._kit_store
        with store.locked(self.connection) as connection:
            self.connection = connection
            self._apply(event)

    # What your app does with each: until you fill them in, each logs.

    def connected(self, event):
        # type: (Any) -> None
        """QuickBooks is connected: show the connection as connected, and start syncing."""
        self.log_event(event)

    def setup_cancelled(self, event):
        # type: (Any) -> None
        """They cancelled the setup: offer Connect QuickBooks Desktop again."""
        self.log_event(event)

    def stalled(self, event):
        # type: (Any) -> None
        """Your requests are waiting and QuickBooks hasn't been reached. Show the customer,
        and tell them what the event's stall_reason (and connection.stall_reason) says:

        - "not_checking_in": the Web Connector isn't calling in. Turn on the QuickBooks
          computer, and check the Web Connector runs.
        - "quickbooks_unavailable": it is calling in and can't reach QuickBooks. Open
          QuickBooks with the company file.

        A stall can send this again with a new reason (the computer was turned on, and
        QuickBooks isn't open yet): show the newest. resumed clears it."""
        self.log_event(event)

    def resumed(self, event):
        # type: (Any) -> None
        """Clear what stalled showed, whichever its reason."""
        self.log_event(event)

    def disconnected(self):
        # type: () -> None
        """The account disconnected it (the disconnect route): delete your rows that point at
        it. Runs in the transaction that deletes it, before its runs and links go."""

    def log_event(self, event):
        # type: (Any) -> None
        """All a handler does until you fill it in."""
        line = "QuBe Sync: connection %s: %s (revision %s)" % (self.connection.id, event.event, event.get("revision"))
        if event.event == "connection.stalled":
            log.warning(line)
        else:
            log.info(line)

    # Only a connection event carries a connection: any other event posted to this URL is
    # skipped as not its connection.
    def _apply(self, event):
        # type: (Any) -> None
        connection = self.connection
        connection_id = event.connection_id if event.type == "connection" else None
        if not self._this_connection(connection_id):
            log.warning(
                "QuBe Sync: connection %s skipped %s for %r: not this connection",
                connection.id,
                event.event,
                connection_id,
            )
            return

        # Applied already, or older than what was.
        if not event.newer_than(connection.revision):
            return

        status = self.STATUS.get(event.event)
        if status:
            connection.status = status
            connection.stall_reason = event.stall_reason if event.event == "connection.stalled" else None
        connection.revision = event.revision

        handler = {
            "connection.connected": self.connected,
            "connection.setup_cancelled": self.setup_cancelled,
            "connection.stalled": self.stalled,
            "connection.resumed": self.resumed,
        }.get(event.event, self.log_event)
        handler(event)
        connection._kit_store.save(connection)

    # The event is about this connection: its connection_id is the one QuBe Sync made it.
    def _this_connection(self, connection_id):
        # type: (Optional[str]) -> bool
        return connection_id is not None and connection_id == self.connection.qube_id
