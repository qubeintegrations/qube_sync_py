"""qubesync.flask: the blueprints through Flask's test client, the SQLAlchemy bases, and the
question template."""
import functools
import logging
import os

import pytest

flask = pytest.importorskip("flask")
pytest.importorskip("sqlalchemy")

from flask import Flask, abort, current_app, render_template_string, request  # noqa: E402

import kit_sqla  # noqa: E402
import qubesync.flask as qube_flask  # noqa: E402
import qubesync.kit as kit  # noqa: E402
from kit_sqla import Account, Invoice, Session  # noqa: E402
from kit_support import (  # noqa: E402,F401
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
    run_event,
    sign,
)

HERE = os.path.dirname(os.path.abspath(__file__))
contexts = []
CreateInvoice, Connection = kit_sqla.make_classes(
    qube_flask.Operation, qube_flask.ConnectionEvents, on_find=lambda: contexts.append(current_app.name)
)


def require_user(view):
    """Stands in for flask_login's login_required."""

    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if not request.headers.get("X-User"):
            abort(401)
        return view(*args, **kwargs)

    return wrapped


def current_account(request):
    return Session().query(Account).filter_by(user=request.headers["X-User"]).first()


def make_app(**options):
    app = Flask("kit_flask_test", **options)
    app.config["TESTING"] = True
    qube_flask.init_app(app, sign_in=require_user)

    @app.teardown_appcontext
    def remove_session(error=None):
        Session.remove()

    return app


@pytest.fixture(autouse=True)
def app(kit_reset):
    kit_sqla.reset()
    contexts.clear()
    fake = FakeClient()
    queued = []
    kit.configure(
        operations={"create_invoice": CreateInvoice},
        connection=Connection,
        webhook_secret=SECRET,
        webhook_url=WEBHOOK_URL,
        client=fake,
        enqueue=lambda *job: queued.append(job),
        current_account=current_account,
    )
    account = kit_sqla.add(Account(user="pat"))
    flask_app = make_app()
    return {"client": fake, "queued": queued, "account_id": account.id, "app": flask_app, "http": flask_app.test_client()}


def invoice(account_id, **fields):
    defaults = {"qube_reference": "ref-1", "qube_revision": 0}
    defaults.update(fields)
    return kit_sqla.add(Invoice(account_id=account_id, **defaults)).id


def asking(app):
    return invoice(app["account_id"], qube_question=PROMPT, qube_links={"decisions": DECISIONS, "search": SEARCH})


def fetch(model, id):
    Session.remove()
    return Session().get(model, id)


def post_webhook(http, path, body, header=None):
    return http.post(path, data=body, headers={"X-QUBE-Signature": header or sign(body), "Content-Type": "application/json"})


def test_blueprints_come_apart_for_the_sign_in():
    bps = qube_flask.blueprints()
    assert [bp.name for bp in bps] == ["qubesync_webhooks", "qubesync_connect", "qubesync_questions"]


# -- Webhooks --------------------------------------------------------------------------------


def test_a_signed_webhook_is_enqueued_without_sign_in(app):
    body = run_event()
    response = post_webhook(app["http"], "/webhooks/qube/create_invoice/42", body)
    assert response.status_code == 200
    assert app["queued"] == [("create_invoice", "42", body)]


def test_a_bad_signature_is_401_and_only_its_reason_is_logged(app, caplog):
    body = run_event()
    with caplog.at_level(logging.WARNING, logger="qubesync.kit"):
        response = post_webhook(app["http"], "/webhooks/qube/create_invoice/42", body, "t=1,v1=00")
    assert response.status_code == 401
    assert "QuBe Sync: refused a webhook: stale" in caplog.messages
    assert app["queued"] == []


