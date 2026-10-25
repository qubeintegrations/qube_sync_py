"""Tests for qubesync.Client (the v2 API client) against a real HTTP server in a thread."""

import base64
import json
import socket
import struct
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

import pytest
import requests

import qubesync
from qubesync import APIError, Client, QubeSyncError

API_KEY = "sk_test_do_not_leak_0123456789"


class QuietServer(ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):
        pass  # a client that timed out and hung up mid-answer


class FakeQube:
    """Records every request and answers from a script (FIFO), else 200 {"data": {}}."""

    def __init__(self):
        self.requests = []
        self.script = []
        self.lock = threading.Lock()
        fake = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *args):
                pass

            def _handle(self):
                length = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(length) if length else b""
                parts = urlsplit(self.path)
                with fake.lock:
                    fake.requests.append(
                        {
                            "method": self.command,
                            "path": parts.path,
                            "raw_query": parts.query,
                            "query": parse_qs(parts.query, keep_blank_values=True),
                            "headers": {k.lower(): v for k, v in self.headers.items()},
                            "body": body,
                        }
                    )
                    step = fake.script.pop(0) if fake.script else None
                if step is None:
                    step = {"status": 200, "json": {"data": {}}}
                if step.get("reset"):
                    # Close the socket with RST, without answering.
                    self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))
                    self.close_connection = True
                    return
                if step.get("sleep"):
                    time.sleep(step["sleep"])
                status = step.get("status", 200)
                headers = dict(step.get("headers") or {})
                if "json" in step:
                    payload = json.dumps(step["json"]).encode()
                    headers.setdefault("Content-Type", "application/json")
                else:
                    payload = step.get("text", "").encode()
                self.send_response(status)
                for k, v in headers.items():
                    self.send_header(k, v)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                if payload:
                    self.wfile.write(payload)

            do_GET = do_POST = do_PUT = do_DELETE = do_PATCH = _handle

        self.server = QuietServer(("127.0.0.1", 0), Handler)
        self.port = self.server.server_address[1]
        self.base_url = "http://127.0.0.1:%d" % self.port
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def answer(self, *steps):
        self.script.extend(steps)

    def reset(self):
        self.requests = []
        self.script = []

    @property
    def last(self):
        return self.requests[-1]


@pytest.fixture(scope="module")
def server():
    fake = FakeQube()
    yield fake
    fake.server.shutdown()
    fake.server.server_close()


@pytest.fixture
def fake(server):
    server.reset()
    return server


@pytest.fixture
def sleeps():
    return []


@pytest.fixture
def client(fake, sleeps):
    return Client(API_KEY, base_url=fake.base_url + "/", sleep=sleeps.append)


def body_of(req):
    return json.loads(req["body"].decode()) if req["body"] else None


# -- Construction --------------------------------------------------------------------------


def test_exports():
    assert qubesync.Client is Client
    assert issubclass(APIError, QubeSyncError)
    assert "Client" in qubesync.__all__ and "APIError" in qubesync.__all__
    assert qubesync.__version__ == "0.3.0"


@pytest.mark.parametrize("key", [None, "", "   "])
def test_api_key_is_required(key):
    with pytest.raises(ValueError):
        Client(key)


def test_defaults_and_trailing_slash():
    c = Client(API_KEY)
    assert c.base_url == "https://qubesync.com"
    assert (c.open_timeout, c.read_timeout, c.max_retries) == (5, 30, 2)
    assert Client(API_KEY, base_url="https://qubesync.com///").base_url == "https://qubesync.com"


def test_repr_hides_the_key(client, fake):
    assert API_KEY not in repr(client)
    assert API_KEY not in str(client)
    assert repr(client) == "<qubesync.Client base_url=%r>" % fake.base_url


# -- Headers and unwrapping ----------------------------------------------------------------


