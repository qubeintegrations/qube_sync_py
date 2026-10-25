"""The routes' work, without a framework: each adapter (qubesync.django, qubesync.flask,
qubesync.fastapi) reads the request, calls one of these and turns the Reply into its
framework's response. An app on another framework can do the same.

    POST quickbooks/connect                       connect: onboarding, behind your sign-in
    POST webhooks/qube/<operation>/<record id>    receive: verify, check the slug, enqueue
    POST qube/questions/<operation>/<record id>   answer: your user's choice, with its fields
    GET  qube/questions/<operation>/<record id>/search
                                                  search: a record field's matches, as JSON
"""
import json
import logging
import math
from typing import Any, Callable, Dict, Mapping, Optional
from urllib.parse import urlparse

from .. import webhooks
from ..v2 import APIError
from ._bases import Operation
from ._defaults import client
from ._job import operation_class
from ._settings import CONFIG_FILE, settings

log = logging.getLogger("qubesync.kit")

__all__ = [
    "Reply",
    "CHANGED",
    "SIGNATURE_HEADER",
    "MAX_WEBHOOK_BODY",
    "receive",
    "connect",
    "answer",
    "search",
    "question_context",
    "find_question",
    "choice",
    "answer_data",
    "number",
    "refusal",
    "back",
]

CHANGED = "This question has changed; reload."

# The largest webhook body the route takes. QuBe Sync's are far smaller; a larger one is
# answered 413 without being verified or read further.
MAX_WEBHOOK_BODY = 5 * 1024 * 1024
SIGNATURE_HEADER = webhooks.HEADER


class Reply(object):
    """What a route answers: a status, and text, JSON or a redirect's location."""

    def __init__(self, status, text=None, json=None, location=None):
        # type: (int, Optional[str], Any, Optional[str]) -> None
        self.status = status
        self.text = text
        self.json = json
        self.location = location

    def __repr__(self):
        return "<Reply %d%s>" % (self.status, " -> %s" % self.location if self.location else "")


# -- Webhooks --------------------------------------------------------------------------------


def receive(operation, record_id, body, signature, enqueue=None):
    # type: (str, str, bytes, Optional[str], Optional[Callable[[str, str, str], Any]]) -> Reply
    """QuBe Sync's webhooks at POST webhooks/qube/<operation>/<record id>, the URL each run was
    started with (Operation.webhook_url), and at webhooks/qube/connection/<account id>, the
    customer's connection's (ConnectionEvents.webhook_url). It only verifies the delivery,
    checks the operation and enqueues it, so it answers well inside the 5 seconds QuBe Sync
    waits: qubesync.kit.run does the rest.

    body is the raw bytes the signature is over, before anything parses them. enqueue is the
    enqueue setting's unless an adapter passes its own default. Any content type is taken, and
    a body over MAX_WEBHOOK_BODY (5 MB) is 413."""
    if body is None or len(body) > MAX_WEBHOOK_BODY:
        log.warning("QuBe Sync: refused a webhook: its body is over %d bytes", MAX_WEBHOOK_BODY)
        return Reply(413)
    try:
        webhooks.verify(body, signature, secrets=settings().webhook_secret)
    except webhooks.SignatureError as error:
        # Its reason (missing, malformed, stale or mismatch) is safe to log: never the
        # secret, the signature or the body.
        log.warning("QuBe Sync: refused a webhook: %s", error.reason)
        return Reply(401)
    if operation_class(operation) is None:
        # A URL none of your operations writes: QuBe Sync retries it, and shows it as a
        # failed delivery, which means a wrong webhook URL.
        return Reply(404)
    # The signature covers the body, not the URL, so the record id is only a pointer: the
    # job checks that the event's reference (a connection event's connection id) is the one
    # saved on that record. The body goes as text, which any queue can carry.
    text = bytes(body).decode("utf-8") if not isinstance(body, str) else body
    (enqueue or settings().enqueue)(operation, record_id, text)
    return Reply(200)


# -- Onboarding ------------------------------------------------------------------------------


def connect(request):
    # type: (Any) -> Reply
    """Connects a customer's QuickBooks Desktop, from a "Connect QuickBooks Desktop" button
    (best clicked on the computer where QuickBooks is installed). QuBe Sync hosts the setup
    and walks them through the Web Connector, and tells your app how it went by webhook (the
    connection class): connection.connected, or connection.setup_cancelled. Until
    connection.connected comes, show the account as waiting for QuickBooks: the setup doesn't
    come back here.

    Behind your sign-in: the connection is kept on the current_account setting's account,
    and a request it finds no account for is answered 401."""
    account = settings().current_account(request)
    if account is None:
        log.warning("QuBe Sync: refused to connect: current_account found no signed-in account")
        return Reply(401, text="Sign in to connect QuickBooks Desktop.")
    events = settings().connection_class()(account)
    # Where QuBe Sync says the connection is set up (connection.connected): the connection
    # class, by this account's id.
    webhook_url = events.webhook_url()
    connection_id = events.saved_connection_id()
    if connection_id:
        # Connected before: the same connection, its webhook URL brought up to date, with a
        # fresh link.
        client().update_connection(connection_id, webhook_url=webhook_url)
        connection = client().regenerate_onboarding(connection_id)
    else:
        connection = client().create_connection(webhook_url=webhook_url)
        events.save_connection_id(connection["id"])
    return Reply(303, location=connection["links"]["onboarding"])


