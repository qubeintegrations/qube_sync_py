"""What the kit's models do, whichever ORM keeps them: Connection, Run, QuickbooksRecord and
QueuedRequest.

qubesync.django.models and qubesync.kit.sqlalchemy declare the tables and mix these in, so a
Django Connection and a SQLAlchemy one link, adopt and summarise the same way. Each reaches its
table through its class's _kit_store (qubesync.kit._store).
"""
import datetime
import json
import logging
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote

from ._defaults import client
from ._errors import UnknownOperation
from ._messages import t
from ._settings import settings
from ._store import (
    CONNECTION,
    NOTIFICATION,
    QUEUED_REQUEST,
    QUICKBOOKS_RECORD,
    REQUEST_DELIVERY,
    RUN,
    SYNC_MARK,
    current_store,
    parse_time,
)

log = logging.getLogger("qubesync.kit")

__all__ = [
    "ConnectionMixin",
    "RunMixin",
    "QuickbooksRecordMixin",
    "QueuedRequestMixin",
    "family_for",
    "prune_runs",
    "advance_sync_mark",
    "dump_json",
    "load_json",
    "STATUSES",
    "NAME_KINDS",
]

STATUSES = ("pending", "connected", "setup_cancelled", "stalled")
NEVER_CONNECTED = ("pending", "setup_cancelled")
NAME_KINDS = ("customer", "vendor", "employee", "other_name")
ENDED_STATES = ("completed", "failed", "cancelled")

# Clock difference allowed between this app and QuBe Sync.
CLOCK_SKEW_SECONDS = 5 * 60

# How long a start may go unconfirmed before the status says so and offers to send it again.
UNCONFIRMED_AFTER_SECONDS = 60

# How long a confirmed run may go without news before the status offers a redelivery.
QUIET_AFTER_SECONDS = 10 * 60

# Nothing ended less than a day ago is pruned: a webhook for a deleted row answers 404, which
# QuBe Sync retries for hours.
MIN_PRUNE_AGE = datetime.timedelta(days=1)
PRUNE_BATCH = 500

# The run states the sync status scopes look for.
ASKING_STATES = ("awaiting_input",)
SENDING_STATES = ("starting", "running")


def dump_json(value):
    # type: (Any) -> Optional[str]
    """How the JSON in qube_runs (input, error, question, links) is kept: as JSON text in a
    plain text column. Nothing queries inside them, and text behaves the same on PostgreSQL,
    MySQL (and MariaDB, whose json is a longtext) and SQLite, on every Django and SQLAlchemy
    version, where the native json types and what each driver hands back differ."""
    return None if value is None else json.dumps(value)


def load_json(text):
    # type: (Any) -> Any
    if text is None or text == "":
        return None
    if not isinstance(text, (str, bytes)):
        return text  # read by a json column's driver already
    return json.loads(text)


def family_for(kind):
    # type: (Any) -> str
    """The list family a kind's ids are unique within: "name" for customers, vendors,
    employees and other names; "item" for "item" and every item_* kind; for anything else (an
    account, a class, a transaction, a kind this version doesn't know) the kind itself. TxnIDs
    are taken as unique per transaction type until QuickBooks shows otherwise."""
    kind = "" if kind is None else str(kind)
    if kind in NAME_KINDS:
        return "name"
    if kind == "item" or kind.startswith("item_"):
        return "item"
    return kind


def _quoted(value):
    # type: (Any) -> str
    return quote(str(value), safe="")


def _humanize(word):
    # type: (Any) -> str
    text = "" if word is None else str(word).replace("_", " ")
    return text[:1].upper() + text[1:]