def test_basic_auth_and_headers(client, fake):
    fake.answer({"json": {"data": [{"id": "c1"}]}})
    assert client.list_connections() == [{"id": "c1"}]
    req = fake.last
    assert req["method"] == "GET"
    assert req["path"] == "/api/v2/connections"
    expected = "Basic " + base64.b64encode((API_KEY + ":").encode()).decode()
    assert req["headers"]["authorization"] == expected
    assert req["headers"]["accept"] == "application/json"
    assert req["headers"]["user-agent"] == "qubesync-python/0.3.0"
    assert "content-type" not in req["headers"]
    assert "idempotency-key" not in req["headers"]


def test_post_sends_json(client, fake):
    fake.answer({"status": 201, "json": {"data": {"id": "c1", "links": {"onboarding": "x"}}}})
    data = client.create_connection(webhook_url="https://app.test/hook", name="Acme")
    assert data == {"id": "c1", "links": {"onboarding": "x"}}
    req = fake.last
    assert (req["method"], req["path"]) == ("POST", "/api/v2/connections")
    assert req["headers"]["content-type"] == "application/json"
    assert body_of(req) == {"webhook_url": "https://app.test/hook", "name": "Acme"}


def test_create_connection_omits_nil_name(client, fake):
    client.create_connection(webhook_url="https://app.test/hook")
    assert body_of(fake.last) == {"webhook_url": "https://app.test/hook"}


# -- Connections ---------------------------------------------------------------------------


def test_connection_methods(client, fake):
    client.get_connection("c 1")
    assert (fake.last["method"], fake.last["path"]) == ("GET", "/api/v2/connections/c%201")

    client.update_connection("c1", name="New")
    assert (fake.last["method"], fake.last["path"]) == ("PUT", "/api/v2/connections/c1")
    assert body_of(fake.last) == {"name": "New"}

    client.update_connection("c1", webhook_url="https://app.test/h2", name="N")
    assert body_of(fake.last) == {"webhook_url": "https://app.test/h2", "name": "N"}

    client.regenerate_onboarding("c1")
    assert (fake.last["method"], fake.last["path"]) == ("POST", "/api/v2/connections/c1/onboarding-url")


def test_delete_connection_204(client, fake):
    fake.answer({"status": 204})
    assert client.delete_connection("c1") is None
    assert (fake.last["method"], fake.last["path"]) == ("DELETE", "/api/v2/connections/c1")


def test_set_password(client, fake):
    fake.answer({"json": {"data": {"id": "c1", "password": "made"}}})
    assert client.set_password("c1") == {"id": "c1", "password": "made"}
    assert fake.last["path"] == "/api/v2/connections/c1/password"
    assert fake.last["body"] == b""
    assert "content-type" not in fake.last["headers"]

    client.set_password("c1", password="mine")
    assert body_of(fake.last) == {"password": "mine"}


def test_get_qwc_returns_the_xml(client, fake):
    fake.answer({"json": {"qwc": "<?xml version=\"1.0\"?><QBWCXML/>"}})
    assert client.get_qwc("c1") == "<?xml version=\"1.0\"?><QBWCXML/>"
    assert (fake.last["method"], fake.last["path"]) == ("POST", "/api/v2/connections/c1/qwc")


# -- Runs ----------------------------------------------------------------------------------


def test_start_run(client, fake):
    fake.answer({"status": 201, "json": {"data": {"id": "r1"}}})
    data = client.start_run("c1", "pull_customers", {"since": "2026-01-01"}, reference="ref-1", webhook_url="https://app.test/h")
    assert data == {"id": "r1"}
    req = fake.last
    assert (req["method"], req["path"]) == ("POST", "/api/v2/connections/c1/workflow-runs")
    assert req["headers"]["idempotency-key"] == "ref-1"
    assert body_of(req) == {
        "workflow": "pull_customers",
        "reference": "ref-1",
        "input": {"since": "2026-01-01"},
        "webhook_url": "https://app.test/h",
    }

    client.start_run("c1", "w", {}, reference="ref-2", webhook_url="https://app.test/h", version=3)
    assert body_of(fake.last)["version"] == 3


