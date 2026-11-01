"""A client for the QuBe Sync v2 API (https://docs.qubesync.com).

    from qubesync import Client

    client = Client(api_key=os.environ["QUBE_API_KEY"])
    connection = client.create_connection(webhook_url="https://example.com/webhooks/qube")

The client never reads the environment: pass the API key in. Every method returns the
response's ``data`` as plain dicts and lists, except where its docstring says otherwise.
A refused request raises :class:`APIError`; a connection that still fails after the retries
raises the ``requests`` exception unchanged.
"""

import datetime
import json
import random
import time
import uuid
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple
from urllib.parse import parse_qs, quote, quote_plus, urlencode, urlsplit

import requests
from urllib3.exceptions import ConnectTimeoutError, NewConnectionError

from ._version import __version__
from .errors import QubeSyncError
from .operations import OPERATIONS
from .operations._accessors import OperationsMixin

__all__ = ["Client", "APIError", "NOT_MODIFIED"]

DEFAULT_BASE_URL = "https://qubesync.com"
API_PREFIX = "/api/v2"

_RETRY_STATUSES = (429, 502, 503, 504)
_RETRY_AFTER_STATUSES = (429, 503)
_RETRY_AFTER_CAP = 30.0
_BACKOFF = (0.5, 1.0)
_RETRY_SAFE_METHODS = ("GET", "PUT", "DELETE")
# Answers after which the request may have been carried out though its answer was lost.
_MAYBE_APPLIED_STATUSES = (502, 504)
_RAW_BODY_LIMIT = 500


class _NotModified(object):
    __slots__ = ()

    def __repr__(self):
        return "NOT_MODIFIED"


# What Client.workflow_types returns when the document is still the one its etag names.
NOT_MODIFIED = _NotModified()


class APIError(QubeSyncError):
    """QuBe Sync answered with a non-2xx status.

    Attributes:
        status: the HTTP status (int).
        errors: the body's ``errors`` as parsed (a string, dict or list), or None when the body
            isn't JSON or has none.
        code: ``errors["code"]`` when ``errors`` is a dict with a string ``code``, else None.
        message: one line for a log: ``"QuBe Sync answered <status>: <text>"``.
        body: the raw response text.
        request_id: the ``x-request-id`` response header, or None.
    """

    def __init__(self, status, body="", errors=None, request_id=None):
        # type: (int, str, Any, Optional[str]) -> None
        self.status = status
        self.body = body or ""
        self.errors = errors
        self.request_id = request_id
        code = errors.get("code") if isinstance(errors, dict) else None
        self.code = code if isinstance(code, str) else None
        self.message = "QuBe Sync answered %d: %s" % (status, _error_text(errors, self.body))
        super().__init__(self.message)

    @classmethod
    def from_response(cls, response):
        # type: (requests.Response) -> APIError
        text = response.text or ""
        errors = None
        try:
            parsed = json.loads(text) if text.strip() else None
        except ValueError:
            parsed = None
        if isinstance(parsed, dict):
            errors = parsed.get("errors")
        return cls(
            response.status_code,
            body=text,
            errors=errors,
            request_id=response.headers.get("x-request-id"),
        )

    def __repr__(self):
        return "APIError(status=%r, code=%r, request_id=%r)" % (self.status, self.code, self.request_id)


def _one_line(text):
    # type: (str) -> str
    return " ".join(str(text).split())


def _error_text(errors, body):
    # type: (Any, str) -> str
    if isinstance(errors, str) and errors.strip():
        return _one_line(errors)
    if isinstance(errors, dict):
        detail = errors.get("detail")
        if isinstance(detail, str) and detail.strip():
            return _one_line(detail)
        fields = []
        for field, messages in errors.items():
            if field == "code":
                continue
            if isinstance(messages, (list, tuple)):
                joined = ", ".join(str(m) for m in messages)
            else:
                joined = str(messages)
            fields.append("%s: %s" % (field, joined))
        if fields:
            return _one_line("; ".join(fields))
    if isinstance(errors, list) and errors:
        problems = []
        for problem in errors:
            if isinstance(problem, dict) and ("path" in problem or "message" in problem):
                path = problem.get("path")
                message = problem.get("message", "")
                problems.append("%s: %s" % (path, message) if path not in (None, "") else str(message))
            else:
                problems.append(str(problem))
        return _one_line("; ".join(problems))
    trimmed = _one_line(body)[:_RAW_BODY_LIMIT]
    return trimmed or "(empty body)"


