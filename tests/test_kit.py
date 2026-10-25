"""qubesync.kit, without a framework: settings, the bases, the job and the routes' work."""
import json
import logging
from pathlib import Path

import pytest

import qubesync.kit as kit
from qubesync import webhooks
from kit_support import (  # noqa: F401
    DECISIONS,
    PROMPT,
    SEARCH,
    SECRET,
    WEBHOOK_URL,
    FakeClient,
    api_error,
    connection_event,
    drain,
    kit_reset,
    notification,
    run_event,
    sign,
)


class Record(object):
    def __init__(self, id=1, **fields):
        self.id = id
        self.qube_reference = fields.pop("qube_reference", "ref-1")
        self.qube_revision = fields.pop("qube_revision", 0)
        self.qube_question = fields.pop("qube_question", None)
        self.qube_links = fields.pop("qube_links", None)
        self.saves = []
        self.__dict__.update(fields)


RECORDS = {}


class Invoicing(kit.Operation):
    workflow = "add_transaction"
    slug = "create_invoice"
    seen = None

    @classmethod
    def find_record(cls, record_id):
        return RECORDS.get(record_id)

    def input(self):
        return {"operation": "invoice.create", "params": {"ref_number": str(self.record.id)}}

    def save_record(self, fields):
        self.record.saves.append(list(fields))

    def notification(self, event):
        type(self).seen.append(("notification", event.delivery_id))

    def ended(self, event):
        type(self).seen.append(("ended", event.outcome))

    def failed(self, event):
        type(self).seen.append(("failed", event.event))


class Account(object):
    def __init__(self, id=7, qube_connection_id=None, qube_connection_revision=None):
        self.id = id
        self.qube_connection_id = qube_connection_id
        self.qube_connection_revision = qube_connection_revision
        self.saves = []


ACCOUNTS = {}


class Connection(kit.ConnectionEvents):
    seen = None

    @classmethod
    def find_record(cls, record_id):
        return ACCOUNTS.get(record_id)

    def save_record(self, fields):
        self.account.saves.append(list(fields))

    def connected(self, event):
        type(self).seen.append("connected")

    def setup_cancelled(self, event):
        type(self).seen.append("setup_cancelled")

    def stalled(self, event):
        type(self).seen.append(("stalled", event.stall_reason))

    def resumed(self, event):
        type(self).seen.append("resumed")


@pytest.fixture(autouse=True)
def app(kit_reset):
    RECORDS.clear()
    ACCOUNTS.clear()
    Invoicing.seen = []
    Connection.seen = []
    fake = FakeClient()
    queued = []
    kit.configure(
        operations={"create_invoice": Invoicing},
        connection=Connection,
        webhook_secret=SECRET,
        webhook_url=WEBHOOK_URL + "/",
        client=fake,
        enqueue=lambda *job: queued.append(job),
    )
    return {"client": fake, "queued": queued}


# -- Settings --------------------------------------------------------------------------------


@pytest.mark.parametrize("name", ["operations", "connection", "current_account"])
def test_an_unset_setting_raises_naming_the_config_file(name):
    kit.reset()
    with pytest.raises(kit.NotConfigured) as raised:
        getattr(kit.settings(), name)
    message = str(raised.value)
    assert "qubesync.kit.configure(%s=...)" % name in message
    assert "quickbooks_desktop/config.py" in message
    assert raised.value.setting == name


def test_unset_environment_settings_name_the_variable_and_the_file():
    kit.reset()
    with pytest.raises(kit.NotConfigured) as raised:
        kit.client()
    assert "QUBE_API_KEY" in str(raised.value)
    assert "quickbooks_desktop/config.py" in str(raised.value)
    with pytest.raises(kit.NotConfigured, match="QUBE_WEBHOOK_SECRET"):
        kit.receive("create_invoice", "1", b"{}", sign("{}"))


def test_the_job_raises_when_operations_isnt_set():
    kit.reset()
    with pytest.raises(kit.NotConfigured, match="operations"):
        kit.run("create_invoice", "1", run_event())


def test_environment_settings_are_read_at_first_use(monkeypatch):
    kit.reset()
    assert kit.settings().base_url == "https://qubesync.com"
    monkeypatch.setenv("QUBE_API_KEY", "sk_from_env")
    monkeypatch.setenv("QUBE_URL", "https://staging.qubesync.example")
    client = kit.client()
    assert client.base_url == "https://staging.qubesync.example"
    assert kit.client() is client  # made once
    kit.configure(base_url="https://qubesync.com")
    assert kit.client() is not client


