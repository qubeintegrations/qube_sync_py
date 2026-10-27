"""Everything the screens say to your users, in English, by key (the same keys as qube_rails'
I18n). The messages setting rewords or translates any of them; the README's "Wording and
translations" lists them. Nothing here names QuBe Sync: to your users it's QuickBooks.
"""
import re
from collections.abc import Mapping
from typing import Any, Dict

__all__ = ["MESSAGES", "t", "messages", "flatten_messages"]

MESSAGES = {
    "status.in_quickbooks": "In QuickBooks",
    "status.added": "Added to QuickBooks",
    "status.done": "Done",
    "status.done_with": "Done: %{outcome}",
    "status.failed": "Couldn't sync",
    "status.not_started": "it couldn't be sent",
    "status.cancelled": "Cancelled",
    "status.cancel_reason": "it was stopped before it finished",
    "status.needs_answer": "Needs your answer",
    "status.starting": "Sending to QuickBooks",
    "status.unconfirmed": "Still waiting for QuickBooks",
    "status.running": "Syncing with QuickBooks",
    "status.quiet": "No update from QuickBooks for a while.",
    "status.check_for_updates": "Check for updates",
    "status.try_again": "Try sending again",
    "status.waiting_for_quickbooks": "Waiting for QuickBooks",
    "status.stalled.not_checking_in": (
        "QuickBooks hasn't checked in for a while, so this is waiting. Make sure the computer with "
        "QuickBooks is on and the Web Connector is running."
    ),
    "status.stalled.quickbooks_unavailable": (
        "The Web Connector is checking in but can't open QuickBooks. Open the company file in "
        "QuickBooks on that computer."
    ),
    "status.stalled.other": (
        "Syncing with QuickBooks has stopped for now. Check the computer with QuickBooks and its Web Connector."
    ),
    "errors.not_starting": "This was already sent, so there's nothing to try again.",
    "errors.not_quiet": "This was updated recently. Check again in a few minutes.",
    "errors.no_update_yet": "There's no update yet. Check again in a few minutes.",
    "errors.checked_just_now": "That was checked a moment ago. Try again in a minute.",
    "errors.unreachable": "Couldn't reach QuickBooks' sync service just now. Try again in a minute.",
    "errors.disconnect_unreachable": (
        "Couldn't reach QuickBooks' sync service just now. Try disconnecting again in a minute."
    ),
    "errors.still_syncing": (
        "Something is still syncing with this company file. Let it finish, or answer its question, then disconnect."
    ),
    "errors.question_changed": (
        "This question changed after the page loaded, so your answer wasn't sent. The page now shows the latest."
    ),
    "errors.answer_refused": "That answer couldn't be used. Check it and try again.",
    "errors.answer_refused_with": "That answer couldn't be used: %{detail}",
    "question.set_all": "Set all to:",
    "question.use_pick": "Use this one",
    "question.use_for_all": "Use for all %{count}",
    "question.or": "or",
    "question.pick_a_match": "Pick one of the matches.",
    "question.no_matches": "No matches",
    "question.searching": "Searching…",
    "question.search_failed": "Search isn't available right now. Try again in a moment.",
}  # type: Dict[str, str]

_PLACEHOLDER = re.compile(r"%\{(\w+)\}")


def flatten_messages(values, prefix=""):
    # type: (Any, str) -> Dict[str, Any]
    """{"status": {"running": "..."}} as {"status.running": "..."}: the messages setting takes
    either shape."""
    flat = {}  # type: Dict[str, Any]
    for key, value in values.items():
        name = "%s%s" % (prefix, key)
        if isinstance(value, Mapping):
            flat.update(flatten_messages(value, name + "."))
        else:
            flat[name] = value
    return flat


def messages():
    # type: () -> Dict[str, str]
    """Every message as the screens say it: the English defaults with the messages setting over
    them."""
    from ._settings import settings

    merged = dict(MESSAGES)
    merged.update(settings().get("messages") or {})
    return merged


def t(key, **values):
    # type: (str, **Any) -> str
    """The message for key (status.running, say), its %{name} placeholders filled from values.
    Raises KeyError for a key that isn't one of MESSAGES'."""
    if key not in MESSAGES:
        raise KeyError("qubesync.kit: no message %r" % (key,))
    text = messages()[key]
    return _PLACEHOLDER.sub(lambda m: str(values[m.group(1)]) if m.group(1) in values else m.group(0), text)