def test_start_run_is_retried_with_its_reference(client, fake, sleeps):
    fake.answer({"status": 503}, {"status": 201, "json": {"data": {"id": "r1"}}})
    assert client.start_run("c1", "w", {}, reference="ref-9", webhook_url="https://app.test/h") == {"id": "r1"}
    assert [r["headers"]["idempotency-key"] for r in fake.requests] == ["ref-9", "ref-9"]
    assert len(sleeps) == 1


def test_get_run_by_link_or_ids(client, fake):
    client.get_run(fake.base_url + "/api/v2/connections/c1/workflow-runs/r1?x=1")
    assert fake.last["path"] == "/api/v2/connections/c1/workflow-runs/r1"
    assert fake.last["raw_query"] == "x=1"

    client.get_run("c1", "r2")
    assert fake.last["path"] == "/api/v2/connections/c1/workflow-runs/r2"


def test_list_runs_drops_nil_filters(client, fake):
    fake.answer({"json": {"data": [{"id": "r1"}]}})
    assert client.list_runs("c1", reference="ref-1", outcome="succeeded") == [{"id": "r1"}]
    assert fake.last["path"] == "/api/v2/connections/c1/workflow-runs"
    assert fake.last["query"] == {"reference": ["ref-1"], "outcome": ["succeeded"]}


def test_cancel_run(client, fake):
    url = fake.base_url + "/api/v2/connections/c1/workflow-runs/r1/cancel"
    client.cancel_run(url)
    assert (fake.last["method"], fake.last["path"]) == ("POST", "/api/v2/connections/c1/workflow-runs/r1/cancel")
    assert body_of(fake.last) == {}
    client.cancel_run(url, reason="customer asked")
    assert body_of(fake.last) == {"reason": "customer asked"}


def test_run_events_returns_the_whole_body(client, fake):
    page = {"data": [{"seq": 1}], "next_after": 1}
    fake.answer({"json": page})
    assert client.run_events("c1", "r1", after=0, limit=50) == page
    assert fake.last["path"] == "/api/v2/connections/c1/workflow-runs/r1/events"
    assert fake.last["query"] == {"after": ["0"], "limit": ["50"]}


# -- Questions -----------------------------------------------------------------------------


def test_answer_posts_to_the_link_with_its_query(client, fake):
    url = fake.base_url + "/api/v2/connections/c1/workflow-runs/r1/decisions?prompt_token=tok"
    fake.answer({"json": {"data": {"id": "r1", "state": "running"}}})
    assert client.answer(url, choice="create") == {"id": "r1", "state": "running"}
    assert fake.last["method"] == "POST"
    assert fake.last["path"] == "/api/v2/connections/c1/workflow-runs/r1/decisions"
    assert fake.last["raw_query"] == "prompt_token=tok"
    assert body_of(fake.last) == {"choice": "create"}

    client.answer(url, choice="use", data={"customer": "80000001-1"})
    assert body_of(fake.last) == {"choice": "use", "data": {"customer": "80000001-1"}}


def test_search_appends_after_the_links_query(client, fake):
    url = fake.base_url + "/api/v2/connections/c1/workflow-runs/r1/search?prompt_token=tok"
    fake.answer({"json": {"data": [{"value": "1", "label": "Acme"}]}})
    assert client.search(url, field="customer", q="Ac me") == [{"value": "1", "label": "Acme"}]
    assert fake.last["method"] == "GET"
    assert fake.last["raw_query"].startswith("prompt_token=tok&")
    assert fake.last["query"] == {"prompt_token": ["tok"], "field": ["customer"], "q": ["Ac me"]}


@pytest.mark.parametrize(
    "url",
    [
        "https://evil.test/api/v2/connections/c1/workflow-runs/r1/cancel",
        "http://127.0.0.1:1/api/v2/connections/c1/workflow-runs/r1/cancel",
        "https://127.0.0.1:{port}/api/v2/connections/c1/workflow-runs/r1/cancel",
        "http://localhost:{port}/api/v2/connections/c1/workflow-runs/r1/cancel",
    ],
)
def test_links_on_another_origin_are_refused(client, fake, url):
    url = url.format(port=fake.port)
    with pytest.raises(ValueError) as info:
        client.cancel_run(url)
    message = str(info.value)
    assert API_KEY not in message
    assert "127.0.0.1:%d" % fake.port in message
    assert fake.requests == []