class ConnectionMixin(object):
    """One QuickBooks Desktop connection: a company file on a customer's computer, reached
    through the Web Connector. Its owner is the account (or shop, or whatever your app's
    customer is) that connected it, and an owner can have any number: two company files, or a
    new file after a reconnect.

    qube_id is QuBe Sync's id for it, None until QuBe Sync answers the create. status is
    "pending" until the setup ends, then "connected", "setup_cancelled" or "stalled" (with
    stall_reason), kept up to date by its own webhooks (ConnectionEvents). revision is the
    last of those applied.

    The QuickBooks ids your app learns are kept against it, by list family (link, qb_id_for,
    find_linked), since a ListID is unique only within one list family of one company file.
    """

    _kit_store = None  # type: Any

    STATUSES = STATUSES

    @classmethod
    def owned_by(cls, owner):
        # type: (Any) -> Any
        """The connections owner has, whatever its key's type, as the ORM's query."""
        type_name, id = cls._kit_store.key_for(owner)
        return cls._kit_store.query(CONNECTION, owner_type=type_name, owner_id=id)

    @property
    def owner(self):
        # type: () -> Any
        """The account (or whatever your app's customer is) that connected it."""
        return self._kit_store.resolve(self.owner_type, self.owner_id)

    @owner.setter
    def owner(self, owner):
        # type: (Any) -> None
        self.owner_type, self.owner_id = self._kit_store.key_for(owner)

    @property
    def webhook_url(self):
        # type: () -> str
        """Where its events go: QUBE_WEBHOOK_URL/connections/<id>."""
        return "%s/connections/%s" % (settings().webhook_url, _quoted(self.id))

    def connected(self):
        # type: () -> bool
        return self.status == "connected"

    def not_checking_in(self):
        # type: () -> bool
        """Stalled because the Web Connector isn't checking in (the QuickBooks computer is
        off, or the Web Connector closed), rather than because it can't open QuickBooks."""
        return self.status == "stalled" and self.stall_reason == "not_checking_in"

    def sync_status(self, record, operation):
        # type: (Any, str) -> Any
        """Where record stands with QuickBooks on this connection for operation (a slug): a
        SyncStatus, derived from its runs and its link, never stored."""
        from ._sync_status import SyncStatus

        return SyncStatus.of(self, record, operation)

    def last_synced_at(self, workflow):
        # type: (Any) -> Optional[datetime.datetime]
        """When its last completed run of workflow started (aware UTC), or None before one: a
        sync's next since. Kept in qube_sync_marks, so pruning runs never loses it."""
        mark = self._kit_store.first(SYNC_MARK, connection_id=self.id, workflow=str(workflow))
        return self._kit_store.utc(mark.started_at) if mark is not None else None

    def disconnect(self):
        # type: () -> None
        """Deletes the row, with its runs (and their notifications), its plain requests (and
        their deliveries), its QuickBooks links and its sync marks, after your ConnectionEvents'
        disconnected(), all in one transaction: for a connection QuBe Sync no longer has. The
        disconnect route deletes QuBe Sync's first."""
        store = self._kit_store
        with store.atomic():
            settings().connection_events_class()(self).disconnected()
            _delete_with(store, store.query(RUN, connection_id=self.id), RUN, NOTIFICATION, "run_id")
            requests = store.query(QUEUED_REQUEST, connection_id=self.id)
            _delete_with(store, requests, QUEUED_REQUEST, REQUEST_DELIVERY, "request_id")
            store.delete_all(QUICKBOOKS_RECORD, connection_id=self.id)
            store.delete_all(SYNC_MARK, connection_id=self.id)
            store.delete(self)

    def in_quickbooks(self, query):
        # type: (Any) -> Any
        """Your records in query (a model, or the ORM's query of one) linked on this connection."""
        return self._kit_store.with_link(query, self.id, linked=True)

    def not_in_quickbooks(self, query):
        # type: (Any) -> Any
        return self._kit_store.with_link(query, self.id, linked=False)

    def needing_answer(self, query, operation):
        # type: (Any, str) -> Any
        """Your records in query whose run of operation on this connection waits for an answer."""
        return self._kit_store.with_run(query, self.id, str(operation), ASKING_STATES)

    def sending(self, query, operation):
        # type: (Any, str) -> Any
        """Your records in query whose run of operation on this connection is starting or running."""
        return self._kit_store.with_run(query, self.id, str(operation), SENDING_STATES)

    def adopt_qube_connection(self):
        # type: () -> Optional[str]
        """For a row without a qube_id: QuBe Sync's connection made for it, when a create
        landed but its id was never saved (it didn't commit, or the process died between the
        call and the save). Saves and returns the id, or None, so a second connection is never
        made for one row.

        It lists the app's connections (GET /api/v2/connections, which isn't paged) and
        adopts one only when exactly one has this row's webhook URL, has never connected
        (last_connected_at is null) or is simulated, was made at or after this row (its created_at), and has
        the row's name when the row has one. So a row id used again (MySQL 5.7 after a restart,
        a restored database) never takes an old connection. A connection with no created_at (a
        server from before v2 sent it) is never adopted. The listing only runs for a row
        without an id, which is rare."""
        if self.qube_id:
            return self.qube_id

        listed = [made for made in (client().list_connections() or []) if isinstance(made, dict)]
        if any(not made.get("created_at") and self._same_url(made) for made in listed):
            log.warning(
                "QuBe Sync: connection %s: QuBe Sync's connections carry no created_at, so none is "
                "adopted; a new one is made instead",
                self.id,
            )
        candidates = [made for made in listed if self._made_for_this_row(made)]
        if len(candidates) > 1:
            log.warning(
                "QuBe Sync: connection %s has no qube_id and %d of QuBe Sync's connections could be "
                "its; adopted none",
                self.id,
                len(candidates),
            )
            return None
        if not candidates:
            return None

        found = candidates[0]
        log.info(
            "QuBe Sync: connection %s adopted QuBe Sync's connection %s, made for it before its id was saved",
            self.id,
            found["id"],
        )
        self.qube_id = found["id"]
        self._kit_store.save(self, fields=["qube_id"])
        return self.qube_id

    def link(self, record, kind, qb_id, edit_sequence=None, name=None):
        # type: (Any, Any, Any, Optional[str], Optional[str]) -> Any
        """Keeps record's QuickBooks id for kind ("invoice", "customer", "item_service"...) on
        this connection, with its EditSequence and its name (FullName, or RefNumber), and
        returns the row. A record has one id per kind, so linking it again replaces its id. An
        id already linked in that kind's family (family_for) to another of your records moves
        to this one, and that's logged: the same QuickBooks record can stand for one of yours
        at a time. The same record and id linked with another kind of the family (an item
        converted from service to non-inventory) changes the row's kind."""
        kind = str(kind)
        qb_id = "" if qb_id is None else str(qb_id)
        if not qb_id:
            raise ValueError("QuBe Sync: link needs a qb_id")

        store = self._kit_store
        family = family_for(kind)
        key = store.key_for(record)
        attempts = 0
        while True:
            try:
                # A savepoint, so a unique-key race inside a caller's transaction (the job's
                # row lock) can be retried.
                with store.atomic(savepoint=True):
                    taken = store.first(QUICKBOOKS_RECORD, lock=True, connection_id=self.id, list=family, qb_id=qb_id)
                    mine = store.first(
                        QUICKBOOKS_RECORD,
                        lock=True,
                        connection_id=self.id,
                        kind=kind,
                        record_type=key[0],
                        record_id=key[1],
                    )
                    if self._replaced(mine, by=taken):
                        log.info(
                            "QuBe Sync: connection %s: %s %s's %s %s replaced by %s",
                            self.id,
                            key[0],
                            key[1],
                            kind,
                            mine.qb_id,
                            qb_id,
                        )
                        store.delete(mine)
                    if self._moved(taken, to=key):
                        log.warning(
                            "QuBe Sync: connection %s: %s %s moved from %s %s to %s %s",
                            self.id,
                            kind,
                            qb_id,
                            taken.record_type,
                            taken.record_id,
                            key[0],
                            key[1],
                        )
                    row = taken or mine or store.new(QUICKBOOKS_RECORD, connection_id=self.id)
                    row.kind = kind
                    row.list = family
                    row.qb_id = qb_id
                    row.record_type, row.record_id = key
                    if edit_sequence is not None:
                        row.edit_sequence = str(edit_sequence)
                    if name is not None:
                        row.name = str(name)
                    store.save(row)
                    return row
            except store.integrity_errors:
                # Another worker linked the same record or id at the same moment: once more,
                # now it's there to find.
                attempts += 1
                if attempts >= 2:
                    raise

    def qb_id_for(self, record, kind):
        # type: (Any, Any) -> Optional[str]
        """record's QuickBooks id for kind on this connection, or None: its link of that kind,
        else, outside the name family, its one link in that kind's family (an item linked as
        item_service, asked for as item or item_non_inventory). In the name family each kind
        is its own QuickBooks record (a customer and a vendor are two names), so a customer's
        id is never handed out as a vendor's. Raises ValueError when the family has several
        and none is that kind."""
        store = self._kit_store
        type_name, id = store.key_for(record)
        mine = {"connection_id": self.id, "record_type": type_name, "record_id": id}
        exact = store.first(QUICKBOOKS_RECORD, kind=str(kind), **mine)
        family = family_for(kind)
        if exact is not None or family == "name":
            return exact.qb_id if exact is not None else None

        row = self._only_one(dict(mine, list=family), "%s %s's %s" % (type_name, id, kind))
        return row.qb_id if row is not None else None

    def find_linked(self, qb_id, kind=None):
        # type: (Any, Optional[str]) -> Any
        """Your record linked to that QuickBooks id, or None."""
        row = self.quickbooks_record(qb_id, kind=kind)
        return row.record if row is not None else None

    def quickbooks_record(self, qb_id, kind=None):
        # type: (Any, Optional[str]) -> Any
        """The row for that QuickBooks id (with its kind, edit_sequence and name), or None.
        With a kind, it's looked up in that kind's family; without one, in every family, and
        an id found in more than one (the same counter value is a customer and an account)
        raises ValueError, so the caller says which kind it means."""
        rows = {"connection_id": self.id, "qb_id": str(qb_id)}
        if kind is not None:
            return self._kit_store.first(QUICKBOOKS_RECORD, list=family_for(kind), **rows)
        return self._only_one(rows, "QuickBooks id %s" % qb_id)

    # The record's own link is a different row from the one holding this qb_id, so it gives way.
    @staticmethod
    def _replaced(mine, by):
        # type: (Any, Any) -> bool
        return mine is not None and by is not None and by.id != mine.id

    # This qb_id was linked to another of your records.
    @staticmethod
    def _moved(taken, to):
        # type: (Any, Tuple[str, str]) -> bool
        return taken is not None and taken.record_id is not None and (taken.record_type, taken.record_id) != tuple(to)

    def _same_url(self, made):
        # type: (Dict[str, Any]) -> bool
        return str(made.get("webhook_url") or "").rstrip("/") == self.webhook_url

    # Nobody can have set it up: it has never connected, or it's simulated (connected from the
    # moment it's made), and only the lost answer to the create carried its setup link.
    @staticmethod
    def _unclaimed(made):
        # type: (Dict[str, Any]) -> bool
        return made.get("last_connected_at") is None or made.get("type") == "simulated"

    def _made_for_this_row(self, made):
        # type: (Dict[str, Any]) -> bool
        if not made.get("id"):
            return False
        if not self._same_url(made):
            return False
        if not self._unclaimed(made):
            return False
        if self.name and made.get("name") != self.name:
            return False

        made_at = parse_time(made.get("created_at"))
        created_at = self._kit_store.utc(self.created_at)
        if made_at is None or created_at is None:
            return False
        return made_at >= created_at - datetime.timedelta(seconds=CLOCK_SKEW_SECONDS)

    def _only_one(self, filters, what):
        # type: (Dict[str, Any], str) -> Any
        store = self._kit_store
        rows = store.filter(QUICKBOOKS_RECORD, limit=2, **filters)
        if len(rows) > 1:
            kinds = ", ".join(sorted(row.kind for row in store.filter(QUICKBOOKS_RECORD, **filters)))
            raise ValueError("QuBe Sync: %s is linked as more than one kind (%s): pass kind=" % (what, kinds))
        return rows[0] if rows else None


