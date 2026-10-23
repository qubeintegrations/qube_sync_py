"""qubesync.webhooks against the server's test vectors (tests/fixtures/test_vectors.json,
written by `mix webhook_vectors.gen` in qube; don't edit it by hand)."""
import ast
import datetime
import json
from pathlib import Path

import pytest

from qubesync import QubeSyncError, SignatureError, webhooks

VECTORS = json.loads((Path(__file__).parent / "fixtures" / "test_vectors.json").read_text(encoding="utf-8"))
T = VECTORS["timestamp"]
SECRETS = VECTORS["secrets"]
SIGNATURES = VECTORS["signatures"]
EVENTS = VECTORS["events"]
VALID = SIGNATURES[0]


def _case_id(case):
    return case["name"]


@pytest.mark.parametrize("case", SIGNATURES, ids=_case_id)
def test_signature_vector(case):
    def run():
        return webhooks.verify(
            case["body"], case["header"], case["secrets"], tolerance=case["tolerance"], now=case["now"]
        )

    if case["valid"]:
        assert run().to_dict() == json.loads(case["body"])
        # Bytes verify the same as str.
        assert webhooks.verify(
            case["body"].encode("utf-8"), case["header"], case["secrets"],
            tolerance=case["tolerance"], now=case["now"],
        ).body == json.loads(case["body"])
    else:
        with pytest.raises(SignatureError) as info:
            run()
        assert info.value.reason == case["reason"]
        assert case["reason"] in str(info.value)


@pytest.mark.parametrize("case", EVENTS, ids=_case_id)
def test_event_vector(case):
    for event in (
        webhooks.verify(case["body"], case["header"], [SECRETS[0]], now=T),
        webhooks.parse(case["body"]),
    ):
        for field, expected in case["expect"].items():
            assert getattr(event, field) == expected, field
        assert event.body == json.loads(case["body"])
        assert event.to_dict() == json.loads(case["body"])


def by_type(name):
    return [webhooks.parse(case["body"]) for case in EVENTS if case["expect"]["type"] == name]


def test_secrets_as_a_single_string():
    event = webhooks.verify(VALID["body"], VALID["header"], SECRETS[0], now=T)
    assert event.type == "request"


def test_secrets_as_bytes():
    assert webhooks.verify(VALID["body"], VALID["header"], [SECRETS[0].encode()], now=T).type == "request"


def test_an_empty_secrets_list_is_a_programming_error():
    with pytest.raises(ValueError) as info:
        webhooks.verify(VALID["body"], VALID["header"], [], now=T)
    assert not isinstance(info.value, SignatureError)
    with pytest.raises(ValueError):
        webhooks.verify(VALID["body"], VALID["header"], None, now=T)


def test_argument_errors_come_before_a_missing_header():
    with pytest.raises(ValueError):
        webhooks.verify(VALID["body"], None, [], now=T)


@pytest.mark.parametrize("parsed", [json.loads(VALID["body"]), [1, 2]])
def test_a_parsed_body_is_refused(parsed):
    with pytest.raises(TypeError, match="raw request body"):
        webhooks.verify(parsed, VALID["header"], SECRETS, now=T)


def test_other_body_types_are_refused():
    with pytest.raises(TypeError):
        webhooks.verify(None, VALID["header"], SECRETS, now=T)


def test_now_as_an_aware_datetime():
    at = datetime.datetime.fromtimestamp(T, tz=datetime.timezone.utc)
    assert webhooks.verify(VALID["body"], VALID["header"], SECRETS, now=at).type == "request"
    late = at + datetime.timedelta(seconds=301)
    with pytest.raises(SignatureError) as info:
        webhooks.verify(VALID["body"], VALID["header"], SECRETS, now=late)
    assert info.value.reason == "stale"


def test_now_as_a_naive_datetime_is_utc():
    at = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=T + 300)
    assert webhooks.verify(VALID["body"], VALID["header"], SECRETS, now=at).type == "request"


def test_now_as_a_float():
    assert webhooks.verify(VALID["body"], VALID["header"], SECRETS, now=T + 300.9).type == "request"


def test_now_defaults_to_the_clock(monkeypatch):
    monkeypatch.setattr(webhooks.time, "time", lambda: float(T + 10))
    assert webhooks.verify(VALID["body"], VALID["header"], SECRETS).type == "request"
    monkeypatch.setattr(webhooks.time, "time", lambda: float(T + 301))
    with pytest.raises(SignatureError):
        webhooks.verify(VALID["body"], VALID["header"], SECRETS)


def test_stale_message_says_how_old_or_how_far_ahead():
    with pytest.raises(SignatureError, match="301 seconds old"):
        webhooks.verify(VALID["body"], VALID["header"], SECRETS, now=T + 301)
    with pytest.raises(SignatureError, match="400 seconds in the future"):
        webhooks.verify(VALID["body"], VALID["header"], SECRETS, now=T - 400)


