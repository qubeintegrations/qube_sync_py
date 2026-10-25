"""Operation, the base of your classes that start workflows, and ConnectionEvents, the base of
your connection class. Your app's subclasses live in quickbooks_desktop/; the configure call
names them (operations and connection)."""
import logging
import uuid
from typing import Any, Dict, List, Optional
from urllib.parse import quote

from .. import webhooks
from ._defaults import client
from ._settings import settings

log = logging.getLogger("qubesync.kit")

__all__ = ["Event", "Operation", "ConnectionEvents", "connection_webhook_url"]

# A webhook, as qubesync.webhooks parsed it: a WorkflowRunEvent, a NotificationEvent or a
# ConnectionEvent, say, each with its fields as attributes (event.outcome).
Event = webhooks.Event


def _webhook_base():
    # type: () -> str
    return settings().webhook_url.rstrip("/")


def connection_webhook_url(account_id):
    # type: (Any) -> str
    """Where a connection's own events go: the webhook_url setting (QUBE_WEBHOOK_URL), then
    connection and the id of the account that keeps it."""
    return "%s/connection/%s" % (_webhook_base(), quote(str(account_id), safe=""))


class Operation(object):
    """One way your app starts a workflow, and what it does with that run's webhooks: a
    subclass per operation, in quickbooks_desktop/. Each run's webhook URL names the
    operation and your record (QUBE_WEBHOOK_URL/<slug>/<record id>), so the job
    (qubesync.kit.run) hands each event back to the same class, with the record found again.

    Subclass your framework's (qubesync.django.Operation, qubesync.flask.Operation or
    qubesync.fastapi.Operation), which knows how to save a record; this one doesn't.

    The run's reference and the last revision applied are kept on the record, in its
    qube_reference (a string) and qube_revision (an integer) fields, and a question the run
    asks, with its links, in qube_question and qube_links (JSON) fields, written with
    save_record. A record whose workflow asks nothing (a sync's) needs only the first two.
    Override saved_reference, save_reference, saved_revision and save_revision, or
    saved_question, saved_links and save_question, to keep them elsewhere.

    What a subclass writes: workflow and slug, find_record, input, and the handlers it needs
    (notification, ended, failed).
    """

    workflow = ""  # the workflow it starts
    slug = ""  # the slug in its webhook URL, and its key in the operations setting

    def __init__(self, record):
        # type: (Any) -> None
        self.record = record

    @classmethod
    def start(cls, record, connection_id):
        # type: (Any, str) -> Dict[str, Any]
        """Starts the operation's run for record, one your app has saved, on the customer's
        connection (the connection id onboarding saved on their account), and returns the run
        as it stands. The reference is new for every run (<slug>-<record id>-<uuid>) and saved
        on the record before the run starts, since a webhook can arrive before this returns."""
        if not cls.slug or not cls.workflow:
            raise NotImplementedError("%s needs its workflow and slug" % cls.__name__)
        operation = cls(record)
        reference = "%s-%s-%s" % (cls.slug, operation.record_id(), uuid.uuid4())
        operation.save_reference(reference)
        return client().start_run(
            connection_id,
            cls.workflow,
            operation.input(),
            reference=reference,
            webhook_url=operation.webhook_url(),
        )

    @classmethod
    def find_record(cls, record_id):
        # type: (str) -> Any
        """Your record, by the id in its webhook URL. Each operation says how."""
        raise NotImplementedError("%s.find_record(%r) isn't written yet" % (cls.__name__, record_id))

    def record_id(self):
        # type: () -> Any
        """The record's id, as its webhook URL and reference carry it: record.id."""
        return self.record.id

    def webhook_url(self):
        # type: () -> str
        """Where this run's webhooks go: QUBE_WEBHOOK_URL, then the operation and the
        record's id."""
        return "%s/%s/%s" % (_webhook_base(), self.slug, quote(str(self.record_id()), safe=""))

    def input(self):
        # type: () -> Dict[str, Any]
        """The run's input, from the record. Each operation says how."""
        raise NotImplementedError("%s.input isn't written yet" % type(self).__name__)

    def handle(self, event):
        # type: (Any) -> None
        """One of the run's webhooks, from the job. Deliveries come at least once and, from
        a queue with more than one worker, in any order:

        - an event whose reference isn't the one saved on the record isn't this record's run
          (an earlier run's, or a signed body posted to another record's URL): it's logged
          and skipped;
        - a notification is taken once, by its delivery_id (the dedupe setting keeps them);
        - any other event is applied only when its revision is newer than the last one
          applied.

        With more than one worker, two of a record's events can also run at once: take a row
        lock on the record around this (the Django base does, with select_for_update).
        """
        reference = event.reference
        if not reference or reference != self.saved_reference():
            log.warning(
                "QuBe Sync: %s %s skipped %s for %r: not its run",
                type(self).__name__,
                self.record_id(),
                event.event,
                reference,
            )
            return

        if event.type == "notification":
            delivery_id = event.dedupe_key  # its delivery_id
            if delivery_id is None:
                self.notification(event)
                return
            store = settings().dedupe
            key = str(delivery_id)
            if store.seen(key):
                return  # a retry of one already taken
            self.notification(event)
            store.remember(key)
            return

        if not hasattr(event, "newer_than") or not event.newer_than(self.saved_revision()):
            return  # applied already, or older than what was

        kind = event.event
        if kind == "workflow_run.awaiting_input":
            self.question(event)
        elif kind == "workflow_run.completed":
            self.ended(event)
        elif kind in ("workflow_run.failed", "workflow_run.cancelled"):
            self.failed(event)
        # A newer event that isn't a question: the one saved was answered, or the run ended.
        if kind != "workflow_run.awaiting_input" and self.saved_question():
            self.save_question(None, None)
        self.save_revision(event.revision)

    def question(self, event):
        # type: (Any) -> None
        """A question the run asks: saved whole on the record, with its links (where to
        answer it, and where a record field searches), for the question template
        (qubesync/question.html) to show on the record's page. Your user's choice answers it,
        through the question routes: nothing here picks one, and the run waits for as long as
        it takes. A newer event that isn't a question forgets it."""
        prompt = event.prompt
        if not prompt:
            return  # answered already: this delivery was a retry
        links = event.links or {}
        self.save_question(prompt, {"decisions": links.get("decisions"), "search": links.get("search")})

    # What an operation does with the rest of its run's events: each operation says, and
    # until it does, each logs.

    def notification(self, event):
        # type: (Any) -> None
        self.log_event(event)

    def ended(self, event):
        # type: (Any) -> None
        self.log_event(event)

    def failed(self, event):
        # type: (Any) -> None
        self.log_event(event)

    def saved_reference(self):
        # type: () -> Optional[str]
        return self.record.qube_reference

    def save_reference(self, reference):
        # type: (str) -> None
        """Saves a new run's reference and forgets the last run's revision, since each run's
        revisions start again at 1, and any question it was asking."""
        self.record.qube_reference = reference
        self.record.qube_revision = 0
        self.save_record(["qube_reference", "qube_revision"])
        if self.saved_question():
            self.save_question(None, None)

    def saved_revision(self):
        # type: () -> Optional[int]
        return self.record.qube_revision

    def save_revision(self, revision):
        # type: (int) -> None
        self.record.qube_revision = revision
        self.save_record(["qube_revision"])

    def saved_question(self):
        # type: () -> Optional[Dict[str, Any]]
        """The question the run is asking, as its webhook's prompt had it, or None. A record
        with no qube_question field has none."""
        return getattr(self.record, "qube_question", None)

    def saved_links(self):
        # type: () -> Optional[Dict[str, Any]]
        """Its links: decisions and, for a record field, search."""
        return getattr(self.record, "qube_links", None)

    def save_question(self, question, links):
        # type: (Optional[Dict[str, Any]], Optional[Dict[str, Any]]) -> None
        self.record.qube_question = question
        self.record.qube_links = links
        self.save_record(["qube_question", "qube_links"])

    def answered(self, token):
        # type: (str) -> None
        """After your user's choice is in: the question is forgotten, unless the run has
        asked another since (its token is the question's own)."""
        question = self.saved_question()
        if question and question.get("token") == token:
            self.save_question(None, None)

    def save_record(self, fields):
        # type: (List[str]) -> None
        """Writes those fields of the record. Your framework's base does (Django's
        save(update_fields=...), or SQLAlchemy's commit); override it to keep them elsewhere."""
        raise NotImplementedError(
            "%s.save_record: subclass qubesync.django.Operation, qubesync.flask.Operation or "
            "qubesync.fastapi.Operation, or write save_record" % type(self).__name__
        )

    def log_event(self, event):
        # type: (Any) -> None
        """All a handler does until you fill it in."""
        prompt = event.get("prompt") or {}
        detail = (prompt.get("id") if isinstance(prompt, dict) else None) or event.get("name") or event.get("outcome")
        failed = event.event in ("workflow_run.failed", "workflow_run.cancelled")
        (log.warning if failed else log.info)(
            "QuBe Sync: %s %s: %s %s (%s)",
            type(self).__name__,
            self.record_id(),
            event.event,
            detail,
            event.reference,
        )