def test_relative_paths_without_a_slash_are_refused(client, fake):
    with pytest.raises(ValueError):
        client.request("GET", "connections")
    with pytest.raises(ValueError):
        client.request("GET", "//evil.test/x")
    assert fake.requests == []


# -- Queued requests -----------------------------------------------------------------------


def test_queue_post(client, fake):
    fake.answer({"status": 201, "json": {"data": {"id": "q1", "state": "waiting"}}})
    data = client.queue("c1", "/customers", {"name": "Acme"}, webhook_url="https://app.test/h?a=1")
    assert data == {"id": "q1", "state": "waiting"}
    req = fake.last
    assert (req["method"], req["path"]) == ("POST", "/api/v2/connections/c1/customers")
    assert req["query"] == {"webhook_url": ["https://app.test/h?a=1"]}
    assert body_of(req) == {"name": "Acme"}
    key = req["headers"]["idempotency-key"]
    assert uuid.UUID(key).version == 4


def test_queue_makes_a_new_key_per_call(client, fake):
    client.queue("c1", "customers", {}, webhook_url="https://app.test/h")
    client.queue("c1", "customers", {}, webhook_url="https://app.test/h")
    keys = [r["headers"]["idempotency-key"] for r in fake.requests]
    assert keys[0] != keys[1]


def test_queue_uses_the_given_key(client, fake):
    client.queue("c1", "invoices", {"ref_number": "1"}, webhook_url="https://app.test/h", method="put", idempotency_key="k-1")
    assert fake.last["method"] == "PUT"
    assert fake.last["headers"]["idempotency-key"] == "k-1"
    assert body_of(fake.last) == {"ref_number": "1"}


def test_queue_get_puts_params_in_the_query(client, fake):
    client.queue(
        "c1",
        "txn-deleteds",
        {"txn_del_type": ["Invoice", "Bill"], "max_returned": 10, "active": True},
        webhook_url="https://app.test/h",
        method="get",
    )
    req = fake.last
    assert (req["method"], req["path"]) == ("GET", "/api/v2/connections/c1/txn-deleteds")
    assert req["body"] == b""
    assert req["query"] == {
        "txn_del_type": ["Invoice", "Bill"],
        "max_returned": ["10"],
        "active": ["true"],
        "webhook_url": ["https://app.test/h"],
    }
    assert "idempotency-key" in req["headers"]


def test_queue_refuses_a_dict_in_the_query(client, fake):
    with pytest.raises(ValueError):
        client.queue("c1", "customers", {"filter": {"name": "x"}}, webhook_url="https://app.test/h", method="get")
    assert fake.requests == []


def test_queue_retries_with_the_same_generated_key(client, fake, sleeps):
    fake.answer({"status": 503}, {"reset": True}, {"status": 201, "json": {"data": {"id": "q1"}}})
    assert client.queue("c1", "customers", {"name": "A"}, webhook_url="https://app.test/h") == {"id": "q1"}
    keys = [r["headers"]["idempotency-key"] for r in fake.requests]
    assert len(keys) == 3 and len(set(keys)) == 1
    assert uuid.UUID(keys[0]).version == 4
    assert len(sleeps) == 2


def test_queue_qbxml(client, fake):
    xml = "<?xml version=\"1.0\"?><QBXML/>"
    client.queue_qbxml("c1", xml, webhook_url="https://app.test/h", idempotency_key="k-2")
    req = fake.last
    assert (req["method"], req["path"]) == ("POST", "/api/v2/connections/c1/queued-requests")
    assert req["query"] == {"webhook_url": ["https://app.test/h"]}
    assert body_of(req) == {"request_xml": xml}
    assert req["headers"]["idempotency-key"] == "k-2"

    client.queue_qbxml("c1", xml, webhook_url="https://app.test/h")
    assert uuid.UUID(fake.last["headers"]["idempotency-key"]).version == 4


