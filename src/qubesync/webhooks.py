"""Verify QuBe Sync webhook deliveries and parse them into typed events.

Framework-free and standard library only::

    from qubesync import webhooks

    try:
        event = webhooks.verify(raw_body, signature_header, secrets=["whsec_..."])
    except webhooks.SignatureError as e:
        # e.reason is "missing", "malformed", "stale" or "mismatch"
        return 401

    if event.type == "request":
        ...

`verify` checks the ``X-QUBE-Signature`` header (``t=<unix seconds>,v1=<hex>[,v1=<hex>...]``),
then parses the body. `parse` builds the event without checking anything.
"""

import datetime
import hashlib
import hmac
import json
import re
import time
from typing import Any, Dict, List, Optional, Union

from .errors import QubeSyncError

__all__ = [
    "SignatureError",
    "verify",
    "parse",
    "Event",
    "RequestEvent",
    "WorkflowRunEvent",
    "NotificationEvent",
    "ConnectionEvent",
    "NameIndexEvent",
    "UnknownEvent",
    "HEADER",
    "DEFAULT_TOLERANCE",
]

HEADER = "X-QUBE-Signature"
DEFAULT_TOLERANCE = 300

_DIGITS = re.compile(r"\A[0-9]+\Z")

RawBody = Union[bytes, bytearray, memoryview, str]
Secrets = Union[str, bytes, List[Union[str, bytes]]]
Now = Union[int, float, datetime.datetime, None]


class SignatureError(QubeSyncError):
    """A delivery failed verification. Answer it with 401.

    ``reason`` is one of ``"missing"``, ``"malformed"``, ``"stale"``, ``"mismatch"``. The message
    is safe to log: it never holds the secret, the signatures or the body.
    """

    def __init__(self, reason, message):
        # type: (str, str) -> None
        super().__init__(message)
        self.reason = reason


def verify(raw_body, header, secrets, tolerance=DEFAULT_TOLERANCE, now=None):
    # type: (RawBody, Optional[str], Secrets, int, Now) -> Event
    """Verify a delivery and return its typed event.

    ``raw_body`` is the body exactly as received (bytes or str), before anything parses it.
    ``header`` is the ``X-QUBE-Signature`` value (None when absent). ``secrets`` is a list of
    webhook secrets (or a single one); any of them may match, so a secret can rotate.
    ``now`` is unix seconds or a ``datetime`` (naive means UTC), defaulting to the current time.

    Raises `SignatureError` (``missing``, ``malformed``, ``stale``, ``mismatch``, checked in
    that order). Raises ``TypeError`` when the body is already parsed and ``ValueError`` when
    ``secrets`` is empty.
    """
    body = _raw_bytes(raw_body)
    keys = _secret_list(secrets)
    current = _unix_seconds(now)

    if isinstance(header, (bytes, bytearray)):
        header = bytes(header).decode("utf-8", errors="replace")
    if header is None or not str(header).strip():
        raise SignatureError("missing", "Webhook signature missing: no %s header." % HEADER)

    timestamp, signatures = _parse_header(str(header))

    age = current - timestamp
    if abs(age) > tolerance:
        when = "%d seconds old" % age if age > 0 else "%d seconds in the future" % -age
        raise SignatureError(
            "stale",
            "Webhook signature stale: the timestamp is %s; it must be within %d seconds of now. "
            "Check this server's clock." % (when, tolerance),
        )

    signed = str(timestamp).encode("ascii") + b"." + body
    expected = [hmac.new(key, signed, hashlib.sha256).hexdigest().encode("ascii") for key in keys]
    matched = False
    for signature in signatures:
        given = signature.encode("utf-8")
        for candidate in expected:
            # Different lengths compare as False without raising.
            if hmac.compare_digest(candidate, given):
                matched = True
    if not matched:
        raise SignatureError(
            "mismatch",
            "Webhook signature mismatch: no v1 signature matches the body under any of the secrets.",
        )

    return parse(body)