def test_repr_hides_the_secrets(monkeypatch):
    monkeypatch.setenv("QUBE_API_KEY", "sk_live_do_not_show")
    kit.configure(webhook_secret=["whsec_one", "whsec_two"])
    shown = repr(kit.settings())
    assert "sk_live_do_not_show" not in shown and "whsec_one" not in shown
    assert "api_key=<hidden> (from QUBE_API_KEY)" in shown
    assert "webhook_secret=<hidden>" in shown
    assert "webhook_url=" in shown


def test_configure_refuses_what_isnt_a_setting():
    with pytest.raises(TypeError, match="no such setting"):
        kit.configure(operation={})
    with pytest.raises(ValueError, match="connection"):
        kit.configure(operations={"connection": Connection})
    with pytest.raises(TypeError, match="authorize_question"):
        kit.configure(authorize_question=True)
    with pytest.raises(TypeError, match="dedupe"):
        kit.configure(dedupe=set())


def test_operations_by_dotted_path_are_imported_at_first_use():
    kit.configure(operations={"create_invoice": "test_kit.Invoicing"}, connection="test_kit:Connection")
    assert kit.operation_class("create_invoice") is Invoicing
    assert kit.operation_class("connection") is Connection
    assert kit.operation_class("nope") is None


def test_webhook_secret_may_be_a_list_while_it_rotates(app):
    kit.configure(webhook_secret=["whsec_new", SECRET])
    assert kit.receive("create_invoice", "1", b"{}", sign("{}")).status == 200


# -- The webhook route -----------------------------------------------------------------------


def test_a_verified_webhook_is_enqueued_and_answered_200(app):
    body = run_event()
    reply = kit.receive("create_invoice", "42", body.encode(), sign(body))
    assert reply.status == 200
    assert app["queued"] == [("create_invoice", "42", body)]


def test_the_connection_slug_is_received_too(app):
    body = connection_event()
    assert kit.receive("connection", "7", body.encode(), sign(body)).status == 200
    assert app["queued"][0][0] == "connection"


def test_a_bad_signature_is_401_and_only_its_reason_is_logged(app, caplog):
    body = run_event(reference="secret-ref")
    header = sign(body, secret="whsec_wrong")
    with caplog.at_level(logging.WARNING, logger="qubesync.kit"):
        reply = kit.receive("create_invoice", "42", body.encode(), header)
    assert reply.status == 401
    assert app["queued"] == []
    assert caplog.messages == ["QuBe Sync: refused a webhook: mismatch"]
    assert SECRET not in caplog.text and "secret-ref" not in caplog.text and header not in caplog.text


def test_a_body_over_5_mb_is_413_and_one_at_5_mb_is_taken(app):
    body = json.dumps({"event": "x", "pad": "a" * (kit.MAX_WEBHOOK_BODY - 30)})
    body += " " * (kit.MAX_WEBHOOK_BODY - len(body))
    assert len(body) == kit.MAX_WEBHOOK_BODY
    assert kit.receive("create_invoice", "1", body.encode(), sign(body)).status == 200
    bigger = body + " "
    assert kit.receive("create_invoice", "1", bigger.encode(), sign(bigger)).status == 413
    assert len(app["queued"]) == 1


def test_a_missing_signature_is_401(app):
    assert kit.receive("create_invoice", "42", b"{}", None).status == 401


def test_an_unknown_slug_is_404_and_not_enqueued(app):
    body = run_event()
    assert kit.receive("delete_everything", "42", body.encode(), sign(body)).status == 404
    assert app["queued"] == []


def test_the_servers_test_vectors_verify(app, monkeypatch):
    vectors = json.loads((Path(__file__).parent / "fixtures" / "test_vectors.json").read_text(encoding="utf-8"))
    case = vectors["signatures"][0]
    monkeypatch.setattr(webhooks.time, "time", lambda: vectors["timestamp"])
    kit.configure(webhook_secret=case["secrets"])
    reply = kit.receive("create_invoice", "42", case["body"].encode("utf-8"), case["header"])
    assert reply.status == 200
    assert app["queued"][0][2] == case["body"]


# -- Operation: start and the job ------------------------------------------------------------


