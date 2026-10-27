"""Operation, the base of your classes that start workflows."""
import json
import logging
import uuid
from typing import Any, Callable, Dict, List, Mapping, Optional

import requests

from ..v2 import APIError
from ._defaults import client
from ._errors import NotConnected, RealtimeRequired
from ._models import advance_sync_mark
from ._settings import settings
from ._store import RUN

log = logging.getLogger("qubesync.kit")

__all__ = ["Operation", "without_nils"]

AWAITING_INPUT = "workflow_run.awaiting_input"
COMPLETED = "workflow_run.completed"
FAILED = "workflow_run.failed"
CANCELLED = "workflow_run.cancelled"

# What a call that got no answer raises (a timeout, a refused or dropped connection).
NETWORK_ERRORS = (requests.ConnectionError, requests.Timeout)

REALTIME_REQUIRED = "Workflows run on realtime connections, and this one is standard."


def _detail(error):
    # type: (APIError) -> Optional[str]
    detail = error.errors.get("detail") if isinstance(error.errors, dict) else None
    return detail if isinstance(detail, str) and detail else None


def without_nils(value):
    # type: (Any) -> Any
    """value without its None values, at every depth: what a mapped operation's input sends,
    so a field your record doesn't have yet is left out rather than sent as null."""
    if isinstance(value, dict):
        return {key: without_nils(inner) for key, inner in value.items() if inner is not None}
    if isinstance(value, (list, tuple)):
        return [without_nils(inner) for inner in value if inner is not None]
    return value


