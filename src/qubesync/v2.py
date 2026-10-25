"""A client for the QuBe Sync v2 API (https://docs.qubesync.com).

    from qubesync import Client

    client = Client(api_key=os.environ["QUBE_API_KEY"])
    connection = client.create_connection(webhook_url="https://example.com/webhooks/qube")

The client never reads the environment: pass the API key in. Every method returns the
response's ``data`` as plain dicts and lists, except where its docstring says otherwise.
A refused request raises :class:`APIError`; a connection that still fails after the retries
raises the ``requests`` exception unchanged.
"""

import json
import random
import time
import uuid
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple
from urllib.parse import quote, urlencode, urlsplit

import requests

from ._version import __version__
from .errors import QubeSyncError

__all__ = ["Client", "APIError"]

DEFAULT_BASE_URL = "https://qubesync.com"
API_PREFIX = "/api/v2"

_RETRY_STATUSES = (429, 502, 503, 504)
_RETRY_AFTER_STATUSES = (429, 503)
_RETRY_AFTER_CAP = 30.0
_BACKOFF = (0.5, 1.0)
_RETRY_SAFE_METHODS = ("GET", "PUT", "DELETE")
_RAW_BODY_LIMIT = 500


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


def _query_value(key, value):
    # type: (str, Any) -> Any
    if isinstance(value, dict):
        raise ValueError("query parameter %r is a dict; only scalars and lists go in a query string" % key)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple)):
        return [_query_value(key, v) for v in value]
    return value


def _encode_query(query):
    # type: (Optional[Dict[str, Any]]) -> str
    if not query:
        return ""
    pairs = []
    for key, value in query.items():
        if value is None:
            continue
        value = _query_value(key, value)
        if isinstance(value, list):
            for v in value:
                pairs.append((key, v))
        else:
            pairs.append((key, value))
    return urlencode(pairs)


def _compact(**values):
    # type: (**Any) -> Dict[str, Any]
    return {k: v for k, v in values.items() if v is not None}


class Client:
    """A QuBe Sync v2 API client.

    Args:
        api_key: your app's API key (required). Sent as HTTP Basic auth, never logged or shown.
        base_url: the QuBe Sync host, ``https://qubesync.com`` by default. The API root is
            ``base_url + "/api/v2"``.
        open_timeout: seconds to wait for the connection to open (5).
        read_timeout: seconds to wait for the answer (30).
        max_retries: how many times to retry a retry-safe request (2).
        sleep: the function that waits between retries (``time.sleep``), for tests.
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
        sleep=None,  # type: Optional[Callable[[float], Any]]
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
        self._sleep = sleep or time.sleep
        self._api_key = api_key
        self._session = session or requests.Session()

    def __repr__(self):
        return "<qubesync.Client base_url=%r>" % self.base_url

    __str__ = __repr__

    # -- Connections -------------------------------------------------------------------------

    def create_connection(self, *, webhook_url, name=None):
        # type: (str, Optional[str]) -> Any
        """POST /connections. Not retried (the endpoint takes no Idempotency-Key)."""
        return self._data("POST", "/connections", _compact(webhook_url=webhook_url, name=name))

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

    def run_events(self, connection_id, run_id, *, after=None, limit=None):
        # type: (str, str, Optional[Any], Optional[int]) -> Any
        """Returns the whole body: ``{"data": [...], "next_after": ...}``."""
        return self.request(
            "GET",
            "/connections/%s/workflow-runs/%s/events" % (_seg(connection_id), _seg(run_id)),
            query=_compact(after=after, limit=limit),
        )

    # -- Questions ---------------------------------------------------------------------------

    def answer(self, decisions_url, *, choice, data=None):
        # type: (str, str, Optional[Dict[str, Any]]) -> Any
        """POST a run's ``links.decisions`` with the chosen choice (and its fields' data). Not retried."""
        return self._data("POST", decisions_url, _compact(choice=choice, data=data))

    def search(self, search_url, *, field, q):
        # type: (str, str, str) -> Any
        """GET a question's ``links.search`` for one field. Returns the list of matches."""
        return self._data("GET", search_url, query={"field": field, "q": q})

    # -- Queued requests ---------------------------------------------------------------------

    def queue(self, connection_id, operation, params=None, *, webhook_url, method="post", idempotency_key=None):
        # type: (str, str, Optional[Dict[str, Any]], Optional[str], str, Optional[str]) -> Any
        """Queue an operation: ``queue(conn_id, "customers", {"name": "Acme"}, webhook_url=...)``.

        ``operation`` is the path after the connection (``"customers"``, ``"txn-deleteds"``...).
        ``webhook_url`` goes in the query string. For ``method="get"`` or ``"delete"`` the params
        go in the query string (scalars and lists only); for ``"post"`` or ``"put"`` they're the
        JSON body. The Idempotency-Key is ``idempotency_key``, or a UUID made for this call and
        reused on its retries.
        """
        if not webhook_url:
            raise ValueError("webhook_url is required")
        verb = str(method).upper()
        if verb not in ("GET", "POST", "PUT", "DELETE"):
            raise ValueError("method must be get, post, put or delete, got %r" % method)
        op = str(operation).lstrip("/")
        if not op:
            raise ValueError("operation is required")
        params = dict(params or {})
        path = "/connections/%s/%s" % (_seg(connection_id), quote(op, safe="/"))
        headers = {"Idempotency-Key": idempotency_key or str(uuid.uuid4())}
        if verb in ("GET", "DELETE"):
            query = dict(params)
            query["webhook_url"] = webhook_url
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

    def get_request(self, connection_id, id):
        # type: (str, str) -> Any
        return self._data("GET", "/connections/%s/queued-requests/%s" % (_seg(connection_id), _seg(id)))

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

        retry_safe = verb in _RETRY_SAFE_METHODS or any(k.lower() == "idempotency-key" for k in send_headers)
        attempts = 1 + (self.max_retries if retry_safe else 0)

        attempt = 0
        while True:
            attempt += 1
            last = attempt >= attempts
            try:
                response = self._session.request(
                    verb,
                    url,
                    data=data,
                    headers=send_headers,
                    auth=(self._api_key, ""),
                    timeout=(self.open_timeout, self.read_timeout),
                )
            except (requests.ConnectionError, requests.Timeout):
                if last:
                    raise
                self._sleep(self._backoff(attempt))
                continue

            if response.status_code in _RETRY_STATUSES and not last:
                wait = self._retry_after(response)
                response.close()
                self._sleep(wait if wait is not None else self._backoff(attempt))
                continue
            return self._parse(response)

    # -- Internals ---------------------------------------------------------------------------

    def _data(self, method, path_or_url, body=None, query=None, headers=None):
        parsed = self.request(method, path_or_url, body, query=query, headers=headers)
        if isinstance(parsed, dict) and "data" in parsed:
            return parsed["data"]
        return parsed

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
