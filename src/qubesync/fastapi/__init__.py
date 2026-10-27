"""QuBe Sync's integration kit for FastAPI: three routers, since they go behind different
things (the webhooks behind nothing, onboarding and the questions behind your sign-in), and
the question and run status templates. The kit's tables are the SQLAlchemy models in
qubesync.kit.sqlalchemy, through your session (the db_session setting: a scoped_session).

    pip install "qubesync[fastapi]>=0.4.0"

    # main.py, where your FastAPI app is made
    import quickbooks_desktop.config  # its qubesync.kit.configure(..., db_session=Session)
    import qubesync.fastapi

    qube = qubesync.fastapi.routers()
    app.include_router(qube.webhooks)
    app.include_router(qube.connections, dependencies=[Depends(signed_in)])
    app.include_router(qube.questions, dependencies=[Depends(signed_in)])

or qubesync.fastapi.router(dependencies=[Depends(signed_in)]), all three in one, with the
dependencies on all but the webhooks. Your sign-in dependency puts the user where
current_account reads it (request.state.user, say). FastAPI has no CSRF protection of its own:
the POSTs from the templates' forms carry a csrf_token you put in their context, for yours.

The routes, relative to where they're included (each named, for request.url_for):

    POST /quickbooks/connections                   qubesync_connections
    POST /quickbooks/connections/{id}/onboarding   qubesync_connection_onboarding
    DELETE /quickbooks/connections/{id}            qubesync_connection (disconnect)
    POST /quickbooks/connections/{id}/disconnect   qubesync_connection_disconnect (a form's)
    POST /webhooks/qube/runs/{id}                  qubesync_run_webhook (no sign-in)
    POST /webhooks/qube/connections/{id}           qubesync_connection_webhook (no sign-in)
    POST /webhooks/qube/requests/{id}              qubesync_request_webhook (no sign-in)
    POST /qube/questions/runs/{id}                 qubesync_question (reads a form: python-multipart)
    GET  /qube/questions/runs/{id}/search          qubesync_question_search
    POST /qube/runs/{id}/retry_start               qubesync_retry_start
    POST /qube/runs/{id}/redeliver                 qubesync_redeliver
    GET  /qube/assets/{name}                       qubesync_asset (question.js, qubesync.css; on the webhooks router: no sign-in)
    GET  /qube/storyboard[/{screen}]               qubesync_storyboard[_screen] (the storyboard setting)
    GET  /qube/storyboard/{screen}/search          qubesync_storyboard_search
    POST /qube/storyboard/{screen}/answer          qubesync_storyboard_answer (sends nothing)

A message from a question or run route (why it didn't go through) goes back to the page in
request.session with Starlette's SessionMiddleware, else in a short-lived qubesync_error cookie
that the template's script clears once it's shown.

The database and the calls to QuBe Sync block, so they run on a worker thread, which removes
its scoped session when the route is done.
"""
try:
    import fastapi as _fastapi  # noqa: F401
except ImportError as error:  # pragma: no cover
    raise ImportError('qubesync.fastapi needs FastAPI: pip install "qubesync[fastapi]"') from error

import os
from collections import namedtuple
from typing import Any, Dict, Optional, Sequence
from urllib.parse import quote, unquote, urlparse

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse, Response
from markupsafe import Markup, escape
from starlette.concurrency import run_in_threadpool

from .. import kit

__all__ = [
    "redirect_back",
    "sync_status",
    "Operation",
    "ConnectionEvents",
    "Routers",
    "routers",
    "router",
    "question_context",
    "run_status_context",
    "question_html",
    "run_status_html",
    "error_html",
    "assets_html",
    "add_templates",
    "take_error",
    "TEMPLATES",
]

Operation = kit.Operation
ConnectionEvents = kit.ConnectionEvents

# The packaged templates (qubesync/question.html, qubesync/run_status.html), shared with
# qubesync.flask.
TEMPLATES = os.path.join(os.path.dirname(os.path.abspath(kit.__file__)), "templates")