def test_start_saves_a_new_reference_before_the_run_starts(app):
    record = Record(id=5, qube_reference="old", qube_revision=9, qube_question=PROMPT, qube_links={})
    Invoicing.start(record, "c1")
    name, args, kwargs = app["client"].calls[0]
    assert name == "start_run"
    assert args[:2] == ("c1", "add_transaction")
    assert args[2] == {"operation": "invoice.create", "params": {"ref_number": "5"}}
    assert kwargs["reference"].startswith("create_invoice-5-")
    assert kwargs["reference"] == record.qube_reference
    assert kwargs["webhook_url"] == WEBHOOK_URL + "/create_invoice/5"
    assert record.qube_revision == 0 and record.qube_question is None
    assert record.saves[0] == ["qube_reference", "qube_revision"]


def test_an_event_for_another_reference_is_skipped_and_logged(caplog):
    RECORDS["1"] = record = Record(qube_reference="ref-current")
    with caplog.at_level(logging.WARNING, logger="qubesync.kit"):
        kit.run("create_invoice", "1", run_event(reference="ref-earlier"))
    assert Invoicing.seen == []
    assert record.saves == []
    assert "not its run" in caplog.text


def test_revisions_apply_in_order_and_late_ones_are_skipped():
    RECORDS["1"] = record = Record()
    kit.run("create_invoice", "1", run_event("workflow_run.completed", revision=3, outcome="added"))
    kit.run("create_invoice", "1", run_event("workflow_run.failed", revision=2))
    kit.run("create_invoice", "1", run_event("workflow_run.completed", revision=3, outcome="added"))
    assert Invoicing.seen == [("ended", "added")]
    assert record.qube_revision == 3


def test_ended_and_failed_dispatch():
    RECORDS["1"] = Record()
    kit.run("create_invoice", "1", run_event("workflow_run.completed", revision=1, outcome="added"))
    kit.run("create_invoice", "1", run_event("workflow_run.failed", revision=2))
    kit.run("create_invoice", "1", run_event("workflow_run.cancelled", revision=3))
    assert Invoicing.seen == [
        ("ended", "added"),
        ("failed", "workflow_run.failed"),
        ("failed", "workflow_run.cancelled"),
    ]


def test_a_question_is_saved_then_forgotten_by_a_newer_event():
    RECORDS["1"] = record = Record()
    kit.run("create_invoice", "1", run_event("workflow_run.awaiting_input", revision=1))
    assert record.qube_question == PROMPT
    assert record.qube_links == {"decisions": DECISIONS, "search": SEARCH}
    kit.run("create_invoice", "1", run_event("workflow_run.completed", revision=2, outcome="added"))
    assert record.qube_question is None and record.qube_links is None
    assert ["qube_question", "qube_links"] in record.saves


def test_a_notification_is_taken_once_by_its_delivery_id():
    RECORDS["1"] = record = Record()
    kit.run("create_invoice", "1", notification(delivery_id="d1"))
    kit.run("create_invoice", "1", notification(delivery_id="d1"))
    kit.run("create_invoice", "1", notification(delivery_id="d2"))
    assert Invoicing.seen == [("notification", "d1"), ("notification", "d2")]
    assert record.qube_revision == 0  # notifications don't move the revision


def test_the_dedupe_setting_keeps_the_delivery_ids():
    class Store(object):
        def __init__(self):
            self.keys = {"d-taken"}

        def seen(self, key):
            return key in self.keys

        def remember(self, key):
            self.keys.add(key)

    store = Store()
    kit.configure(dedupe=store)
    RECORDS["1"] = Record()
    kit.run("create_invoice", "1", notification(delivery_id="d-taken"))
    kit.run("create_invoice", "1", notification(delivery_id="d-new"))
    assert Invoicing.seen == [("notification", "d-new")]
    assert store.keys == {"d-taken", "d-new"}


def test_the_in_memory_dedupe_warns_once(caplog):
    RECORDS["1"] = Record()
    with caplog.at_level(logging.WARNING, logger="qubesync.kit"):
        kit.run("create_invoice", "1", notification(delivery_id="d1"))
        kit.run("create_invoice", "1", notification(delivery_id="d2"))
    assert sum("kept in memory" in message for message in caplog.messages) == 1


def test_the_job_refuses_an_unknown_slug_or_record():
    with pytest.raises(LookupError):
        kit.run("nope", "1", run_event())
    with pytest.raises(LookupError, match="found nothing"):
        kit.run("create_invoice", "missing", run_event())


