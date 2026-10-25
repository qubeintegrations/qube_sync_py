"""qubesync.fastapi: the routers through FastAPI's TestClient, background tasks as the default
queue, and the question template."""
import logging
import os

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
pytest.importorskip("sqlalchemy")

from fastapi import Depends, FastAPI, HTTPException, Request  # noqa: E402
from fastapi.templating import Jinja2Templates  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import kit_sqla  # noqa: E402
import qubesync.fastapi as qube_fastapi  # noqa: E402
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
    kit_reset,
    run_event,
    sign,
)

HERE = os.path.dirname(os.path.abspath(__file__))
CreateInvoice, Connection = kit_sqla.make_classes(qube_fastapi.Operation, qube_fastapi.ConnectionEvents)


def signed_in(request: Request) -> None:
    """Stands in for the app's sign-in dependency: it puts the user on request.state."""
    user = request.headers.get("x-user")
    if not user:
        raise HTTPException(status_code=401)
    request.state.user = user


def current_account(request):
    return Session().query(Account).filter_by(user=request.state.user).first()


def mine(request, record, operation):
    return Session().get(Account, record.account_id).user == request.state.user


def make_app(combined=False):
    app = FastAPI()
    if combined:
        app.include_router(qube_fastapi.router(dependencies=[Depends(signed_in)]))
    else:
        qube = qube_fastapi.routers()
        app.include_router(qube.webhooks)
        app.include_router(qube.connect, dependencies=[Depends(signed_in)])
        app.include_router(qube.questions, dependencies=[Depends(signed_in)])

    @app.middleware("http")
    async def remove_session(request, call_next):
        try:
            return await call_next(request)
        finally:
            Session.remove()

    return app


@pytest.fixture(autouse=True)
def app(kit_reset):
    kit_sqla.reset()
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
    fastapi_app = make_app()
    http = TestClient(fastapi_app, follow_redirects=False) if _takes_follow_redirects() else TestClient(fastapi_app)
    return {"client": fake, "queued": queued, "account_id": account.id, "app": fastapi_app, "http": http}


def _takes_follow_redirects():
    import inspect

    return "follow_redirects" in inspect.signature(TestClient.__init__).parameters


def post(http, url, **kwargs):
    if not _takes_follow_redirects():
        kwargs["allow_redirects"] = False
    return http.post(url, **kwargs)


def invoice(account_id, **fields):
    defaults = {"qube_reference": "ref-1", "qube_revision": 0}
    defaults.update(fields)
    return kit_sqla.add(Invoice(account_id=account_id, **defaults)).id


def asking(app):
    return invoice(app["account_id"], qube_question=PROMPT, qube_links={"decisions": DECISIONS, "search": SEARCH})


def fetch(model, id):
    Session.remove()
    return Session().get(model, id)


def post_webhook(http, path, body, header=None, content_type="application/json"):
    return http.post(path, content=body, headers={"X-QUBE-Signature": header or sign(body), "Content-Type": content_type})


# -- Webhooks --------------------------------------------------------------------------------


def test_a_signed_webhook_is_enqueued_without_sign_in(app):
    body = run_event()
    response = post_webhook(app["http"], "/webhooks/qube/create_invoice/42", body, content_type="text/plain")
    assert response.status_code == 200
    assert app["queued"] == [("create_invoice", "42", body)]


def test_a_bad_signature_is_401_and_only_its_reason_is_logged(app, caplog):
    body = run_event()
    with caplog.at_level(logging.WARNING, logger="qubesync.kit"):
        response = post_webhook(app["http"], "/webhooks/qube/create_invoice/42", body, header="nonsense")
    assert response.status_code == 401
    assert "QuBe Sync: refused a webhook: malformed" in caplog.messages
    assert app["queued"] == []


def test_an_unknown_slug_is_404_and_a_huge_body_413(app):
    body = run_event()
    assert post_webhook(app["http"], "/webhooks/qube/nope/42", body).status_code == 404
    huge = run_event(pad="a" * (5 * 1024 * 1024))
    assert post_webhook(app["http"], "/webhooks/qube/create_invoice/42", huge).status_code == 413


def test_the_default_queue_is_a_background_task(app, caplog):
    kit.configure(enqueue=None)
    record_id = invoice(app["account_id"])
    body = run_event("workflow_run.completed", revision=1, outcome="added")
    with caplog.at_level(logging.WARNING, logger="qubesync.kit"):
        assert post_webhook(app["http"], "/webhooks/qube/create_invoice/%d" % record_id, body).status_code == 200
        # A job that fails is logged, and the delivery still had its 200.
        assert post_webhook(app["http"], "/webhooks/qube/create_invoice/999", body).status_code == 200
    record = fetch(Invoice, record_id)
    assert (record.status, record.qube_revision) == ("sent", 1)
    assert "a webhook job failed" in caplog.text


def test_connection_events_save_through_the_session(app):
    account = fetch(Account, app["account_id"])
    account.qube_connection_id = "c1"
    Session().commit()
    kit.run("connection", str(app["account_id"]), connection_event("connection.connected", revision=1))
    account = fetch(Account, app["account_id"])
    assert (account.connected, account.qube_connection_revision) == (True, 1)


# -- Onboarding ------------------------------------------------------------------------------


def test_connect_is_behind_the_sign_in_dependency(app):
    assert post(app["http"], "/quickbooks/connect").status_code == 401
    assert app["client"].calls == []