Routers = namedtuple("Routers", ["webhooks", "connections", "questions"])


# How long the error cookie lasts if no page shows it.
ERROR_COOKIE_SECONDS = 60


def _response(reply, request=None):
    # type: (kit.Reply, Optional[Request]) -> Response
    if reply.location is not None:
        redirect = RedirectResponse(reply.location, status_code=reply.status)
        if reply.error is not None:
            _keep_error(request, redirect, reply.error)
        return redirect
    if reply.json is not None:
        return JSONResponse(reply.json, status_code=reply.status)
    if reply.text is not None:
        return PlainTextResponse(reply.text, status_code=reply.status)
    return Response(status_code=reply.status)


async def _raw_body(request):
    # type: (Request) -> Optional[bytes]
    """The body as received, whatever its content type, or None once it's over
    MAX_WEBHOOK_BODY (5 MB), which the route answers 413 without reading the rest."""
    try:
        length = int(request.headers.get("content-length") or 0)
    except ValueError:
        length = 0
    if length > kit.MAX_WEBHOOK_BODY:
        return None
    chunks = []
    size = 0
    async for chunk in request.stream():
        size += len(chunk)
        if size > kit.MAX_WEBHOOK_BODY:
            return None
        chunks.append(chunk)
    return b"".join(chunks)


def _has_session(request):
    # type: (Optional[Request]) -> bool
    return request is not None and "session" in request.scope


def _keep_error(request, response, message):
    # type: (Optional[Request], Response, str) -> None
    if _has_session(request):
        request.session[kit.ERROR_KEY] = message
        return
    response.set_cookie(kit.ERROR_KEY, quote(message), max_age=ERROR_COOKIE_SECONDS, path="/", samesite="lax")


def redirect_back(request, error=None):
    # type: (Request, Optional[str]) -> Response
    """Back to the page the request came from (303), with error, if any, for the templates to
    show once: for your own routes, such as a start button's."""
    referer = request.headers.get("referer")
    if error is None:
        return _response(kit.Reply(303, location=kit.back(referer, _host(request))), request)
    return _response(kit.back_with_error(error, 422, referer, _host(request)), request)


def sync_status(record, operation, connection=None):
    # type: (Any, str, Any) -> kit.SyncStatus
    """record's SyncStatus for operation (on connection, else on its latest run's): the
    qube_sync_status Jinja global."""
    if connection is not None:
        return kit.SyncStatus.of(connection, record, operation)
    return kit.SyncStatus.latest(record, operation)


def take_error(request):
    # type: (Request) -> Dict[str, Any]
    """The message a question or run route left (session or cookie), as the templates' error and
    clear_cookie, once per page."""
    if getattr(request.state, "qubesync_error_taken", False):
        return {"error": None}
    request.state.qubesync_error_taken = True
    if _has_session(request):
        return {"error": request.session.pop(kit.ERROR_KEY, None)}
    message = request.cookies.get(kit.ERROR_KEY)
    if not message:
        return {"error": None}
    return {"error": unquote(message), "clear_cookie": kit.ERROR_KEY}


def _production(request):
    # type: (Request) -> bool
    return not getattr(request.app, "debug", False)


def _host(request):
    # type: (Request) -> str
    return request.url.netloc


def _unit(fn, *args):
    # type: (Any, *Any) -> kit.Reply
    """fn on this worker thread, then the thread's scoped session removed: the pool's threads
    are reused, and a session left open would keep its transaction (and its snapshot) for the
    next request on the thread."""
    try:
        return fn(*args)
    finally:
        _cleanup()


def _cleanup():
    # type: () -> None
    from ..kit._store import current_store

    try:
        current_store().cleanup()
    except kit.NotConfigured:
        pass