def test_handlers_log_until_written(caplog):
    class Plain(kit.Operation):
        slug = "plain"

        def save_record(self, fields):
            pass

    record = Record()
    with caplog.at_level(logging.INFO, logger="qubesync.kit"):
        Plain(record).handle(webhooks.parse(run_event("workflow_run.failed", revision=1)))
    assert "Plain 1: workflow_run.failed" in caplog.text


def test_the_base_wont_save_without_a_framework():
    with pytest.raises(NotImplementedError, match="qubesync.django.Operation"):
        kit.Operation(Record()).save_revision(1)


# -- The default queue -----------------------------------------------------------------------


def test_the_default_enqueue_runs_the_job_on_a_thread_and_logs_failures(caplog):
    kit.configure(enqueue=None)
    RECORDS["1"] = record = Record()
    body = run_event("workflow_run.completed", revision=1, outcome="added")
    with caplog.at_level(logging.WARNING, logger="qubesync.kit"):
        assert kit.receive("create_invoice", "1", body.encode(), sign(body)).status == 200
        assert kit.receive("create_invoice", "missing", body.encode(), sign(body)).status == 200
        drain()
    assert record.qube_revision == 1
    assert "a webhook job failed" in caplog.text
    assert sum("a restart loses what hasn't run" in m for m in caplog.messages) == 1


# -- ConnectionEvents ------------------------------------------------------------------------


def test_connection_events_for_another_connection_are_skipped(caplog):
    ACCOUNTS["7"] = account = Account(qube_connection_id="c1")
    with caplog.at_level(logging.WARNING, logger="qubesync.kit"):
        kit.run("connection", "7", connection_event(connection_id="c-other"))
        kit.run("connection", "7", run_event())  # not a connection's event at all
    assert Connection.seen == []
    assert account.saves == []
    assert caplog.text.count("not its connection") == 2


def test_connection_events_dispatch_to_the_four_handlers_in_revision_order():
    ACCOUNTS["7"] = account = Account(qube_connection_id="c1", qube_connection_revision=0)
    kit.run("connection", "7", connection_event("connection.connected", revision=1))
    kit.run("connection", "7", connection_event("connection.setup_cancelled", revision=2))
    kit.run("connection", "7", connection_event("connection.resumed", revision=4))
    kit.run("connection", "7", connection_event("connection.stalled", revision=3, stall_reason="not_checking_in"))
    kit.run("connection", "7", connection_event("connection.stalled", revision=5, stall_reason="quickbooks_unavailable"))
    assert Connection.seen == ["connected", "setup_cancelled", "resumed", ("stalled", "quickbooks_unavailable")]
    assert account.qube_connection_revision == 5


# -- Onboarding ------------------------------------------------------------------------------


def test_connect_creates_a_connection_and_keeps_its_id(app):
    account = Account(id="acct/7", qube_connection_revision=4)
    kit.configure(current_account=lambda request: account)
    reply = kit.connect(object())
    assert (reply.status, reply.location) == (303, "https://qubesync.com/onboard/new")
    assert app["client"].calls == [
        ("create_connection", (), {"webhook_url": WEBHOOK_URL + "/connection/acct%2F7"})
    ]
    assert account.qube_connection_id == "c-new"
    assert account.qube_connection_revision is None  # a new connection's revisions start again
    assert account.saves == [["qube_connection_id", "qube_connection_revision"]]


def test_connect_reuses_the_saved_connection(app):
    account = Account(qube_connection_id="c1", qube_connection_revision=3)
    kit.configure(current_account=lambda request: account)
    reply = kit.connect(object())
    assert reply.location == "https://qubesync.com/onboard/again"
    assert app["client"].names() == ["update_connection", "regenerate_onboarding"]
    assert app["client"].calls[0][2] == {"webhook_url": WEBHOOK_URL + "/connection/7"}
    assert account.saves == [] and account.qube_connection_revision == 3


def test_connect_refuses_without_an_account(app):
    kit.configure(current_account=lambda request: None)
    assert kit.connect(object()).status == 401
    assert app["client"].calls == []


def test_connect_raises_while_current_account_isnt_set():
    with pytest.raises(kit.NotConfigured, match="current_account"):
        kit.connect(object())


# -- Questions -------------------------------------------------------------------------------


def asking(**fields):
    RECORDS["1"] = record = Record(qube_question=PROMPT, qube_links={"decisions": DECISIONS, "search": SEARCH}, **fields)
    return record


