"""QuBe Sync's integration kit for Flask: three blueprints, since they go behind different
things (the webhooks behind nothing, onboarding and the questions behind your sign-in), the
question template, and Operation and ConnectionEvents bases that save through SQLAlchemy.

    pip install "qubesync[flask]>=0.4.0"

    # app.py, where your Flask app is made
    import quickbooks_desktop.config  # its qubesync.kit.configure(...)
    import qubesync.flask
    from flask_login import login_required

    qubesync.flask.init_app(app, sign_in=login_required)

or, to put each blueprint where you like:

    bps = qubesync.flask.blueprints(sign_in=login_required)
    app.register_blueprint(bps.webhooks)
    app.register_blueprint(bps.connect)
    app.register_blueprint(bps.questions)

The routes, relative to url_prefix:

    POST /quickbooks/connect                        qubesync_connect.connect
    POST /webhooks/qube/<operation>/<record id>     qubesync_webhooks.webhook (no sign-in, no CSRF)
    POST /qube/questions/<operation>/<record id>    qubesync_questions.answer
    GET  /qube/questions/<operation>/<record id>/search  qubesync_questions.search

With Flask-WTF's CSRFProtect set up before the blueprints are registered, the webhooks
blueprint is exempted from it (QuBe Sync signs its webhooks instead); set up after, call
csrf.exempt(bps.webhooks) yourself. The answer form carries csrf_token() when Flask-WTF
provides it.
"""
try:
    import flask as _flask  # noqa: F401
except ImportError as error:  # pragma: no cover
    raise ImportError('qubesync.flask needs Flask: pip install "qubesync[flask]"') from error

import os
from collections import namedtuple
from typing import Any, Callable, Dict, Optional

from flask import Blueprint, current_app, jsonify, redirect, render_template, request
from markupsafe import Markup

from .. import kit
from ..kit import _defaults
from ..kit.sqlalchemy import ConnectionEvents, Operation

__all__ = [
    "Operation",
    "ConnectionEvents",
    "Blueprints",
    "blueprints",
    "init_app",
    "question_context",
    "question_html",
    "TEMPLATES",
]

# The packaged templates (qubesync/question.html), shared with qubesync.fastapi.
TEMPLATES = os.path.join(os.path.dirname(os.path.abspath(kit.__file__)), "templates")

Blueprints = namedtuple("Blueprints", ["webhooks", "connect", "questions"])

TEMPLATE = "qubesync/question.html"


def _response(reply):
    # type: (kit.Reply) -> Any
    if reply.location is not None:
        return redirect(reply.location, code=reply.status)
    if reply.json is not None:
        return jsonify(reply.json), reply.status
    if reply.text is not None:
        return reply.text, reply.status, {"Content-Type": "text/plain; charset=utf-8"}
    return "", reply.status


def _in_process(operation, record_id, body):
    # type: (str, str, str) -> None
    """The enqueue setting's default under Flask: the kit's worker thread, in an app context
    of this app's, since the job runs outside this request."""
    app = current_app._get_current_object()

    def job():
        with app.app_context():
            kit.run(operation, record_id, body)

    _defaults.default_queue().submit(job)


def blueprints(sign_in=None, url_prefix=None):
    # type: (Optional[Callable[[Any], Any]], Optional[str]) -> Blueprints
    """The kit's blueprints: webhooks, connect and questions. sign_in, a view decorator
    (flask_login's login_required, say), goes on connect, answer and search; without one, put
    your sign-in on those two blueprints (bp.before_request). current_account and
    authorize_question (qubesync.kit.configure) decide the rest."""
    guard = sign_in or (lambda view: view)

    webhooks = Blueprint("qubesync_webhooks", __name__, url_prefix=url_prefix)

    @webhooks.route("/webhooks/qube/<operation>/<record_id>", methods=["POST"])
    def webhook(operation, record_id):
        enqueue = None if kit.settings().is_set("enqueue") else _in_process
        # The raw bytes the signature is over, whatever the content type; not request.json.
        # Over MAX_WEBHOOK_BODY (5 MB) is a 413 without reading it. An app's MAX_CONTENT_LENGTH
        # under 5 MB refuses first.
        too_big = (request.content_length or 0) > kit.MAX_WEBHOOK_BODY
        body = None if too_big else request.get_data()
        signature = request.headers.get(kit.SIGNATURE_HEADER)
        return _response(kit.receive(operation, record_id, body, signature, enqueue=enqueue))

    @webhooks.record_once
    def _exempt_from_csrf(state):
        csrf = state.app.extensions.get("csrf")
        if csrf is not None and hasattr(csrf, "exempt"):
            csrf.exempt(webhooks)

    connect = Blueprint("qubesync_connect", __name__, url_prefix=url_prefix)

    @connect.route("/quickbooks/connect", methods=["POST"], endpoint="connect")
    @guard
    def connect_view():
        return _response(kit.connect(request))

    questions = Blueprint("qubesync_questions", __name__, url_prefix=url_prefix, template_folder=TEMPLATES)

    @questions.route("/qube/questions/<operation>/<record_id>", methods=["POST"], endpoint="answer")
    @guard
    def answer_view(operation, record_id):
        reply = kit.answer(request, operation, record_id, request.form, request.referrer, request.host)
        return _response(reply)

    @questions.route("/qube/questions/<operation>/<record_id>/search", endpoint="search")
    @guard
    def search_view(operation, record_id):
        return _response(kit.search(request, operation, record_id, request.args))

    return Blueprints(webhooks, connect, questions)


def init_app(app, sign_in=None, url_prefix=None):
    # type: (Any, Optional[Callable[[Any], Any]], Optional[str]) -> Blueprints
    """Registers the three blueprints on app, and returns them."""
    bps = blueprints(sign_in=sign_in, url_prefix=url_prefix)
    for bp in bps:
        app.register_blueprint(bp)
    return bps


def question_context(slug, record):
    # type: (str, Any) -> Dict[str, Any]
    """What the question template reads, for the record's page: the question the run is
    asking about record, if any, and where it's answered. In the page's view:

        return render_template("invoice.html", invoice=invoice,
                               **qubesync.flask.question_context("create_invoice", invoice))

    and in invoice.html, {% include "qubesync/question.html" %}."""
    from flask import url_for

    action = url_for("qubesync_questions.answer", operation=slug, record_id=record.id)
    return kit.question_context(slug, record, action)


def question_html(slug, record, **context):
    # type: (str, Any, **Any) -> Markup
    """The question template rendered for record, for a page that doesn't include it: the
    render_question setting's, when it's set, else qubesync/question.html (yours, at
    templates/qubesync/question.html, comes first). context adds to it (csp_nonce, say)."""
    values = dict(question_context(slug, record), **context)
    render = kit.settings().get("render_question")
    if render is not None:
        return Markup(render(values))
    return Markup(render_template(TEMPLATE, **values))
