"""Typed workflow starts: turns an app's workflow input types (``Client.workflow_types``, GET
/api/v2/workflows/types) into one Python module you check in, with a namespace per workflow
(``add_transaction``), a start method and an input builder per branch of its input, and a
TypedDict per input whose operation bodies are typed as the operation's own params
(``qubesync.operations.invoice.InvoiceCreateParams``).

    from qubesync import workflow_types

    files = workflow_types.render(client.workflow_types(), source="https://qubesync.com/api/v2/workflows/types")
    with open("qube_workflows.py", "w") as f:
        f.write(files.python)

``qubesync workflows`` (and ``python -m qubesync workflows``) does this, and ``--check`` compares
a written module with what QuBe Sync serves. The same document gives a byte-identical module.
"""

import re
from typing import Any, Dict, List, NamedTuple, Optional

import requests

from ..v2 import NOT_MODIFIED, APIError
from ._renderer import Renderer
from ._workflow import Error, Workflow

__all__ = ["render", "check", "header", "changes", "select", "Files", "Header", "Check", "Error", "COMMAND"]

COMMAND = "qubesync workflows"

# What a call that got no answer raises (a timeout, a refused or dropped connection).
NETWORK_ERRORS = (requests.ConnectionError, requests.Timeout, OSError)


class Files(NamedTuple):
    """A render: the module's source, and the digest and drafts flag its header records."""

    python: str
    digest: str
    drafts: bool
    warnings: List[str]


class Header(NamedTuple):
    """What a generated module's header records: the document's digest, and whether it was made
    with drafts."""

    digest: str
    drafts: bool


class Check(NamedTuple):
    """What a --check found. status is "current", "stale" (changes lists the workflows, as
    "add_transaction (changed)", "resolve (new)", "upsert (removed)"), "unreachable" (QuBe Sync
    didn't answer, or answered 5xx: nothing was checked) or "error" (a 401, another 4xx, a file
    without a header). message is one line."""

    status: str
    message: str
    changes: List[str]
    warnings: List[str]

    @property
    def exit_status(self):
        # type: () -> int
        """0 when the module is current, and when QuBe Sync couldn't be reached (CI warns, and
        the module keeps working); 1 otherwise."""
        return 0 if self.status in ("current", "unreachable") else 1


def render(document, source, drafts=False, command=COMMAND):
    # type: (Any, str, bool, str) -> Files
    """Renders a document's workflows: each published one at its published version, or with
    ``drafts=True`` each workflow's draft where it has one. ``source`` is the URL the header
    names, ``command`` the command it says to run again."""
    document = validate(document)
    workflows = [Workflow(key, entry if isinstance(entry, dict) else {}) for key, entry in select(document, drafts).items()]
    again = command + " --drafts" if drafts else command
    lines = header_lines(source, again, document["digest"], drafts)
    return Files(
        python=Renderer(workflows, lines).render(),
        digest=document["digest"],
        drafts=drafts,
        warnings=warnings(document),
    )


def select(document, drafts):
    # type: (Dict[str, Any], bool) -> Dict[str, Any]
    """The workflows a render types, by key, sorted: the published ones, each replaced by its
    draft when drafts is true, and the drafts of workflows never published."""
    chosen = dict(document.get("workflows") or {})
    if drafts:
        chosen.update(document.get("drafts") or {})
    return dict(sorted(chosen.items()))


def header(source):
    # type: (str) -> Optional[Header]
    """The digest and drafts a generated module's header records, or None when it has none."""
    digest = drafts = None
    for line in (source or "").splitlines()[:10]:
        found = re.match(r"\A# digest: (\S+)\s*\Z", line)
        if found and digest is None:
            digest = found.group(1)
        found = re.match(r"\A# drafts: (true|false)\s*\Z", line)
        if found and drafts is None:
            drafts = found.group(1) == "true"
    if digest is None or drafts is None:
        return None
    return Header(digest, drafts)


