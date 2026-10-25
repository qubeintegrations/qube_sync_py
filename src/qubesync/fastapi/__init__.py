"""QuBe Sync's integration kit for FastAPI: three routers, since they go behind different
things (the webhooks behind nothing, onboarding and the questions behind your sign-in), the
question template, and Operation and ConnectionEvents bases that save through SQLAlchemy.

    pip install "qubesync[fastapi]>=0.4.0"

    # main.py, where your FastAPI app is made
    import quickbooks_desktop.config  # its qubesync.kit.configure(...)
    import qubesync.fastapi

    qube = qubesync.fastapi.routers()
    app.include_router(qube.webhooks)
    app.include_router(qube.connect, dependencies=[Depends(signed_in)])
    app.include_router(qube.questions, dependencies=[Depends(signed_in)])

or qubesync.fastapi.router(dependencies=[Depends(signed_in)]), all three in one, with the
dependencies on connect and the questions only. Your sign-in dependency puts the user where
current_account and authorize_question read it (request.state.user, say).

The routes, relative to where they're included (each named, for request.url_for):

    POST /quickbooks/connect                        qubesync_connect
    POST /webhooks/qube/{operation}/{record_id}     qubesync_webhook (no sign-in, no CSRF)
    POST /qube/questions/{operation}/{record_id}    qubesync_answer (reads a form:
                                                    python-multipart)
    GET  /qube/questions/{operation}/{record_id}/search  qubesync_search

The record and the calls to QuBe Sync block, so they run on a worker thread.
"""
try:
    import fastapi as _fastapi  # noqa: F401
except ImportError as error:  # pragma: no cover
    raise ImportError('qubesync.fastapi needs FastAPI: pip install "qubesync[fastapi]"') from error

import functools
import logging
import threading
from collections import namedtuple
from typing import Any, Dict, Optional, Sequence
from urllib.parse import urlparse

from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse, Response
from markupsafe import Markup
from starlette.concurrency import run_in_threadpool

from .. import kit
from ..kit.sqlalchemy import ConnectionEvents, Operation

__all__ = [
    "Operation",
    "ConnectionEvents",
    "Routers",
    "routers",
    "router",
    "question_context",
    "question_html",
    "add_templates",
    "TEMPLATES",
]

log = logging.getLogger("qubesync.kit")

TEMPLATE = "qubesync/question.html"


def _templates_dir():
    # type: () -> str
    import os

    return os.path.join(os.path.dirname(os.path.abspath(kit.__file__)), "templates")


# The packaged templates (qubesync/question.html), shared with qubesync.flask.
TEMPLATES = _templates_dir()

Routers = namedtuple("Routers", ["webhooks", "connect", "questions"])


def _response(reply):
    # type: (kit.Reply) -> Response
    if reply.location is not None:
        return RedirectResponse(reply.location, status_code=reply.status)
    if reply.json is not None:
        return JSONResponse(reply.json, status_code=reply.status)
    if reply.text is not None:
        return PlainTextResponse(reply.text, status_code=reply.status)
    return Response(status_code=reply.status)


# The enqueue setting's default under FastAPI: BackgroundTasks, which runs each in this
# process once the response is sent, each request's on a thread of its own: one job at a
# time. A restart loses what it hasn't run, so point enqueue at a durable queue (Celery, arq,
# RQ) before production.
_one_at_a_time = threading.Lock()
_warned = []  # type: list


def _background(operation, record_id, body):
    # type: (str, str, str) -> None
    with _one_at_a_time:
        try:
            kit.run(operation, record_id, body)
        except Exception:
            log.exception("QuBe Sync: a webhook job failed")


def _warn_once():
    # type: () -> None
    if not _warned:
        _warned.append(True)
        log.warning(
            "QuBe Sync: webhooks run as background tasks in this process (the enqueue setting's "
            "default), so a restart loses what hasn't run: set enqueue to a durable queue before "
            "production."
        )


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


