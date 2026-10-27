"""Every screen the templates show, from sample data, for GET qube/storyboard: the run status in
each state, the one-shot error, and a question of each kind (kit/storyboard/*.json, prompts
shaped as QuBe Sync sends them, the same samples as qube_rails'). Nothing is read from or
written to QuBe Sync or the database: the runs are stand-ins, never saved.
"""
import datetime
import json
import os
from collections import OrderedDict, namedtuple
from typing import Any, Callable, Dict, List, Optional

from ._messages import t
from ._models import RunMixin
from ._store import utc
from ._sync_status import SyncStatus
from ._views import FieldView, QuestionView, RunStatusView

__all__ = ["Screen", "QUESTIONS", "RUN_STATUSES", "screens", "find", "matches", "override_path", "page"]

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "storyboard")

Screen = namedtuple("Screen", ["key", "group", "title", "note", "pieces", "kind", "sample"])

QUESTIONS = (
    "near_match record_search choose enum_select number_boolean name_clash ask_about_add missing_record rows refusal"
).split()

# key, title, SyncStatus status, the run's attributes (ages in seconds), extra pieces, note.
RUN_STATUSES = [
    ("not_sent", "Not sent", "not_sent", None, [], "A record with no run: the run status template renders nothing."),
    ("starting", "Starting", "sending", {"state": "starting", "age": 5}, [], "A start QuBe Sync is confirming."),
    (
        "unconfirmed",
        "A start not confirmed",
        "sending",
        {"state": "starting", "age": 120},
        ["run_status/retry"],
        "QuBe Sync hasn't confirmed the start for a minute: the retry button sends it again, same reference.",
    ),
    (
        "running",
        "Running",
        "sending",
        {"state": "running", "qube_run_id": "run-sample", "age": 30},
        [],
        "QuBe Sync confirmed it; the Web Connector is working through it.",
    ),
    (
        "stalled_not_checking_in",
        "Waiting: QuickBooks isn't checking in",
        "sending",
        {"state": "running", "qube_run_id": "run-sample", "age": 30 * 60, "stall": "not_checking_in"},
        ["run_status/stall"],
        "A run going on a connection QuBe Sync says stalled (not_checking_in): the Web Connector hasn't called in. "
        "No redeliver button: the cause is known.",
    ),
    (
        "stalled_quickbooks_unavailable",
        "Waiting: QuickBooks is closed",
        "sending",
        {"state": "running", "qube_run_id": "run-sample", "age": 30 * 60, "stall": "quickbooks_unavailable"},
        ["run_status/stall"],
        "The same, stalled as quickbooks_unavailable: the Web Connector calls in but can't open the company file.",
    ),
    (
        "needs_answer",
        "Waiting for an answer",
        "needs_answer",
        {"state": "awaiting_input", "qube_run_id": "run-sample", "age": 30, "question": {"message": "?"}},
        [],
        "The run asks a question: the question template shows it (below).",
    ),
    (
        "looks_stuck",
        "Looks stuck",
        "sending",
        {"state": "running", "qube_run_id": "run-sample", "age": 15 * 60},
        ["run_status/redeliver"],
        "No news for 10 minutes: the redeliver button asks QuBe Sync to send its latest event again.",
    ),
    (
        "in_quickbooks",
        "In QuickBooks",
        "in_quickbooks",
        {"state": "completed", "outcome": "added", "ended": True},
        [],
        "The record is linked to its QuickBooks id.",
    ),
    (
        "done",
        "Done",
        "done",
        {"state": "completed", "outcome": "completed", "ended": True},
        [],
        "Completed, linking nothing (an operation that doesn't link its record).",
    ),
    (
        "failed",
        "Failed",
        "failed",
        {
            "state": "failed",
            "ended": True,
            "error": {
                "message": "QuickBooks refused the invoice because Riverbend Electric is inactive",
                "detail": "Make Riverbend Electric active in QuickBooks, then send it again.",
            },
        },
        ["run_status/detail"],
        "A failure: the pill says it couldn't sync; below it, why (the error's message) and what to do (its detail).",
    ),
    (
        "cancelled",
        "Cancelled",
        "cancelled",
        {"state": "cancelled", "ended": True, "cancel_reason": "The order was cancelled in the app."},
        [],
        "Cancelled by your app, with its reason.",
    ),
]


class _SampleStore(object):
    def now(self):
        # type: () -> datetime.datetime
        return datetime.datetime.now(datetime.timezone.utc)

    def utc(self, value):
        # type: (Any) -> Any
        return utc(value)


class _SampleConnection(object):
    def __init__(self, status, stall_reason):
        # type: (str, Optional[str]) -> None
        self.status = status
        self.stall_reason = stall_reason


class _SampleRun(RunMixin):
    """A run that's never saved: the attributes RunMixin reads, and its connection."""

    _kit_store = _SampleStore()

    def __init__(self, connection, **attributes):
        # type: (Any, **Any) -> None
        self.connection = connection
        self.id = "storyboard"
        self.operation = "storyboard"
        self.reference = "storyboard"
        for name in ("state", "outcome", "error", "cancel_reason", "qube_run_id", "question"):
            setattr(self, name, attributes.get(name))
        self.links = {}  # type: Dict[str, Any]
        self.created_at = attributes.get("created_at")
        self.updated_at = attributes.get("updated_at")
        self.ended_at = attributes.get("ended_at")


def _load(key):
    # type: (str) -> Dict[str, Any]
    with open(os.path.join(DIR, "%s.json" % key)) as handle:
        loaded = json.load(handle)  # type: Dict[str, Any]
    return loaded


