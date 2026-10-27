"""What the kit's tests share: signing a body as QuBe Sync does, the server's webhook test
vectors, a fake client, and the settings reset."""
import copy
import datetime
import hashlib
import hmac
import json
import time
from pathlib import Path

import pytest
import requests

import qubesync.kit as kit
from qubesync import APIError

SECRET = "whsec_kit_test"
API_KEY = "qube_test_api_key"
WEBHOOK_URL = "https://app.example/webhooks/qube"
ONBOARDING = "https://qubesync.com/onboard/abc"

VECTORS = json.loads((Path(__file__).parent / "fixtures" / "test_vectors.json").read_text())
# The vectors' connection id: a connection made with it receives the vectors' events.
QUBE_ID = "0196a1c0-0000-7000-8000-00000000c001"
# The vectors' plain request id.
REQUEST_ID = "0196a1c0-0000-7000-8000-00000000e001"
DELIVERY_ID = "0196a1c0-0000-7000-8000-00000000d001"

DECISIONS = "https://qubesync.com/api/v2/connections/c/workflow-runs/r/decisions?prompt_token=tok"
SEARCH = "https://qubesync.com/api/v2/connections/c/workflow-runs/r/search?prompt_token=tok"

QUESTION = {
    "token": "tok",
    "message": "Which customer?",
    "choices": [
        {"id": "use:1", "label": "Riverbend Electric", "fields": []},
        {
            "id": "add",
            "label": "Add it",
            "fields": [
                {"name": "name", "type": "text"},
                {"name": "count", "type": "number"},
                {"name": "rate", "type": "number"},
                {"name": "taxable", "type": "boolean"},
                {"name": "note", "type": "text"},
            ],
        },
    ],
}


def sign(body, secret=SECRET, timestamp=None):
    """The X-QUBE-Signature header for body, as QuBe Sync's server writes it."""
    if isinstance(body, str):
        body = body.encode("utf-8")
    t = int(time.time()) if timestamp is None else timestamp
    digest = hmac.new(secret.encode("utf-8"), str(t).encode("ascii") + b"." + body, hashlib.sha256)
    return "t=%d,v1=%s" % (t, digest.hexdigest())


def vector(name):
    for entry in VECTORS["events"]:
        if entry["name"] == name:
            return entry
    raise KeyError("no vector %s" % name)


def vector_body(name, changes=None):
    """A body from the server's webhook test vectors, by its name, with changes merged in."""
    body = json.loads(vector(name)["body"])
    body.update(changes or {})
    return json.dumps(body)


def run_body(name, run, changes=None):
    """A vector's run event, made this run's (its reference and its connection's qube_id)."""
    merged = {"reference": run.reference, "connection_id": run.connection.qube_id}
    merged.update(changes or {})
    return vector_body(name, merged)


def vector_prompt():
    return json.loads(vector("workflow_run.awaiting_input")["body"])["prompt"]


def api_error(status, errors=None):
    body = json.dumps({"errors": errors}) if errors is not None else ""
    return APIError(status, body=body, errors=errors)


def iso(moment):
    return moment.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class FakeClient(object):
    """Records each call. raises[name] is raised, returns[name] answered (a callable is called
    with the call's arguments first), else a plausible default."""

    def __init__(self):
        self.calls = []
        self.raises = {}
        self.returns = {}

    def _call(self, method, *args, **kwargs):
        self.calls.append((method, args, kwargs))
        if method in self.raises:
            raise self.raises[method]
        answer = self.returns.get(method)
        if callable(answer):
            return answer(*args, **kwargs)
        return copy.deepcopy(answer)

    def names(self):
        return [call[0] for call in self.calls]

    def called(self, name):
        return [call for call in self.calls if call[0] == name]

    def create_connection(self, *, webhook_url, name=None, type=None):
        kwargs = {"webhook_url": webhook_url, "name": name}
        if type is not None:
            kwargs["type"] = type
        made = self._call("create_connection", **kwargs)
        return made or {"id": "conn-q-1", "links": {"onboarding": ONBOARDING}}

    def redeliver_run(self, connection_id, run_id):
        sent = self._call("redeliver_run", connection_id, run_id)
        return sent or {"run_id": run_id, "event": "workflow_run.completed", "revision": 3, "webhook_url": "x"}

    def delete_connection(self, id):
        return self._call("delete_connection", id) or {"id": id}

    def queue(self, operation_id, connection_id, params=None, *, webhook_url, idempotency_key=None):
        queued = self._call(
            "queue", operation_id, connection_id, params, webhook_url=webhook_url, idempotency_key=idempotency_key
        )
        return queued or {"id": "req-q-1", "state": "queued"}

    def update_connection(self, id, *, webhook_url=None, name=None):
        return self._call("update_connection", id, webhook_url=webhook_url) or {"id": id}

    def regenerate_onboarding(self, id):
        return self._call("regenerate_onboarding", id) or {"id": id, "links": {"onboarding": ONBOARDING}}

    def list_connections(self):
        listed = self._call("list_connections")
        return [] if listed is None else listed

    def start_run(self, connection_id, workflow, input, *, reference, webhook_url, version=None):
        started = self._call("start_run", connection_id, workflow, input, reference=reference, webhook_url=webhook_url)
        return started or {"id": "run-q-1", "state": "running"}

    def answer(self, decisions_url, *, choice, data=None):
        return self._call("answer", decisions_url, choice=choice, data=data) or {"state": "running"}

    def search(self, search_url, *, field, q):
        found = self._call("search", search_url, field=field, q=q)
        return found if found is not None else [{"value": "80000001-1", "label": "Riverbend Electric", "detail": None}]


def timeout():
    return requests.ConnectTimeout("no answer")


@pytest.fixture(autouse=True)
def kit_reset(monkeypatch):
    """Each test starts with no settings and none of QUBE_* in the environment. Import it into
    a test module (from kit_support import kit_reset) to apply it there."""
    for name in ("QUBE_API_KEY", "QUBE_URL", "QUBE_WEBHOOK_SECRET", "QUBE_WEBHOOK_URL"):
        monkeypatch.delenv(name, raising=False)
    kit.reset()
    yield
    kit.reset()


def drain():
    """Waits for the in-process queue's jobs to finish, and for the retries they submit."""
    from qubesync.kit import _defaults

    queue = _defaults.default_queue()
    for _ in range(100):
        with queue._lock:
            executor, queue._executor = queue._executor, None
        if executor is None:
            return
        executor.shutdown(wait=True)