def test_request_reads(client, fake):
    fake.answer({"json": {"data": {"id": "q1"}}}, {"json": {"data": [{"page": 1}]}})
    assert client.get_request("c1", "q1") == {"id": "q1"}
    assert fake.last["path"] == "/api/v2/connections/c1/queued-requests/q1"
    assert client.request_pages("c1", "q1") == [{"page": 1}]
    assert fake.last["path"] == "/api/v2/connections/c1/queued-requests/q1/pages"

    client.discard_request("c1", "q1")
    assert (fake.last["method"], fake.last["path"]) == ("POST", "/api/v2/connections/c1/queued-requests/q1/discard")


def test_list_requests_returns_the_whole_body(client, fake):
    body = {"data": [{"id": "q1"}], "meta": {"page": 2, "total_pages": 3}}
    fake.answer({"json": body})
    assert client.list_requests("c1", page=2, page_size=1, state="error", sort="inserted_at") == body
    assert fake.last["query"] == {"page": ["2"], "page_size": ["1"], "state": ["error"], "sort": ["inserted_at"]}


def test_iter_requests_walks_every_page(client, fake):
    fake.answer(
        {"json": {"data": [{"id": "a"}, {"id": "b"}], "meta": {"page": 1, "total_pages": 3}}},
        {"json": {"data": [{"id": "c"}], "meta": {"page": 2, "total_pages": 3}}},
        {"json": {"data": [{"id": "d"}], "meta": {"page": 3, "total_pages": 3}}},
    )
    gen = client.iter_requests("c1", state="error")
    assert fake.requests == []  # a generator: nothing is sent until it's read
    assert [r["id"] for r in gen] == ["a", "b", "c", "d"]
    assert [r["query"]["page"] for r in fake.requests] == [["1"], ["2"], ["3"]]
    assert all(r["query"]["state"] == ["error"] for r in fake.requests)


def test_iter_requests_stops_on_an_empty_page(client, fake):
    fake.answer(
        {"json": {"data": [{"id": "a"}], "meta": {"page": 1, "total_pages": 5}}},
        {"json": {"data": [], "meta": {"page": 2, "total_pages": 5}}},
    )
    assert [r["id"] for r in client.iter_requests("c1")] == ["a"]
    assert len(fake.requests) == 2


# -- The escape hatch ----------------------------------------------------------------------


def test_request_returns_the_whole_body(client, fake):
    fake.answer({"json": {"data": [], "meta": {"x": 1}}}, {"status": 200, "text": ""})
    assert client.request("GET", "/workflows", query={"a": "b"}, headers={"X-Extra": "1"}) == {"data": [], "meta": {"x": 1}}
    assert fake.last["path"] == "/api/v2/workflows"
    assert fake.last["query"] == {"a": ["b"]}
    assert fake.last["headers"]["x-extra"] == "1"
    assert client.request("POST", "/workflows/validate", {"chart": {}}) is None


def test_a_2xx_that_isnt_json_raises(client, fake):
    fake.answer({"status": 200, "text": "<html>"})
    with pytest.raises(ValueError):
        client.get_connection("c1")


# -- Retries -------------------------------------------------------------------------------


@pytest.mark.parametrize("status", [429, 502, 503, 504])
def test_get_is_retried_on_transient_statuses(client, fake, sleeps, status):
    fake.answer({"status": status}, {"status": status}, {"json": {"data": {"id": "c1"}}})
    assert client.get_connection("c1") == {"id": "c1"}
    assert len(fake.requests) == 3
    assert len(sleeps) == 2
    assert 0.5 <= sleeps[0] <= 0.625
    assert 1.0 <= sleeps[1] <= 1.25


def test_retries_run_out(client, fake, sleeps):
    fake.answer({"status": 503}, {"status": 503}, {"status": 503, "json": {"errors": "busy"}})
    with pytest.raises(APIError) as info:
        client.get_connection("c1")
    assert info.value.status == 503
    assert len(fake.requests) == 3
    assert len(sleeps) == 2