def screens():
    # type: () -> List[Screen]
    """Every screen: the run statuses, the error, then a question of each kind."""
    listed = []
    for key, title, status, run, pieces, note in RUN_STATUSES:
        shown = [] if status == "not_sent" else ["run_status/status", "run_status/summary"] + pieces
        listed.append(Screen(key, "Run status", title, note, shown, "run_status", {"status": status, "run": run}))
    listed.append(
        Screen(
            "error",
            "Run status",
            "A one-shot error",
            "A route's message, kept for the page and shown once by whichever template comes first, or by the "
            "error template (qube_error) on a page without them.",
            ["error"],
            "error",
            {"message": t("errors.question_changed")},
        )
    )
    for key in QUESTIONS:
        sample = _load(key)
        listed.append(Screen(key, "Questions", sample["title"], sample["note"], _question_pieces(sample), "question", sample))
    return listed


def find(key):
    # type: (Any) -> Optional[Screen]
    for screen in screens():
        if screen.key == str(key):
            return screen
    return None


def run_status_view(screen, answer_url):
    # type: (Screen, str) -> RunStatusView
    """The screen's status, every button posting to the storyboard's no-op answer."""
    return RunStatusView.from_sync(_sync_status(screen.sample), lambda run: answer_url, lambda run: answer_url)


def question_view(screen, answer_url, search_url):
    # type: (Screen, str, str) -> QuestionView
    return QuestionView(screen.sample["prompt"], action_url=answer_url, search_url=search_url, error=screen.sample.get("error"))


def matches(screen, field, q):
    # type: (Optional[Screen], Any, Any) -> List[Dict[str, Any]]
    """The sample's matches for a search: at most 20 whose label holds q."""
    if screen is None or screen.kind != "question":
        return []
    listed = (screen.sample.get("search") or {}).get(str(field or "")) or []
    q = str(q or "").strip().lower()
    return [m for m in listed if q in str(m.get("label") or "").lower()][:20]


def override_path(piece):
    # type: (str) -> str
    """Where an app puts its own copy of a piece, in a template directory searched first."""
    return "templates/qubesync/%s.html" % piece


def page(key, url_for, notice=False):
    # type: (Optional[str], Callable[..., str], bool) -> Optional[Dict[str, Any]]
    """What qubesync/storyboard.html reads: every screen (key None) or one, each with its view
    built (run_status, message or question), its answer URL and its override files; the nav by
    group; and the notice after an answer. url_for(name, key) gives "screen", "answer" and
    "search" URLs, and url_for("index", None) the storyboard's. None for a key that isn't one."""
    every = screens()
    chosen = every if key is None else [s for s in every if s.key == str(key)]
    if not chosen:
        return None
    single = key is not None
    shown = []
    for screen in chosen:
        answer = url_for("answer", screen.key)
        entry = {
            "screen": screen,
            "key": screen.key,
            "title": screen.title,
            "group": screen.group,
            "note": screen.note,
            "kind": screen.kind,
            "url": url_for("screen", screen.key),
            "files": [override_path(piece) for piece in screen.pieces],
            "run_status": None,
            "question": None,
            "message": None,
        }
        if screen.kind == "run_status":
            entry["run_status"] = run_status_view(screen, answer)
        elif screen.kind == "error":
            entry["message"] = screen.sample["message"]
        else:
            entry["question"] = question_view(screen, answer, url_for("search", screen.key))
        shown.append(entry)
    groups = OrderedDict()  # type: Dict[str, List[Dict[str, Any]]]
    for screen in every:
        href = url_for("screen", screen.key) if single else "#qube-storyboard-%s" % screen.key
        current = single and chosen[0].key == screen.key
        groups.setdefault(screen.group, []).append({"key": screen.key, "title": screen.title, "href": href, "current": current})
    return {
        "screens": shown,
        "single": single,
        "nav": [{"group": group, "screens": listed} for group, listed in groups.items()],
        "index_url": url_for("index", None),
        "notice": "Storyboard: nothing was sent." if notice else None,
        "canvas_themes": [("app", "As your page"), ("light", "Light"), ("dark", "Dark")],
    }


def _question_pieces(sample):
    # type: (Dict[str, Any]) -> List[str]
    prompt = sample["prompt"]
    pieces = ["question/question", "question/message"]
    if prompt.get("details"):
        pieces.append("question/details")
    view = QuestionView(prompt, action_url="", search_url="")
    if view.picks:
        pieces.extend(["question/picks", "question/pick"])
    if view.forms or view.exits:
        pieces.append("question/choice")
    if view.exits:
        pieces.append("question/footer")
    if sample.get("error"):
        pieces.append("error")
    for choice in prompt.get("choices") or []:
        for field in choice.get("fields") or []:
            type = FieldView.type_of(field)
            if type != "rows":
                pieces.append("question/field")
            pieces.append("question/fields/%s" % type)
            if type != "rows":
                continue
            pieces.extend(["question/rows/row", "question/rows/cell", "question/rows/segmented", "question/field"])
            for column in field.get("columns") or []:
                pieces.append("question/fields/%s" % FieldView.type_of(column))
    seen = []  # type: List[str]
    for piece in pieces:
        if piece not in seen:
            seen.append(piece)
    return seen


def _sync_status(sample):
    # type: (Dict[str, Any]) -> SyncStatus
    attrs = sample["run"]
    if not attrs:
        return SyncStatus("not_sent")
    now = datetime.datetime.now(datetime.timezone.utc)
    created = now - datetime.timedelta(seconds=attrs.get("age") or 0)
    stall = attrs.get("stall")
    connection = _SampleConnection("stalled" if stall else "connected", stall)
    run = _SampleRun(
        connection,
        created_at=created,
        updated_at=created,
        ended_at=now if attrs.get("ended") else None,
        **{name: attrs.get(name) for name in ("state", "outcome", "error", "cancel_reason", "qube_run_id", "question")}
    )
    return SyncStatus(sample["status"], run, None)