def _seg(value):
    # type: (Any) -> str
    """One path segment, escaped."""
    return quote(str(value), safe="")


def _origin(parts):
    scheme = (parts.scheme or "").lower()
    host = (parts.hostname or "").lower()
    port = parts.port
    if port is None:
        port = {"http": 80, "https": 443}.get(scheme)
    return scheme, host, port


def _origin_text(parts):
    scheme, host, port = _origin(parts)
    return "%s://%s:%s" % (scheme, host, port)


def _scalar(key, value):
    # type: (str, Any) -> str
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, (str, int, float)):
        return str(value)
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()
    raise ValueError("query parameter %s must be a string, number, boolean, list or dict" % key)


def _query_pairs(key, value, top, pairs):
    # type: (str, Any, bool, List[Tuple[str, str]]) -> None
    if value is None:
        return
    if isinstance(value, (list, tuple)):
        for item in value:
            if item is None:
                continue
            if isinstance(item, (list, tuple)):
                raise ValueError("query parameter %s can't hold a list of lists" % key)
            if isinstance(item, dict):
                _query_pairs(key + "[]", item, False, pairs)
            else:
                pairs.append((key if top else key + "[]", _scalar(key, item)))
        return
    if isinstance(value, dict):
        for sub, inner in value.items():
            _query_pairs("%s[%s]" % (key, sub), inner, False, pairs)
        return
    pairs.append((key, _scalar(key, value)))


def _quote(text, safe="", encoding=None, errors=None):
    # As a WHATWG URLSearchParams writes it (what the Node library sends): `*` kept, `~` escaped.
    return quote_plus(text, safe="*", encoding=encoding, errors=errors).replace("~", "%7E")


def _encode_query(query):
    # type: (Optional[Dict[str, Any]]) -> str
    """A query string as the v2 API reads it: a top-level list of scalars repeats its bare key
    (``ref_number=A&ref_number=B``), a dict brackets its keys (``name_range[from]=A``), a list
    inside one brackets too (``filter[list_id][]=a``), booleans are ``true``/``false``."""
    if not query:
        return ""
    pairs = []  # type: List[Tuple[str, str]]
    for key, value in query.items():
        _query_pairs(str(key), value, True, pairs)
    return urlencode(pairs, quote_via=_quote)


def _has_prompt_token(url):
    # type: (Any) -> bool
    if not isinstance(url, str):
        return False
    tokens = parse_qs(urlsplit(url).query).get("prompt_token") or []
    return any(t.strip() for t in tokens)


def _may_have_reached_the_server(error):
    # type: (Exception) -> bool
    """False for a connection that never opened (refused, a connect timeout, a name that
    doesn't resolve); True for a read timeout, or a connection reset or closed after opening."""
    if isinstance(error, requests.ConnectTimeout):
        return False
    if isinstance(error, requests.ReadTimeout):
        return True
    reason = error.args[0] if error.args else None
    reason = getattr(reason, "reason", reason)
    return not isinstance(reason, (NewConnectionError, ConnectTimeoutError))


def _unwrap(parsed):
    if isinstance(parsed, dict) and "data" in parsed:
        return parsed["data"]
    return parsed


def _entity_tag(value):
    # type: (Any) -> str
    text = str(value)
    return text if text.startswith('"') or text.startswith("W/") else '"%s"' % text


def _compact(**values):
    # type: (**Any) -> Dict[str, Any]
    return {k: v for k, v in values.items() if v is not None}


