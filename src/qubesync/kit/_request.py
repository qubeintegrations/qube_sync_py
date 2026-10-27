"""Request, the base of your classes that queue one plain v2 operation, with no workflow."""
import json
import logging
import uuid
from typing import Any, Dict, Set

from ..v2 import APIError
from ._defaults import client
from ._errors import NotConnected
from ._store import QUEUED_REQUEST, REQUEST_DELIVERY

log = logging.getLogger("qubesync.kit")

__all__ = ["Request"]

FINAL_STATES = ("error", "timed_out", "discarded")
LAST_PAGE = ("done", "not_applicable")


class Request(object):
    """One v2 operation your app queues itself, and what it does with that request's webhooks:
    subclass it once per request, list it in the operations setting by its slug, and see the
    README's "Plain requests".

        class FindCustomer(qubesync.kit.Request):
            operation = "customer.query"  # a v2 operation id
            slug = "find_customer"

            def params(self):
                return {"full_name": self.record.name}

            def answered(self, event):
                found = (event.response_json or {}).get("data") or []
                ...

        row = FindCustomer.queue(customer, connection)
    """

    operation = ""  # the v2 operation id it queues
    slug = ""  # its key in the operations setting, kept on each row

    def __init__(self, record, queued_request):
        # type: (Any, Any) -> None
        self.record = record
        self.queued_request = queued_request

    @classmethod
    def queue(cls, record, connection):
        # type: (Any, Any) -> Any
        """The QueuedRequest for record (saved) on connection (one with a qube_id). While the
        last one hasn't ended it's returned (row.reused), sent again first if QuBe Sync never
        confirmed it."""
        if not (getattr(connection, "_kit_store", None) is not None and getattr(connection, "qube_id", None)):
            raise NotConnected(
                "QuBe Sync: %s.queue needs a connection QuBe Sync has made (one with a qube_id): "
                "the customer finishes onboarding first" % cls.__name__
            )
        if not cls.slug or not cls.operation:
            raise NotImplementedError("%s needs its operation and slug" % cls.__name__)

        row, params_error = cls._claim(record, connection)
        if params_error is not None:
            raise params_error
        if not row.reused:
            return cls._send_queue(row)
        row = cls.retry_queue(row)
        row.reused = True
        return row

    @classmethod
    def retry_queue(cls, row):
        # type: (Any) -> Any
        """Sends a queue that got no answer again, with the same params and Idempotency-Key. A
        row QuBe Sync confirmed is returned as it is."""
        if row.qube_id:
            return row
        if row.state != "queued":
            raise ValueError(
                "QuBe Sync: request %s is %s: only a queue that got no answer is sent again" % (row.id, row.state)
            )
        return cls._send_queue(row)

    @classmethod
    def _claim(cls, record, connection):
        # type: (Any, Any) -> Any
        # Under the connection row's lock, so a double click finds the first click's row.
        store = connection._kit_store
        type_name, record_id = store.key_for(record)
        with store.locked(connection) as locked:
            going = store.first(
                QUEUED_REQUEST,
                order=["-created_at", "-id"],
                connection_id=locked.id,
                record_type=type_name,
                record_id=record_id,
                operation=cls.slug,
            )
            if going is not None and not going.ended():
                going.reused = True
                return going, None
            return cls._new_row(store, record, locked)

    @classmethod
    def _new_row(cls, store, record, connection):
        # type: (Any, Any, Any) -> Any
        row = store.new(
            QUEUED_REQUEST,
            connection_id=connection.id,
            operation=cls.slug,
            record=record,
            reference="%s-%s-%s" % (cls.slug, store.key_for(record)[1], uuid.uuid4()),
            state="queued",
            pages_answered=0,
        )
        request = cls(record, row)
        request._connection = connection  # an unsaved row may not reach it yet
        try:
            # As JSON reads it back, so a resend sends exactly what the first did.
            row.params = json.loads(json.dumps(request.params()))
        except Exception as error:  # params not written yet (NotImplementedError), too
            row.state = "failed"
            row.ended_at = store.now()
            store.save(row)
            return row, error
        store.save(row)
        return row, None

    @classmethod
    def _send_queue(cls, row):
        # type: (Any) -> Any
        try:
            answer = client().queue(
                cls.operation,
                row.connection.qube_id,
                row.params or {},
                webhook_url=row.webhook_url,
                idempotency_key=row.reference,
            )
        except APIError as error:
            # A 4xx queued nothing, but a 409 is the key in use by a call still in flight.
            if 400 <= error.status < 500 and error.status != 409:
                row.state = "failed"
                row.ended_at = row._kit_store.now()
                row._kit_store.save(row, fields=["state", "ended_at"])
            raise
        answer = answer if isinstance(answer, dict) else {}
        with row._kit_store.locked(row) as locked:
            locked.qube_id = locked.qube_id or answer.get("id")
            row._kit_store.save(locked)
        return locked

    @classmethod
    def find_record(cls, id):
        # type: (str) -> Any
        """Your record, by the id its row keeps (a string). Leave it out and the row's
        record_type finds it."""
        raise NotImplementedError(
            "%s.find_record(%r) isn't written: leave it out to find the record by the row's record_type"
            % (cls.__name__, id)
        )

    @classmethod
    def record_for(cls, row):
        # type: (Any) -> Any
        if getattr(cls.find_record, "__func__", None) is Request.find_record.__func__:
            return row.record
        return cls.find_record(row.record_id)

    @property
    def connection(self):
        # type: () -> Any
        return self.__dict__.get("_connection") or self.queued_request.connection

    # What your request does: params says what to send, the rest what to do with its webhooks.

    def params(self):
        # type: () -> Dict[str, Any]
        """The operation's params, from the record."""
        raise NotImplementedError("%s.params isn't written yet" % type(self).__name__)

    def answered(self, event):
        # type: (Any) -> None
        """One page answered: event.response_json["data"], event.page."""
        self.log_event(event)

    def done(self):
        # type: () -> None
        """Every page 1..N answered. Called once."""

    def failed(self, event):
        # type: (Any) -> None
        """error or discarded: event.error["user_message"] is safe to show."""
        self.log_event(event)

    def retrying(self, event):
        # type: (Any) -> None
        """QuBe Sync keeps trying (QuickBooks closed, a dialog open): show
        event.error["user_message"], never resend."""
        self.log_event(event)

    def timed_out(self, event):
        # type: (Any) -> None
        """The answer never came back: QuickBooks may have applied it. A query can be queued
        again; check a write first. Default: failed(event)."""
        self.failed(event)

    def handle(self, event):
        # type: (Any) -> None
        """One webhook, from the job, under the row's lock. Deliveries come at least once, in
        any order."""
        store = self.queued_request._kit_store
        with store.locked(self.queued_request) as row:
            self.queued_request = row
            self._apply(event)

    def log_event(self, event):
        # type: (Any) -> None
        """All a handler does until you fill it in."""
        error = event.get("error")
        code = ""
        if isinstance(error, dict):
            code = " %s" % (error.get("error_code") or error.get("error_type"))
        line = "QuBe Sync: %s %s (request %s): %s page %s%s" % (
            type(self).__name__,
            self.queued_request._kit_store.key_for(self.record)[1],
            self.queued_request.id,
            event.get("state"),
            _page_of(event),
            code,
        )
        if event.get("state") == "response_received":
            log.info(line)
        else:
            log.warning(line)

    def _apply(self, event):
        # type: (Any) -> None
        row = self.queued_request
        if not self._this_request(event):
            log.warning(
                "QuBe Sync: %s request %s skipped %s %r: not this request",
                type(self).__name__,
                row.id,
                event.type,
                event.get("id"),
            )
            return
        if not self._take_once(event):
            return

        row.qube_id = row.qube_id or event.id
        state = event.state
        if state == "response_received":
            self._page_answered(event)
        elif state == "retryable":
            self._retryable(event)
        elif state in FINAL_STATES:
            self._final(event)
        else:
            log.warning("QuBe Sync: %s request %s: unknown state %r", type(self).__name__, row.id, state)
        row._kit_store.save(row)

    # Request events carry no connection id: the id is checked once the row has one.
    def _this_request(self, event):
        # type: (Any) -> bool
        if event.type != "request":
            return False
        qube_id = self.queued_request.qube_id
        return qube_id is None or event.id == qube_id

    # Records the delivery in this transaction: False for one taken already.
    def _take_once(self, event):
        # type: (Any) -> bool
        row = self.queued_request
        store = row._kit_store
        key = event.dedupe_key or ""
        if store.exists(REQUEST_DELIVERY, request_id=row.id, dedupe_key=key):
            return False
        try:
            with store.atomic(savepoint=True):
                delivery = store.new(
                    REQUEST_DELIVERY, request_id=row.id, dedupe_key=key, page=_page_of(event), state=str(event.state)
                )
                store.save(delivery)
        except store.integrity_errors:
            return False
        return True

    def _page_answered(self, event):
        # type: (Any) -> None
        row = self.queued_request
        if event.iteration_state in LAST_PAGE:
            row.last_page = _page_of(event)
        if not row.ended():
            row.state = "response_received"
        self.answered(event)

        pages = self._answered_pages()
        row.pages_answered = len(pages)
        if row.ended() or row.last_page is None:
            return
        if len([page for page in pages if 1 <= page <= row.last_page]) != row.last_page:
            return
        row.ended_at = row._kit_store.now()
        self.done()

    def _retryable(self, event):
        # type: (Any) -> None
        row = self.queued_request
        if self._page_settled(event):
            log.info(
                "QuBe Sync: %s request %s page %s: skipped a retryable that came after its answer",
                type(self).__name__,
                row.id,
                _page_of(event),
            )
            return
        if not row.ended():
            row.state = "retryable"
            row.error = event.error
        self.retrying(event)

    def _final(self, event):
        # type: (Any) -> None
        row = self.queued_request
        if not row.ended():
            row.state = event.state
            row.error = event.error
            row.ended_at = row._kit_store.now()
        if event.state == "timed_out":
            self.timed_out(event)
        else:
            self.failed(event)

    def _answered_pages(self):
        # type: () -> Set[int]
        row = self.queued_request
        taken = row._kit_store.filter(REQUEST_DELIVERY, request_id=row.id, state="response_received")
        return {delivery.page for delivery in taken if delivery.page is not None}

    def _page_settled(self, event):
        # type: (Any) -> bool
        row = self.queued_request
        return row._kit_store.exists(
            REQUEST_DELIVERY, request_id=row.id, page=_page_of(event), state__not="retryable"
        )


# An answer that wasn't paged is page 1.
def _page_of(event):
    # type: (Any) -> int
    page = event.get("page")
    return page if isinstance(page, int) and not isinstance(page, bool) else 1

