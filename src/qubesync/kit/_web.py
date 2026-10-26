"""The routes' work, without a framework: each adapter (qubesync.django, qubesync.flask,
qubesync.fastapi) reads the request, calls one of these and turns the Reply into its
framework's response. An app on another framework can do the same.

    POST quickbooks/connections                  connect: a connection for the signed-in account
    POST quickbooks/connections/<id>/onboarding  onboarding: one of its connections, through setup again
    POST webhooks/qube/runs/<id>                 receive("run", ...): a run's webhooks
    POST webhooks/qube/connections/<id>          receive("connection", ...): a connection's
    POST qube/questions/runs/<id>                answer: your user's choice, with its fields
    GET  qube/questions/runs/<id>/search         search: a record field's matches, as JSON
    POST qube/runs/<id>/retry_start              retry_start: an unconfirmed start sent again
    POST qube/runs/<id>/redeliver                redeliver: a stuck run's latest event sent again

Onboarding, the questions and the retry go behind your sign-in (and CSRF, for the POSTs). The
webhooks go behind nothing: the signature is what proves QuBe Sync sent them.
"""
import json
import logging
import math
from typing import Any, Callable, Dict, Mapping, Optional, Tuple, Union
from urllib.parse import urlparse

from .. import webhooks
from ..v2 import APIError
from ._defaults import client
from ._job import CONNECTION_KIND, RUN_KIND, enqueue_in_process
from ._operation import NETWORK_ERRORS
from ._settings import settings
from ._store import CONNECTION, RUN, current_store

log = logging.getLogger("qubesync.kit")

__all__ = [
    "Reply",
    "CHANGED",
    "NOT_STARTING",
    "NOT_QUIET",
    "REDELIVERY_REFUSED",
    "NO_ANSWER",
    "ERROR_KEY",
    "SIGNATURE_HEADER",
    "MAX_WEBHOOK_BODY",
    "receive",
    "connect",
    "onboarding",
    "answer",
    "search",
    "retry_start",
    "redeliver",
    "authorized_run",
    "owner_answers",
    "question_context",
    "run_status_context",
    "choice",
    "answer_data",
    "number",
    "refusal",
    "back",
]

CHANGED = "This question has changed; reload."
NOT_STARTING = "This run isn't waiting for its start to be confirmed."
NOT_QUIET = "QuBe Sync has been heard from about this run lately: nothing to ask for."
REDELIVERY_REFUSED = {
    409: "QuBe Sync has no news about this run to send yet.",
    429: "That was asked a moment ago: give it a minute.",
}
NO_ANSWER = "QuBe Sync didn't answer: try again in a minute."

# Where an adapter keeps a Reply's error for the templates to show once (session key, cookie).
ERROR_KEY = "qubesync_error"

# What to check, by the reason a webhook's signature was refused.
SIGNATURE_HINTS = {
    "mismatch": "it isn't signed with QUBE_WEBHOOK_SECRET (the webhook_secret setting). Set that to this "
    "app's webhook secret, which `qube env --write .env` writes, and restart; QuBe Sync sends it again",
    "stale": "its signature's time is over 5 minutes from this server's clock. Check the clock",
    "missing": "it has no X-Qube-Signature header, so it isn't from QuBe Sync",
    "malformed": "its X-Qube-Signature header isn't t=<seconds>,v1=<hex>, so it isn't from QuBe Sync",
}

# The largest body taken: a pull_changes page can be a few megabytes. Anything larger is
# answered 413 before it's read.
MAX_WEBHOOK_BODY = 5 * 1024 * 1024
SIGNATURE_HEADER = webhooks.HEADER

_MODELS = {RUN_KIND: RUN, CONNECTION_KIND: CONNECTION}


class Reply(object):
    """What a route answers: a status, and text, JSON or a redirect's location. error is a
    message for the page the redirect goes back to, which the adapter keeps for the templates
    to show once; fallback is the Reply to answer when it can't keep it (no session)."""

    def __init__(self, status, text=None, json=None, location=None, error=None, fallback=None):
        # type: (int, Optional[str], Any, Optional[str], Optional[str], Optional[Reply]) -> None
        self.status = status
        self.text = text
        self.json = json
        self.location = location
        self.error = error
        self.fallback = fallback

    def __repr__(self):
        return "<Reply %d%s>" % (self.status, " -> %s" % self.location if self.location else "")


# -- Webhooks --------------------------------------------------------------------------------


