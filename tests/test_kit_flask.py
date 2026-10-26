"""What's Flask's own in qubesync.flask: the blueprints come apart (and the webhooks one is
exempt from Flask-WTF's CSRF), the Jinja globals and templates, an app's own template, and the
default queue running each job in an app context. The routes' status codes are in
test_kit_routes.py, on all three adapters."""
import os

import pytest

pytest.importorskip("flask")
pytest.importorskip("sqlalchemy")

from flask import Flask, current_app, render_template_string  # noqa: E402

import qubesync.flask as qube_flask  # noqa: E402
import qubesync.kit as kit  # noqa: E402
from kit_support import DECISIONS, QUESTION, drain, kit_reset, run_body, sign  # noqa: E402,F401
from kit_worlds import CreateInvoice, make_driver, world as current_world  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def app(kit_reset):
    return make_driver("flask")


@pytest.fixture
def world(app):
    return app[1]


@pytest.fixture
def account(world):
    return world.account()


def test_the_blueprints_come_apart_for_the_sign_in():
    bps = qube_flask.blueprints()

    assert [bp.name for bp in bps] == ["qubesync_webhooks", "qubesync_connections", "qubesync_questions"]
    app = Flask("apart")
    app.register_blueprint(bps.webhooks, url_prefix="/hooks")
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/hooks/webhooks/qube/runs/<id>" in rules
    assert not any(rule.startswith("/quickbooks") for rule in rules)


def test_the_webhooks_blueprint_is_exempt_from_flask_wtf_csrf():
    class CSRF(object):
        def __init__(self):
            self.exempted = []

        def exempt(self, view):
            self.exempted.append(view)

    app = Flask("csrf")
    csrf = CSRF()
    app.extensions["csrf"] = csrf
    bps = qube_flask.init_app(app)

    assert csrf.exempted == [bps.webhooks]


def test_init_app_registers_the_jinja_globals(app, world, account):
    http = app[0]
    invoice = world.invoice(account)
    run = world.run(invoice, world.connection(account), question=QUESTION, links={"decisions": DECISIONS})

    with http.app.test_request_context("/"):
        shown = render_template_string("{{ qube_run_status(invoice, 'create_invoice') }}{{ qube_question(invoice, 'create_invoice') }}", invoice=invoice)

    assert '<p class="qube-run-summary">Running</p>' in shown
    assert 'action="/qube/questions/runs/%s"' % run.id in shown


def test_the_forms_carry_flask_wtfs_csrf_token(app, world, account):
    http = app[0]
    invoice = world.invoice(account)
    world.ago(world.run(invoice, world.connection(account), state="starting", question=QUESTION, links={"decisions": DECISIONS}), 120)
    http.app.jinja_env.globals["csrf_token"] = lambda: "tok-123"
    try:
        with http.app.test_request_context("/"):
            shown = qube_flask.question_html(invoice, "create_invoice") + qube_flask.run_status_html(invoice, "create_invoice")
    finally:
        del http.app.jinja_env.globals["csrf_token"]

    assert shown.count('name="csrf_token"') == 3  # two choices and the retry
    assert 'value="tok-123"' in shown


def test_an_apps_own_template_comes_first(world, account, kit_reset):
    invoice = world.invoice(account)
    world.run(invoice, world.connection(account), question=QUESTION, links={"decisions": DECISIONS})
    app = Flask("override", template_folder=os.path.join(HERE, "kit_templates", "override"))
    qube_flask.init_app(app)

    with app.test_request_context("/"):
        shown = qube_flask.question_html(invoice, "create_invoice")

    assert shown.strip() == '<div class="app-own-question">Which customer?</div>'


def test_the_default_queue_runs_each_job_in_an_app_context(app, world, account, monkeypatch):
    http = app[0]
    run = world.run(world.invoice(account), world.connection(account))
    contexts = []
    find = CreateInvoice.find_record.__func__

    def find_record(cls, id):
        contexts.append(current_app.name)
        return find(cls, id)

    monkeypatch.setattr(CreateInvoice, "find_record", classmethod(find_record))
    body = run_body("workflow_run.completed", run)

    response = http.post("/webhooks/qube/runs/%s" % run.id, body=body, headers={"X-QUBE-Signature": sign(body)})
    drain()

    assert response.status == 200
    assert contexts == ["kit_flask_test"]
    assert world.reload(run).state == "completed"
    assert current_world() is world


def test_simulated_connect_follows_debug_and_testing_unless_production_is_set(app, world, account):
    http = app[0]
    made = iter(range(10))
    kit.settings().client.returns["create_connection"] = lambda **kwargs: {"id": "conn-q-sim-%d" % next(made)}
    assert http.post("/quickbooks/connections", {"simulated": "1"}, account=account).status == 303  # TESTING

    http.app.testing = False
    try:
        assert http.post("/quickbooks/connections", {"simulated": "1"}, account=account).status == 404
        http.app.debug = True
        assert http.post("/quickbooks/connections", {"simulated": "1"}, account=account).status == 303
    finally:
        http.app.testing, http.app.debug = True, False
    kit.configure(production=True)
    assert http.post("/quickbooks/connections", {"simulated": "1"}, account=account).status == 404


def test_without_a_secret_key_an_answer_that_cant_go_through_answers_as_text(app, world, account):
    http = app[0]
    run = world.run(world.invoice(account), world.connection(account), question=QUESTION, links={"decisions": DECISIONS})
    http.app.secret_key = None
    try:
        response = http.post("/qube/questions/runs/%s" % run.id, {"choice": "nope"}, account=account)
    finally:
        http.app.secret_key = "kit-tests"

    assert (response.status, response.text) == (409, kit.CHANGED)


def test_run_status_html_takes_a_connection(app, world, account):
    invoice = world.invoice(account)
    connection = world.connection(account)
    connection.link(invoice, kind="invoice", qb_id="TXN-1")

    with app[0].app.test_request_context("/"):
        shown = qube_flask.run_status_html(invoice, "create_invoice", connection=connection)

    assert 'data-qube-sync-status="in_quickbooks"' in shown


def test_redirect_back_goes_back_with_the_message_for_the_page(app):
    flask_app = app[0].app
    with flask_app.test_request_context("/start", method="POST", headers={"Referer": "/invoices/1"}):
        response = qube_flask.redirect_back("Connect first.")
        assert (response.status_code, response.location) == (303, "/invoices/1")
        assert qube_flask.take_error() == "Connect first."
    with flask_app.test_request_context("/start", method="POST", headers={"Referer": "https://elsewhere.example/x"}):
        response = qube_flask.redirect_back()
        assert (response.status_code, response.location) == (303, "/")
        assert qube_flask.take_error() is None