class RunMixin(object):
    """One workflow run, of one operation, for one of your records, on one connection.
    Written before the run starts (Operation.start), so a webhook that arrives first finds it;
    its webhook URL is QUBE_WEBHOOK_URL/runs/<id>.

    reference is new for every run and sent with it, and every event is checked against it and
    the connection's qube_id. revision is the last event applied; state ("starting", then the
    run's own: "running", "awaiting_input", "completed", "failed", "cancelled") and outcome
    are the run's as of that event. question and links are the question it's asking, if any,
    for the question template. input is what the run was started with. A start QuBe Sync
    refused (a 4xx), or whose input raised, leaves state "failed"; one that got no answer (a
    timeout, a 5xx, a dropped connection) stays "starting", for retry_start().
    """

    _kit_store = None  # type: Any

    ENDED_STATES = ENDED_STATES

    # True on the run Operation.start returned instead of starting another. Not saved.
    reused = False

    @classmethod
    def latest_for(cls, record, operation):
        # type: (Any, str) -> Any
        """record's newest run of operation (a slug), or None: the one whose question and
        status the templates show."""
        type_name, id = cls._kit_store.key_for(record)
        return cls._kit_store.first(
            RUN,
            order=["-created_at", "-id"],
            record_type=type_name,
            record_id=id,
            operation=str(operation),
        )

    @classmethod
    def prunable(cls, older_than):
        # type: (datetime.timedelta) -> Any
        """Ended runs whose end (ended_at, else updated_at: a run that failed before it started
        has none) is older than older_than, and never under a day, as the ORM's query."""
        return cls._kit_store.prunable(RUN, _cutoff(cls._kit_store, older_than), ENDED_STATES)

    @property
    def record(self):
        # type: () -> Any
        """Your record, by the run's record_type and record_id."""
        return self._kit_store.resolve(self.record_type, self.record_id)

    @record.setter
    def record(self, record):
        # type: (Any) -> None
        self.record_type, self.record_id = self._kit_store.key_for(record)

    @property
    def webhook_url(self):
        # type: () -> str
        return "%s/runs/%s" % (settings().webhook_url, _quoted(self.id))

    def retry_start(self):
        # type: () -> Any
        """Sends a start that didn't get an answer again: same reference (the
        Idempotency-Key), workflow, input and webhook URL, so QuBe Sync answers with the run
        the first one started, if it did, instead of starting another. See
        Operation.retry_start."""
        operation = settings().operation_class(self.operation)
        if operation is None:
            raise UnknownOperation("QuBe Sync: no operation has the slug %r" % (self.operation,))
        return operation.retry_start(self)

    def ended(self):
        # type: () -> bool
        """Whether it has ended: completed, failed or cancelled."""
        return self.state in ENDED_STATES

    def failed(self):
        # type: () -> bool
        return self.state == "failed"

    def cancelled(self):
        # type: () -> bool
        """Cancelled by your app (state "cancelled"), or a chart that ended on its own
        "cancelled" outcome (the app chose to stop): neither is a success."""
        return self.state == "cancelled" or (self.state == "completed" and self.outcome == "cancelled")

    def unconfirmed(self):
        # type: () -> bool
        """A start QuBe Sync hasn't confirmed for a minute: send it again with retry_start()."""
        store = self._kit_store
        created_at = store.utc(self.created_at)
        if self.state != "starting" or created_at is None:
            return False
        return created_at < store.utc(store.now()) - datetime.timedelta(seconds=UNCONFIRMED_AFTER_SECONDS)

    def looks_stuck(self):
        # type: () -> bool
        """Confirmed, not ended, and quiet for QUIET_AFTER_SECONDS while running or waiting on a
        question this app never received: its webhook may have been lost."""
        return self._quiet() and (self.state == "running" or self._question_missing())

    def _quiet(self):
        # type: () -> bool
        store = self._kit_store
        updated_at = store.utc(self.updated_at)
        if not self.qube_run_id or self.ended() or updated_at is None:
            return False
        return updated_at < store.utc(store.now()) - datetime.timedelta(seconds=QUIET_AFTER_SECONDS)

    def _question_missing(self):
        # type: () -> bool
        return self.state == "awaiting_input" and self.open_question is None

    @property
    def summary_text(self):
        # type: () -> str
        """Where it stands, in a few words for a person: "Added to QuickBooks", "Done",
        "Couldn't sync", "Cancelled", "Needs your answer", "Sending to QuickBooks", "Still
        waiting for QuickBooks" (a start unconfirmed for a minute) or "Syncing with QuickBooks".
        Why it failed or was cancelled is reason_text. The words are the messages setting's."""
        if self.cancelled():
            return t("status.cancelled")
        state = self.state
        if state == "starting":
            return t("status.unconfirmed" if self.unconfirmed() else "status.starting")
        if state == "completed":
            outcome = self.outcome or ""
            if outcome == "added":
                return t("status.added")
            if outcome in ("", "completed"):
                return t("status.done")
            return t("status.done_with", outcome=_humanize(outcome))
        if state == "failed":
            return t("status.failed")
        if state == "awaiting_input":
            return t("status.needs_answer")
        return t("status.running")

    @property
    def reason_text(self):
        # type: () -> Optional[str]
        """Why it failed (its error's message) or was cancelled (the reason it carried), as a
        sentence, or None."""
        if self.cancelled():
            text = (self.cancel_reason or "").strip()
        elif self.state == "failed":
            text = (self.error_message or "").strip()
        else:
            return None
        if not text:
            return None
        text = text[:1].upper() + text[1:]
        return text if text[-1] in ".!?" else text + "."

    @property
    def cancel_reason_text(self):
        # type: () -> str
        """Why it was cancelled: the reason it carried, else what a cancelled outcome means."""
        reason = (self.cancel_reason or "").strip()
        return reason or t("status.cancel_reason")

    @property
    def error_message(self):
        # type: () -> Optional[str]
        """A failed run's message: its error's own (a sentence, or the message of a code,
        message and detail), else its outcome in words, or None."""
        error = self.error
        text = None
        if isinstance(error, str):
            text = error
        elif isinstance(error, dict):
            text = error.get("message") or error.get("detail")
        text = ("" if text is None else str(text)).strip()
        if text:
            return text
        if self.outcome is None and self.ended_at is None:
            return t("status.not_started")
        if not self.outcome or self.outcome == "failed":
            return None
        return _humanize(self.outcome)

    @property
    def error_detail(self):
        # type: () -> Optional[str]
        """The error's detail, when it carries one apart from its message."""
        error = self.error
        if not isinstance(error, dict):
            return None
        detail = ("" if error.get("detail") is None else str(error.get("detail"))).strip()
        if not detail or detail == self.error_message:
            return None
        return detail

    @property
    def open_question(self):
        # type: () -> Optional[Dict[str, Any]]
        """The question it's asking, as its webhook's prompt had it, or None."""
        question = self.question
        return question if isinstance(question, dict) else None