def receive(kind, id, body, signature, enqueue=None, path=None):
    # type: (str, Any, Optional[bytes], Optional[str], Optional[Callable[[Dict[str, Any]], Any]], Optional[str]) -> Reply
    """QuBe Sync's webhooks at POST webhooks/qube/runs/<run id>, the URL each run was started
    with (Run.webhook_url), and at webhooks/qube/connections/<connection id>, each
    connection's (Connection.webhook_url). It only verifies the delivery, checks the row is
    there and enqueues it, so it answers well inside the 5 seconds QuBe Sync waits: the job
    does the rest.

    body is the raw bytes the signature is over, before anything parses them (None when the
    adapter found it over MAX_WEBHOOK_BODY). enqueue is the adapter's default queue, used when
    the enqueue setting isn't set. path is the request's, for the log."""
    if body is None or len(body) > MAX_WEBHOOK_BODY:
        log.warning("QuBe Sync: refused a webhook: its body is over %d bytes", MAX_WEBHOOK_BODY)
        return Reply(413)
    try:
        webhooks.verify(body, signature, secrets=settings().webhook_secret)
    except webhooks.SignatureError as error:
        # The reason is safe to log; never the secret, the signature or the body.
        log.warning(
            "QuBe Sync: refused a webhook: %s (%s): %s",
            error.reason,
            path or "%s %s" % (kind, id),
            SIGNATURE_HINTS.get(error.reason, ""),
        )
        return Reply(401)
    except ValueError as error:
        # Signed, but not a JSON object: nothing a job could take.
        log.warning("QuBe Sync: refused a webhook: its body isn't a JSON object (%s)", type(error).__name__)
        return Reply(400)

    id = str(id)
    # A row that isn't there (deleted, or a wrong webhook_url): QuBe Sync retries it, and shows
    # it as a failed delivery.
    if current_store().get(_MODELS[kind], id) is None:
        return Reply(404)

    # The signature covers the body, not the URL, so the id is only a pointer: the job checks
    # the event's reference and connection id against the row. The body goes as text, which
    # any queue can carry; the job parses it again. A 200 tells QuBe Sync it's taken and it
    # won't send it again, so a queue that didn't take it answers 503 and QuBe Sync retries.
    text = body.decode("utf-8") if isinstance(body, (bytes, bytearray)) else str(body)
    if _enqueued({"kind": kind, "id": id, "body": text}, enqueue):
        return Reply(200)
    return Reply(503)


def _enqueued(delivery, default):
    # type: (Dict[str, Any], Optional[Callable[[Dict[str, Any]], Any]]) -> bool
    # False from the enqueue, or an error from it, is a delivery not taken. Logged without the
    # body, or the error's message, which could carry it.
    config = settings()
    enqueue = config.enqueue if config.is_set("enqueue") else (default or enqueue_in_process)
    try:
        result = enqueue(delivery)
    except Exception as error:
        log.error(
            "QuBe Sync: couldn't enqueue a webhook for %s %s (%s); answered 503 so QuBe Sync sends it again",
            delivery["kind"],
            delivery["id"],
            type(error).__name__,
        )
        return False
    if result is False:
        log.error(
            "QuBe Sync: couldn't enqueue a webhook for %s %s: the enqueue returned False; answered 503 "
            "so QuBe Sync sends it again",
            delivery["kind"],
            delivery["id"],
        )
        return False
    return True


# -- Onboarding ------------------------------------------------------------------------------


def connect(request, form, referer=None, host=None, production=True):
    # type: (Any, Mapping[str, Any], Optional[str], Optional[str], bool) -> Reply
    """POST quickbooks/connections, from a "Connect QuickBooks Desktop" button, with an
    optional name: the account's newest never-connected connection back through setup, or a
    new one (none yet, or new=1). With simulated=1, unless production (the production
    setting, else the adapter's guess), a new connection to a simulated company file, and back
    to referer. The README's "Routes" has the details."""
    account = _signed_in_account(request)
    if account is None:
        return Reply(401, text="Sign in to connect QuickBooks Desktop.")
    if str(form.get("simulated") or "") == "1":
        return _connect_simulated(account, form, referer, host, settings().get("production", production))

    store = current_store()
    if str(form.get("new") or "") != "1":
        owner_type, owner_id = store.key_for(account)
        waiting = store.first(
            CONNECTION,
            order=["-created_at", "-id"],
            owner_type=owner_type,
            owner_id=owner_id,
            status=("pending", "setup_cancelled"),
        )
        if waiting is not None:
            return _send_to_setup(waiting)

    made = store.create(CONNECTION, owner=account, name=_connection_name(form), status="pending")
    return _send_to_setup(made, fresh=True)