def routers():
    # type: () -> Routers
    """The kit's routers: webhooks, connections and questions. Include connections and
    questions behind your sign-in (dependencies=[Depends(...)]); current_account and
    authorize_question (qubesync.kit.configure) decide the rest. The enqueue setting's
    default is the kit's worker thread, with retries."""
    webhooks = APIRouter()

    @webhooks.post("/webhooks/qube/runs/{id}", name="qubesync_run_webhook")
    async def run_webhook(id: str, request: Request) -> Response:
        body = await _raw_body(request)  # the raw bytes the signature is over
        signature = request.headers.get(kit.SIGNATURE_HEADER)
        reply = await run_in_threadpool(_unit, kit.receive, "run", id, body, signature, None, request.url.path)
        return _response(reply)

    @webhooks.post("/webhooks/qube/connections/{id}", name="qubesync_connection_webhook")
    async def connection_webhook(id: str, request: Request) -> Response:
        body = await _raw_body(request)
        signature = request.headers.get(kit.SIGNATURE_HEADER)
        reply = await run_in_threadpool(_unit, kit.receive, "connection", id, body, signature, None, request.url.path)
        return _response(reply)

    @webhooks.post("/webhooks/qube/requests/{id}", name="qubesync_request_webhook")
    async def request_webhook(id: str, request: Request) -> Response:
        body = await _raw_body(request)
        signature = request.headers.get(kit.SIGNATURE_HEADER)
        reply = await run_in_threadpool(_unit, kit.receive, "request", id, body, signature, None, request.url.path)
        return _response(reply)

    # The behaviour script and the stylesheet, behind nothing as the webhooks are: two files.
    @webhooks.get("/qube/assets/{name}", name="qubesync_asset")
    def asset(name: str) -> Response:
        found = kit.asset(name)
        if found is None:
            return Response(status_code=404)
        return FileResponse(found[0], media_type=found[1], headers={"Cache-Control": "public, max-age=3600"})

    connections = APIRouter()

    @connections.post("/quickbooks/connections", name="qubesync_connections")
    async def connect(request: Request) -> Response:
        form = await request.form()
        referer = request.headers.get("referer")
        reply = await run_in_threadpool(_unit, kit.connect, request, form, referer, _host(request), _production(request))
        return _response(reply)

    @connections.post("/quickbooks/connections/{id}/onboarding", name="qubesync_connection_onboarding")
    def onboarding(id: str, request: Request) -> Response:
        return _response(_unit(kit.onboarding, request, id))

    @connections.delete("/quickbooks/connections/{id}", name="qubesync_connection")
    def disconnect(id: str, request: Request) -> Response:
        return _response(_unit(kit.disconnect, request, id, request.headers.get("referer"), _host(request)), request)

    # The same, for an HTML form, which can't send DELETE.
    @connections.post("/quickbooks/connections/{id}/disconnect", name="qubesync_connection_disconnect")
    def disconnect_form(id: str, request: Request) -> Response:
        return _response(_unit(kit.disconnect, request, id, request.headers.get("referer"), _host(request)), request)

    questions = APIRouter()

    @questions.post("/qube/questions/runs/{id}", name="qubesync_question")
    async def answer(id: str, request: Request) -> Response:
        form = await request.form()
        referer = request.headers.get("referer")
        reply = await run_in_threadpool(_unit, kit.answer, request, id, form, referer, _host(request))
        return _response(reply, request)

    @questions.get("/qube/questions/runs/{id}/search", name="qubesync_question_search")
    def search(id: str, request: Request) -> Response:
        return _response(_unit(kit.search, request, id, request.query_params))

    @questions.post("/qube/runs/{id}/retry_start", name="qubesync_retry_start")
    def retry_start(id: str, request: Request) -> Response:
        return _response(_unit(kit.retry_start, request, id, request.headers.get("referer"), _host(request)), request)

    @questions.post("/qube/runs/{id}/redeliver", name="qubesync_redeliver")
    def redeliver(id: str, request: Request) -> Response:
        return _response(_unit(kit.redeliver, request, id, request.headers.get("referer"), _host(request)), request)

    @questions.get("/qube/storyboard", name="qubesync_storyboard")
    def storyboard(request: Request) -> Response:
        return _storyboard_page(request, None)

    @questions.get("/qube/storyboard/{screen}", name="qubesync_storyboard_screen")
    def storyboard_screen(screen: str, request: Request) -> Response:
        return _storyboard_page(request, screen)

    @questions.get("/qube/storyboard/{screen}/search", name="qubesync_storyboard_search")
    def storyboard_search(screen: str, request: Request) -> Response:
        if not _storyboard_on(request):
            return _response(kit.Reply(404, json=[]))
        return _response(kit.storyboard_search(screen, request.query_params))

    @questions.post("/qube/storyboard/{screen}/answer", name="qubesync_storyboard_answer")
    def storyboard_answer(screen: str, request: Request) -> Response:
        if not _storyboard_on(request):
            return Response(status_code=404)
        return _response(kit.storyboard_answer(screen, _storyboard_url(request)("screen", screen)))

    return Routers(webhooks, connections, questions)