def test_connect_creates_then_reuses_the_connection(app):
    http = app["http"]
    response = post(http, "/quickbooks/connect", headers={"x-user": "pat"})
    assert (response.status_code, response.headers["location"]) == (303, "https://qubesync.com/onboard/new")
    account = fetch(Account, app["account_id"])
    assert (account.qube_connection_id, account.qube_connection_revision) == ("c-new", None)
    response = post(http, "/quickbooks/connect", headers={"x-user": "pat"})
    assert response.headers["location"] == "https://qubesync.com/onboard/again"
    assert app["client"].names() == ["create_connection", "update_connection", "regenerate_onboarding"]


def test_connect_without_an_account_is_401(app):
    response = post(app["http"], "/quickbooks/connect", headers={"x-user": "nobody"})
    assert response.status_code == 401


# -- Questions -------------------------------------------------------------------------------


def test_answers_are_refused_while_authorize_question_isnt_set(app):
    record_id = asking(app)
    url = "/qube/questions/create_invoice/%d" % record_id
    assert post(app["http"], url, data={"choice": "skip"}, headers={"x-user": "pat"}).status_code == 403
    assert app["http"].get(url + "/search?q=river&field=customer", headers={"x-user": "pat"}).status_code == 403


def test_an_answer_posts_typed_data_and_goes_back(app):
    kit.configure(authorize_question=mine)
    record_id = asking(app)
    response = post(
        app["http"],
        "/qube/questions/create_invoice/%d" % record_id,
        data={"choice": "use", "data[customer]": "80000001-1", "data[amount]": "7", "data[notify]": "true"},
        headers={"x-user": "pat", "referer": "http://testserver/invoices/%d" % record_id},
    )
    assert (response.status_code, response.headers["location"]) == (303, "http://testserver/invoices/%d" % record_id)
    assert app["client"].calls[0][2] == {"choice": "use", "data": {"customer": "80000001-1", "amount": 7, "notify": True}}
    assert fetch(Invoice, record_id).qube_question is None


def test_another_users_answer_is_404(app):
    kit.configure(authorize_question=mine)
    kit_sqla.add(Account(user="sam"))
    record_id = asking(app)
    response = post(app["http"], "/qube/questions/create_invoice/%d" % record_id, data={"choice": "skip"}, headers={"x-user": "sam"})
    assert response.status_code == 404


def test_a_stale_answer_forgets_the_question_and_a_refused_one_is_422(app):
    kit.configure(authorize_question=mine)
    record_id = asking(app)
    url = "/qube/questions/create_invoice/%d" % record_id
    app["client"].raises["answer"] = api_error(422, {"detail": "amount is too big"})
    response = post(app["http"], url, data={"choice": "skip"}, headers={"x-user": "pat"})
    assert response.status_code == 422 and "amount is too big" in response.text
    assert fetch(Invoice, record_id).qube_question == PROMPT
    app["client"].raises["answer"] = api_error(400, {"code": "not_awaiting_input"})
    response = post(app["http"], url, data={"choice": "skip"}, headers={"x-user": "pat"})
    assert (response.status_code, response.text) == (409, kit.CHANGED)
    assert fetch(Invoice, record_id).qube_question is None


def test_search_is_bounded_and_answers_json(app):
    kit.configure(authorize_question=mine)
    record_id = asking(app)
    url = "/qube/questions/create_invoice/%d/search" % record_id
    assert app["http"].get(url + "?q=r&field=customer", headers={"x-user": "pat"}).json() == []
    response = app["http"].get(url + "?q=river&field=customer", headers={"x-user": "pat"})
    assert response.status_code == 200 and response.json()[0]["label"] == "Riverbend"


def test_the_combined_router_signs_in_only_connect_and_questions(app):
    http = TestClient(make_app(combined=True))
    body = run_event()
    assert post_webhook(http, "/webhooks/qube/create_invoice/1", body).status_code == 200
    assert post(http, "/quickbooks/connect").status_code == 401


# -- The question template -------------------------------------------------------------------


def _request(app, path="/invoices/1"):
    scope = {"type": "http", "method": "GET", "path": path, "headers": [], "query_string": b"", "app": app["app"],
             "router": app["app"].router, "scheme": "http", "server": ("testserver", 80), "root_path": ""}
    return Request(scope)


def test_question_html_renders_the_packaged_template(app):
    record_id = asking(app)
    record = Session().get(Invoice, record_id)
    html = qube_fastapi.question_html(_request(app), "create_invoice", record, csrf_token="csrf-9", csp_nonce="n1")
    assert 'action="/qube/questions/create_invoice/%d"' % record_id in html
    assert 'value="csrf-9"' in html and 'nonce="n1"' in html
    assert 'class="qube-choice-button"' in html


def test_add_templates_lets_the_apps_own_template_win(app):
    record_id = asking(app)
    record = Session().get(Invoice, record_id)
    own = qube_fastapi.add_templates(Jinja2Templates(directory=os.path.join(HERE, "kit_templates", "override")))
    html = qube_fastapi.question_html(_request(app), "create_invoice", record, templates=own)
    assert 'class="app-own-question"' in html
    packaged = qube_fastapi.add_templates(Jinja2Templates(directory=os.path.join(HERE, "kit_templates", "empty")))
    html = packaged.env.from_string('{% include "qubesync/question.html" %}').render(
        **qube_fastapi.question_context(_request(app), "create_invoice", record)
    )
    assert 'class="qube-question"' in html
