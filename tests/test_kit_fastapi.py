"""What's FastAPI's own in qubesync.fastapi: the routers apart and combined (the sign-in on all
but the webhooks), add_templates and its globals, the packaged templates without one, and the
scoped session removed after each route. The routes' status codes are in test_kit_routes.py,
on all three adapters."""
import os

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
pytest.importorskip("sqlalchemy")

from fastapi import Depends, FastAPI, HTTPException, Request  # noqa: E402
from fastapi.templating import Jinja2Templates  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import qubesync.fastapi as qube_fastapi  # noqa: E402
import qubesync.kit as kit  # noqa: E402
from kit_support import DECISIONS, QUESTION, kit_reset, run_body, sign  # noqa: E402,F401
from kit_worlds import make_driver  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def app(kit_reset):
    return make_driver("fastapi")


@pytest.fixture
def world(app):
    return app[1]


@pytest.fixture
def account(world):
    return world.account()


def signed_in(request: Request) -> None:
    if not request.headers.get("x-user"):
        raise HTTPException(status_code=401)
    request.state.user = request.headers["x-user"]


def test_the_routers_apart_put_the_sign_in_where_the_app_says(world, account, app):
    run = world.run(world.invoice(account), world.connection(account))
    handed = []
    kit.configure(enqueue=lambda delivery: handed.append(delivery))
    api = FastAPI()
    qube = qube_fastapi.routers()
    api.include_router(qube.webhooks)
    api.include_router(qube.connections, dependencies=[Depends(signed_in)])
    api.include_router(qube.questions, dependencies=[Depends(signed_in)])
    client = TestClient(api)
    body = run_body("workflow_run.completed", run)

    assert client.post("/webhooks/qube/runs/%s" % run.id, content=body, headers={"X-QUBE-Signature": sign(body)}).status_code == 200
    assert client.post("/quickbooks/connections", follow_redirects=False).status_code == 401
    assert client.post("/qube/runs/%s/retry_start" % run.id, follow_redirects=False).status_code == 401
    assert len(handed) == 1


def test_the_combined_router_names_every_route_under_its_prefix(app):
    api = FastAPI()
    api.include_router(qube_fastapi.router(prefix="/qube-sync"))

    assert api.url_path_for("qubesync_connections") == "/qube-sync/quickbooks/connections"
    for name, path in (
        ("qubesync_connection_onboarding", "/qube-sync/quickbooks/connections/7/onboarding"),
        ("qubesync_run_webhook", "/qube-sync/webhooks/qube/runs/7"),
        ("qubesync_connection_webhook", "/qube-sync/webhooks/qube/connections/7"),
        ("qubesync_question", "/qube-sync/qube/questions/runs/7"),
        ("qubesync_question_search", "/qube-sync/qube/questions/runs/7/search"),
        ("qubesync_retry_start", "/qube-sync/qube/runs/7/retry_start"),
        ("qubesync_redeliver", "/qube-sync/qube/runs/7/redeliver"),
    ):
        assert api.url_path_for(name, id="7") == path


def test_add_templates_registers_the_globals_and_lets_the_apps_template_win(app, world, account):
    http = app[0]
    invoice = world.invoice(account)
    run = world.run(invoice, world.connection(account), question=QUESTION, links={"decisions": DECISIONS})
    request = Request({"type": "http", "app": http.app, "router": http.app.router, "headers": [], "path": "/", "query_string": b""})

    templates = qube_fastapi.add_templates(Jinja2Templates(directory=os.path.join(HERE, "kit_templates", "empty")))
    shown = templates.env.from_string("{{ qube_run_status(request, invoice, 'create_invoice') }}{{ qube_question(request, invoice, 'create_invoice') }}").render(
        request=request, invoice=invoice
    )
    assert '<p class="qube-run-summary">Running</p>' in shown
    assert 'action="/qube/questions/runs/%s"' % run.id in shown

    own = qube_fastapi.add_templates(Jinja2Templates(directory=os.path.join(HERE, "kit_templates", "override")))
    assert qube_fastapi.question_html(request, invoice, "create_invoice", templates=own).strip() == (
        '<div class="app-own-question">Which customer?</div>'
    )