def parse(raw_body):
    # type: (Union[RawBody, Dict[str, Any]]) -> Event
    """Build the typed event from a body without verifying it.

    For tests, and for code that verified the delivery elsewhere. Accepts the raw body or an
    already-parsed dict. Raises ``ValueError`` when the body isn't a JSON object.
    """
    if isinstance(raw_body, dict):
        data = raw_body
    else:
        data = json.loads(_raw_bytes(raw_body).decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("A webhook body is a JSON object; this one is a %s." % type(data).__name__)
    return _event_class(data)(data)


def _event_class(data):
    event = data.get("event")
    if event is None:
        if data.get("page_request_id") is not None:
            return RequestEvent
        return UnknownEvent
    if not isinstance(event, str):
        return UnknownEvent
    if event in WorkflowRunEvent.EVENTS:
        return WorkflowRunEvent
    if event == NotificationEvent.EVENT:
        return NotificationEvent
    if event.startswith("connection."):
        return ConnectionEvent
    if event.startswith("name_index."):
        return NameIndexEvent
    return UnknownEvent


def _raw_bytes(raw_body):
    if isinstance(raw_body, str):
        return raw_body.encode("utf-8")
    if isinstance(raw_body, (bytes, bytearray, memoryview)):
        return bytes(raw_body)
    if isinstance(raw_body, (dict, list)):
        raise TypeError(
            "Pass the raw request body (bytes or str) as received, not a parsed %s: "
            "the signature covers the exact bytes." % type(raw_body).__name__
        )
    raise TypeError(
        "Pass the raw request body as bytes or str, not %s." % type(raw_body).__name__
    )


def _secret_list(secrets):
    if isinstance(secrets, (str, bytes, bytearray)):
        secrets = [secrets]
    if secrets is None:
        raise ValueError("verify() needs at least one webhook secret.")
    keys = []
    for secret in secrets:
        if isinstance(secret, str):
            keys.append(secret.encode("utf-8"))
        elif isinstance(secret, (bytes, bytearray)):
            keys.append(bytes(secret))
        else:
            raise TypeError("Each webhook secret is a str or bytes, not %s." % type(secret).__name__)
    if not keys:
        raise ValueError("verify() needs at least one webhook secret; the list is empty.")
    return keys


def _unix_seconds(now):
    if now is None:
        return int(time.time())
    if isinstance(now, datetime.datetime):
        if now.tzinfo is None:
            now = now.replace(tzinfo=datetime.timezone.utc)
        return int(now.timestamp() // 1)
    if isinstance(now, bool) or not isinstance(now, (int, float)):
        raise TypeError("now is unix seconds or a datetime, not %s." % type(now).__name__)
    return int(now // 1)


def _parse_header(header):
    timestamp = None
    signatures = []
    for part in header.split(","):
        key, sep, value = part.strip().partition("=")
        if not sep:
            continue
        if key == "t" and timestamp is None:
            timestamp = value
        elif key == "v1" and value:
            signatures.append(value)
    if timestamp is None or not _DIGITS.match(timestamp) or not signatures:
        raise SignatureError(
            "malformed",
            "Webhook signature malformed: the %s header needs a t of whole unix seconds "
            "and at least one v1." % HEADER,
        )
    return int(timestamp), signatures


class Event(object):
    """A parsed webhook body. Missing keys read as None."""

    type = "unknown"  # type: str

    def __init__(self, body):
        # type: (Dict[str, Any]) -> None
        self.body = body

    def get(self, key, default=None):
        # type: (str, Any) -> Any
        return self.body.get(key, default)

    def to_dict(self):
        # type: () -> Dict[str, Any]
        return self.body

    @property
    def event(self):
        # type: () -> Optional[str]
        return self.body.get("event")

    @property
    def timestamp(self):
        return self.body.get("timestamp")

    @property
    def app_id(self):
        # type: () -> Optional[str]
        return self.body.get("app_id")

    @property
    def sandbox(self):
        # type: () -> Optional[bool]
        return self.body.get("sandbox")

    @property
    def dedupe_key(self):
        # type: () -> Optional[str]
        """A key to store so a redelivery is handled once, or None when the type has none."""
        return None

    @property
    def revision(self):
        # type: () -> Optional[int]
        return None

    @property
    def reference(self):
        # type: () -> Optional[str]
        return None

    def __repr__(self):
        return "<%s event=%r>" % (type(self).__name__, self.event)


class _Revisioned(Event):
    @property
    def revision(self):
        # type: () -> Optional[int]
        return self.body.get("revision")

    def newer_than(self, stored_revision):
        # type: (Optional[int]) -> bool
        """True when there's nothing stored yet or this revision is higher than the stored one.

        Apply the event only when this is true; an older or equal revision arrived late.
        """
        if stored_revision is None:
            return True
        revision = self.revision
        if revision is None:
            return False
        return revision > stored_revision


class RequestEvent(Event):
    """A queued request's answer (one page of it, for a paginated query)."""

    type = "request"

    @property
    def id(self):
        return self.body.get("id")

    @property
    def page_request_id(self):
        return self.body.get("page_request_id")

    @property
    def state(self):
        return self.body.get("state")

    @property
    def page(self):
        return self.body.get("page")

    @property
    def iteration_state(self):
        return self.body.get("iteration_state")

    @property
    def response_json(self):
        return self.body.get("response_json")

    @property
    def error(self):
        return self.body.get("error")

    @property
    def dedupe_key(self):
        # type: () -> Optional[str]
        """``"<page_request_id>:<state>"``: one page in one state is handled once."""
        page_request_id = self.page_request_id
        if page_request_id is None:
            return None
        state = self.state
        return "%s:%s" % (page_request_id, "" if state is None else state)


class WorkflowRunEvent(_Revisioned):
    """A workflow run is waiting for an answer, or finished. Apply it only when newer_than()."""

    type = "workflow_run"
    EVENTS = (
        "workflow_run.awaiting_input",
        "workflow_run.completed",
        "workflow_run.failed",
        "workflow_run.cancelled",
    )

    @property
    def run_id(self):
        return self.body.get("run_id")

    @property
    def reference(self):
        return self.body.get("reference")

    @property
    def run_state(self):
        return self.body.get("run_state")

    @property
    def workflow(self):
        return self.body.get("workflow")

    @property
    def connection_id(self):
        return self.body.get("connection_id")

    @property
    def prompt(self):
        return self.body.get("prompt")

    @property
    def outcome(self):
        return self.body.get("outcome")

    @property
    def output(self):
        return self.body.get("output")

    @property
    def error(self):
        return self.body.get("error")

    @property
    def summary(self):
        return self.body.get("summary")

    @property
    def cancel_reason(self):
        return self.body.get("cancel_reason")

    @property
    def links(self):
        return self.body.get("links")


class NotificationEvent(Event):
    """Data a running workflow sent out. Never skip one by revision; dedupe on delivery_id."""

    type = "notification"
    EVENT = "workflow_run.notification"

    @property
    def run_id(self):
        return self.body.get("run_id")

    @property
    def reference(self):
        return self.body.get("reference")

    @property
    def revision(self):
        return self.body.get("revision")

    @property
    def connection_id(self):
        return self.body.get("connection_id")

    @property
    def delivery_id(self):
        return self.body.get("delivery_id")

    @property
    def seq(self):
        return self.body.get("seq")

    @property
    def name(self):
        return self.body.get("name")

    @property
    def state(self):
        return self.body.get("state")

    @property
    def from_(self):
        """The body's ``from`` (``from`` is a Python keyword)."""
        return self.body.get("from")

    @property
    def data(self):
        return self.body.get("data")

    @property
    def dedupe_key(self):
        return self.delivery_id


class ConnectionEvent(_Revisioned):
    """A connection connected, cancelled setup, stalled or resumed. Apply it only when newer_than()."""

    type = "connection"

    @property
    def delivery_id(self):
        return self.body.get("delivery_id")

    @property
    def connection(self):
        return self.body.get("connection")

    @property
    def connection_id(self):
        connection = self.connection
        return connection.get("id") if isinstance(connection, dict) else None

    @property
    def stall_reason(self):
        connection = self.connection
        if isinstance(connection, dict) and connection.get("stall_reason") is not None:
            return connection.get("stall_reason")
        return self.body.get("stall_reason")

    @property
    def dedupe_key(self):
        return self.delivery_id


class NameIndexEvent(Event):
    """A connection's name index is ready or failed."""

    type = "name_index"

    @property
    def connection_id(self):
        return self.body.get("connection_id")

    @property
    def name_index(self):
        return self.body.get("name_index")


class UnknownEvent(Event):
    """An event this library doesn't know yet. Read it through body / get()."""

    type = "unknown"