@pytest.mark.parametrize("status", [429, 503])
def test_retry_after_is_honoured_and_capped(client, fake, sleeps, status):
    fake.answer(
        {"status": status, "headers": {"Retry-After": "3"}},
        {"status": status, "headers": {"Retry-After": "120"}},
        {"json": {"data": {}}},
    )
    client.get_connection("c1")
    assert sleeps == [3.0, 30.0]


def test_retry_after_is_ignored_on_a_502(client, fake, sleeps):
    fake.answer({"status": 502, "headers": {"Retry-After": "20"}}, {"json": {"data": {}}})
    client.get_connection("c1")
    assert 0.5 <= sleeps[0] <= 0.625


def test_put_and_delete_are_retried(client, fake, sleeps):
    fake.answer({"status": 502}, {"json": {"data": {}}}, {"status": 504}, {"status": 204})
    client.update_connection("c1", name="x")
    assert client.delete_connection("c1") is None
    assert [r["method"] for r in fake.requests] == ["PUT", "PUT", "DELETE", "DELETE"]


@pytest.mark.parametrize(
    "call",
    [
        lambda c, base: c.create_connection(webhook_url="https://app.test/h"),
        lambda c, base: c.answer(base + "/api/v2/connections/c1/workflow-runs/r1/decisions", choice="x"),
        lambda c, base: c.cancel_run(base + "/api/v2/connections/c1/workflow-runs/r1/cancel"),
        lambda c, base: c.set_password("c1"),
        lambda c, base: c.get_qwc("c1"),
        lambda c, base: c.regenerate_onboarding("c1"),
        lambda c, base: c.discard_request("c1", "q1"),
    ],
)
def test_post_without_a_key_is_sent_once(client, fake, sleeps, call):
    fake.answer({"status": 503}, {"json": {"data": {}}})
    with pytest.raises(APIError):
        call(client, fake.base_url)
    assert len(fake.requests) == 1
    assert sleeps == []


def test_post_without_a_key_is_not_retried_on_a_reset(client, fake, sleeps):
    fake.answer({"reset": True})
    with pytest.raises(requests.ConnectionError):
        client.create_connection(webhook_url="https://app.test/h")
    assert len(fake.requests) == 1
    assert sleeps == []


@pytest.mark.parametrize("status", [400, 401, 404, 409, 422])
def test_client_errors_are_not_retried(client, fake, sleeps, status):
    fake.answer({"status": status, "json": {"errors": "no"}})
    with pytest.raises(APIError) as info:
        client.get_connection("c1")
    assert info.value.status == status
    assert len(fake.requests) == 1
    assert sleeps == []


def test_a_reset_connection_is_retried(client, fake, sleeps):
    fake.answer({"reset": True}, {"json": {"data": {"id": "c1"}}})
    assert client.get_connection("c1") == {"id": "c1"}
    assert len(fake.requests) == 2
    assert len(sleeps) == 1


def test_a_reset_on_every_try_raises_the_requests_error(client, fake, sleeps):
    fake.answer({"reset": True}, {"reset": True}, {"reset": True})
    with pytest.raises(requests.ConnectionError):
        client.get_connection("c1")
    assert len(fake.requests) == 3
    assert len(sleeps) == 2


def test_a_refused_connection_is_retried_then_raised(sleeps):
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    c = Client(API_KEY, base_url="http://127.0.0.1:%d" % port, sleep=sleeps.append, open_timeout=1)
    with pytest.raises(requests.ConnectionError) as info:
        c.get_connection("c1")
    assert len(sleeps) == 2
    assert API_KEY not in str(info.value)


def test_max_retries_zero(fake, sleeps):
    c = Client(API_KEY, base_url=fake.base_url, max_retries=0, sleep=sleeps.append)
    fake.answer({"status": 503})
    with pytest.raises(APIError):
        c.get_connection("c1")
    assert len(fake.requests) == 1