def _connect_simulated(account, form, referer, host, production):
    # type: (Any, Mapping[str, Any], Optional[str], Optional[str], Any) -> Reply
    if production is not False:
        return Reply(404, text="Not found.")

    made = current_store().create(CONNECTION, owner=account, name=_connection_name(form), status="pending")
    created = client().create_connection(webhook_url=made.webhook_url, name=made.name, type="simulated")
    made.qube_id = created["id"]
    made._kit_store.save(made, fields=["qube_id"])
    return Reply(303, location=back(referer, host))


def onboarding(request, connection_id):
    # type: (Any, Any) -> Reply
    """POST quickbooks/connections/<id>/onboarding: sends one of the signed-in account's
    connections back through setup (a new company file, a Web Connector set up again), with
    its webhook URL brought up to date. Another account's connection answers 404."""
    account = _signed_in_account(request)
    if account is None:
        return Reply(401, text="Sign in to connect QuickBooks Desktop.")

    store = current_store()
    owner_type, owner_id = store.key_for(account)
    found = store.get(CONNECTION, connection_id)
    if not _owned(found, owner_type, owner_id):
        return Reply(404, text="Not found.")
    return _send_to_setup(found)


def _signed_in_account(request):
    # type: (Any) -> Any
    account = settings().current_account(request)
    if account is None:
        log.warning("QuBe Sync: refused a connect: current_account found no signed-in account")
    return account


def _owned(connection, owner_type, owner_id):
    # type: (Any, str, str) -> bool
    return connection is not None and connection.owner_type == owner_type and str(connection.owner_id) == owner_id


def _connection_name(form):
    # type: (Mapping[str, Any]) -> Optional[str]
    name = str(form.get("name") or "").strip()
    return name[:255] or None


def _send_to_setup(connection, fresh=False):
    # type: (Any, bool) -> Reply
    # fresh: a row this request wrote, which no earlier create can have been made for. Any
    # other row without an id may have an earlier create that landed before its id was saved:
    # that connection, not a second one.
    if not fresh and not connection.qube_id:
        connection.adopt_qube_connection()
    api = client()
    if connection.qube_id:
        api.update_connection(connection.qube_id, webhook_url=connection.webhook_url)
        made = api.regenerate_onboarding(connection.qube_id)
    else:
        made = api.create_connection(webhook_url=connection.webhook_url, name=connection.name)
        connection.qube_id = made["id"]
        connection._kit_store.save(connection, fields=["qube_id"])

    # 303, so the browser follows the POST with a GET.
    return Reply(303, location=made["links"]["onboarding"])


# -- Questions and the start retry -----------------------------------------------------------


def owner_answers(request, record, run):
    # type: (Any, Any, Any) -> bool
    """The default authorize_question: the signed-in account (current_account) owns the run's
    connection. Compared by type and id, as the connection keeps them, so a None or unsaved
    account never matches."""
    account = settings().current_account(request)
    store = run._kit_store
    if account is None or not store.persisted(account):
        return False

    owner_type, owner_id = store.key_for(account)
    connection = run.connection
    return owner_type == connection.owner_type and owner_id == str(connection.owner_id)


def authorized_run(request, run_id, action):
    # type: (Any, Any, str) -> Union[Reply, Tuple[Any, Any, Any]]
    """(run, operation class, record) for a route that names a run, when the run, its
    operation and its record are there and authorize_question(request, record, run) says
    True; else the Reply that refuses it, logged. Only True lets it through: a truthy record,
    or a forgotten return, doesn't. A refusal answers as a run that doesn't exist does (404),
    so a user can't tell another customer's run is there. The default authorize_question reads
    current_account, which raises NotConfigured while it isn't set, as every unset setting
    does at its first use."""
    config = settings()
    store = current_store()
    found = store.get(RUN, run_id)
    operation = config.operation_class(found.operation) if found is not None else None
    record = _record_for(store, operation, found) if operation is not None else None
    if record is None:
        return Reply(404, text="Not found.")

    if config.authorize_question(request, record, found) is not True:
        log.warning("QuBe Sync: refused %s for run %s: authorize_question said no", action, found.id)
        return Reply(404, text="Not found.")
    return found, operation, record


def _record_for(store, operation, run):
    # type: (Any, Any, Any) -> Any
    try:
        return operation.record_for(run)
    except store.not_found_errors:  # a find_record written with get()
        return None


