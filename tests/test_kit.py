"""qubesync.kit without a framework or an ORM: the settings, the client, the answer's parts,
what the webhook route checks before it reads a table, and the job's own rules. The rest runs
on both ORMs in test_kit_models.py and through every adapter in test_kit_routes.py."""
import datetime
import logging
import subprocess
import sys
from pathlib import Path

import pytest

import qubesync.kit as kit
from kit_support import SECRET, api_error, kit_reset, sign, vector_body  # noqa: F401
from qubesync import webhooks


class Plain(kit.Operation):
    workflow = "add_transaction"
    slug = "create_invoice"


# -- Settings --------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "setting,named",
    [
        ("operations", "operations="),
        ("connection_events", "connection_events="),
        ("current_account", "current_account="),
        ("api_key", "QUBE_API_KEY"),
        ("webhook_secret", "QUBE_WEBHOOK_SECRET"),
        ("webhook_url", "QUBE_WEBHOOK_URL"),
    ],
)
def test_an_unset_setting_raises_naming_it_and_the_config_file(setting, named):
    with pytest.raises(kit.NotConfigured) as raised:
        getattr(kit.settings(), setting)

    assert named in str(raised.value)
    assert "quickbooks_desktop/config.py" in str(raised.value)
    assert raised.value.setting == setting


def test_reads_the_environment_at_first_use(monkeypatch):
    monkeypatch.setenv("QUBE_API_KEY", "key-from-env")
    monkeypatch.setenv("QUBE_WEBHOOK_SECRET", "secret-from-env")
    monkeypatch.setenv("QUBE_WEBHOOK_URL", "https://app.example/webhooks/qube/")

    config = kit.settings()
    assert config.api_key == "key-from-env"
    assert config.webhook_secret == "secret-from-env"
    assert config.webhook_url == "https://app.example/webhooks/qube"
    assert config.base_url == "https://qubesync.com"


def test_prefers_what_configure_sets(monkeypatch):
    monkeypatch.setenv("QUBE_URL", "https://env.example")
    kit.configure(base_url="https://set.example", webhook_url="https://app.example/hooks/")

    assert kit.settings().base_url == "https://set.example"
    assert kit.settings().webhook_url == "https://app.example/hooks"


def test_has_the_defaults_the_plan_names():
    config = kit.settings()

    assert config.job_attempts == 10
    assert isinstance(config.dedupe, kit.DatabaseDedupe)
    assert config.authorize_question is kit.owner_answers
    assert not config.is_set("enqueue")


def test_resolves_operations_and_connection_events_at_use():
    kit.configure(
        operations={"create_invoice": Plain, "by_path": "test_kit.Plain", "other": "test_kit.Nope"},
        connection_events="qubesync.kit.ConnectionEvents",
    )

    assert kit.settings().operation_class("create_invoice") is Plain
    assert kit.settings().operation_class("by_path") is Plain
    assert kit.settings().operation_class("missing") is None
    assert kit.settings().operation_class(None) is None
    assert kit.settings().connection_events_class() is kit.ConnectionEvents
    with pytest.raises(AttributeError):
        kit.settings().operation_class("other")


def test_refuses_settings_it_cant_use():
    with pytest.raises(TypeError, match="no such setting connection"):
        kit.configure(connection=object)
    with pytest.raises(TypeError, match="current_account"):
        kit.configure(current_account="Account.first")
    with pytest.raises(TypeError, match="authorize_question"):
        kit.configure(authorize_question=True)
    with pytest.raises(TypeError, match=r"seen\(key\)"):
        kit.configure(dedupe=object())
    with pytest.raises(TypeError, match="job_attempts"):
        kit.configure(job_attempts=0)
    with pytest.raises(TypeError, match="job_attempts"):
        kit.configure(job_attempts=True)


def test_takes_job_attempts_and_a_dedupe_with_once():
    class Once(object):
        def once(self, run, delivery_id, fn):
            return fn()

    kit.configure(job_attempts=3, dedupe=Once())

    assert kit.settings().job_attempts == 3
    assert isinstance(kit.settings().dedupe, Once)


def test_never_shows_a_secret_in_repr(monkeypatch):
    monkeypatch.setenv("QUBE_WEBHOOK_SECRET", "whsec_from_env")
    kit.configure(api_key="qube_live_supersecret")

    shown = repr(kit.settings())
    assert "supersecret" not in shown and "whsec_from_env" not in shown
    assert "api_key=[hidden]" in shown

    kit.configure(webhook_secret=["whsec_one", "whsec_two"])
    assert "whsec_one" not in repr(kit.settings())


def test_makes_the_client_from_the_settings_with_no_key_in_its_repr():
    kit.configure(api_key="qube_test_api_key", base_url="https://qube.example")

    assert kit.client().base_url == "https://qube.example"
    assert kit.client() is kit.client()
    assert "qube_test_api_key" not in repr(kit.client())


def test_logs_a_retry_without_its_query_or_any_key(caplog):
    kit.log_retry({"method": "GET", "url": "https://qube.example/api/v2/x", "status": 503, "delay": 0.25})

    assert "QuBe Sync: retrying GET https://qube.example/api/v2/x (503) in 0.2 s" in caplog.text


def test_the_tables_need_db_session_or_qubesync_django(monkeypatch):
    from qubesync.kit import _store

    monkeypatch.setattr(_store, "_registered", [])

    with pytest.raises(kit.NotConfigured, match=r"db_session=.*INSTALLED_APPS"):
        _store.current_store()


# -- The answer's parts ----------------------------------------------------------------------