def test_question_html_without_templates_uses_the_packaged_one_with_a_csrf_token(app, world, account):
    http = app[0]
    invoice = world.invoice(account)
    world.run(invoice, world.connection(account), question=QUESTION, links={"decisions": DECISIONS})
    request = Request({"type": "http", "app": http.app, "router": http.app.router, "headers": [], "path": "/", "query_string": b""})

    shown = qube_fastapi.question_html(request, invoice, "create_invoice", csrf_token="tok-123")

    assert shown.count('value="tok-123"') == 2


def test_each_route_removes_its_threads_session(app, world, account, monkeypatch):
    http = app[0]
    removed = []
    session = world.Session
    remove = session.remove
    monkeypatch.setattr(session, "remove", lambda: (removed.append(True), remove()))

    response = http.post("/quickbooks/connections/0/onboarding", account=account)

    assert response.status == 404
    assert removed


def test_simulated_connect_follows_app_debug_unless_production_is_set(app, world, account):
    http = app[0]
    assert http.post("/quickbooks/connections", {"simulated": "1"}, account=account).status == 404

    http.app.debug = True
    try:
        assert http.post("/quickbooks/connections", {"simulated": "1"}, account=account).status == 303
        kit.configure(production=True)
        assert http.post("/quickbooks/connections", {"simulated": "1"}, account=account).status == 404
    finally:
        http.app.debug = False


def test_with_session_middleware_the_message_goes_in_the_session(world, account, app):
    from starlette.middleware.sessions import SessionMiddleware

    invoice = world.invoice(account)
    run = world.run(invoice, world.connection(account), question=QUESTION, links={"decisions": DECISIONS})
    api = FastAPI()
    api.add_middleware(SessionMiddleware, secret_key="kit-tests")
    api.include_router(qube_fastapi.router(dependencies=[Depends(signed_in)]))

    @api.get("/invoices/{id}")
    def page(id: int, request: Request):
        from fastapi.responses import HTMLResponse

        try:
            return HTMLResponse(qube_fastapi.run_status_html(request, world.find(world.Invoice, id), "create_invoice"))
        finally:
            world.Session.remove()

    client = TestClient(api)
    headers = {"x-user": account.user, "referer": "/invoices/%s" % invoice.id}
    response = client.post("/qube/questions/runs/%s" % run.id, data={"choice": "nope"}, headers=headers, follow_redirects=False)

    assert response.status_code == 303
    assert kit.ERROR_KEY not in response.cookies
    assert client.get("/invoices/%s" % invoice.id).text.count("qube-error") == 1
    assert "qube-error" not in client.get("/invoices/%s" % invoice.id).text


def test_without_a_session_the_message_is_a_short_cookie_the_page_clears(app, world, account):
    http = app[0]
    invoice = world.invoice(account)
    run = world.run(invoice, world.connection(account), question=QUESTION, links={"decisions": DECISIONS})

    response = http.client.post(
        "/qube/questions/runs/%s" % run.id,
        data={"choice": "nope"},
        headers={"x-user": account.user, "referer": "/invoices/%s" % invoice.id},
        follow_redirects=False,
    )

    cookie = response.headers["set-cookie"]
    assert cookie.startswith("%s=" % kit.ERROR_KEY) and "Max-Age=60" in cookie and "Path=/" in cookie
    shown = http.get("/invoices/%s" % invoice.id, account=account).text
    assert shown.count('<p class="qube-error">This question has changed; reload.</p>') == 1
    assert 'document.cookie = "%s=; Max-Age=0; Path=/; SameSite=Lax"' % kit.ERROR_KEY in shown


def test_redirect_back_goes_back_with_the_message_for_the_page():
    made = FastAPI()

    @made.post("/start")
    def start(request: Request):
        return qube_fastapi.redirect_back(request, "Connect first.")

    @made.post("/fine")
    def fine(request: Request):
        return qube_fastapi.redirect_back(request)

    http = TestClient(made)
    response = http.post("/start", headers={"Referer": "/invoices/1"}, follow_redirects=False)
    assert (response.status_code, response.headers["location"]) == (303, "/invoices/1")
    assert "qubesync_error=" in response.headers["set-cookie"]
    response = http.post("/fine", headers={"Referer": "https://elsewhere.example/x"}, follow_redirects=False)
    assert (response.status_code, response.headers["location"]) == (303, "/")
    assert "set-cookie" not in response.headers