class ConnectionEvents(object):
    """The customer's connection's own events, which QuBe Sync POSTs to the connection's
    webhook URL: QUBE_WEBHOOK_URL/connection/<account id>, which onboarding (POST
    quickbooks/connect) sets when they click Connect. The job hands each one here, with the
    account found again.

        connection.connected        the Web Connector checked in: QuickBooks is connected
        connection.setup_cancelled  they chose "Cancel setup" on the setup page
        connection.stalled          requests are stuck; see stall_reason
        connection.resumed          after a stall, they're being taken again

    The setup ends on the QuickBooks computer, which usually isn't signed in to your app, so
    nothing comes back to it there: connection.connected, signed by QuBe Sync, is how your app
    knows. A simulated connection is connected as it's made, so its connection.connected can
    come before create_connection returns: onboarding saves the id as soon as it has it.

    The account keeps the connection's id and the last event's revision, in its
    qube_connection_id (a string) and qube_connection_revision (an integer) fields, written
    with save_record. Override saved_connection_id, save_connection_id, saved_revision and
    save_revision to keep them elsewhere.

    What your subclass writes: find_record, and the four handlers. Subclass your framework's
    (qubesync.django.ConnectionEvents, say), which knows how to save the account.
    """

    def __init__(self, account):
        # type: (Any) -> None
        self.account = account

    @classmethod
    def find_record(cls, record_id):
        # type: (str) -> Any
        """Your account, by the id in the connection's webhook URL."""
        raise NotImplementedError("%s.find_record(%r) isn't written yet" % (cls.__name__, record_id))

    def account_id(self):
        # type: () -> Any
        """The account's id, as the connection's webhook URL carries it: account.id."""
        return self.account.id

    def webhook_url(self):
        # type: () -> str
        """Where this account's connection's events go."""
        return connection_webhook_url(self.account_id())

    def handle(self, event):
        # type: (Any) -> None
        """One of the connection's webhooks, from the job, as qubesync.webhooks parsed it (a
        ConnectionEvent). Deliveries come at least once and, from a queue with more than one
        worker, in any order:

        - an event whose connection isn't the one saved on the account (a signed body posted
          to another account's URL, or an event that isn't a connection's) is logged and
          skipped;
        - any other is applied only when its revision is newer than the last one applied, so
          a retried connection.stalled that comes after its connection.resumed is skipped.
        """
        connection_id = event.connection_id if event.type == "connection" else None
        if not connection_id or connection_id != self.saved_connection_id():
            log.warning(
                "QuBe Sync: account %s skipped %s for %r: not its connection",
                self.account_id(),
                event.event,
                connection_id,
            )
            return

        if not event.newer_than(self.saved_revision()):
            return  # applied already, or older than what was

        kind = event.event
        if kind == "connection.connected":
            self.connected(event)
        elif kind == "connection.setup_cancelled":
            self.setup_cancelled(event)
        elif kind == "connection.stalled":
            self.stalled(event)
        elif kind == "connection.resumed":
            self.resumed(event)
        else:
            self.log_event(event)
        self.save_revision(event.revision)

    # What your app does with each: until you fill them in, each logs.

    def connected(self, event):
        # type: (Any) -> None
        """QuickBooks is connected: mark the account connected, and start syncing."""
        self.log_event(event)

    def setup_cancelled(self, event):
        # type: (Any) -> None
        """They cancelled the setup: offer Connect QuickBooks Desktop again."""
        self.log_event(event)

    def stalled(self, event):
        # type: (Any) -> None
        """Your requests are waiting and QuickBooks hasn't been reached. Show the customer,
        and tell them what the event's stall_reason says:

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

    def saved_connection_id(self):
        # type: () -> Optional[str]
        """The connection id kept on the account, or None. Every run starts on it."""
        return getattr(self.account, "qube_connection_id", None)

    def save_connection_id(self, connection_id):
        # type: (str) -> None
        """Keeps a new connection's id on the account, and forgets the last connection's
        revision (cleared), since a new connection's revisions start again at 1."""
        self.account.qube_connection_id = connection_id
        self.account.qube_connection_revision = None
        self.save_record(["qube_connection_id", "qube_connection_revision"])

    def saved_revision(self):
        # type: () -> Optional[int]
        return getattr(self.account, "qube_connection_revision", None)

    def save_revision(self, revision):
        # type: (int) -> None
        self.account.qube_connection_revision = revision
        self.save_record(["qube_connection_revision"])

    def save_record(self, fields):
        # type: (List[str]) -> None
        """Writes those fields of the account. Your framework's base does; override it to
        keep them elsewhere."""
        raise NotImplementedError(
            "%s.save_record: subclass qubesync.django.ConnectionEvents, qubesync.flask."
            "ConnectionEvents or qubesync.fastapi.ConnectionEvents, or write save_record"
            % type(self).__name__
        )

    def log_event(self, event):
        # type: (Any) -> None
        """All a handler does until you fill it in."""
        stalled = event.event == "connection.stalled"
        (log.warning if stalled else log.info)(
            "QuBe Sync: account %s: %s (revision %s)",
            self.account_id(),
            event.event,
            event.revision,
        )