QUESTION = {
    "choices": [
        {
            "id": "add",
            "fields": [
                {"name": "name", "type": "text"},
                {"name": "count", "type": "number"},
                {"name": "rate", "type": "number"},
                {"name": "taxable", "type": "boolean"},
                {"name": "note", "type": "text"},
            ],
        }
    ]
}


def test_answer_data_takes_each_field_as_its_type():
    picked = kit.choice(QUESTION, "add")
    form = {"data[name]": " Lone Star ", "data[count]": "3", "data[rate]": "1.5", "data[taxable]": "true", "data[note]": ""}

    assert kit.answer_data(picked, form) == {"name": "Lone Star", "count": 3, "rate": 1.5, "taxable": True}
    assert kit.answer_data(picked, {"data[count]": "three"}) == {"count": "three", "taxable": False}
    assert kit.choice(QUESTION, "nope") is None
    assert kit.choice(None, "add") is None


def test_number_keeps_what_isnt_a_finite_number():
    assert kit.number("12") == 12
    assert kit.number("-1.5") == -1.5
    assert kit.number("nan") == "nan"
    assert kit.number("inf") == "inf"


def test_refusal_says_what_quickbooks_said():
    assert kit.refusal(api_error(422, {"detail": "count must be a whole number"})) == (
        "That answer couldn't be used: count must be a whole number"
    )
    assert kit.refusal(api_error(422)) == "That answer couldn't be used. Check it and try again."


def test_back_goes_to_this_apps_pages_only():
    assert kit.back("https://app.example/invoices/1", "app.example") == "https://app.example/invoices/1"
    assert kit.back("/invoices/1", "app.example") == "/invoices/1"
    assert kit.back("https://evil.example/", "app.example") == "/"
    assert kit.back("//evil.example/x", "app.example") == "/"
    assert kit.back("/\\evil.example/x", "app.example") == "/"
    assert kit.back(None, "app.example") == "/"


# -- The webhook route, before any table -----------------------------------------------------


def test_receive_answers_413_before_reading_and_401_for_a_bad_signature(caplog):
    kit.configure(webhook_secret=SECRET)
    body = vector_body("workflow_run.completed").encode()

    assert kit.receive("run", "1", None, sign(body)).status == 413
    assert kit.receive("run", "1", b"x" * (kit.MAX_WEBHOOK_BODY + 1), sign(body)).status == 413
    assert kit.receive("run", "1", body, None).status == 401
    assert kit.receive("run", "1", body, sign(body, secret="whsec_other")).status == 401
    assert "refused a webhook: missing" in caplog.text
    assert "refused a webhook: mismatch" in caplog.text
    assert SECRET not in caplog.text


# -- The job and the bases -------------------------------------------------------------------


def test_run_takes_a_run_a_connection_or_a_request_only():
    with pytest.raises(ValueError, match="a run, a connection or a request"):
        kit.run("operation", "1", vector_body("workflow_run.completed"))


def test_retry_delay_grows_with_each_attempt():
    # Ten attempts wait nine times.
    delays = [kit.retry_delay(attempt) for attempt in range(1, 10)]

    assert delays == sorted(delays)
    assert 3 <= delays[0] < 4
    assert 4 * 3600 < sum(delays) < 5 * 3600


def test_start_needs_a_connection_quickbooks_has_made():
    class Pending(object):
        qube_id = None
        _kit_store = object()

    with pytest.raises(kit.NotConnected, match="qube_id"):
        Plain.start(object(), Pending())
    with pytest.raises(kit.NotConnected):
        Plain.start(object(), object())


def test_the_base_find_record_names_the_fallback():
    with pytest.raises(NotImplementedError, match="record_type"):
        Plain.find_record("1")


# -- Helpers ---------------------------------------------------------------------------------


def test_family_for():
    assert kit.family_for("vendor") == "name"
    assert kit.family_for("item_inventory_assembly") == "item"
    assert kit.family_for("items") == "items"
    assert kit.family_for("invoice") == "invoice"


def test_mapping_helpers():
    class Thing(object):
        contract = None

    assert kit.get(Thing(), "contract", "po_number") is None
    assert kit.rows(None) == [] and kit.rows((1, 2)) == [1, 2]
    event = webhooks.parse(vector_body("workflow_run.completed", {"output": {"record": {"txn_id": "T1"}}}))
    assert kit.dig(event, "output", "record", "txn_id") == "T1"
    assert kit.as_string(True) == "true" and kit.as_number("n/a") is None and kit.as_integer("2.9") == 2
    assert kit.as_date(datetime.datetime(2026, 10, 24, 9, 30)) == "2026-10-24"
    assert kit.without_nils({"a": None, "b": [None, {"c": None, "d": 1}]}) == {"b": [{"d": 1}]}


def test_the_kit_imports_no_framework_or_orm():
    code = (
        "import sys, qubesync, qubesync.kit; "
        "loaded = {'django', 'flask', 'fastapi', 'starlette', 'sqlalchemy', 'jinja2'} & set(sys.modules); "
        "assert not loaded, loaded"
    )
    subprocess.run([sys.executable, "-c", code], check=True, env={"PYTHONPATH": str(Path(kit.__file__).parents[2])})


def test_logs_to_the_qubesync_kit_logger(caplog):
    with caplog.at_level(logging.INFO, logger="qubesync.kit"):
        kit.log_retry({"method": "PUT", "url": "u", "status": None, "error": OSError(), "delay": 1})

    assert caplog.records[-1].name == "qubesync.kit"
    assert "(OSError)" in caplog.text