def test_a_whitespace_header_is_missing():
    with pytest.raises(SignatureError) as info:
        webhooks.verify(VALID["body"], "  ", SECRETS, now=T)
    assert info.value.reason == "missing"


def test_signature_error_is_a_qubesync_error():
    assert issubclass(SignatureError, QubeSyncError)
    assert webhooks.SignatureError is SignatureError


@pytest.mark.parametrize("case", [c for c in SIGNATURES if not c["valid"]], ids=_case_id)
def test_error_messages_hold_no_secret_signature_or_body(case):
    with pytest.raises(SignatureError) as info:
        webhooks.verify(case["body"], case["header"], case["secrets"], tolerance=case["tolerance"], now=case["now"])
    message = str(info.value)
    for secret in SECRETS + case["secrets"]:
        assert secret not in message
    for part in (case["header"] or "").split(","):
        value = part.strip().partition("=")[2]
        if len(value) > 4:
            assert value not in message
    assert case["body"] not in message
    assert "Northwind" not in message


def test_newer_than():
    for event in by_type("workflow_run") + by_type("connection"):
        rev = event.revision
        assert event.newer_than(None) is True
        assert event.newer_than(rev - 1) is True
        assert event.newer_than(rev) is False
        assert event.newer_than(rev + 1) is False


def test_newer_than_without_a_revision_is_false_once_one_is_stored():
    event = webhooks.parse('{"event":"connection.connected"}')
    assert event.newer_than(None) is True
    assert event.newer_than(1) is False


def test_notifications_have_no_newer_than():
    (notification,) = by_type("notification")
    assert not hasattr(notification, "newer_than")
    assert notification.revision == 5


@pytest.mark.parametrize(
    "event,type_name",
    [
        ('{"page_request_id":"p"}', "request"),
        ('{"event":"workflow_run.completed"}', "workflow_run"),
        ('{"event":"workflow_run.notification"}', "notification"),
        ('{"event":"connection.connected"}', "connection"),
        ('{"event":"name_index.ready"}', "name_index"),
        ("{}", "unknown"),
    ],
)
def test_missing_keys_read_as_none(event, type_name):
    parsed = webhooks.parse(event)
    assert parsed.type == type_name
    names = [n for n in dir(type(parsed)) if isinstance(getattr(type(parsed), n), property)]
    for name in names:
        value = getattr(parsed, name)
        if name in ("type", "event", "dedupe_key", "page_request_id"):
            continue
        assert value is None, name
    assert parsed.get("nothing") is None
    if type_name == "request":
        assert parsed.dedupe_key == "p:"
    else:
        assert parsed.dedupe_key is None


def test_an_unknown_event_is_never_refused():
    (unknown,) = by_type("unknown")
    assert unknown.event == "invoice.paid_somewhere_new"
    assert unknown.get("something_new") == {"nested": [1, 2, 3]}
    assert unknown.app_id == "0196a1c0-0000-7000-8000-00000000a001"
    assert unknown.sandbox is True
    assert webhooks.parse('{"event":"workflow_run.paused"}').type == "unknown"
    assert webhooks.parse('{"event":42}').type == "unknown"


def test_typed_accessors():
    (request,) = [e for e in by_type("request") if e.page == 2]
    assert request.iteration_state == "continue"
    assert request.page_request_id == "0196a1c0-0000-7000-8000-00000000e002"
    assert request.response_json["status"] == "success"

    awaiting = [e for e in by_type("workflow_run") if e.event == "workflow_run.awaiting_input"][0]
    assert awaiting.run_state == "awaiting_input"
    assert awaiting.prompt["token"] == "Vq3kT9xRb2LmW8sZ"
    assert awaiting.links["ui"].startswith("https://")
    assert awaiting.connection_id.endswith("c001")

    (notification,) = by_type("notification")
    assert notification.name == "page"
    assert notification.seq == 1
    assert notification.from_["workflow"] == "stream_query"
    assert notification.data["records"][0]["full_name"] == "Acme Co"

    stalled = [e for e in by_type("connection") if e.event == "connection.stalled"][0]
    assert stalled.connection_id == "0196a1c0-0000-7000-8000-00000000c001"
    assert stalled.stall_reason == "not_checking_in"

    ready = [e for e in by_type("name_index") if e.event == "name_index.ready"][0]
    assert ready.name_index["records"] == 1240
    assert ready.timestamp == T


def test_parse_refuses_a_body_that_is_not_an_object():
    with pytest.raises(ValueError):
        webhooks.parse("[1, 2]")
    with pytest.raises(ValueError):
        webhooks.parse("not json")


def test_repr_holds_no_body():
    event = webhooks.parse(VALID["body"])
    assert "Northwind" not in repr(event)


def test_the_module_needs_only_the_standard_library():
    source = Path(webhooks.__file__).read_text(encoding="utf-8")
    imported = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            imported.add(node.module.split(".")[0])
    assert imported <= {"datetime", "hashlib", "hmac", "json", "re", "time", "typing"}