# -- Questions -------------------------------------------------------------------------------


def question_context(operation, record, action):
    # type: (str, Any, str) -> Dict[str, Any]
    """What the question template (qubesync/question.html) reads, for the record's page: the
    question the run is asking about record, if any, and action, where it's answered (the
    answer route's URL for this operation and record; each adapter's question_context works
    it out). Raises LookupError for a slug no operation has."""
    cls = _question_operation(operation)
    if cls is None:
        raise LookupError("qubesync.kit: no operation has the slug %r" % (operation,))
    return {"question": cls(record).saved_question(), "action": action, "operation": operation}


def find_question(request, operation, record_id, refused="answer"):
    # type: (Any, str, str, str) -> Any
    """The operation for a question route, with its record found and authorize_question
    (request, record, operation) asked before anything else, or the Reply that refuses it (404
    for a slug or record that isn't there, or one authorize_question doesn't answer True for;
    403 while authorize_question isn't set). Each refusal is logged."""
    cls = _question_operation(operation)
    if cls is None:
        return Reply(404, text="No such operation.")
    authorize = settings().get("authorize_question")
    if authorize is None:
        # The record's id comes from the URL, so authorize_question is all that keeps one
        # customer's users off another's records: until it's written, every answer and search
        # is refused.
        log.warning(
            "QuBe Sync: refused a question's %s (%s %s): authorize_question isn't set, so every "
            "answer and search is refused until it is: set it with qubesync.kit.configure("
            "authorize_question=...) in your app's %s",
            refused,
            operation,
            record_id,
            CONFIG_FILE,
        )
        return Reply(403, text="Answering questions isn't set up yet.")
    record = cls.find_record(record_id)
    if record is None:
        return Reply(404, text="Not found.")
    allowed = authorize(request, record, operation)
    if allowed is not True:
        # Only True allows: a None from a lookup that found nothing refuses too.
        log.warning(
            "QuBe Sync: refused a question's %s (%s %s): authorize_question answered %r",
            refused,
            operation,
            record_id,
            allowed,
        )
        return Reply(404, text="Not found.")
    return cls(record)


def answer(request, operation, record_id, form, referer=None, host=None):
    # type: (Any, str, str, Mapping[str, Any], Optional[str], Optional[str]) -> Reply
    """Posts your user's choice, with what they filled in for its fields, to the question's
    links.decisions, and sends them back to the page (referer, when it's this app's: host).
    The question is forgotten once it's answered, or once QuBe Sync says it was answered or
    asked again since (a 409, or a 400 not_awaiting_input); the run's next webhook says what
    came of it. The call to QuBe Sync is made here, with the API key, so the browser only ever
    talks to your app."""
    found = find_question(request, operation, record_id, "answer")
    if isinstance(found, Reply):
        return found
    question = found.saved_question()
    links = found.saved_links() or {}
    picked = choice(question, form.get("choice"))
    if not question or not picked or not links.get("decisions"):
        return Reply(409, text=CHANGED)
    try:
        client().answer(links["decisions"], choice=picked["id"], data=answer_data(picked, form))
    except APIError as error:
        if error.status == 422:  # a field QuBe Sync couldn't take: errors.detail says which
            return Reply(422, text=refusal(error))
        # Any 400 (not_awaiting_input, say) or 409 (prompt_changed): the question changed.
        if error.status not in (400, 409):
            raise
        found.answered(question["token"])
        return Reply(409, text=CHANGED)
    found.answered(question["token"])
    return Reply(303, location=back(referer, host))


def search(request, operation, record_id, args):
    # type: (Any, str, str, Mapping[str, Any]) -> Reply
    """The matches for a record field, for what your user typed (args q and field):
    [{value, label, detail}], at most 20, from the question's links.search, which a run sets
    while it asks with one. A q under 2 or over 100 characters, or a field that's empty or over
    100, answers [] without asking."""
    found = find_question(request, operation, record_id, "search")
    if isinstance(found, Reply):
        return Reply(found.status, json=[])
    links = found.saved_links() or {}
    if not links.get("search"):
        return Reply(409, json=[])
    q = (args.get("q") or "").strip()
    field = (args.get("field") or "").strip()
    if not 2 <= len(q) <= 100 or not 1 <= len(field) <= 100:
        return Reply(200, json=[])
    try:
        return Reply(200, json=client().search(links["search"], field=field, q=q))
    except APIError as error:
        if not 400 <= error.status < 500:
            raise
        return Reply(error.status, json=[])  # the question has changed (409), say


def _question_operation(slug):
    # type: (str) -> Any
    # A slug none of your operations has: the connection's own events ask nothing.
    if slug == "connection":
        return None
    cls = settings().operation(slug)
    if not (isinstance(cls, type) and issubclass(cls, Operation)):
        return None
    return cls


# -- The answer's parts ----------------------------------------------------------------------


def choice(question, choice_id):
    # type: (Optional[Dict[str, Any]], Any) -> Optional[Dict[str, Any]]
    """The choice your user picked, while the saved question still offers it."""
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
        text = (form.get("data[%s]" % name) or "").strip()
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
    """The page the answer came from, when it's this app's; else /."""
    if referer and host and urlparse(referer).netloc == host:
        return referer
    return "/"