class Operation(object):
    """One way your app starts a workflow, and what it does with that run's webhooks: subclass
    it once per operation, in quickbooks_desktop/, and list it in the operations setting by
    its slug.

        class CreateInvoice(qubesync.kit.Operation):
            workflow = "add_transaction"
            slug = "create_invoice"

            def input(self):
                return {"operation": "invoice.create", "params": {"ref_number": self.record.number}}

            def ended(self, event):
                txn = (event.get("output") or {}).get("record") or {}
                self.connection.link(self.record, kind="invoice", qb_id=txn["txn_id"],
                                     edit_sequence=txn.get("edit_sequence"), name=txn.get("ref_number"))

        run = CreateInvoice.start(invoice, connection)

    With your app's typed workflow starts (``qubesync workflows`` writes qube_workflows.py, see
    qubesync.workflow_types), input can return what a branch's input builder returns, typed as
    that branch's input, so a misspelled field fails the type check rather than the run:

        from qube_workflows import AddTransactionInvoiceInput, add_transaction

        class CreateInvoice(qubesync.kit.Operation):
            ...

            def input(self) -> AddTransactionInvoiceInput:
                return add_transaction.invoice_input({"customer_ref": ..., "ref_number": self.record.number})

    Each run is a row in qube_runs (Run), written before the run starts, and its webhook URL is
    QUBE_WEBHOOK_URL/runs/<run id>, so the job hands each event back to the same class with the
    record, the run and its connection found again. Your record's table needs no QuBe columns:
    the run keeps its reference, revision, state and question, and the QuickBooks ids an ending
    carries go on the connection (connection.link), keyed by kind.
    """

    workflow = ""  # the workflow it starts
    slug = ""  # its key in the operations setting, kept on each run

    def __init__(self, record, run):
        # type: (Any, Any) -> None
        self.record = record
        self.run = run

    @classmethod
    def start(cls, record, connection):
        # type: (Any, Any) -> Any
        """Starts the operation's run for record (saved) on connection (one with a qube_id) and
        returns the run row, or returns the record's run there that hasn't ended (run.reused),
        sending its start again while unconfirmed. The README's "Writing an operation" says how a
        refusal, a raising input and no answer leave the row."""
        if not cls._made_by_qube_sync(connection):
            raise NotConnected(
                "QuBe Sync: %s.start needs a connection QuBe Sync has made (one with a qube_id): "
                "the customer finishes onboarding first" % cls.__name__
            )
        if not cls.slug or not cls.workflow:
            raise NotImplementedError("%s needs its workflow and slug" % cls.__name__)

        run, input_error = cls._claim_run(record, connection)
        if input_error is not None:
            raise input_error
        if not run.reused:
            return cls._send_start(run, run.input)
        if cls._unconfirmed_start(run):
            run = cls._send_start(run, run.input)
            run.reused = True
        return run

    @classmethod
    def _claim_run(cls, record, connection):
        # type: (Any, Any) -> Any
        # Under the connection row's lock, so a double click finds the first click's row.
        # Returns (run, error an input raised): the failed row commits before it's raised.
        store = connection._kit_store
        type_name, record_id = store.key_for(record)
        with store.locked(connection) as locked:
            going = store.first(
                RUN,
                order=["-created_at", "-id"],
                connection_id=locked.id,
                record_type=type_name,
                record_id=record_id,
                operation=cls.slug,
            )
            if going is not None and not going.ended():
                going.reused = True
                return going, None
            return cls._new_run(store, record, locked)

    @classmethod
    def _new_run(cls, store, record, connection):
        # type: (Any, Any, Any) -> Any
        run = store.new(
            RUN,
            connection_id=connection.id,
            operation=cls.slug,
            record=record,
            reference="%s-%s-%s" % (cls.slug, store.key_for(record)[1], uuid.uuid4()),
            state="starting",
            revision=0,
        )
        operation = cls(record, run)
        operation._connection = connection  # an unsaved run may not reach it yet
        try:
            # As JSON reads it back, so a retry sends exactly what the first start did.
            run.input = json.loads(json.dumps(operation.input()))
        except Exception as error:  # an input not written yet (NotImplementedError), too
            run.state = "failed"
            store.save(run)
            return run, error
        store.save(run)
        return run, None

    # Sent, but no answer from QuBe Sync yet.
    @staticmethod
    def _unconfirmed_start(run):
        # type: (Any) -> bool
        return not run.qube_run_id and run.state == "starting"

    @classmethod
    def retry_start(cls, run):
        # type: (Any) -> Any
        """Sends a start that got no answer again (run.retry_start() calls it): the same
        reference as the Idempotency-Key, the same workflow, input and webhook URL. QuBe Sync
        answers a repeat of a start it took with the run that start made (201,
        Idempotent-Replayed: true) rather than starting another, for as long as that run is
        kept (60 days after it ends); a start it never took starts now. Returns the run; a run
        already answered is returned as it is."""
        if run.qube_run_id:
            return run
        if run.state != "starting":
            raise ValueError(
                "QuBe Sync: run %s is %s: only a start that got no answer is sent again" % (run.id, run.state)
            )
        return cls._send_start(run, run.input)

    @classmethod
    def _send_start(cls, run, input):
        # type: (Any, Any) -> Any
        try:
            started = client().start_run(
                run.connection.qube_id,
                cls.workflow,
                input,
                reference=run.reference,
                webhook_url=run.webhook_url,
            )
        except APIError as error:
            if cls._refused(error):
                cls._mark_failed(run)
            if error.code == "realtime_required":
                raise RealtimeRequired(_detail(error) or REALTIME_REQUIRED) from error
            raise
        return cls._record_start(run, started if isinstance(started, dict) else {})

    # A 4xx started nothing, but a 409 is the Idempotency-Key in use by another call still in
    # flight (the other click), which may land: that run stays "starting".
    @staticmethod
    def _refused(error):
        # type: (APIError) -> bool
        return 400 <= error.status < 500 and error.status != 409

    @classmethod
    def _mark_failed(cls, run):
        # type: (Any) -> None
        run.state = "failed"
        run._kit_store.save(run, fields=["state"])

    @classmethod
    def _record_start(cls, run, started):
        # type: (Any, Dict[str, Any]) -> Any
        # The run's id, links and state from QuBe Sync's answer. Its webhooks may have come
        # first, so the state is taken only while the row still says "starting".
        links = started.get("links") if isinstance(started.get("links"), dict) else {}
        with run._kit_store.locked(run) as locked:
            locked.qube_run_id = started.get("id")
            locked.run_url = links.get("run")
            locked.cancel_url = links.get("cancel")
            if locked.state == "starting" and started.get("state"):
                locked.state = started["state"]
            run._kit_store.save(locked)
        return locked

    # A Connection QuBe Sync has made: one with a qube_id.
    @staticmethod
    def _made_by_qube_sync(connection):
        # type: (Any) -> bool
        return getattr(connection, "_kit_store", None) is not None and bool(getattr(connection, "qube_id", None))

    @classmethod
    def find_record(cls, id):
        # type: (str) -> Any
        """Your record, by the id its run keeps (a string). Leave it out and the run finds it
        by its record_type (run.record); write it to load what input and the handlers read
        with it:

            @classmethod
            def find_record(cls, id):
                return Invoice.objects.select_related("customer").filter(pk=id).first()
        """
        raise NotImplementedError(
            "%s.find_record(%r) isn't written: leave it out to find the record by the run's record_type"
            % (cls.__name__, id)
        )

    @classmethod
    def record_for(cls, run):
        # type: (Any) -> Any
        """The run's record: find_record when the operation writes one, else the run's own
        lookup."""
        if getattr(cls.find_record, "__func__", None) is Operation.find_record.__func__:
            return run.record
        return cls.find_record(run.record_id)

    @property
    def connection(self):
        # type: () -> Any
        """The connection the run is on (a Connection): where the QuickBooks ids an ending
        carries are kept (connection.link), and where the ones the input names are read
        (connection.qb_id_for)."""
        return self.__dict__.get("_connection") or self.run.connection

    def last_synced_at(self):
        # type: () -> Any
        """When this connection's last completed run of this operation's workflow started (aware
        UTC), or None before one: an incremental sync's since."""
        return self.connection.last_synced_at(self.workflow)

    def input(self):
        # type: () -> Mapping[str, Any]
        """The run's input, from the record. Each operation says how: a dict, or what an input
        builder of your typed workflow starts returns (``add_transaction.invoice_input(...)``,
        typed ``AddTransactionInvoiceInput``), which is one. It's sent as JSON either way."""
        raise NotImplementedError("%s.input isn't written yet" % type(self).__name__)

    def handle(self, event):
        # type: (Any) -> None
        """One of the run's webhooks, from the job, as qubesync.webhooks parsed it: a
        WorkflowRunEvent or a NotificationEvent. Deliveries come at least once and, from a
        queue with more than one worker, in any order:

        - an event whose reference isn't the run's, or whose connection_id isn't its
          connection's qube_id (a signed body posted to another run's URL), is logged and
          skipped;
        - a notification is taken once, by its delivery_id (in qube_notifications, with what
          the handler writes; the dedupe setting);
        - any other event is applied only when its revision is newer than the last one applied.

        It holds the run row's lock while it does (reading it again), so two workers never
        apply one run's events at once, and what a handler writes is saved with the revision or
        not at all.
        """
        store = self.run._kit_store
        with store.locked(self.run) as run:
            self.run = run
            self._apply(event)

    def question(self, event):
        # type: (Any) -> None
        """A question the run asks: kept whole on the run, with its links (where to answer it,
        and where a record field searches), for the question template to show on the record's
        page. Your user's choice answers it, through the question routes: nothing here picks
        one, and the run waits for as long as it takes. A newer event that isn't a question
        forgets it."""
        prompt = event.get("prompt")
        if not prompt:
            return  # answered already: this delivery was a retry

        links = event.get("links") or {}
        self.run.question = prompt
        self.run.links = {"decisions": links.get("decisions"), "search": links.get("search")}

    # What an operation does with the rest of its run's events: each operation says, and until
    # it does, each logs. The kit has already kept every ending on the run (state, outcome,
    # error, cancel_reason, ended_at: the run status template shows it), so these are for your
    # own records: an invoice marked sent, a sync's last-finished time.

    def notification(self, event):
        # type: (Any) -> None
        self.log_event(event)

    def ended(self, event):
        # type: (Any) -> None
        self.log_event(event)

    def failed(self, event):
        # type: (Any) -> None
        self.log_event(event)

    def quickbooks_ref(self, app_record, kind, name=None):
        # type: (Any, str, Optional[str]) -> Optional[Dict[str, str]]
        """How the input refers to one of your records in QuickBooks: {"list_id": ...} when
        it's linked on this run's connection (connection.qb_id_for), else {"full_name": name},
        or None when there's neither. Refer by id where you can: a name can match another
        record, or none after a rename.

            "customer_ref": self.quickbooks_ref(customer, kind="customer", name=customer and customer.name)
        """
        list_id = self.connection.qb_id_for(app_record, kind=kind) if app_record is not None else None
        if list_id:
            return {"list_id": list_id}
        if not name:
            return None
        return {"full_name": name}

    def link_references(self, event, fn):
        # type: (Any, Callable[[str, Dict[str, Any]], Any]) -> List[Any]
        """Links each QuickBooks record an ending carries (event output's "references", keyed
        by the input's path: "customer_ref", "invoice_line_add.0.item_ref") to the record of
        yours fn returns for it, on this run's connection, so the next run refers to it by id.
        fn gets the path and the entry (kind, outcome and record: the record's own list as
        "type", with list_id, edit_sequence and full_name) and returns your record, or None to
        skip it. An entry with no record (not found, or not reached before a cancel) is
        skipped. Works on an added ending and on a cancelled one, which can carry some.
        Returns the rows linked.

            self.link_references(event, lambda path, entry: customer if path == "customer_ref" else None)
        """
        output = event.get("output")
        references = output.get("references") if isinstance(output, dict) else None
        if not isinstance(references, dict):
            return []

        linked = []
        for path, entry in references.items():
            if not (isinstance(entry, dict) and isinstance(entry.get("record"), dict)):
                continue
            found = entry["record"]
            if not found.get("list_id"):
                continue
            app_record = fn(path, entry)
            if app_record is None:
                continue
            kind = found.get("type") or entry.get("kind")
            linked.append(
                self.connection.link(
                    app_record,
                    kind=kind,
                    qb_id=found["list_id"],
                    edit_sequence=found.get("edit_sequence"),
                    name=found.get("full_name"),
                )
            )
        return linked

    def answered(self, token, taken=False):
        # type: (Optional[str], bool) -> None
        """After your user's choice is in: the question is forgotten, unless the run has asked
        another since (its token is the question's own). taken: QuBe Sync took the answer, so
        the run is "running" again until its next webhook, which waits on the Web Connector's
        next poll."""
        store = self.run._kit_store
        with store.locked(self.run) as run:
            self.run = run
            question = run.open_question
            if question and question.get("token") == token:
                run.question = None
                run.links = None
                if taken:
                    run.state = "running"
                store.save(run)

    def without_nils(self, value):
        # type: (Any) -> Any
        """value without its None values, at every depth (qubesync.kit.without_nils)."""
        return without_nils(value)

    def log_event(self, event):
        # type: (Any) -> None
        """All a handler does until you fill it in."""
        prompt = event.get("prompt")
        detail = (prompt.get("id") if isinstance(prompt, dict) else None) or event.get("name") or event.get("outcome")
        line = "QuBe Sync: %s %s (run %s): %s %s (%s)" % (
            type(self).__name__,
            self.run._kit_store.key_for(self.record)[1],
            self.run.id,
            event.event,
            detail,
            event.reference,
        )
        if event.type == "workflow_run" and self._stopped(event):
            log.warning(line)
        else:
            log.info(line)

    # Only a run's events and its notifications carry a reference: any other event posted to
    # this URL is skipped with the rest that aren't this run's.
    def _apply(self, event):
        # type: (Any) -> None
        run = self.run
        if not self._this_run(event):
            log.warning(
                "QuBe Sync: %s run %s skipped %s for %r on %r: not this run",
                type(self).__name__,
                run.id,
                event.event,
                event.reference,
                event.get("connection_id"),
            )
            return

        if event.type == "notification":
            self._take_once(event.dedupe_key, lambda: self.notification(event))  # its delivery_id
            return
        if event.type != "workflow_run":
            return
        # Applied already, or older than what was.
        if not event.newer_than(run.revision):
            return

        # The run as of this event, before your handler runs, so every ending is on the run row
        # whatever the handler does: state, outcome, and a failure's error or a cancel's reason.
        run.state = event.run_state or self._run_state_for(event)
        run.outcome = event.outcome
        if self._ended(event):
            run.ended_at = run.ended_at or run._kit_store.now()
            if event.event == FAILED:
                run.error = event.error
            if event.event == CANCELLED:
                run.cancel_reason = event.cancel_reason

        if event.event == AWAITING_INPUT:
            self.question(event)
        elif event.event == COMPLETED:
            advance_sync_mark(run.connection, type(self).workflow, run.created_at)
            self.ended(event)
        elif self._stopped(event):
            self.failed(event)
        # A newer event that isn't a question: the one saved was answered, or the run ended.
        if event.event != AWAITING_INPUT:
            run.question = None
            run.links = None
        run.revision = event.revision
        run._kit_store.save(run)

    # The event names this run: its reference, on its connection.
    def _this_run(self, event):
        # type: (Any) -> bool
        return self._same_reference(event) and self._on_this_connection(event)

    def _same_reference(self, event):
        # type: (Any) -> bool
        return event.reference is not None and event.reference == self.run.reference

    def _on_this_connection(self, event):
        # type: (Any) -> bool
        qube_id = self.run.connection.qube_id
        return qube_id is not None and event.get("connection_id") == qube_id

    # The run is over: completed, failed or cancelled.
    def _ended(self, event):
        # type: (Any) -> bool
        return event.event == COMPLETED or self._stopped(event)

    # The run ended without completing: failed or cancelled, which the failed handler takes.
    @staticmethod
    def _stopped(event):
        # type: (Any) -> bool
        return event.event in (FAILED, CANCELLED)

    def _run_state_for(self, event):
        # type: (Any) -> str
        return {
            AWAITING_INPUT: "awaiting_input",
            COMPLETED: "completed",
            FAILED: "failed",
            CANCELLED: "cancelled",
        }.get(event.event, self.run.state)

    def _take_once(self, delivery_id, fn):
        # type: (Any, Callable[[], Any]) -> None
        # Runs fn once per delivery_id of this run, kept in the dedupe store. The default store
        # writes its row inside this run's lock and transaction, so the row and the handler's
        # writes commit together, or neither does.
        store = settings().dedupe
        if callable(getattr(store, "once", None)):
            store.once(self.run, delivery_id, fn)
            return

        key = "qube-sync/delivery/%s" % ("" if delivery_id is None else delivery_id)
        if store.seen(key):
            return  # a retry of one already taken
        fn()
        store.remember(key)
