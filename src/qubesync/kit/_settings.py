"""The kit's settings: the one place it reads your app from.

Your app sets them once, in quickbooks_desktop/config.py:

    import qubesync.kit

    qubesync.kit.configure(
        operations={"create_invoice": CreateInvoice},
        connection=Connection,
        current_account=lambda request: request.user.account,
        authorize_question=lambda request, record, operation: record.account_id == request.user.account_id,
    )

A setting your app hasn't written raises NotConfigured the first time it's needed, naming that
file, so nothing silently passes. The rest have defaults.
"""
import importlib
import os
import threading
from typing import Any, Callable, Dict, Optional

from ..errors import QubeSyncError

__all__ = ["NotConfigured", "Settings", "configure", "settings", "reset"]

CONFIG_FILE = "quickbooks_desktop/config.py"

# Each setting, and what it is, for the error an unset one raises and for repr.
_DESCRIPTIONS = {
    "operations": 'each operation class by the slug in its webhook URL: {"create_invoice": CreateInvoice}',
    "connection": "the connection class (a ConnectionEvents subclass)",
    "current_account": "a function of the request that returns the signed-in customer's account",
    "authorize_question": (
        "a function of (request, record, operation) that returns True when the signed-in user "
        "may answer or search that record's question (anything but True refuses)"
    ),
    "enqueue": "a function of (operation, record_id, body) that hands a verified webhook to your queue",
    "dedupe": "a store with seen(key) and remember(key), for notification delivery ids",
    "api_key": "your app's QuBe Sync API key",
    "base_url": "QuBe Sync's URL",
    "webhook_secret": "your app's webhook secret, or a list of them while one rotates",
    "webhook_url": "the base of each run's and each connection's webhook URL",
    "client": "a qubesync.Client to use instead of the one made from api_key and base_url",
    "render_question": "a function of the question template's context that returns its HTML",
}

# Read from the environment at first use, when configure didn't set them.
_ENVIRONMENT = {
    "api_key": "QUBE_API_KEY",
    "base_url": "QUBE_URL",
    "webhook_secret": "QUBE_WEBHOOK_SECRET",
    "webhook_url": "QUBE_WEBHOOK_URL",
}
_ENVIRONMENT_DEFAULTS = {"base_url": "https://qubesync.com"}

_SECRET = ("api_key", "webhook_secret")


class NotConfigured(QubeSyncError, LookupError):
    """A setting the kit needs and your app hasn't written. Its message names the setting and
    where to write it."""

    def __init__(self, name, message=None):
        # type: (str, Optional[str]) -> None
        self.setting = name
        if message is None:
            message = "qubesync.kit: the %s setting isn't set (%s). Set it with qubesync.kit.configure(%s=...) in your app's %s." % (
                name,
                _DESCRIPTIONS.get(name, name),
                name,
                CONFIG_FILE,
            )
        super().__init__(message)


class Settings(object):
    """The settings as configure left them. Read one as an attribute (settings().operations);
    an unset one without a default raises NotConfigured."""

    def __init__(self):
        # type: () -> None
        self._values = {}  # type: Dict[str, Any]
        self._lock = threading.Lock()
        self._client = None  # type: Any

    # -- writing ---------------------------------------------------------------------------

    def update(self, **values):
        # type: (**Any) -> None
        unknown = sorted(set(values) - set(_DESCRIPTIONS))
        if unknown:
            raise TypeError(
                "qubesync.kit.configure: no such setting %s; the settings are %s"
                % (", ".join(unknown), ", ".join(sorted(_DESCRIPTIONS)))
            )
        for name, value in values.items():
            _validate(name, value)
        with self._lock:
            for name, value in values.items():
                if value is None:
                    self._values.pop(name, None)
                elif name == "operations":
                    self._values[name] = dict(value)
                else:
                    self._values[name] = value
            if {"api_key", "base_url", "client"} & set(values):
                self._client = None

    def clear(self):
        # type: () -> None
        with self._lock:
            self._values = {}
            self._client = None

    # -- reading ---------------------------------------------------------------------------

    def is_set(self, name):
        # type: (str) -> bool
        """True when configure set it, or (for the four read from it) the environment has it."""
        if name in self._values:
            return True
        variable = _ENVIRONMENT.get(name)
        return bool(variable and os.environ.get(variable))

    def get(self, name, default=None):
        # type: (str, Any) -> Any
        """The setting, or default when it isn't set: never raises."""
        try:
            return getattr(self, name)
        except NotConfigured:
            return default

    def __getattr__(self, name):
        # type: (str) -> Any
        if name.startswith("_") or name not in _DESCRIPTIONS:
            raise AttributeError(name)
        values = self.__dict__["_values"]
        if name in values:
            return values[name]
        if name in _ENVIRONMENT:
            value = os.environ.get(_ENVIRONMENT[name]) or _ENVIRONMENT_DEFAULTS.get(name)
            if value:
                return value
            raise NotConfigured(
                name,
                "qubesync.kit: %s isn't set: put %s in the environment (`qube env --write .env` "
                "writes it), or set it with qubesync.kit.configure(%s=...) in your app's %s."
                % (name, _ENVIRONMENT[name], name, CONFIG_FILE),
            )
        if name == "dedupe":
            from ._defaults import memory_dedupe

            return memory_dedupe()
        if name == "enqueue":
            from ._defaults import in_process_enqueue

            return in_process_enqueue
        raise NotConfigured(name)

    def operation(self, slug):
        # type: (str) -> Any
        """The operation class for a slug, or None when no operation has it. A class named by
        its dotted path ("quickbooks_desktop.create_invoice.CreateInvoice") is imported here,
        at first use. Raises NotConfigured when operations isn't set."""
        operations = self.operations
        value = operations.get(slug) if isinstance(slug, str) else None
        if value is None:
            return None
        if isinstance(value, str):
            value = _import(value)
            with self._lock:
                self._values["operations"][slug] = value
        return value

    def connection_class(self):
        # type: () -> Any
        value = self.connection
        if isinstance(value, str):
            value = _import(value)
            with self._lock:
                self._values["connection"] = value
        return value

    def __repr__(self):
        parts = []
        for name in sorted(self._values):
            value = self._values[name]
            shown = "<hidden>" if name in _SECRET else repr(value)
            parts.append("%s=%s" % (name, shown))
        for name in sorted(_ENVIRONMENT):
            if name not in self._values and os.environ.get(_ENVIRONMENT[name]):
                shown = "<hidden>" if name in _SECRET else repr(os.environ[_ENVIRONMENT[name]])
                parts.append("%s=%s (from %s)" % (name, shown, _ENVIRONMENT[name]))
        return "<qubesync.kit settings %s>" % " ".join(parts)

    __str__ = __repr__