class QuickbooksRecordMixin(object):
    """A QuickBooks record your app knows on one connection: its kind ("customer",
    "item_service", "invoice"...), its list family (list), its ListID or TxnID (qb_id), its
    EditSequence and its name, and which of your records it stands for, if any. Written
    through Connection.link.

    QuickBooks makes a ListID unique within a list family, not within one kind (verified on
    QuickBooks Enterprise 24.0): customers, vendors, employees and other names share one
    counter, every item type shares another, and each other list (accounts, classes,
    terms...) has its own, while the same counter value turns up in several families. So a row
    is unique by connection, family and qb_id, and by connection, kind and your record (one
    contact can be both a customer and a vendor, as two QuickBooks names).
    """

    _kit_store = None  # type: Any

    NAME_KINDS = NAME_KINDS
    family_for = staticmethod(family_for)

    @property
    def record(self):
        # type: () -> Any
        """The record of yours it stands for, or None."""
        if self.record_type is None:
            return None
        return self._kit_store.resolve(self.record_type, self.record_id)


class QueuedRequestMixin(object):
    """One plain v2 request (qubesync.kit.Request.queue) for one of your records, on one
    connection. Written before it's sent; its webhook URL is QUBE_WEBHOOK_URL/requests/<id>.

    operation is the Request's slug. reference is the Idempotency-Key, params what was sent.
    state is "queued", "retryable", "response_received", "error", "timed_out", "discarded", or
    "failed" (QuBe Sync refused the queue, or params raised); error is the webhook's.
    pages_answered and last_page count the pages in; ended_at is set once every page is in,
    or on a final error. It never keeps a response body.
    """

    _kit_store = None  # type: Any

    # True on the row Request.queue returned instead of queueing another. Not saved.
    reused = False

    @classmethod
    def latest_for(cls, record, operation):
        # type: (Any, str) -> Any
        """record's newest request of operation (a slug), or None."""
        type_name, id = cls._kit_store.key_for(record)
        return cls._kit_store.first(
            QUEUED_REQUEST,
            order=["-created_at", "-id"],
            record_type=type_name,
            record_id=id,
            operation=str(operation),
        )

    @classmethod
    def prunable(cls, older_than):
        # type: (datetime.timedelta) -> Any
        """Ended requests older than older_than (never under a day), as the ORM's query."""
        return cls._kit_store.prunable(QUEUED_REQUEST, _cutoff(cls._kit_store, older_than))

    @property
    def record(self):
        # type: () -> Any
        return self._kit_store.resolve(self.record_type, self.record_id)

    @record.setter
    def record(self, record):
        # type: (Any) -> None
        self.record_type, self.record_id = self._kit_store.key_for(record)

    @property
    def webhook_url(self):
        # type: () -> str
        return "%s/requests/%s" % (settings().webhook_url, _quoted(self.id))

    def ended(self):
        # type: () -> bool
        return self.ended_at is not None

    def done(self):
        # type: () -> bool
        """Every page answered."""
        return self.ended() and self.state == "response_received"

    def retry_queue(self):
        # type: () -> Any
        """Sends a queue QuBe Sync never confirmed again: same params and Idempotency-Key."""
        request = settings().operation_class(self.operation)
        if request is None:
            raise UnknownOperation("QuBe Sync: no operation has the slug %r" % (self.operation,))
        return request.retry_queue(self)


