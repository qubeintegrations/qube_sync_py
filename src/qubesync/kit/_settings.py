"""The kit's settings: the only place it reads your app from.

Your app sets them once, in quickbooks_desktop/config.py:

    import qubesync.kit

    qubesync.kit.configure(
        operations={"create_invoice": "quickbooks_desktop.create_invoice.CreateInvoice"},
        connection_events="quickbooks_desktop.connection_events.ConnectionEvents",
        current_account=lambda request: request.user.account,
    )

A setting your app hasn't written raises NotConfigured the first time it's needed, naming that
file, so nothing silently passes. The rest have defaults. The environment is read at first use.
"""
import datetime
import importlib
import os
import threading
from typing import Any, Dict, Optional

from ._errors import CONFIG_FILE, NotConfigured

__all__ = ["Settings", "configure", "settings", "reset"]

# Each setting, and what it is, for the error an unset one raises.
_DESCRIPTIONS = {
    "operations": 'each operation class by its slug: {"create_invoice": CreateInvoice}, or its dotted path',
    "connection_events": "your ConnectionEvents class, or its dotted path",
    "current_account": "a function of the request that returns the signed-in customer's account",
    "authorize_question": (
        "a function of (request, record, run) that returns True when the signed-in user may "
        "answer or search that run's question"
    ),
    "enqueue": 'a function of the delivery ({"kind", "id", "body"}) that hands it to your queue',
    "dedupe": "a store with once(run, delivery_id, fn), or seen(key) and remember(key)",
    "job_attempts": "how many times the default queue runs a delivery whose work raised",
    "db_session": (
        "a function that returns your SQLAlchemy session (a scoped_session, or "
        "Flask-SQLAlchemy's db.session)"
    ),
    "api_key": "your app's QuBe Sync API key",
    "base_url": "QuBe Sync's URL",
    "webhook_secret": "your app's webhook secret, or a list of them while one rotates",
    "webhook_url": "the base of each run's and each connection's webhook URL",
    "client": "a qubesync.Client to use instead of the one made from api_key and base_url",
    "production": "True in production, where Connect refuses simulated=1 (404)",
    "prune_runs_after": "a datetime.timedelta of a day or more: how long ended runs and requests are kept",
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
_CALLABLE = ("current_account", "authorize_question", "enqueue", "db_session")

DEFAULT_JOB_ATTEMPTS = 10


class Settings(object):
    """The settings as configure left them. Read one as an attribute (settings().operations);
    an unset one without a default raises NotConfigured."""

    def __init__(self):
        # type: () -> None
        self._values = {}  # type: Dict[str, Any]
        self._lock = threading.Lock()
        self._client = None  # type: Any
        self._dedupe = None  # type: Any

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
                    self._values[name] = {str(slug): op for slug, op in value.items()}
                else:
                    self._values[name] = value
            if {"api_key", "base_url", "client"} & set(values):
                self._client = None

    def clear(self):
        # type: () -> None
        with self._lock:
            self._values = {}
            self._client = None
            self._dedupe = None

    def is_set(self, name):
        # type: (str) -> bool
        """True when configure set it, or (for the four read from it) the environment has it."""
        if name in self._values:
            return True
        return _env(_ENVIRONMENT.get(name)) is not None

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
            value = values[name]
            return value.rstrip("/") if name == "webhook_url" else value
        if name in _ENVIRONMENT:
            value = _env(_ENVIRONMENT[name]) or _ENVIRONMENT_DEFAULTS.get(name)
            if value:
                return value.rstrip("/") if name == "webhook_url" else value
            raise NotConfigured(
                name,
                "QuBe Sync: %s isn't set yet. Set %s in the environment, or %s= in "
                "qubesync.kit.configure, in %s." % (name, _ENVIRONMENT[name], name, CONFIG_FILE),
            )
        if name == "job_attempts":
            return DEFAULT_JOB_ATTEMPTS
        if name == "prune_runs_after":
            return None  # off until set
        if name == "dedupe":
            return self._default_dedupe()
        if name == "authorize_question":
            from ._web import owner_answers

            return owner_answers
        raise NotConfigured(
            name,
            "QuBe Sync: %s isn't set yet. Set %s= (%s) in qubesync.kit.configure, in %s."
            % (name, name, _DESCRIPTIONS[name], CONFIG_FILE),
        )

    def _default_dedupe(self):
        # type: () -> Any
        # The database table (qube_notifications), written in the handler's transaction.
        with self._lock:
            if self._dedupe is None:
                from ._defaults import DatabaseDedupe

                self._dedupe = DatabaseDedupe()
            return self._dedupe

    def operation_class(self, slug):
        # type: (Any) -> Any
        """The operation class for a slug, or None when none of your operations has it. A
        class named by its dotted path is imported here, at first use. A fixed list, so a
        class is never looked up from anything a request says. Raises NotConfigured when
        operations isn't set."""
        operations = self.operations
        value = operations.get(slug) if isinstance(slug, str) else None
        if value is None:
            return None
        return _resolve(value)

    def connection_events_class(self):
        # type: () -> Any
        return _resolve(self.connection_events)

    def __repr__(self):
        # Never the API key or a webhook secret.
        parts = []
        for name in sorted(self._values):
            shown = "[hidden]" if name in _SECRET else repr(self._values[name])
            parts.append("%s=%s" % (name, shown))
        for name in sorted(_ENVIRONMENT):
            if name not in self._values and _env(_ENVIRONMENT[name]) is not None:
                shown = "[hidden]" if name in _SECRET else repr(os.environ[_ENVIRONMENT[name]])
                parts.append("%s=%s (from %s)" % (name, shown, _ENVIRONMENT[name]))
        return "<qubesync.kit settings %s>" % " ".join(parts)

    __str__ = __repr__


def _env(variable):
    # type: (Optional[str]) -> Optional[str]
    value = os.environ.get(variable) if variable else None
    if value is None or not value.strip():
        return None
    return value


def _validate(name, value):
    # type: (str, Any) -> None
    if value is None:
        return
    if name == "operations":
        if not isinstance(value, dict):
            raise TypeError("qubesync.kit: operations is a dict of slug to operation class, in %s" % CONFIG_FILE)
        for slug, operation in value.items():
            if not isinstance(slug, str) or not slug:
                raise TypeError("qubesync.kit: each operation's slug is a non-empty string, not %r" % (slug,))
            if not isinstance(operation, (type, str)):
                raise TypeError("qubesync.kit: operations[%r] is a class or its dotted path" % slug)
    elif name == "connection_events":
        if not isinstance(value, (type, str)):
            raise TypeError("qubesync.kit: connection_events is a class or its dotted path")
    elif name in _CALLABLE:
        if not callable(value):
            raise TypeError(
                "qubesync.kit: %s must be callable (%s), in %s" % (name, _DESCRIPTIONS[name], CONFIG_FILE)
            )
    elif name == "dedupe":
        if not _dedupe_store(value):
            raise TypeError(
                "qubesync.kit: dedupe needs once(run, delivery_id, fn), or seen(key) and remember(key), in %s"
                % CONFIG_FILE
            )
    elif name == "job_attempts":
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise TypeError("qubesync.kit: job_attempts is a whole number of 1 or more, in %s" % CONFIG_FILE)
    elif name == "webhook_secret":
        secrets = [value] if isinstance(value, (str, bytes)) else value
        if not isinstance(secrets, (list, tuple)) or not secrets:
            raise TypeError("qubesync.kit: webhook_secret is a string, or a list of them")
    elif name == "prune_runs_after":
        if not isinstance(value, datetime.timedelta) or value < datetime.timedelta(days=1):
            raise TypeError(
                "qubesync.kit: prune_runs_after is None or a datetime.timedelta of a day or more, in %s" % CONFIG_FILE
            )
    elif name == "production":
        if not isinstance(value, bool):
            raise TypeError("qubesync.kit: production is True or False, in %s" % CONFIG_FILE)
    elif name in ("api_key", "base_url", "webhook_url"):
        if not isinstance(value, str) or not value.strip():
            raise TypeError("qubesync.kit: %s is a non-empty string" % name)


def _dedupe_store(store):
    # type: (Any) -> bool
    """Answers once(run, delivery_id, fn), or seen(key) and remember(key)."""
    if callable(getattr(store, "once", None)):
        return True
    return callable(getattr(store, "seen", None)) and callable(getattr(store, "remember", None))


def _resolve(value):
    # type: (Any) -> Any
    if not isinstance(value, str):
        return value
    module, sep, attribute = value.rpartition(":")
    if not sep:
        module, _, attribute = value.rpartition(".")
    if not module or not attribute:
        raise ValueError("qubesync.kit: %r isn't a dotted path to a class" % value)
    return getattr(importlib.import_module(module), attribute)


_SETTINGS = Settings()


def configure(**values):
    # type: (**Any) -> Settings
    """Sets the kit's settings (any of them; a later call changes only those it names, and
    None unsets one). Call it once at startup, from quickbooks_desktop/config.py.

    operations          slug -> operation class, or its dotted path (imported at first use)
    connection_events   your ConnectionEvents class, or its dotted path
    current_account     (request) -> the signed-in customer's account, which owns its
                        connections; None answers 401
    authorize_question  (request, record, run) -> True when the signed-in user may answer or
                        search that run's question, or send its start again. Only True
                        allows. Default: current_account owns the run's connection
    enqueue             (delivery) -> hands {"kind", "id", "body"} to your queue, whose job
                        calls qubesync.kit.run(kind, id, body). False or an exception answers
                        503. Default: a worker thread in this process, with retries
    job_attempts        how many times the default queue runs a delivery whose work raised.
                        Default 10
    dedupe              once(run, delivery_id, fn), or seen(key) and remember(key). Default:
                        the qube_notifications table, in the handler's transaction
    db_session          () -> your SQLAlchemy session, for Flask and FastAPI (a scoped_session,
                        or Flask-SQLAlchemy's db.session). Django needs none
    api_key, base_url, webhook_secret, webhook_url
                        default to QUBE_API_KEY, QUBE_URL (https://qubesync.com),
                        QUBE_WEBHOOK_SECRET and QUBE_WEBHOOK_URL, read at first use
    client              a qubesync.Client to use instead (tests, or one made your way)
    production          True where Connect must refuse simulated=1 (404). Default: the
                        adapter's guess (Django: not DEBUG; Flask: not debug or testing;
                        FastAPI: not app.debug); with none, True
    prune_runs_after    a timedelta of a day or more: qubesync.kit.prune_runs() deletes ended
                        runs and requests older than that. Default None: kept
    """
    _SETTINGS.update(**values)
    return _SETTINGS


def settings():
    # type: () -> Settings
    """The kit's settings, as configure left them."""
    return _SETTINGS


def reset():
    # type: () -> None
    """Unsets every setting, forgets the client and stops the default queue: for tests."""
    _SETTINGS.clear()
    from ._defaults import _reset_defaults

    _reset_defaults()