def answer(request, run_id, form, referer=None, host=None):
    # type: (Any, Any, Mapping[str, Any], Optional[str], Optional[str]) -> Reply
    """POST qube/questions/runs/<id>: posts your user's choice, with what they filled in for
    its fields, to the question's links.decisions, and sends them back to the page (referer,
    when it's this app's: host), with why when it didn't go through. The question is forgotten
    once it's answered, or once QuBe Sync says it was answered or asked again since (a 409, or
    a 400 such as not_awaiting_input)."""
    found = authorized_run(request, run_id, "an answer or search")
    if isinstance(found, Reply):
        return found
    run, operation, record = found
    question = run.open_question
    links = run.links or {}
    picked = choice(question, form.get("choice"))
    if picked is None or not links.get("decisions"):
        return back_with_error(CHANGED, 409, referer, host)

    asked = operation(record, run)
    try:
        client().answer(links["decisions"], choice=picked["id"], data=answer_data(picked, form))
    except APIError as error:
        if error.status not in (400, 409, 422):
            raise
        # A field QuBe Sync couldn't take: its errors.detail says which.
        if error.status == 422:
            return back_with_error(refusal(error), 422, referer, host)
        asked.answered(question.get("token"))
        return back_with_error(CHANGED, 409, referer, host)
    asked.answered(question.get("token"))
    return Reply(303, location=back(referer, host))


def search(request, run_id, args):
    # type: (Any, Any, Mapping[str, Any]) -> Reply
    """GET qube/questions/runs/<id>/search: the matches for a record field, for what your user
    typed: [{value, label, detail}], at most 20, from the question's links.search, which a run
    sets while it asks with one. q of 2 to 100 characters and a field name of at most 100 are
    asked about; anything else has no matches."""
    found = authorized_run(request, run_id, "an answer or search")
    if isinstance(found, Reply):
        return Reply(found.status, json=[])
    run = found[0]
    links = run.links or {}
    q = str(args.get("q") or "").strip()
    field = str(args.get("field") or "")
    if not links.get("search"):
        return Reply(409, json=[])
    if not _searchable(q, field):
        return Reply(200, json=[])

    try:
        return Reply(200, json=client().search(links["search"], field=field, q=q))
    except APIError as error:
        if not 400 <= error.status < 500:
            raise
        return Reply(error.status, json=[])  # the question has changed (409), say


# What a search is asked about: q of 2 to 100 characters, a field name of 1 to 100.
def _searchable(q, field):
    # type: (str, str) -> bool
    return 2 <= len(q) <= 100 and 1 <= len(field) <= 100


def retry_start(request, run_id, referer=None, host=None):
    # type: (Any, Any, Optional[str], Optional[str]) -> Reply
    """POST qube/runs/<id>/retry_start, from the run status template's "Try the start again"
    button: sends a start QuBe Sync never confirmed (a run still "starting") again, with the
    same reference as its Idempotency-Key (Run.retry_start), so a start that did land answers
    with its run rather than making another. authorize_question decides who may, as for
    answering the run's questions."""
    found = authorized_run(request, run_id, "a start retry")
    if isinstance(found, Reply):
        return found
    run = found[0]
    if run.state != "starting":
        return back_with_error(NOT_STARTING, 409, referer, host)

    try:
        run.retry_start()
    except (APIError,) + NETWORK_ERRORS as error:
        # Refused (the run is now failed) or no answer again (still unconfirmed): the status on
        # the page says which.
        log.warning("QuBe Sync: run %s's start retry didn't go through (%s)", run.id, type(error).__name__)
    return Reply(303, location=back(referer, host))


def redeliver(request, run_id, referer=None, host=None):
    # type: (Any, Any, Optional[str], Optional[str]) -> Reply
    """POST qube/runs/<id>/redeliver, from the run status template's "Send its latest news
    again" button on a run that looks stuck (Run.looks_stuck): QuBe Sync sends the run's latest
    event again, through the webhook route. Back to the page, with why when it can't."""
    found = authorized_run(request, run_id, "a redelivery")
    if isinstance(found, Reply):
        return found
    run = found[0]
    if not run.looks_stuck():
        return back_with_error(NOT_QUIET, 409, referer, host)

    try:
        client().redeliver_run(run.connection.qube_id, run.qube_run_id)
    except APIError as error:
        if error.status not in REDELIVERY_REFUSED:
            raise
        return back_with_error(REDELIVERY_REFUSED[error.status], error.status, referer, host)
    except NETWORK_ERRORS:
        return back_with_error(NO_ANSWER, 503, referer, host)
    return Reply(303, location=back(referer, host))


def back_with_error(message, status, referer=None, host=None):
    # type: (str, int, Optional[str], Optional[str]) -> Reply
    """Back to the page with message for the templates to show once, or, where the adapter
    can't keep it, message as text with status."""
    return Reply(303, location=back(referer, host), error=message, fallback=Reply(status, text=message))


# -- The templates' context ------------------------------------------------------------------