def test_any_content_type_up_to_5_mb_and_413_beyond(app):
    body = run_event(pad="a" * (3 * 1024 * 1024))
    headers = {"X-QUBE-Signature": sign(body), "Content-Type": "text/plain"}
    response = app["http"].post("/webhooks/qube/create_invoice/1", data=body, headers=headers)
    assert response.status_code == 200 and app["queued"][0][2] == body
    huge = run_event(pad="a" * (5 * 1024 * 1024))
    assert post_webhook(app["http"], "/webhooks/qube/create_invoice/1", huge).status_code == 413


def test_an_unknown_slug_is_404(app):
    body = run_event()
    assert post_webhook(app["http"], "/webhooks/qube/nope/42", body).status_code == 404


def test_the_default_queue_runs_the_job_in_an_app_context(app):
    kit.configure(enqueue=None)
    record_id = invoice(app["account_id"])
    body = run_event("workflow_run.completed", revision=1, outcome="added")
    assert post_webhook(app["http"], "/webhooks/qube/create_invoice/%d" % record_id, body).status_code == 200
    drain()
    record = fetch(Invoice, record_id)
    assert (record.status, record.qube_revision) == ("sent", 1)
    assert contexts == ["kit_flask_test"]


# -- The SQLAlchemy bases --------------------------------------------------------------------


def test_the_bases_save_through_the_session(app):
    record_id = invoice(app["account_id"])
    with app["app"].app_context():
        kit.run("create_invoice", str(record_id), run_event("workflow_run.awaiting_input", revision=1))
    assert fetch(Invoice, record_id).qube_question == PROMPT
    with app["app"].app_context():
        kit.run("create_invoice", str(record_id), run_event("workflow_run.completed", revision=2, outcome="added"))
    record = fetch(Invoice, record_id)
    assert (record.qube_question, record.qube_revision, record.status) == (None, 2, "sent")


def test_connection_events_save_through_the_session(app):
    account = fetch(Account, app["account_id"])
    account.qube_connection_id = "c1"
    Session().commit()
    kit.run("connection", str(app["account_id"]), connection_event("connection.connected", revision=1))
    account = fetch(Account, app["account_id"])
    assert (account.connected, account.qube_connection_revision) == (True, 1)


def test_a_record_outside_a_session_cant_be_saved():
    with pytest.raises(RuntimeError, match="session"):
        CreateInvoice(Invoice(id=1)).save_revision(1)


# -- Onboarding ------------------------------------------------------------------------------


def test_connect_is_behind_the_sign_in(app):
    assert app["http"].post("/quickbooks/connect").status_code == 401
    assert app["client"].calls == []


def test_connect_creates_then_reuses_the_connection(app):
    http = app["http"]
    response = http.post("/quickbooks/connect", headers={"X-User": "pat"})
    assert (response.status_code, response.headers["Location"]) == (303, "https://qubesync.com/onboard/new")
    account = fetch(Account, app["account_id"])
    assert account.qube_connection_id == "c-new"
    assert app["client"].calls[0][2] == {"webhook_url": "%s/connection/%d" % (WEBHOOK_URL, account.id)}
    response = http.post("/quickbooks/connect", headers={"X-User": "pat"})
    assert response.headers["Location"] == "https://qubesync.com/onboard/again"
    assert app["client"].names() == ["create_connection", "update_connection", "regenerate_onboarding"]


# -- Questions -------------------------------------------------------------------------------


def mine(request, record, operation):
    return Session().get(Account, record.account_id).user == request.headers.get("X-User")


def test_answers_are_refused_while_authorize_question_isnt_set(app, caplog):
    record_id = asking(app)
    with caplog.at_level(logging.WARNING, logger="qubesync.kit"):
        response = app["http"].post("/qube/questions/create_invoice/%d" % record_id, data={"choice": "skip"}, headers={"X-User": "pat"})
    assert response.status_code == 403
    assert "authorize_question isn't set" in caplog.text