def changes(before, after):
    # type: (str, str) -> List[str]
    """The workflows whose generated section differs between two renders, by key, sorted."""
    old = workflow_sections(before)
    new = workflow_sections(after)
    out = []
    for key in sorted(set(old) | set(new)):
        if key not in old:
            out.append("%s (new)" % key)
        elif key not in new:
            out.append("%s (removed)" % key)
        elif old[key] != new[key]:
            out.append("%s (changed)" % key)
    return out


def check(existing, client, source, path, command=COMMAND):
    # type: (str, Any, str, str, str) -> Check
    """Compares a generated module (its source) with what QuBe Sync serves now, fetched with the
    drafts flag the module records. client is a qubesync.Client, or anything answering
    workflow_types as it does; path names the module in messages."""
    recorded = header(existing)
    if recorded is None:
        return Check("error", "%s has no digest header: run `%s` to write it" % (path, command), [], [])

    again = command + " --drafts" if recorded.drafts else command
    try:
        document = client.workflow_types(include_drafts=recorded.drafts, etag=recorded.digest)
    except APIError as error:
        if error.status >= 500:
            return unreachable("QuBe Sync answered %d" % error.status)
        return Check("error", error.message, [], [])
    except NETWORK_ERRORS as error:
        return unreachable("%s: %s" % (type(error).__name__, error))
    if document is NOT_MODIFIED:
        return current(path, [])

    files = render(document, source=source, drafts=recorded.drafts, command=command)
    if files.digest == recorded.digest:
        return current(path, files.warnings)

    changed = changes(existing, files.python)
    what = ", ".join(changed) if changed else "the served types changed"
    message = "%s is out of date (%s): run `%s` and commit the result" % (path, what, again)
    return Check("stale", message, changed, files.warnings)


def current(path, found):
    # type: (str, List[str]) -> Check
    return Check("current", "%s is up to date" % path, [], found)


def unreachable(why):
    # type: (str) -> Check
    return Check("unreachable", "couldn't reach QuBe Sync (%s), so the workflow types weren't checked" % why, [], [])


def warnings(document):
    # type: (Dict[str, Any]) -> List[str]
    """A served operations_digest other than this version's: the document's $operation ids may
    name operations it doesn't type."""
    from .._version import __version__
    from ..operations import DIGEST

    served = document.get("operations_digest")
    if served is None or served == DIGEST:
        return []
    return [
        "QuBe Sync's operations (%s) aren't the ones qubesync %s was generated from (%s): an operation "
        "it doesn't know is typed as a plain dict. Update qubesync to type it." % (served, __version__, DIGEST)
    ]


def validate(document):
    # type: (Any) -> Dict[str, Any]
    if not (
        isinstance(document, dict)
        and isinstance(document.get("digest"), str)
        and isinstance(document.get("workflows"), dict)
    ):
        raise Error("not a workflow types document (expected digest and workflows)")
    if not re.match(r"\A[\w:.\-]+\Z", document["digest"]):
        raise Error("not a workflow types document: digest %r" % (document["digest"],))
    return document


def header_lines(source, command, digest, drafts):
    # type: (str, str, str, bool) -> List[str]
    source = " ".join(str(source).split())
    return [
        "# Generated by `%s` from %s: don't edit." % (command, source),
        "# Run it again when a workflow changes; `%s --check` fails while this file is out of date." % command,
        "# digest: %s" % digest,
        "# drafts: %s" % ("true" if drafts else "false"),
    ]


def workflow_sections(source):
    # type: (str) -> Dict[str, str]
    """Each workflow's section of a generated module (from its ``# -- <key> ---`` line to the
    next), by key."""
    sections = {}  # type: Dict[str, List[str]]
    key = None
    for line in (source or "").splitlines():
        found = re.match(r"\A# -- ([a-z][a-z0-9_]*) -+\Z", line)
        if found:
            key = found.group(1)
            sections[key] = []
        if key is not None:
            sections[key].append(line)
    return {key: "\n".join(lines).rstrip() for key, lines in sections.items()}