FORM = {
    "choice": "use",
    "data[customer]": "80000001-1",
    "data[amount]": " 12 ",
    "data[ratio]": "2.5",
    "data[notify]": "true",
    "data[note]": "rush",
    "data[blank]": "  ",
}


def test_every_answer_and_search_is_refused_while_authorize_question_isnt_set(app, caplog):
    asking()
    with caplog.at_level(logging.WARNING, logger="qubesync.kit"):
        answered = kit.answer(object(), "create_invoice", "1", FORM)
        searched = kit.search(object(), "create_invoice", "1", {"q": "river", "field": "customer"})
    assert answered.status == 403 and searched.status == 403 and searched.json == []
    assert app["client"].calls == []
    assert "authorize_question isn't set" in caplog.text
    assert "quickbooks_desktop/config.py" in caplog.text


def test_authorize_question_gets_the_request_and_the_record(app):
    record = asking()
    request = object()
    asked = []
    kit.configure(authorize_question=lambda req, rec, slug: asked.append((req, rec, slug)) or False)
    assert kit.answer(request, "create_invoice", "1", FORM).status == 404
    assert asked == [(request, record, "create_invoice")]
    assert app["client"].calls == []


@pytest.mark.parametrize("answer", [1, "yes", None, [True]])
def test_only_true_from_authorize_question_allows(app, answer, caplog):
    asking()
    kit.configure(authorize_question=lambda request, record, operation: answer)
    with caplog.at_level(logging.WARNING, logger="qubesync.kit"):
        assert kit.answer(object(), "create_invoice", "1", FORM).status == 404
        assert kit.search(object(), "create_invoice", "1", {"q": "river", "field": "customer"}).status == 404
    assert app["client"].calls == []
    assert "authorize_question answered %r" % (answer,) in caplog.text


def test_an_unknown_slug_record_or_the_connection_slug_is_404(app):
    kit.configure(authorize_question=lambda request, record, operation: True)
    asking()
    assert kit.answer(object(), "nope", "1", FORM).status == 404
    assert kit.answer(object(), "connection", "7", FORM).status == 404
    assert kit.answer(object(), "create_invoice", "missing", FORM).status == 404


def test_an_answer_sends_the_choices_fields_as_their_types_and_goes_back(app):
    kit.configure(authorize_question=lambda request, record, operation: True)
    record = asking()
    reply = kit.answer(object(), "create_invoice", "1", FORM, "https://app.example/invoices/1", "app.example")
    assert (reply.status, reply.location) == (303, "https://app.example/invoices/1")
    assert app["client"].calls == [
        (
            "answer",
            (DECISIONS,),
            {
                "choice": "use",
                "data": {"customer": "80000001-1", "amount": 12, "ratio": 2.5, "notify": True, "note": "rush"},
            },
        )
    ]
    assert record.qube_question is None


def test_an_unticked_checkbox_is_false_and_a_bad_number_goes_as_typed():
    picked = PROMPT["choices"][0]
    data = kit.answer_data(picked, {"data[amount]": "lots", "data[ratio]": "inf"})
    assert data == {"amount": "lots", "ratio": "inf", "notify": False}


def test_an_answer_from_another_site_goes_back_to_root(app):
    kit.configure(authorize_question=lambda request, record, operation: True)
    asking()
    reply = kit.answer(object(), "create_invoice", "1", {"choice": "skip"}, "https://evil.example/x", "app.example")
    assert reply.location == "/"


def test_a_choice_the_question_doesnt_offer_is_409(app):
    kit.configure(authorize_question=lambda request, record, operation: True)
    asking()
    reply = kit.answer(object(), "create_invoice", "1", {"choice": "delete"})
    assert (reply.status, reply.text) == (409, kit.CHANGED)
    assert app["client"].calls == []


@pytest.mark.parametrize(
    "error",
    [api_error(409, {"code": "prompt_changed"}), api_error(400, {"code": "not_awaiting_input"}), api_error(400)],
)
def test_an_answer_quBe_sync_says_is_stale_forgets_the_question_and_is_409(app, error):
    kit.configure(authorize_question=lambda request, record, operation: True)
    record = asking()
    app["client"].raises["answer"] = error
    reply = kit.answer(object(), "create_invoice", "1", {"choice": "skip"})
    assert (reply.status, reply.text) == (409, kit.CHANGED)
    assert record.qube_question is None