def question_context(record, operation, action_for, error=None):
    # type: (Any, str, Callable[[Any], str], Optional[str]) -> Dict[str, Any]
    """What the question template (qubesync/question.html) reads: the open question of
    record's latest run of operation (a slug), if it's asking, action (action_for(run), its
    question route), and error (a message to show once). Raises ValueError for a slug none of
    your operations has."""
    _check_operation(operation)
    run = current_store().model(RUN).latest_for(record, operation)
    question = run.open_question if run is not None else None
    if question is None:
        return {"question": None, "run": run, "action": None, "error": error}
    return {"question": question, "run": run, "action": action_for(run), "error": error}


def run_status_context(record, operation, retry_action_for, redeliver_action_for=None, connection=None, error=None):
    # type: (Any, str, Callable[[Any], str], Optional[Callable[[Any], str]], Any, Optional[str]) -> Dict[str, Any]
    """What the run status template (qubesync/run_status.html) reads: sync (the SyncStatus on
    connection, else on the latest run's), its run, summary, state (for the class), a failure's
    detail, retry_action for an unconfirmed start, redeliver_action for a run that looks stuck,
    and error (a message to show once). Raises ValueError for a slug none of your operations
    has."""
    from ._sync_status import SyncStatus

    _check_operation(operation)
    if connection is not None:
        sync = connection.sync_status(record, operation)
    else:
        sync = SyncStatus.latest(record, operation)
    run = sync.run
    return {
        "sync": sync,
        "status": sync.status,
        "run": run,
        "summary": sync.summary_text,
        "state": _state_class(run),
        "detail": run.error_detail if sync.status == "failed" else None,
        "retry_action": retry_action_for(run) if sync.unconfirmed else None,
        "redeliver_action": _redeliver_action(run, redeliver_action_for),
        "error": error,
    }


def _state_class(run):
    # type: (Any) -> Optional[str]
    # A completed run that chose to stop reads as cancelled.
    if run is None:
        return None
    return "cancelled" if run.cancelled() else run.state


def _redeliver_action(run, redeliver_action_for):
    # type: (Any, Optional[Callable[[Any], str]]) -> Optional[str]
    if run is None or redeliver_action_for is None or not run.looks_stuck():
        return None
    return redeliver_action_for(run)


def _check_operation(operation):
    # type: (str) -> None
    if settings().operation_class(operation) is None:
        raise ValueError("QuBe Sync: no operation has the slug %r (the operations setting)" % (operation,))


# -- The answer's parts ----------------------------------------------------------------------


def choice(question, choice_id):
    # type: (Optional[Dict[str, Any]], Any) -> Optional[Dict[str, Any]]
    """The choice your user picked, while the question still offers it."""
    for offered in (question or {}).get("choices") or []:
        if offered.get("id") == choice_id:
            return offered
    return None


def answer_data(picked, form):
    # type: (Dict[str, Any], Mapping[str, Any]) -> Dict[str, Any]
    """The choice's own fields from the form (data[<name>]), each as its type: a checkbox True
    or False, a number as a number (or as typed, for QuBe Sync's 422 to name), and a blank one
    left out."""
    data = {}  # type: Dict[str, Any]
    for field in picked.get("fields") or []:
        name = field["name"]
        text = str(form.get("data[%s]" % name) or "").strip()
        if field.get("type") == "boolean":
            data[name] = text == "true"
        elif text:
            data[name] = number(text) if field.get("type") == "number" else text
    return data


def number(text):
    # type: (str) -> Any
    """text as an int or a float, or as it is when it isn't a finite number."""
    try:
        return int(text)
    except ValueError:
        pass
    try:
        parsed = float(text)
    except ValueError:
        return text
    return parsed if math.isfinite(parsed) else text


def refusal(error):
    # type: (APIError) -> str
    """What QuBe Sync said was wrong with an answer, in words (its errors.detail)."""
    try:
        detail = json.loads(error.body)["errors"]["detail"]
    except (ValueError, KeyError, TypeError):
        detail = None
    if detail:
        return "QuBe Sync couldn't take that answer: %s" % detail
    return "QuBe Sync couldn't take that answer."


def back(referer, host):
    # type: (Optional[str], Optional[str]) -> str
    """The page the request came from, when it's this app's; else /."""
    if not referer:
        return "/"
    if _local_path(referer):
        return referer
    if host and urlparse(referer).netloc == host:
        return referer
    return "/"


# A path on this app ("/invoices/1"), not one a browser takes as another host
# ("//evil.example", "/\\evil.example").
def _local_path(referer):
    # type: (str) -> bool
    return referer.startswith("/") and not referer.startswith(("//", "/\\"))