def _storyboard_on(request):
    # type: (Request) -> bool
    return kit.storyboard_on(bool(getattr(request.app, "debug", False)))


def _storyboard_url(request):
    # type: (Request) -> Any
    def url_for(name, key):
        # type: (str, Optional[str]) -> str
        if name == "index":
            return urlparse(str(request.url_for("qubesync_storyboard"))).path
        return urlparse(str(request.url_for("qubesync_storyboard_%s" % name, screen=str(key)))).path

    return url_for


def _storyboard_page(request, key):
    # type: (Request, Optional[str]) -> Response
    """Every screen (or one) from sample data, rendered with the templates add_templates was
    last given (so your layout and pieces apply), in the storyboard_layout setting's template."""
    if not _storyboard_on(request):
        return Response(status_code=404)
    page = kit.storyboard_page(key, _storyboard_url(request), notice="sent" in request.query_params)
    if page is None:
        return Response(status_code=404)
    values = {
        "storyboard": page,
        "layout": kit.settings().storyboard_layout,
        "assets": assets_html(request, stylesheet=True),
        "request": request,
    }
    templates = _templates[-1] if _templates else None
    return HTMLResponse(_render(templates, "qubesync/storyboard.html", values))


def router(dependencies=None, prefix=""):
    # type: (Optional[Sequence[Any]], str) -> APIRouter
    """All three routers in one, with dependencies (your sign-in) on all but the webhooks."""
    parts = routers()
    combined = APIRouter(prefix=prefix)
    combined.include_router(parts.webhooks)
    combined.include_router(parts.connections, dependencies=list(dependencies or []))
    combined.include_router(parts.questions, dependencies=list(dependencies or []))
    return combined


def _path(request, name, run):
    # type: (Request, str, Any) -> str
    return urlparse(str(request.url_for(name, id=str(run.id)))).path


def question_context(request, record, operation):
    # type: (Request, Any, str) -> Dict[str, Any]
    """What qubesync/question.html reads, for the record's page: the open question of record's
    latest run of operation (a slug), if it's asking, where it's answered, and the message a
    route left (take_error)."""
    shown = take_error(request)
    values = kit.question_context(
        record, operation, lambda run: _path(request, "qubesync_question", run), error=shown["error"]
    )
    values["clear_cookie"] = shown.get("clear_cookie")
    return values


def run_status_context(request, record, operation, connection=None):
    # type: (Request, Any, str, Any) -> Dict[str, Any]
    """What qubesync/run_status.html reads: record's sync status for operation (on connection,
    else on its latest run's), with the retry and redelivery routes when they apply, and the
    message a route left (take_error)."""
    shown = take_error(request)
    values = kit.run_status_context(
        record,
        operation,
        lambda run: _path(request, "qubesync_retry_start", run),
        lambda run: _path(request, "qubesync_redeliver", run),
        connection=connection,
        error=shown["error"],
    )
    values["clear_cookie"] = shown.get("clear_cookie")
    return values