def test_a_refused_answer_is_422_with_quBe_syncs_words_and_keeps_the_question(app):
    kit.configure(authorize_question=lambda request, record, operation: True)
    record = asking()
    app["client"].raises["answer"] = api_error(422, {"code": "invalid_data", "detail": "amount must be a number"})
    reply = kit.answer(object(), "create_invoice", "1", {"choice": "skip"})
    assert (reply.status, reply.text) == (422, "QuBe Sync couldn't take that answer: amount must be a number")
    assert record.qube_question == PROMPT


def test_a_server_error_answering_raises(app):
    kit.configure(authorize_question=lambda request, record, operation: True)
    asking()
    app["client"].raises["answer"] = api_error(500)
    with pytest.raises(kit.APIError):
        kit.answer(object(), "create_invoice", "1", {"choice": "skip"})


def test_answered_keeps_a_question_asked_since():
    record = Record(qube_question=dict(PROMPT, token="tok2"))
    Invoicing(record).answered("tok1")
    assert record.qube_question["token"] == "tok2"


def test_search_asks_quBe_sync_within_its_bounds(app):
    kit.configure(authorize_question=lambda request, record, operation: True)
    asking()
    assert kit.search(object(), "create_invoice", "1", {"q": "r", "field": "customer"}).json == []
    assert kit.search(object(), "create_invoice", "1", {"q": "r" * 101, "field": "customer"}).json == []
    assert kit.search(object(), "create_invoice", "1", {"q": "river", "field": ""}).json == []
    assert kit.search(object(), "create_invoice", "1", {"q": "river"}).json == []
    assert kit.search(object(), "create_invoice", "1", {"q": "river", "field": "f" * 101}).json == []
    assert app["client"].calls == []
    reply = kit.search(object(), "create_invoice", "1", {"q": " river ", "field": "customer"})
    assert reply.status == 200 and reply.json[0]["label"] == "Riverbend"
    assert app["client"].calls == [("search", (SEARCH,), {"field": "customer", "q": "river"})]


def test_search_without_a_search_link_or_after_a_change_is_the_status_and_empty(app):
    kit.configure(authorize_question=lambda request, record, operation: True)
    RECORDS["1"] = Record(qube_question=PROMPT, qube_links={"decisions": DECISIONS})
    assert kit.search(object(), "create_invoice", "1", {"q": "river", "field": "customer"}).status == 409
    asking()
    app["client"].raises["search"] = api_error(409, {"code": "prompt_changed"})
    reply = kit.search(object(), "create_invoice", "1", {"q": "river", "field": "customer"})
    assert (reply.status, reply.json) == (409, [])
    app["client"].raises["search"] = api_error(503)
    with pytest.raises(kit.APIError):
        kit.search(object(), "create_invoice", "1", {"q": "river", "field": "customer"})


def test_question_context():
    record = asking()
    context = kit.question_context("create_invoice", record, "/qube/questions/create_invoice/1")
    assert context == {"question": PROMPT, "action": "/qube/questions/create_invoice/1", "operation": "create_invoice"}
    with pytest.raises(LookupError):
        kit.question_context("connection", record, "/x")


# -- Mapping helpers -------------------------------------------------------------------------


def test_mapping_helpers():
    import datetime

    class Thing(object):
        contract = None

    assert kit.get(Thing(), "contract", "po_number") is None
    assert kit.rows(None) == [] and kit.rows((1, 2)) == [1, 2]
    assert kit.dig(webhooks.parse(run_event(output={"record": {"txn_id": "T1"}})), "output", "record", "txn_id") == "T1"
    assert kit.as_string(True) == "true" and kit.as_number("n/a") is None and kit.as_integer("2.9") == 2
    assert kit.as_date(datetime.datetime(2026, 10, 24, 9, 30)) == "2026-10-24"
    assert kit.without_nils({"a": None, "b": [None, {"c": None, "d": 1}]}) == {"b": [{"d": 1}]}


def test_the_kit_imports_no_framework():
    import subprocess
    import sys

    code = (
        "import sys, qubesync, qubesync.kit, qubesync.kit.sqlalchemy; "
        "loaded = {'django', 'flask', 'fastapi', 'starlette', 'sqlalchemy', 'jinja2'} & set(sys.modules); "
        "assert not loaded, loaded"
    )
    subprocess.run([sys.executable, "-c", code], check=True, env={"PYTHONPATH": str(Path(kit.__file__).parents[2])})