def _cutoff(store, older_than):
    # type: (Any, datetime.timedelta) -> datetime.datetime
    if not isinstance(older_than, datetime.timedelta):
        raise TypeError("QuBe Sync: older_than is a datetime.timedelta")
    return store.now() - max(older_than, MIN_PRUNE_AGE)


def _delete_with(store, query, model_name, child, foreign_key):
    # type: (Any, Any, str, str, str) -> int
    # In batches: the children of each first, since only some ORMs cascade.
    deleted = 0
    while True:
        ids = store.ids(query, PRUNE_BATCH)
        if not ids:
            return deleted
        with store.atomic():
            store.delete_all(child, **{foreign_key: ids})
            count = store.delete_all(model_name, id=ids)
        if not count:
            return deleted
        deleted += count


def prune_runs():
    # type: () -> None
    """Deletes ended runs older than the prune_runs_after setting (Run.prunable), with their
    notifications, and ended plain requests (QueuedRequest.prunable) with their deliveries.
    QuickBooks links and sync marks stay. Does nothing until the setting is set: schedule it
    (cron, Celery beat) once a day."""
    after = settings().prune_runs_after
    if after is None:
        return
    store = current_store()
    _delete_with(store, store.model(RUN).prunable(after), RUN, NOTIFICATION, "run_id")
    _delete_with(store, store.model(QUEUED_REQUEST).prunable(after), QUEUED_REQUEST, REQUEST_DELIVERY, "request_id")


def advance_sync_mark(connection, workflow, started_at):
    # type: (Any, Any, datetime.datetime) -> None
    """Moves connection's mark for workflow to started_at, never back: runs can complete out
    of order."""
    store = connection._kit_store
    workflow = str(workflow)
    for attempt in range(2):
        try:
            # A savepoint, so a unique-key race inside the handler's transaction can be retried.
            with store.atomic(savepoint=True):
                mark = store.first(SYNC_MARK, lock=True, connection_id=connection.id, workflow=workflow)
                if mark is None:
                    store.save(store.new(SYNC_MARK, connection_id=connection.id, workflow=workflow, started_at=started_at))
                elif store.utc(mark.started_at) < store.utc(started_at):
                    mark.started_at = started_at
                    store.save(mark)
                return
        except store.integrity_errors:
            if attempt:
                raise