def add_templates(templates):
    # type: (Any) -> Any
    """Lets a Jinja2Templates (or a jinja2 Environment) find qubesync/question.html and
    qubesync/run_status.html, after its own directories, so yours come first, and registers
    qube_question(request, record, operation), qube_run_status(request, record, operation),
    qube_sync_status(record, operation), qube_error(request) and qube_assets(request,
    stylesheet=False) as its globals (with qube_classes and qube_t, which the pieces call). The
    storyboard renders with the templates it was last given."""
    from jinja2 import ChoiceLoader, FileSystemLoader

    env = getattr(templates, "env", templates)
    ours = FileSystemLoader(TEMPLATES)
    env.loader = ChoiceLoader([env.loader, ours]) if env.loader is not None else ours
    _templates[:] = [env]
    env.globals.update(
        qube_assets=assets_html,
        qube_classes=kit.qube_classes,
        qube_t=kit.t,
        qube_question=lambda request, record, operation, **context: question_html(
            request, record, operation, templates=env, **context
        ),
        qube_run_status=lambda request, record, operation, connection=None, **context: run_status_html(
            request, record, operation, connection=connection, templates=env, **context
        ),
        qube_sync_status=sync_status,
        qube_error=lambda request, **context: error_html(request, templates=env, **context),
    )
    return templates


_environment = []  # type: list
_templates = []  # type: list


def _own_environment():
    # type: () -> Any
    if not _environment:
        from jinja2 import Environment, FileSystemLoader, select_autoescape

        env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(default=True))
        env.globals.update(qube_classes=kit.qube_classes, qube_t=kit.t, qube_assets=assets_html)
        _environment.append(env)
    return _environment[0]


def _render(templates, name, values):
    # type: (Any, str, Dict[str, Any]) -> Markup
    env = getattr(templates, "env", templates) if templates is not None else _own_environment()
    values = dict({"qube_classes": kit.qube_classes, "qube_t": kit.t}, **values)
    return Markup(env.get_template(name).render(**values))


def question_html(request, record, operation, templates=None, **context):
    # type: (Request, Any, str, Any, **Any) -> Markup
    """qubesync/question.html rendered for record, from templates (your Jinja2Templates, after
    add_templates) or the packaged one. context adds to it (csrf_token, csp_nonce)."""
    values = dict(question_context(request, record, operation), request=request, **context)
    return _render(templates, "qubesync/question.html", values)


def run_status_html(request, record, operation, connection=None, templates=None, **context):
    # type: (Request, Any, str, Any, Any, **Any) -> Markup
    """qubesync/run_status.html rendered for record. context adds to it (csrf_token)."""
    values = dict(run_status_context(request, record, operation, connection), request=request, **context)
    return _render(templates, "qubesync/run_status.html", values)


def error_html(request, templates=None, **context):
    # type: (Request, Any, **Any) -> Markup
    """qubesync/_error.html with the message a route left (a disconnect refused, say), once:
    for a page without the run status or question."""
    shown = take_error(request)
    values = dict(shown, message=shown["error"], request=request, **context)
    return _render(templates, "qubesync/error.html", values)


def assets_html(request, stylesheet=False, csp_nonce=None):
    # type: (Request, bool, Optional[str]) -> Markup
    """The behaviour script's tag (deferred, with csp_nonce when you pass one) and, with
    stylesheet=True, the opt-in stylesheet's: the qube_assets global, for your layout."""

    def href(name):
        # type: (str) -> str
        return urlparse(str(request.url_for("qubesync_asset", name=name))).path

    tags = []
    if stylesheet:
        tags.append('<link rel="stylesheet" href="%s" media="all">' % escape(href("qubesync.css")))
    nonce = ' nonce="%s"' % escape(csp_nonce) if csp_nonce else ""
    tags.append('<script src="%s" defer%s></script>' % (escape(href("question.js")), nonce))
    return Markup("\n".join(tags))
