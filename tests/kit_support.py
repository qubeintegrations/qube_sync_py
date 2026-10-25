"""What the kit's tests share: signing a body as QuBe Sync does, a fake client, and webhook
bodies."""
import hashlib
import hmac
import json
import time

from qubesync import APIError

SECRET = "whsec_kit_test"
WEBHOOK_URL = "https://app.example/webhooks/qube"

DECISIONS = "https://qubesync.com/api/v2/connections/c1/workflow-runs/r1/decisions?prompt_token=tok1"
SEARCH = "https://qubesync.com/api/v2/connections/c1/workflow-runs/r1/search?prompt_token=tok1"


def sign(body, secret=SECRET, timestamp=None):
    """The X-QUBE-Signature header for body, as QuBe Sync's server writes it."""
    if isinstance(body, str):
        body = body.encode("utf-8")
    t = int(time.time()) if timestamp is None else timestamp
    digest = hmac.new(secret.encode("utf-8"), str(t).encode("ascii") + b"." + body, hashlib.sha256)
    return "t=%d,v1=%s" % (t, digest.hexdigest())


PROMPT = {
    "id": "ask_about_add",
    "token": "tok1",
    "message": "Riverbend Electric isn't in QuickBooks yet.",
    "details": [{"label": "Customer", "value": "Riverbend Electric"}],
    "choices": [
        {
            "id": "use",
            "label": "Use another",
            "detail": "an existing customer",
            "fields": [
                {"name": "customer", "type": "record", "label": "Customer", "required": True},
                {"name": "amount", "type": "number"},
                {"name": "ratio", "type": "number"},
                {"name": "notify", "type": "boolean"},
                {"name": "note", "type": "text"},
                {"name": "blank", "type": "text"},
            ],
        },
        {"id": "skip", "label": "Skip it", "description": "Nothing is added."},
    ],
}


def run_event(kind="workflow_run.completed", reference="ref-1", revision=1, **extra):
    body = {
        "event": kind,
        "reference": reference,
        "revision": revision,
        "run_id": "r1",
        "connection_id": "c1",
        "timestamp": int(time.time()),
    }
    if kind == "workflow_run.awaiting_input":
        body.setdefault("prompt", PROMPT)
        body.setdefault("links", {"decisions": DECISIONS, "search": SEARCH})
    body.update(extra)
    return json.dumps(body)


def notification(reference="ref-1", delivery_id="d1", revision=2):
    return json.dumps(
        {
            "event": "workflow_run.notification",
            "reference": reference,
            "revision": revision,
            "delivery_id": delivery_id,
            "name": "page",
            "data": {"n": 1},
        }
    )


def connection_event(kind="connection.connected", connection_id="c1", revision=1, **connection):
    return json.dumps(
        {
            "event": kind,
            "revision": revision,
            "delivery_id": "cd-%s-%d" % (kind, revision),
            "connection": dict({"id": connection_id}, **connection),
        }
    )


def api_error(status, errors=None):
    body = json.dumps({"errors": errors}) if errors is not None else ""
    return APIError(status, body=body, errors=errors)


class FakeClient(object):
    """Records each call; raises what raises[name] holds, else answers returns[name] or a
    plausible default."""

    def __init__(self):
        self.calls = []
        self.raises = {}
        self.returns = {}

    def _call(self, name, *args, **kwargs):
        self.calls.append((name, args, kwargs))
        if name in self.raises:
            raise self.raises[name]
        return self.returns.get(name)

    def names(self):
        return [call[0] for call in self.calls]

    def create_connection(self, *, webhook_url, name=None):
        made = self._call("create_connection", webhook_url=webhook_url)
        return made or {"id": "c-new", "links": {"onboarding": "https://qubesync.com/onboard/new"}}

    def update_connection(self, id, *, webhook_url=None, name=None):
        return self._call("update_connection", id, webhook_url=webhook_url) or {"id": id}

    def regenerate_onboarding(self, id):
        made = self._call("regenerate_onboarding", id)
        return made or {"id": id, "links": {"onboarding": "https://qubesync.com/onboard/again"}}

    def start_run(self, connection_id, workflow, input, *, reference, webhook_url, version=None):
        return self._call(
            "start_run", connection_id, workflow, input, reference=reference, webhook_url=webhook_url
        ) or {"id": "r1", "state": "running"}

    def answer(self, decisions_url, *, choice, data=None):
        return self._call("answer", decisions_url, choice=choice, data=data) or {"id": "r1"}

    def search(self, search_url, *, field, q):
        found = self._call("search", search_url, field=field, q=q)
        return found if found is not None else [{"value": "80000001-1", "label": "Riverbend", "detail": "Austin"}]


import pytest  # noqa: E402

import qubesync.kit as kit  # noqa: E402


@pytest.fixture(autouse=True)
def kit_reset(monkeypatch):
    """Each test starts with no settings and none of QUBE_* in the environment. Import it
    into a test module (from kit_support import kit_reset) to apply it there."""
    for name in ("QUBE_API_KEY", "QUBE_URL", "QUBE_WEBHOOK_SECRET", "QUBE_WEBHOOK_URL"):
        monkeypatch.delenv(name, raising=False)
    kit.reset()
    yield
    kit.reset()


def drain():
    """Waits for the in-process queue's jobs to finish."""
    from qubesync.kit import _defaults

    _defaults.default_queue().shutdown(wait=True)
