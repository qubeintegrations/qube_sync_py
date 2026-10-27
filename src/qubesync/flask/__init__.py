"""QuBe Sync's integration kit for Flask: three blueprints, since they go behind different
things (the webhooks behind nothing, onboarding and the questions behind your sign-in), and
the question and run status templates. The kit's tables are the SQLAlchemy models in
qubesync.kit.sqlalchemy, through your session (the db_session setting).

    pip install "qubesync[flask]>=0.4.0"

    # app.py, where your Flask app is made
    import quickbooks_desktop.config  # its qubesync.kit.configure(..., db_session=db.session)
    import qubesync.flask
    from flask_login import login_required

    qubesync.flask.init_app(app, sign_in=login_required)

or, to put each blueprint where you like:

    bps = qubesync.flask.blueprints(sign_in=login_required)
    app.register_blueprint(bps.webhooks)
    app.register_blueprint(bps.connections)
    app.register_blueprint(bps.questions)

The routes, relative to url_prefix:

    POST /quickbooks/connections                   qubesync_connections.connections
    POST /quickbooks/connections/<id>/onboarding   qubesync_connections.connection_onboarding
    DELETE /quickbooks/connections/<id>            qubesync_connections.connection (disconnect)
    POST /quickbooks/connections/<id>/disconnect   qubesync_connections.connection_disconnect (a form's)
    POST /webhooks/qube/runs/<id>                  qubesync_webhooks.run_webhook (no sign-in, no CSRF)
    POST /webhooks/qube/connections/<id>           qubesync_webhooks.connection_webhook (likewise)
    POST /webhooks/qube/requests/<id>              qubesync_webhooks.request_webhook (likewise)
    POST /qube/questions/runs/<id>                 qubesync_questions.question
    GET  /qube/questions/runs/<id>/search          qubesync_questions.question_search
    POST /qube/runs/<id>/retry_start               qubesync_questions.retry_start
    POST /qube/runs/<id>/redeliver                 qubesync_questions.redeliver
    GET  /qube/assets/<name>                       qubesync_questions.asset (question.js, qubesync.css; no sign-in)
    GET  /qube/storyboard[/<screen>]               qubesync_questions.storyboard[_screen] (the storyboard setting)
    GET  /qube/storyboard/<screen>/search          qubesync_questions.storyboard_search
    POST /qube/storyboard/<screen>/answer          qubesync_questions.storyboard_answer (sends nothing)

With Flask-WTF's CSRFProtect set up before the blueprints are registered, the webhooks
blueprint is exempted from it (QuBe Sync signs its webhooks instead); set up after, call
csrf.exempt(bps.webhooks) yourself. The templates' forms carry csrf_token() when Flask-WTF
provides it. init_app registers qube_question(record, operation) and qube_run_status(record,
operation, connection=None) as Jinja globals, for a record's page, qube_error(), a route's
message on a page without them (a disconnect's), and qube_assets(stylesheet=False), the
behaviour script's tag (and the opt-in stylesheet's) for your layout's <head>. A message from a question or
run route (why it didn't go through) is kept in Flask's session, so it needs a SECRET_KEY;
without one, the route answers it as text.
"""
try:
    import flask as _flask  # noqa: F401
except ImportError as error:  # pragma: no cover
    raise ImportError('qubesync.flask needs Flask: pip install "qubesync[flask]"') from error

import os
from collections import namedtuple
from typing import Any, Callable, Dict, Optional