def test_an_answer_posts_typed_data_and_goes_back(app):
    kit.configure(authorize_question=mine)
    record_id = asking(app)
    response = app["http"].post(
        "/qube/questions/create_invoice/%d" % record_id,
        data={"choice": "use", "data[customer]": "80000001-1", "data[ratio]": "0.5"},
        headers={"X-User": "pat", "Referer": "http://localhost/invoices/%d" % record_id},
    )
    assert (response.status_code, response.headers["Location"]) == (303, "http://localhost/invoices/%d" % record_id)
    assert app["client"].calls[0][2] == {"choice": "use", "data": {"customer": "80000001-1", "ratio": 0.5, "notify": False}}
    assert fetch(Invoice, record_id).qube_question is None


def test_another_users_answer_is_404(app):
    kit.configure(authorize_question=mine)
    record_id = asking(app)
    response = app["http"].post("/qube/questions/create_invoice/%d" % record_id, data={"choice": "skip"}, headers={"X-User": "sam"})
    assert response.status_code == 404


def test_a_stale_answer_forgets_the_question_and_is_409(app):
    kit.configure(authorize_question=mine)
    record_id = asking(app)
    app["client"].raises["answer"] = api_error(409, {"code": "prompt_changed"})
    response = app["http"].post("/qube/questions/create_invoice/%d" % record_id, data={"choice": "skip"}, headers={"X-User": "pat"})
    assert (response.status_code, response.get_data(as_text=True)) == (409, kit.CHANGED)
    assert fetch(Invoice, record_id).qube_question is None


def test_a_refused_answer_is_422(app):
    kit.configure(authorize_question=mine)
    record_id = asking(app)
    app["client"].raises["answer"] = api_error(422, {"detail": "ratio is too big"})
    response = app["http"].post("/qube/questions/create_invoice/%d" % record_id, data={"choice": "skip"}, headers={"X-User": "pat"})
    assert response.status_code == 422 and "ratio is too big" in response.get_data(as_text=True)


def test_search_is_bounded_and_answers_json(app):
    kit.configure(authorize_question=mine)
    record_id = asking(app)
    url = "/qube/questions/create_invoice/%d/search" % record_id
    assert app["http"].get(url + "?q=r&field=customer", headers={"X-User": "pat"}).get_json() == []
    response = app["http"].get(url + "?q=river&field=customer", headers={"X-User": "pat"})
    assert response.status_code == 200 and response.get_json()[0]["label"] == "Riverbend"
    assert app["http"].get(url + "?q=river", headers={}).status_code == 401


# -- The question template -------------------------------------------------------------------


def test_the_template_renders_by_include_with_the_csrf_token(app):
    record_id = asking(app)
    with app["app"].test_request_context("/invoices/%d" % record_id):
        record = Session().get(Invoice, record_id)
        context = qube_flask.question_context("create_invoice", record)
        html = render_template_string(
            '{% include "qubesync/question.html" %}', csrf_token=lambda: "csrf-123", **context
        )
    assert context["action"] == "/qube/questions/create_invoice/%d" % record_id
    assert 'name="csrf_token"' in html and 'value="csrf-123"' in html
    assert 'action="/qube/questions/create_invoice/%d"' % record_id in html
    assert "Riverbend Electric isn&#39;t in QuickBooks yet." in html


def test_question_html_and_the_apps_own_template(app):
    record_id = asking(app)
    own = make_app(template_folder=os.path.join(HERE, "kit_templates", "override"))
    with own.test_request_context("/"):
        html = qube_flask.question_html("create_invoice", Session().get(Invoice, record_id))
    assert 'class="app-own-question"' in html


def test_question_html_takes_a_render_function(app):
    record_id = asking(app)
    kit.configure(render_question=lambda context: "<b>%s</b>" % context["question"]["id"])
    with app["app"].test_request_context("/"):
        html = qube_flask.question_html("create_invoice", Session().get(Invoice, record_id))
    assert html == "<b>ask_about_add</b>"