def routers():
    # type: () -> Routers
    """The kit's routers: webhooks, connect and questions. Include connect and questions
    behind your sign-in (dependencies=[Depends(...)]); current_account and authorize_question
    (qubesync.kit.configure) decide the rest."""
    webhooks = APIRouter()

    @webhooks.post("/webhooks/qube/{operation}/{record_id}", name="qubesync_webhook")
    async def webhook(operation: str, record_id: str, request: Request, background_tasks: BackgroundTasks) -> Response:
        body = await _raw_body(request)  # the raw bytes the signature is over
        signature = request.headers.get(kit.SIGNATURE_HEADER)
        enqueue = None
        if not kit.settings().is_set("enqueue"):
            _warn_once()
            enqueue = functools.partial(background_tasks.add_task, _background)
        reply = await run_in_threadpool(kit.receive, operation, record_id, body, signature, enqueue)
        return _response(reply)

    connect = APIRouter()

    @connect.post("/quickbooks/connect", name="qubesync_connect")
    def connect_view(request: Request) -> Response:
        return _response(kit.connect(request))

    questions = APIRouter()

    @questions.post("/qube/questions/{operation}/{record_id}", name="qubesync_answer")
    async def answer(operation: str, record_id: str, request: Request) -> Response:
        form = await request.form()
        referer = request.headers.get("referer")
        reply = await run_in_threadpool(kit.answer, request, operation, record_id, form, referer, request.url.netloc)
        return _response(reply)

    @questions.get("/qube/questions/{operation}/{record_id}/search", name="qubesync_search")
    def search(operation: str, record_id: str, request: Request) -> Response:
        return _response(kit.search(request, operation, record_id, request.query_params))

    return Routers(webhooks, connect, questions)


def router(dependencies=None, prefix=""):
    # type: (Optional[Sequence[Any]], str) -> APIRouter
    """All three routers in one, with dependencies (your sign-in) on connect and the
    questions only."""
    parts = routers()
    combined = APIRouter(prefix=prefix)
    combined.include_router(parts.webhooks)
    combined.include_router(parts.connect, dependencies=list(dependencies or []))
    combined.include_router(parts.questions, dependencies=list(dependencies or []))
    return combined


def question_context(request, slug, record):
    # type: (Request, str, Any) -> Dict[str, Any]
    """What the question template reads, for the record's page: the question the run is
    asking about record, if any, and where it's answered. In the page's route:

        context = {"request": request, "invoice": invoice,
                   **qubesync.fastapi.question_context(request, "create_invoice", invoice)}
        return templates.TemplateResponse("invoice.html", context)

    and in invoice.html, {% include "qubesync/question.html" %} (add_templates(templates)
    first, so your Jinja environment finds it)."""
    action = request.url_for("qubesync_answer", operation=slug, record_id=str(record.id))
    return kit.question_context(slug, record, urlparse(str(action)).path)


def add_templates(templates):
    # type: (Any) -> Any
    """Lets a Jinja2Templates (or a jinja2 Environment) find qubesync/question.html, after
    its own directories, so yours at templates/qubesync/question.html comes first."""
    from jinja2 import ChoiceLoader, FileSystemLoader

    env = getattr(templates, "env", templates)
    ours = FileSystemLoader(TEMPLATES)
    env.loader = ChoiceLoader([env.loader, ours]) if env.loader is not None else ours
    return templates


_environment = []  # type: list


def _own_environment():
    # type: () -> Any
    if not _environment:
        from jinja2 import Environment, FileSystemLoader, select_autoescape

        _environment.append(
            Environment(loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(default=True))
        )
    return _environment[0]


def question_html(request, slug, record, templates=None, **context):
    # type: (Request, str, Any, Any, **Any) -> Markup
    """The question template rendered for record, for a page that doesn't include it: the
    render_question setting's, when it's set, else qubesync/question.html from templates
    (your Jinja2Templates, after add_templates) or the packaged one. context adds to it
    (csrf_token, csp_nonce)."""
    values = dict(question_context(request, slug, record), request=request, **context)
    render = kit.settings().get("render_question")
    if render is not None:
        return Markup(render(values))
    env = getattr(templates, "env", templates) if templates is not None else _own_environment()
    return Markup(env.get_template(TEMPLATE).render(**values))