from flask import (
    Blueprint,
    abort,
    current_app,
    has_request_context,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from markupsafe import Markup, escape

from .. import kit
from ..kit._job import enqueue_in_process

__all__ = [
    "redirect_back",
    "sync_status",
    "Operation",
    "ConnectionEvents",
    "Blueprints",
    "blueprints",
    "init_app",
    "question_context",
    "run_status_context",
    "question_html",
    "run_status_html",
    "error_html",
    "assets_html",
    "take_error",
    "TEMPLATES",
]

Operation = kit.Operation
ConnectionEvents = kit.ConnectionEvents

# The packaged templates (qubesync/question.html, qubesync/run_status.html), shared with
# qubesync.fastapi.
TEMPLATES = os.path.join(os.path.dirname(os.path.abspath(kit.__file__)), "templates")

Blueprints = namedtuple("Blueprints", ["webhooks", "connections", "questions"])


def _response(reply):
    # type: (kit.Reply) -> Any
    if reply.error is not None and not _keep_error(reply.error):
        return _response(reply.fallback)
    if reply.location is not None:
        return redirect(reply.location, code=reply.status)
    if reply.json is not None:
        return jsonify(reply.json), reply.status
    if reply.text is not None:
        return reply.text, reply.status, {"Content-Type": "text/plain; charset=utf-8"}
    return "", reply.status


def _keep_error(message):
    # type: (str) -> bool
    # In the session, for the templates to show once; a NullSession (no SECRET_KEY) can't.
    try:
        session[kit.ERROR_KEY] = message
    except RuntimeError:
        return False
    return True


def redirect_back(error=None):
    # type: (Optional[str]) -> Any
    """Back to the page the request came from (303), with error, if any, for the templates to
    show once: for your own views, such as a start button's."""
    referer = request.headers.get("Referer")
    if error is None:
        return _response(kit.Reply(303, location=kit.back(referer, request.host)))
    return _response(kit.back_with_error(error, 422, referer, request.host))


def sync_status(record, operation, connection=None):
    # type: (Any, str, Any) -> kit.SyncStatus
    """record's SyncStatus for operation (on connection, else on its latest run's): the
    qube_sync_status Jinja global."""
    if connection is not None:
        return kit.SyncStatus.of(connection, record, operation)
    return kit.SyncStatus.latest(record, operation)


def take_error():
    # type: () -> Any
    """The message a question or run route left in the session, removed: shown once."""
    if not has_request_context():
        return None
    try:
        return session.pop(kit.ERROR_KEY, None)
    except RuntimeError:
        return None


def _production():
    # type: () -> bool
    app = current_app
    return not (app.debug or app.testing)


def _in_process(delivery):
    # type: (Dict[str, Any]) -> None
    """The enqueue setting's default under Flask: the kit's worker thread, each attempt in an
    app context of this app's, since the job runs outside this request (Flask-SQLAlchemy's
    db.session needs one)."""
    app = current_app._get_current_object()

    def in_context(work):
        # type: (Callable[[], None]) -> None
        with app.app_context():
            work()

    enqueue_in_process(delivery, wrap=in_context)


def _raw_body():
    # type: () -> Optional[bytes]
    # The raw bytes the signature is over, whatever the content type; not request.json. Over
    # MAX_WEBHOOK_BODY (5 MB) is a 413 without reading it. An app's MAX_CONTENT_LENGTH under
    # 5 MB refuses first.
    if (request.content_length or 0) > kit.MAX_WEBHOOK_BODY:
        return None
    return request.get_data()


def blueprints(sign_in=None, url_prefix=None):
    # type: (Optional[Callable[[Any], Any]], Optional[str]) -> Blueprints
    """The kit's blueprints: webhooks, connections and questions. sign_in, a view decorator
    (flask_login's login_required, say), goes on every route but the webhooks; without one,
    put your sign-in on the connections and questions blueprints (bp.before_request).
    current_account and authorize_question (qubesync.kit.configure) decide the rest."""
    guard = sign_in or (lambda view: view)

    webhooks = Blueprint("qubesync_webhooks", __name__, url_prefix=url_prefix)

    @webhooks.route("/webhooks/qube/runs/<id>", methods=["POST"], endpoint="run_webhook")
    def run_webhook(id):
        signature = request.headers.get(kit.SIGNATURE_HEADER)
        return _response(kit.receive("run", id, _raw_body(), signature, enqueue=_in_process, path=request.path))

    @webhooks.route("/webhooks/qube/connections/<id>", methods=["POST"], endpoint="connection_webhook")
    def connection_webhook(id):
        signature = request.headers.get(kit.SIGNATURE_HEADER)
        return _response(
            kit.receive("connection", id, _raw_body(), signature, enqueue=_in_process, path=request.path)
        )

    @webhooks.route("/webhooks/qube/requests/<id>", methods=["POST"], endpoint="request_webhook")
    def request_webhook(id):
        signature = request.headers.get(kit.SIGNATURE_HEADER)
        return _response(kit.receive("request", id, _raw_body(), signature, enqueue=_in_process, path=request.path))

    @webhooks.record_once
    def _exempt_from_csrf(state):
        csrf = state.app.extensions.get("csrf")
        if csrf is not None and hasattr(csrf, "exempt"):
            csrf.exempt(webhooks)

    connections = Blueprint("qubesync_connections", __name__, url_prefix=url_prefix)

    @connections.route("/quickbooks/connections", methods=["POST"], endpoint="connections")
    @guard
    def connect():
        return _response(kit.connect(request, request.form, request.referrer, request.host, _production()))

    @connections.route("/quickbooks/connections/<id>/onboarding", methods=["POST"], endpoint="connection_onboarding")
    @guard
    def onboarding(id):
        return _response(kit.onboarding(request, id))

    @connections.route("/quickbooks/connections/<id>", methods=["DELETE"], endpoint="connection")
    @guard
    def disconnect(id):
        return _response(kit.disconnect(request, id, request.referrer, request.host))

    # The same, for an HTML form, which can't send DELETE.
    @connections.route("/quickbooks/connections/<id>/disconnect", methods=["POST"], endpoint="connection_disconnect")
    @guard
    def disconnect_form(id):
        return _response(kit.disconnect(request, id, request.referrer, request.host))

    questions = Blueprint("qubesync_questions", __name__, url_prefix=url_prefix, template_folder=TEMPLATES)

    @questions.route("/qube/questions/runs/<id>", methods=["POST"], endpoint="question")
    @guard
    def answer(id):
        return _response(kit.answer(request, id, request.form, request.referrer, request.host))

    @questions.route("/qube/questions/runs/<id>/search", endpoint="question_search")
    @guard
    def search(id):
        return _response(kit.search(request, id, request.args))

    @questions.route("/qube/runs/<id>/retry_start", methods=["POST"], endpoint="retry_start")
    @guard
    def retry_start(id):
        return _response(kit.retry_start(request, id, request.referrer, request.host))

    @questions.route("/qube/runs/<id>/redeliver", methods=["POST"], endpoint="redeliver")
    @guard
    def redeliver(id):
        return _response(kit.redeliver(request, id, request.referrer, request.host))

    # The behaviour script and the stylesheet, not behind sign-in: two files, nothing else.
    @questions.route("/qube/assets/<name>", endpoint="asset")
    def asset(name):
        found = kit.asset(name)
        if found is None:
            abort(404)
        return send_file(found[0], mimetype=found[1].split(";")[0], max_age=3600)

    @questions.route("/qube/storyboard", endpoint="storyboard")
    @guard
    def storyboard():
        return _storyboard_page(None)

    @questions.route("/qube/storyboard/<screen>", endpoint="storyboard_screen")
    @guard
    def storyboard_screen(screen):
        return _storyboard_page(screen)

    @questions.route("/qube/storyboard/<screen>/search", endpoint="storyboard_search")
    @guard
    def storyboard_search(screen):
        if not _storyboard_on():
            return _response(kit.Reply(404, json=[]))
        return _response(kit.storyboard_search(screen, request.args))

    @questions.route("/qube/storyboard/<screen>/answer", methods=["POST"], endpoint="storyboard_answer")
    @guard
    def storyboard_answer(screen):
        if not _storyboard_on():
            abort(404)
        return _response(kit.storyboard_answer(screen, _storyboard_url("screen", screen)))

    return Blueprints(webhooks, connections, questions)


def _storyboard_on():
    # type: () -> bool
    return kit.storyboard_on(bool(current_app.debug))


def _storyboard_url(name, key):
    # type: (str, Optional[str]) -> str
    if name == "index":
        return url_for("qubesync_questions.storyboard")
    return url_for("qubesync_questions.storyboard_%s" % name, screen=key)


def _storyboard_page(key):
    # type: (Optional[str]) -> Any
    """Every screen (or one) from sample data, in the storyboard_layout setting's template."""
    if not _storyboard_on():
        abort(404)
    page = kit.storyboard_page(key, _storyboard_url, notice="sent" in request.args)
    if page is None:
        abort(404)
    values = dict(_helpers(), storyboard=page, layout=kit.settings().storyboard_layout, assets=assets_html(stylesheet=True))
    return render_template("qubesync/storyboard.html", **values)


def _helpers():
    # type: () -> Dict[str, Any]
    # What the pieces call: their classes and their words.
    return {"qube_classes": kit.qube_classes, "qube_t": kit.t}


def assets_html(stylesheet=False, csp_nonce=None):
    # type: (bool, Optional[str]) -> Markup
    """The behaviour script's tag (deferred, with csp_nonce when you pass one) and, with
    stylesheet=True, the opt-in stylesheet's: the qube_assets Jinja global, for your layout."""
    tags = []
    if stylesheet:
        href = url_for("qubesync_questions.asset", name="qubesync.css")
        tags.append('<link rel="stylesheet" href="%s" media="all">' % escape(href))
    nonce = ' nonce="%s"' % escape(csp_nonce) if csp_nonce else ""
    tags.append('<script src="%s" defer%s></script>' % (escape(url_for("qubesync_questions.asset", name="question.js")), nonce))
    return Markup("\n".join(tags))


def init_app(app, sign_in=None, url_prefix=None):
    # type: (Any, Optional[Callable[[Any], Any]], Optional[str]) -> Blueprints
    """Registers the three blueprints on app, and qube_question, qube_run_status,
    qube_sync_status, qube_error and qube_assets as Jinja globals (with qube_classes and
    qube_t, which the pieces call), and returns the blueprints."""
    bps = blueprints(sign_in=sign_in, url_prefix=url_prefix)
    for bp in bps:
        app.register_blueprint(bp)
    app.jinja_env.globals.update(
        qube_question=question_html,
        qube_run_status=run_status_html,
        qube_sync_status=sync_status,
        qube_error=error_html,
        qube_assets=assets_html,
        **_helpers()
    )
    return bps


def question_context(record, operation):
    # type: (Any, str) -> Dict[str, Any]
    """What qubesync/question.html reads, for the record's page: the open question of record's
    latest run of operation (a slug), if it's asking, where it's answered, and the session's
    message (taken)."""
    return kit.question_context(
        record, operation, lambda run: url_for("qubesync_questions.question", id=run.id), error=take_error()
    )


def run_status_context(record, operation, connection=None):
    # type: (Any, str, Any) -> Dict[str, Any]
    """What qubesync/run_status.html reads: record's sync status for operation (on connection,
    else on its latest run's), with the retry and redelivery routes when they apply, and the
    session's message (taken)."""
    return kit.run_status_context(
        record,
        operation,
        lambda run: url_for("qubesync_questions.retry_start", id=run.id),
        lambda run: url_for("qubesync_questions.redeliver", id=run.id),
        connection=connection,
        error=take_error(),
    )


def question_html(record, operation, **context):
    # type: (Any, str, **Any) -> Markup
    """qubesync/question.html rendered for record (yours, at templates/qubesync/question.html,
    comes first). context adds to it (csp_nonce, say)."""
    values = dict(_helpers(), **question_context(record, operation))
    return Markup(render_template("qubesync/question.html", **dict(values, **context)))


def run_status_html(record, operation, connection=None, **context):
    # type: (Any, str, Any, **Any) -> Markup
    """qubesync/run_status.html rendered for record."""
    values = dict(_helpers(), **run_status_context(record, operation, connection))
    return Markup(render_template("qubesync/run_status.html", **dict(values, **context)))


def error_html(**context):
    # type: (**Any) -> Markup
    """qubesync/_error.html with the message a route left (a disconnect refused, say), once."""
    message = take_error()
    return Markup(render_template("qubesync/error.html", **dict(_helpers(), message=message, error=message, **context)))