# -- Timeouts ------------------------------------------------------------------------------


def test_read_timeout(fake, sleeps):
    c = Client(API_KEY, base_url=fake.base_url, read_timeout=0.2, max_retries=1, sleep=sleeps.append)
    fake.answer({"sleep": 1, "json": {"data": {}}}, {"sleep": 1, "json": {"data": {}}})
    started = time.monotonic()
    with pytest.raises(requests.ReadTimeout):
        c.get_connection("c1")
    assert time.monotonic() - started < 1.5
    assert len(sleeps) == 1


def test_timeouts_are_passed_to_requests():
    seen = {}

    class Session:
        def request(self, method, url, **kwargs):
            seen.update(kwargs)
            response = requests.Response()
            response.status_code = 204
            response._content = b""
            return response

    c = Client(API_KEY, open_timeout=2, read_timeout=7, session=Session())
    assert c.delete_connection("c1") is None
    assert seen["timeout"] == (2, 7)
    assert seen["auth"] == (API_KEY, "")


# -- Errors --------------------------------------------------------------------------------


def raise_for(fake, client, step):
    fake.answer(step)
    with pytest.raises(APIError) as info:
        client.get_connection("c1")
    return info.value


def test_error_a_sentence(fake, client):
    e = raise_for(fake, client, {"status": 422, "json": {"errors": "unknown parameter: \"emial\""}, "headers": {"x-request-id": "req-1"}})
    assert e.status == 422
    assert e.errors == "unknown parameter: \"emial\""
    assert e.code is None
    assert e.message == "QuBe Sync answered 422: unknown parameter: \"emial\""
    assert str(e) == e.message
    assert e.request_id == "req-1"
    assert json.loads(e.body) == {"errors": "unknown parameter: \"emial\""}


def test_error_detail_and_code(fake, client):
    e = raise_for(fake, client, {"status": 409, "json": {"errors": {"detail": "The question changed", "code": "prompt_changed"}}})
    assert e.code == "prompt_changed"
    assert e.errors == {"detail": "The question changed", "code": "prompt_changed"}
    assert e.message == "QuBe Sync answered 409: The question changed"
    assert e.request_id is None


def test_error_a_non_string_code_is_none(fake, client):
    e = raise_for(fake, client, {"status": 404, "json": {"errors": {"detail": "Not Found", "code": 7}}})
    assert e.code is None


def test_error_fields(fake, client):
    e = raise_for(
        fake,
        client,
        {"status": 422, "json": {"errors": {"webhook_url": ["can't be blank", "must be https"], "name": ["is too long"]}}},
    )
    assert e.code is None
    assert e.message == "QuBe Sync answered 422: webhook_url: can't be blank, must be https; name: is too long"


def test_error_a_list_of_problems(fake, client):
    e = raise_for(
        fake,
        client,
        {"status": 422, "json": {"errors": [{"path": "/input/since", "message": "is not a date"}, {"path": "/workflow", "message": "unknown"}]}},
    )
    assert isinstance(e.errors, list)
    assert e.message == "QuBe Sync answered 422: /input/since: is not a date; /workflow: unknown"


def test_error_plain_text_401(fake, client):
    e = raise_for(fake, client, {"status": 401, "text": "Unauthorized", "headers": {"WWW-Authenticate": "Basic realm=\"Application\""}})
    assert e.status == 401
    assert e.errors is None
    assert e.code is None
    assert e.body == "Unauthorized"
    assert e.message == "QuBe Sync answered 401: Unauthorized"


def test_error_long_bodies_are_trimmed(fake, client):
    e = raise_for(fake, client, {"status": 500, "text": "x" * 2000 + "\n"})
    assert e.message == "QuBe Sync answered 500: " + "x" * 500
    assert len(e.body) == 2001


def test_errors_never_show_the_key(fake, client):
    e = raise_for(fake, client, {"status": 401, "text": "Unauthorized"})
    for text in (str(e), repr(e), e.message, e.body):
        assert API_KEY not in text
    assert "authorization" not in repr(e).lower()
