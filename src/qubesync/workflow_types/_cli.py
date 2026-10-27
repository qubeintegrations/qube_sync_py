"""``qubesync workflows [--drafts] [--check] [--output qube_workflows.py]``

Fetches the app's workflow types with QUBE_API_KEY (from QUBE_BASE_URL, https://qubesync.com
unless set; with or without /api/v2) and writes the typed module. With --check it writes nothing:
it exits 1 when the module is out of date (or QuBe Sync refuses the key), and 0 when it's current
or QuBe Sync can't be reached, with a warning, so CI isn't held up by an outage.
"""

import argparse
import os
import sys
from typing import Any, Callable, List, Mapping, Optional, TextIO

from ..v2 import API_PREFIX, DEFAULT_BASE_URL, APIError, Client
from . import COMMAND, NETWORK_ERRORS, Error, check, render, select

USAGE = "qubesync workflows [--drafts] [--check] [--output PATH]"
DEFAULT_OUTPUT = "qube_workflows.py"


def parser():
    # type: () -> argparse.ArgumentParser
    top = argparse.ArgumentParser(prog="qubesync", description="QuBe Sync's command line tools.")
    commands = top.add_subparsers(dest="command", metavar="command")
    workflows = commands.add_parser(
        "workflows",
        usage=USAGE,
        help="write your app's typed workflow starts",
        description="Writes your app's typed workflow starts from QuBe Sync's workflow types. "
        "QUBE_API_KEY is your app's API key; QUBE_BASE_URL is https://qubesync.com unless set.",
    )
    workflows.add_argument("--drafts", action="store_true", help="type each workflow's draft where it has one")
    workflows.add_argument("--check", action="store_true", help="write nothing; exit 1 when the module is out of date")
    workflows.add_argument("--output", default=DEFAULT_OUTPUT, metavar="PATH", help="the module (%s)" % DEFAULT_OUTPUT)
    return top


def main(argv=None, env=None, out=None, err=None, client_factory=None):
    # type: (Optional[List[str]], Optional[Mapping[str, str]], Optional[TextIO], Optional[TextIO], Optional[Callable[..., Any]]) -> int
    """Runs the command line; returns the exit status. env, out, err and client_factory (called
    with api_key= and base_url=) are for tests."""
    env = os.environ if env is None else env
    out = sys.stdout if out is None else out
    err = sys.stderr if err is None else err
    try:
        args = parser().parse_args(sys.argv[1:] if argv is None else argv)
    except SystemExit as exit:
        return exit.code if isinstance(exit.code, int) else 1
    if args.command != "workflows":
        parser().print_usage(err)
        return 1

    api_key = (env.get("QUBE_API_KEY") or "").strip()
    if not api_key:
        print("qubesync: set QUBE_API_KEY to your app's API key", file=err)
        return 1
    # The site, or its API: QUBE_BASE_URL may name either.
    base_url = (env.get("QUBE_BASE_URL") or "").strip() or DEFAULT_BASE_URL
    base_url = base_url.rstrip("/")
    if base_url.endswith(API_PREFIX):
        base_url = base_url[: -len(API_PREFIX)]
    try:
        factory = client_factory or Client
        client = factory(api_key=api_key, base_url=base_url)
        source = "%s%s/workflows/types" % (client.base_url, API_PREFIX)
        if args.check:
            return _check(client, source, args, out, err)
        return _generate(client, source, args, out, err)
    except (Error, ValueError) as error:
        print("qubesync: %s" % error, file=err)
        return 1


def _generate(client, source, args, out, err):
    # type: (Any, str, argparse.Namespace, TextIO, TextIO) -> int
    try:
        document = client.workflow_types(include_drafts=args.drafts)
    except APIError as error:
        print("qubesync: %s" % error.message, file=err)
        return 1
    except NETWORK_ERRORS as error:
        print("qubesync: couldn't reach QuBe Sync (%s: %s); nothing was written" % (type(error).__name__, error), file=err)
        return 1
    files = render(document, source=source, drafts=args.drafts)
    for warning in files.warnings:
        print("warning: %s" % warning, file=err)
    _write(args.output, files.python, out)
    count = len(select(document, args.drafts))
    print(
        "qubesync: %d workflow%s from %s%s"
        % (count, "" if count == 1 else "s", source, " (with drafts)" if args.drafts else ""),
        file=out,
    )
    return 0


def _check(client, source, args, out, err):
    # type: (Any, str, argparse.Namespace, TextIO, TextIO) -> int
    path = args.output
    if not os.path.isfile(path):
        print("qubesync: %s isn't there: run `%s` to write it" % (path, COMMAND), file=err)
        return 1
    with open(path, encoding="utf-8", newline="") as f:
        existing = f.read()
    result = check(existing, client, source=source, path=path)
    for warning in result.warnings:
        print("warning: %s" % warning, file=err)
    if result.status == "current":
        print("qubesync: %s" % result.message, file=out)
    elif result.status == "unreachable":
        print("warning: %s" % result.message, file=err)
    else:
        print("qubesync: %s" % result.message, file=err)
    return result.exit_status


def _write(path, content, out):
    # type: (str, str, TextIO) -> None
    if os.path.isfile(path):
        with open(path, encoding="utf-8", newline="") as f:
            if f.read() == content:
                print("identical %s" % path, file=out)
                return
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("wrote %s" % path, file=out)