class Client(OperationsMixin):
    """A QuBe Sync v2 API client.

    Every QuickBooks operation is a method on its entity: ``client.customer.create(...)``,
    ``client.invoice.query(...)``, ``client.txn_void.execute(...)`` (``class`` is ``client.class_``).
    An entity's module is imported the first time it's used.

    Args:
        api_key: your app's API key (required). Sent as HTTP Basic auth, never logged or shown.
        base_url: the QuBe Sync host, ``https://qubesync.com`` by default. The API root is
            ``base_url + "/api/v2"``.
        open_timeout: seconds to wait for the connection to open (5).
        read_timeout: seconds to wait for the answer (30).
        max_retries: how many times to retry a retry-safe request (2).
        total_timeout: seconds within which every call returns or raises, retries and their
            waits included (60). Each attempt's timeouts are cut to the time left, and a retry
            whose wait would leave under a second isn't made.
        on_retry: called with a dict before each retry's wait: ``attempt`` (the retry about to
            be made, from 1), ``max_retries``, ``delay`` and ``elapsed`` (seconds), ``method``,
            ``url`` (without its query string), ``status`` (the HTTP status, or None) and
            ``error`` (the network exception, or None). Never the key, headers or body. An
            exception it raises stops the call and reaches the caller.
        sleep: the function that waits between retries (``time.sleep``), for tests.
        clock: a monotonic clock in seconds (``time.monotonic``), for tests.
        session: a ``requests.Session`` to send through (one is made by default).
    """

    def __init__(
        self,
        api_key,  # type: str
        *,
        base_url=DEFAULT_BASE_URL,  # type: str
        open_timeout=5,  # type: float
        read_timeout=30,  # type: float
        max_retries=2,  # type: int
        total_timeout=60,  # type: float
        on_retry=None,  # type: Optional[Callable[[Dict[str, Any]], Any]]
        sleep=None,  # type: Optional[Callable[[float], Any]]
        clock=None,  # type: Optional[Callable[[], float]]
        session=None,  # type: Optional[requests.Session]
    ):
        if not isinstance(api_key, str) or not api_key.strip():
            raise ValueError("api_key is required")
        if not isinstance(base_url, str) or not base_url.strip():
            raise ValueError("base_url is required")
        if not isinstance(max_retries, int) or isinstance(max_retries, bool) or max_retries < 0:
            raise ValueError("max_retries must be an int of 0 or more")
        self.base_url = base_url.strip().rstrip("/")
        parts = urlsplit(self.base_url)
        if parts.scheme not in ("http", "https") or not parts.hostname:
            raise ValueError("base_url must be an http or https URL, got %r" % self.base_url)
        self._origin = _origin(parts)
        self._api_root = self.base_url + API_PREFIX
        self.open_timeout = open_timeout
        self.read_timeout = read_timeout
        self.max_retries = max_retries
        if isinstance(total_timeout, bool) or not isinstance(total_timeout, (int, float)) or total_timeout <= 0:
            raise ValueError("total_timeout must be a number of seconds above 0")
        if on_retry is not None and not callable(on_retry):
            raise ValueError("on_retry must be callable")
        self.total_timeout = total_timeout
        self._on_retry = on_retry
        self._sleep = sleep or time.sleep
        self._clock = clock or time.monotonic
        self._api_key = api_key
        self._session = session or requests.Session()

    def __repr__(self):
        return "<qubesync.Client base_url=%r>" % self.base_url

    __str__ = __repr__

    # -- Connections -------------------------------------------------------------------------

    def create_connection(self, *, webhook_url, name=None, type=None):
        # type: (str, Optional[str], Optional[str]) -> Any
        """POST /connections. Not retried (the endpoint takes no Idempotency-Key).
        ``type="simulated"`` makes a connection to a simulated company file, connected as it's made."""
        return self._data("POST", "/connections", _compact(webhook_url=webhook_url, name=name, type=type))

    def get_connection(self, id):
        # type: (str) -> Any
        return self._data("GET", "/connections/%s" % _seg(id))

    def list_connections(self):
        # type: () -> Any
        return self._data("GET", "/connections")

    def update_connection(self, id, *, webhook_url=None, name=None):
        # type: (str, Optional[str], Optional[str]) -> Any
        """PUT /connections/{id} with only the keys given."""
        return self._data("PUT", "/connections/%s" % _seg(id), _compact(webhook_url=webhook_url, name=name))

    def delete_connection(self, id):
        # type: (str) -> Any
        return self._data("DELETE", "/connections/%s" % _seg(id))

    def regenerate_onboarding(self, id):
        # type: (str) -> Any
        return self._data("POST", "/connections/%s/onboarding-url" % _seg(id))

    def set_password(self, id, *, password=None):
        # type: (str, Optional[str]) -> Any
        """POST /connections/{id}/password: sets ``password``, or makes one when it's None.
        Returns ``{"id": ..., "password": ...}``."""
        body = {"password": password} if password is not None else None
        return self._data("POST", "/connections/%s/password" % _seg(id), body)

    def get_qwc(self, id):
        # type: (str) -> Optional[str]
        """POST /connections/{id}/qwc. Returns the QWC file's XML as a string."""
        body = self.request("POST", "/connections/%s/qwc" % _seg(id))
        return body.get("qwc") if isinstance(body, dict) else None

    # -- Workflow runs -----------------------------------------------------------------------

    def start_run(self, connection_id, workflow, input, *, reference, webhook_url, version=None):
        # type: (str, str, Any, str, str, Optional[int]) -> Any
        """POST /connections/{id}/workflow-runs, with ``reference`` as the Idempotency-Key."""
        body = _compact(workflow=workflow, reference=reference, input=input, webhook_url=webhook_url, version=version)
        return self._data(
            "POST",
            "/connections/%s/workflow-runs" % _seg(connection_id),
            body,
            headers={"Idempotency-Key": str(reference)},
        )

    def get_run(self, run_url_or_connection_id, run_id=None):
        # type: (str, Optional[str]) -> Any
        """``get_run(run.links.run)`` or ``get_run(connection_id, run_id)``."""
        if run_id is None:
            return self._data("GET", run_url_or_connection_id)
        return self._data(
            "GET", "/connections/%s/workflow-runs/%s" % (_seg(run_url_or_connection_id), _seg(run_id))
        )

    def list_runs(self, connection_id, *, reference=None, state=None, outcome=None):
        # type: (str, Optional[str], Optional[str], Optional[str]) -> Any
        return self._data(
            "GET",
            "/connections/%s/workflow-runs" % _seg(connection_id),
            query=_compact(reference=reference, state=state, outcome=outcome),
        )

    def cancel_run(self, cancel_url, *, reason=None):
        # type: (str, Optional[str]) -> Any
        """POST a run's ``links.cancel``. Not retried."""
        return self._data("POST", cancel_url, _compact(reason=reason))

    def redeliver_run(self, connection_id, run_id):
        # type: (str, str) -> Any
        """POST .../workflow-runs/{run_id}/redeliver: QuBe Sync sends the run's latest event again.
        Returns ``{"run_id", "event", "revision", "webhook_url"}``; 409 when there's nothing to
        send yet, 429 when asked again too soon. Not retried."""
        return self._data(
            "POST", "/connections/%s/workflow-runs/%s/redeliver" % (_seg(connection_id), _seg(run_id))
        )

    def run_events(self, connection_id, run_id, *, after=None, limit=None):
        # type: (str, str, Optional[Any], Optional[int]) -> Any
        """Returns the whole body: ``{"data": [...], "next_after": ...}``."""
        return self.request(
            "GET",
            "/connections/%s/workflow-runs/%s/events" % (_seg(connection_id), _seg(run_id)),
            query=_compact(after=after, limit=limit),
        )

    # -- Workflow types ----------------------------------------------------------------------

    def workflow_types(self, *, include_drafts=False, etag=None):
        # type: (bool, Optional[str]) -> Any
        """GET /workflows/types: the input types of the app's workflows, which ``qubesync
        workflows`` writes as a typed module (``qubesync.workflow_types``). Returns the document
        (the response's ``data``): ``digest``, ``operations_digest``, ``include_drafts``,
        ``workflows`` (each published workflow at its published version) and, with
        ``include_drafts=True`` (``?include=drafts``), ``drafts`` (each workflow whose working
        copy differs from it). With ``etag`` (a document's ``digest``, or the ETag it came with)
        it returns ``NOT_MODIFIED`` when the document is still that one."""
        headers = {"If-None-Match": _entity_tag(etag)} if etag else None
        try:
            return self._data(
                "GET",
                "/workflows/types",
                query=_compact(include="drafts" if include_drafts else None),
                headers=headers,
            )
        except APIError as error:
            if error.status != 304:
                raise
            return NOT_MODIFIED

    # -- Questions ---------------------------------------------------------------------------

    def answer(self, decisions_url, *, choice, data=None):
        # type: (str, str, Optional[Dict[str, Any]]) -> Any
        """POST a run's ``links.decisions`` with the chosen choice (and its fields' data).

        Retried like a GET when the URL's query has a ``prompt_token`` (a run's
        ``links.decisions`` always does while it asks): the token ties the answer to that one
        question. A retry after a lost answer may raise a 409 ``APIError`` with code
        ``prompt_changed``: the question was already answered, by the first attempt or by
        someone else. Without a ``prompt_token`` the answer is sent once, since one sent again
        could be taken for the run's next question."""
        retry_safe = _has_prompt_token(decisions_url)
        parsed = self._request("POST", decisions_url, _compact(choice=choice, data=data), retry_safe=retry_safe)
        return _unwrap(parsed)

    def search(self, search_url, *, field, q, row=None):
        # type: (str, str, str, Optional[str]) -> Any
        """GET a question's ``links.search`` for one field. Returns the list of matches.

        For a rows field's record column, ``field`` is ``"<field>.<column>"`` and ``row`` the
        row's key, whose kind of record it searches."""
        return self._data("GET", search_url, query=_compact(field=field, q=q, row=row))

    # -- Queued requests ---------------------------------------------------------------------

    def queue(
        self,
        operation_id,  # type: str
        connection_id,  # type: str
        params=None,  # type: Optional[Dict[str, Any]]
        *,
        webhook_url,  # type: str
        idempotency_key=None,  # type: Optional[str]
        method=None,  # type: Optional[str]
        path=None,  # type: Optional[str]
    ):
        # type: (...) -> Any
        """Queue an operation by its id: ``queue("customer.create", conn_id, {"name": "Acme"}, webhook_url=...)``
        is ``client.customer.create(conn_id, {"name": "Acme"}, webhook_url=...)``.

        A known id takes its method, path and params placement from ``qubesync.operations.OPERATIONS``.
        An operation newer than this version needs ``method=`` (``"post"``, ``"get"``...) and
        ``path=``, the path after the connection (``"customers"``); its params go in the query
        string for a GET or DELETE (nested dicts bracketed), else in the JSON body. Given for a
        known id, ``method`` and ``path`` replace the index's. ``webhook_url`` goes in the query
        string. The Idempotency-Key is ``idempotency_key``, or a UUID made for this call and
        reused on its retries. Returns the queued request.
        """
        known = OPERATIONS.get(operation_id)
        if known is None and (method is None or path is None):
            raise ValueError(
                "unknown operation %r: this version of qubesync doesn't know it, so pass method= and path= "
                '(the path after the connection, e.g. "customers")' % (operation_id,)
            )
        verb = str(method if method is not None else known.method).upper()
        if verb not in ("GET", "POST", "PUT", "DELETE"):
            raise ValueError("method must be get, post, put or delete, got %r" % method)
        rel = str(path if path is not None else known.path).lstrip("/")
        if not rel:
            raise ValueError("path is required")
        if known is not None and method is None:
            params_in = known.params_in
        else:
            params_in = "query" if verb in ("GET", "DELETE") else "body"
        return self._queue(verb, connection_id, rel, params_in, params, webhook_url, idempotency_key)

    def _queue_operation(self, operation_id, connection_id, params, webhook_url, idempotency_key):
        # type: (str, str, Optional[Dict[str, Any]], str, Optional[str]) -> Any
        """What the generated methods (``client.customer.create``...) call."""
        op = OPERATIONS[operation_id]
        return self._queue(op.method, connection_id, op.path, op.params_in, params, webhook_url, idempotency_key)

    def _queue(self, verb, connection_id, rel, params_in, params, webhook_url, idempotency_key):
        if not webhook_url:
            raise ValueError("webhook_url is required")
        params = dict(params or {})
        path = "/connections/%s/%s" % (_seg(connection_id), quote(rel, safe="/"))
        headers = {"Idempotency-Key": idempotency_key or str(uuid.uuid4())}
        if params_in == "query":
            query = {"webhook_url": webhook_url}  # type: Dict[str, Any]
            query.update((k, v) for k, v in params.items() if k != "webhook_url")
            return self._data(verb, path, query=query, headers=headers)
        return self._data(verb, path, params, query={"webhook_url": webhook_url}, headers=headers)

    def queue_qbxml(self, connection_id, request_xml, *, webhook_url, idempotency_key=None):
        # type: (str, str, str, Optional[str]) -> Any
        """POST /connections/{id}/queued-requests with qbXML as written."""
        if not webhook_url:
            raise ValueError("webhook_url is required")
        return self._data(
            "POST",
            "/connections/%s/queued-requests" % _seg(connection_id),
            {"request_xml": request_xml},
            query={"webhook_url": webhook_url},
            headers={"Idempotency-Key": idempotency_key or str(uuid.uuid4())},
        )

    def get_request(self, connection_id_or_link, id=None):
        # type: (str, Optional[str]) -> Any
        """``get_request(connection_id, id)`` or ``get_request(event.self_link)``."""
        if id is None:
            return self._data("GET", connection_id_or_link)
        return self._data("GET", "/connections/%s/queued-requests/%s" % (_seg(connection_id_or_link), _seg(id)))

    def response_xml_for(self, event):
        # type: (Any) -> Optional[str]
        """A request event's ``response_xml``, fetched from ``links.self`` when it was omitted."""
        if not event.response_xml_omitted:
            return event.response_xml
        link = event.self_link
        if not link:
            raise ValueError("response_xml was omitted but the event has no links.self")
        request = self.get_request(link)
        return request.get("response_xml") if isinstance(request, dict) else None

    def request_pages(self, connection_id, id):
        # type: (str, str) -> Any
        return self._data("GET", "/connections/%s/queued-requests/%s/pages" % (_seg(connection_id), _seg(id)))

    def list_requests(
        self,
        connection_id,  # type: str
        *,
        page=None,  # type: Optional[int]
        page_size=None,  # type: Optional[int]
        state=None,  # type: Optional[str]
        webhook_state=None,  # type: Optional[str]
        sort=None,  # type: Optional[str]
        sort_direction=None,  # type: Optional[str]
        search_phrase=None,  # type: Optional[str]
    ):
        # type: (...) -> Any
        """Returns the whole body: ``{"data": [...], "meta": {"page": ..., "total_pages": ...}}``."""
        return self.request(
            "GET",
            "/connections/%s/queued-requests" % _seg(connection_id),
            query=_compact(
                page=page,
                page_size=page_size,
                state=state,
                webhook_state=webhook_state,
                sort=sort,
                sort_direction=sort_direction,
                search_phrase=search_phrase,
            ),
        )

    def iter_requests(
        self,
        connection_id,  # type: str
        *,
        page_size=None,  # type: Optional[int]
        state=None,  # type: Optional[str]
        webhook_state=None,  # type: Optional[str]
        sort=None,  # type: Optional[str]
        sort_direction=None,  # type: Optional[str]
        search_phrase=None,  # type: Optional[str]
    ):
        # type: (...) -> Iterator[Dict[str, Any]]
        """Yields every queued request, walking the pages from 1 to ``meta.total_pages``."""
        page = 1
        while True:
            body = self.list_requests(
                connection_id,
                page=page,
                page_size=page_size,
                state=state,
                webhook_state=webhook_state,
                sort=sort,
                sort_direction=sort_direction,
                search_phrase=search_phrase,
            )
            items = (body or {}).get("data") or []
            for item in items:
                yield item
            total = ((body or {}).get("meta") or {}).get("total_pages")
            if not items or not isinstance(total, int) or page >= total:
                return
            page += 1

    def discard_request(self, connection_id, id):
        # type: (str, str) -> Any
        return self._data("POST", "/connections/%s/queued-requests/%s/discard" % (_seg(connection_id), _seg(id)))

    # -- Anything else -----------------------------------------------------------------------

    def request(self, method, path_or_url, body=None, *, query=None, headers=None):
        # type: (str, str, Any, Optional[Dict[str, Any]], Optional[Dict[str, str]]) -> Any
        """Send any v2 request. ``path_or_url`` is a path under ``/api/v2`` (``"/connections"``)
        or an absolute URL on the client's own origin (a ``links`` URL). Returns the whole parsed
        JSON body, or None for an empty one. GET, PUT, DELETE and anything with an
        Idempotency-Key header are retried; other requests are sent once."""
        return self._request(method, path_or_url, body, query=query, headers=headers)

    # -- Internals ---------------------------------------------------------------------------

    def _data(self, method, path_or_url, body=None, query=None, headers=None):
        return _unwrap(self._request(method, path_or_url, body, query=query, headers=headers))

    def _request(self, method, path_or_url, body=None, query=None, headers=None, retry_safe=False):
        verb = str(method).upper()
        url = self._url(path_or_url, query)
        send_headers = {
            "Accept": "application/json",
            "User-Agent": "qubesync-python/%s" % __version__,
        }
        data = None
        if body is not None:
            send_headers["Content-Type"] = "application/json"
            data = json.dumps(body).encode("utf-8")
        for key, value in (headers or {}).items():
            send_headers[key] = value

        retry_safe = (
            retry_safe
            or verb in _RETRY_SAFE_METHODS
            or any(k.lower() == "idempotency-key" for k in send_headers)
        )
        attempts = 1 + (self.max_retries if retry_safe else 0)
        started = self._clock()
        # Whether an earlier attempt of this call may have been carried out, its answer lost.
        maybe_applied = False

        attempt = 0
        while True:
            attempt += 1
            left = self.total_timeout - (self._clock() - started)
            timeout = (min(self.open_timeout, left), min(self.read_timeout, left))
            response = None
            error = None
            try:
                response = self._session.request(
                    verb,
                    url,
                    data=data,
                    headers=send_headers,
                    auth=(self._api_key, ""),
                    timeout=timeout,
                )
            except (requests.ConnectionError, requests.Timeout) as e:
                error = e

            if response is not None and response.status_code not in _RETRY_STATUSES:
                if verb == "DELETE" and response.status_code == 404 and maybe_applied:
                    # An earlier attempt deleted it and its answer was lost: done, as a 204 is.
                    response.close()
                    return None
                return self._parse(response)

            if error is not None:
                maybe_applied = maybe_applied or _may_have_reached_the_server(error)
            elif response.status_code in _MAYBE_APPLIED_STATUSES:
                maybe_applied = True

            delay = None
            if attempt < attempts:
                delay = self._retry_after(response) if response is not None else None
                if delay is None:
                    delay = self._backoff(attempt)
                elapsed = self._clock() - started
                if self.total_timeout - (elapsed + delay) < 1:
                    delay = None  # the wait doesn't fit in what's left: no retry
            if delay is None:
                if error is not None:
                    raise error
                return self._parse(response)

            if response is not None:
                response.close()
            if self._on_retry is not None:
                self._on_retry(
                    {
                        "attempt": attempt,
                        "max_retries": self.max_retries,
                        "delay": float(delay),
                        "elapsed": float(elapsed),
                        "method": verb,
                        "url": url.split("?", 1)[0],
                        "status": response.status_code if response is not None else None,
                        "error": error,
                    }
                )
            self._sleep(delay)

    def _url(self, path_or_url, query):
        # type: (str, Optional[Dict[str, Any]]) -> str
        if not isinstance(path_or_url, str) or not path_or_url:
            raise ValueError("a path (starting with /) or a link URL is required")
        if path_or_url.startswith("/") and not path_or_url.startswith("//"):
            url = self._api_root + path_or_url
        else:
            parts = urlsplit(path_or_url)
            if not parts.scheme or not parts.hostname:
                raise ValueError("expected a path starting with / or an absolute URL, got %r" % path_or_url)
            if _origin(parts) != self._origin:
                raise ValueError(
                    "refusing to send the API key to %s: this client talks to %s"
                    % (_origin_text(parts), _origin_text(urlsplit(self.base_url)))
                )
            url = path_or_url.split("#", 1)[0]
        extra = _encode_query(query)
        if extra:
            url += ("&" if "?" in url else "?") + extra
        return url

    @staticmethod
    def _backoff(attempt):
        # type: (int) -> float
        base = _BACKOFF[min(attempt - 1, len(_BACKOFF) - 1)]
        return base * (1 + random.uniform(0, 0.25))

    @staticmethod
    def _retry_after(response):
        # type: (requests.Response) -> Optional[float]
        if response.status_code not in _RETRY_AFTER_STATUSES:
            return None
        value = response.headers.get("Retry-After")
        if value is None:
            return None
        try:
            seconds = float(value.strip())
        except ValueError:
            return None
        if seconds < 0:
            return None
        return min(seconds, _RETRY_AFTER_CAP)

    @staticmethod
    def _parse(response):
        # type: (requests.Response) -> Any
        if not 200 <= response.status_code < 300:
            raise APIError.from_response(response)
        if response.status_code == 204 or not response.content or not response.content.strip():
            return None
        return response.json()