def _validate(name, value):
    # type: (str, Any) -> None
    if value is None:
        return
    if name == "operations":
        if not isinstance(value, dict):
            raise TypeError("qubesync.kit: operations is a dict of slug to operation class")
        for slug, operation in value.items():
            if not isinstance(slug, str) or not slug:
                raise TypeError("qubesync.kit: each operation's slug is a non-empty string, not %r" % (slug,))
            if slug == "connection":
                raise ValueError(
                    "qubesync.kit: connection is the connection's own slug, not an operation's: "
                    "set connection=YourConnectionClass instead"
                )
            if "/" in slug:
                raise ValueError("qubesync.kit: a slug is one URL segment, without /: %r" % slug)
            if not (isinstance(operation, (type, str))):
                raise TypeError("qubesync.kit: operations[%r] is a class or its dotted path" % slug)
    elif name == "connection":
        if not isinstance(value, (type, str)):
            raise TypeError("qubesync.kit: connection is a class or its dotted path")
    elif name in ("current_account", "authorize_question", "enqueue", "render_question"):
        if not callable(value):
            raise TypeError("qubesync.kit: %s is a function (%s)" % (name, _DESCRIPTIONS[name]))
    elif name == "dedupe":
        if not (callable(getattr(value, "seen", None)) and callable(getattr(value, "remember", None))):
            raise TypeError("qubesync.kit: dedupe has seen(key) and remember(key)")
    elif name == "webhook_secret":
        secrets = [value] if isinstance(value, (str, bytes)) else value
        if not isinstance(secrets, (list, tuple)) or not secrets:
            raise TypeError("qubesync.kit: webhook_secret is a string, or a list of them")
    elif name in ("api_key", "base_url", "webhook_url"):
        if not isinstance(value, str) or not value.strip():
            raise TypeError("qubesync.kit: %s is a non-empty string" % name)


def _import(path):
    # type: (str) -> Any
    module, sep, attribute = path.rpartition(":")
    if not sep:
        module, _, attribute = path.rpartition(".")
    if not module or not attribute:
        raise ValueError("qubesync.kit: %r isn't a dotted path to a class" % path)
    return getattr(importlib.import_module(module), attribute)


_SETTINGS = Settings()


def configure(**values):
    # type: (**Any) -> Settings
    """Sets the kit's settings (any of them; a later call changes only those it names, and
    None unsets one). Call it once at startup, from quickbooks_desktop/config.py.

    operations          slug -> operation class, or its dotted path (imported at first use)
    connection          the connection class (ConnectionEvents), or its dotted path
    current_account     (request) -> the signed-in customer's account
    authorize_question  (request, record, operation) -> True when the signed-in user may answer
                        or search that record's question (operation is its slug). Only True
                        allows; until it's set, every answer and search is refused
    enqueue             (operation, record_id, body) -> None: hands a verified webhook to your
                        queue, whose job calls qubesync.kit.run(operation, record_id, body).
                        Default: one worker thread in this process (not durable)
    dedupe              an object with seen(key) and remember(key). Default: in memory
    api_key, base_url, webhook_secret, webhook_url
                        default to QUBE_API_KEY, QUBE_URL (https://qubesync.com),
                        QUBE_WEBHOOK_SECRET and QUBE_WEBHOOK_URL, read at first use
    client              a qubesync.Client to use instead (tests, or one made your way)
    render_question     (context) -> HTML, instead of the packaged question template
    """
    _SETTINGS.update(**values)
    return _SETTINGS


def settings():
    # type: () -> Settings
    """The kit's settings, as configure left them."""
    return _SETTINGS


def reset():
    # type: () -> None
    """Unsets every setting and forgets the client: for tests."""
    _SETTINGS.clear()
    from ._defaults import _reset_defaults

    _reset_defaults()
