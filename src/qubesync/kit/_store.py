"""Where the kit's tables live: the one interface between the kit's code and an ORM.

The kit owns four tables (qube_connections, qube_runs, qube_quickbooks_records and
qube_notifications). Django keeps them as qubesync.django's models; Flask and FastAPI as the
SQLAlchemy models in qubesync.kit.sqlalchemy. Everything the kit does with them (link a
QuickBooks id, apply an event under a run's lock, take a notification once) is written once,
against this interface, so the two ORMs behave the same.

Each model class names its store (_kit_store), so a row always goes back to the ORM it came
from. The job and the routes, which start from an id, use current_store(): the SQLAlchemy
store when the db_session setting is set, else Django's once qubesync.django is installed.
"""
import contextlib
import datetime
import importlib
from typing import Any, Iterator, List, Optional, Tuple

from ._errors import CONFIG_FILE, NotConfigured
from ._settings import settings

__all__ = ["Store", "current_store", "register_store", "utc", "parse_time"]

UTC = datetime.timezone.utc

# The model names a store answers for.
CONNECTION = "connection"
RUN = "run"
QUICKBOOKS_RECORD = "quickbooks_record"
NOTIFICATION = "notification"


class Store(object):
    """What the kit needs from an ORM. Rows are the ORM's own model instances.

    Filters are keyword arguments of column=value; a list or tuple value means "in". order is a
    list of column names, "-" first for descending."""

    # The exceptions a unique-key violation raises.
    integrity_errors = ()  # type: Tuple[type, ...]
    # The exceptions a lookup of one row that isn't there raises (find_record written with get).
    not_found_errors = ()  # type: Tuple[type, ...]

    def model(self, model_name):
        # type: (str) -> Any
        raise NotImplementedError

    def new(self, model_name, **fields):
        # type: (str, **Any) -> Any
        """A row, not saved yet."""
        return self.model(model_name)(**fields)

    def create(self, model_name, **fields):
        # type: (str, **Any) -> Any
        """A row, saved and committed (unless inside atomic)."""
        row = self.new(model_name, **fields)
        with self.atomic():
            self.save(row)
        return row

    def get(self, model_name, id):
        # type: (str, Any) -> Any
        """The row with that id, or None (an id that isn't one, too: "abc" for an integer)."""
        raise NotImplementedError

    def filter(self, model_name, order=None, limit=None, lock=False, **filters):
        # type: (str, Optional[List[str]], Optional[int], bool, **Any) -> List[Any]
        raise NotImplementedError

    def first(self, model_name, order=None, lock=False, **filters):
        # type: (str, Optional[List[str]], bool, **Any) -> Any
        rows = self.filter(model_name, order=order, limit=1, lock=lock, **filters)
        return rows[0] if rows else None

    def exists(self, model_name, **filters):
        # type: (str, **Any) -> bool
        return self.first(model_name, **filters) is not None

    def query(self, model_name, **filters):
        # type: (str, **Any) -> Any
        """The ORM's own query for those rows (a QuerySet, or a SQLAlchemy Query)."""
        raise NotImplementedError

    def save(self, row, fields=None):
        # type: (Any, Optional[List[str]]) -> None
        """Writes row (only those fields, when given, so a row a webhook changed meanwhile
        keeps the rest). Inside atomic it's part of that transaction; outside, it's
        committed."""
        raise NotImplementedError

    def delete(self, row):
        # type: (Any) -> None
        raise NotImplementedError

    @contextlib.contextmanager
    def atomic(self, savepoint=False):
        # type: (bool) -> Iterator[None]
        """A transaction: committed when the block ends, rolled back when it raises. Inside
        another, it joins it, or with savepoint=True is a savepoint of its own, so a unique-key
        violation can be retried without aborting the outer one (PostgreSQL's)."""
        raise NotImplementedError
        yield  # pragma: no cover

    @contextlib.contextmanager
    def locked(self, row):
        # type: (Any) -> Iterator[Any]
        """row read again under a row lock (SELECT ... FOR UPDATE), inside atomic, so two
        workers never apply one row's events at once and what the block writes is saved with
        it or not at all. Yields the row as read."""
        raise NotImplementedError
        yield  # pragma: no cover

    def key_for(self, obj):
        # type: (Any) -> Tuple[str, str]
        """The type and id a polymorphic column keeps for obj (owner_type and owner_id,
        record_type and record_id): a name the store can find its class by, and its id as a
        string, so integer and UUID keys both fit."""
        raise NotImplementedError

    def resolve(self, type_name, id):
        # type: (Optional[str], Optional[str]) -> Any
        """The object key_for named, or None when it isn't there."""
        raise NotImplementedError

    def persisted(self, obj):
        # type: (Any) -> bool
        """obj is saved: it has an id the database gave it."""
        raise NotImplementedError

    def now(self):
        # type: () -> datetime.datetime
        """Now, as the store keeps a datetime."""
        raise NotImplementedError

    def utc(self, value):
        # type: (Optional[datetime.datetime]) -> Optional[datetime.datetime]
        """A datetime the store kept, as an aware UTC one."""
        return utc(value)

    def cleanup(self):
        # type: () -> None
        """After a job on the default queue's thread: give back what it held."""


def utc(value):
    # type: (Optional[datetime.datetime]) -> Optional[datetime.datetime]
    """value as an aware UTC datetime; a naive one is taken as UTC already."""
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def parse_time(value):
    # type: (Any) -> Optional[datetime.datetime]
    """An ISO 8601 time as QuBe Sync writes it ("2026-10-25T13:00:00Z"), aware, or None."""
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith("Z") or text.endswith("z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.datetime.fromisoformat(text)
    except ValueError:
        return None
    return utc(parsed)


def import_path(path):
    # type: (str) -> Any
    """The class a module.qualname path names, or None."""
    # A nested class's qualname has dots too: try each split, longest module first.
    parts = path.split(".")
    for cut in range(len(parts) - 1, 0, -1):
        module_name, qualname = ".".join(parts[:cut]), parts[cut:]
        try:
            target = importlib.import_module(module_name)
        except ImportError:
            continue
        for name in qualname:
            target = getattr(target, name, None)
            if target is None:
                break
        if isinstance(target, type):
            return target
    return None


_registered = []  # type: List[Store]


def register_store(store):
    # type: (Store) -> None
    """The store current_store answers when db_session isn't set: qubesync.django's app
    registers Django's once the apps are ready."""
    _registered[:] = [store]


def current_store():
    # type: () -> Store
    """The store the job and the routes use: SQLAlchemy's when db_session is set, else the
    one an installed adapter registered (Django's)."""
    if settings().is_set("db_session"):
        from .sqlalchemy import STORE

        return STORE
    if _registered:
        return _registered[0]
    raise NotConfigured(
        "db_session",
        "QuBe Sync: the kit's tables aren't set up yet. With SQLAlchemy (Flask, FastAPI), set "
        "db_session= in qubesync.kit.configure, in %s; with Django, add \"qubesync.django\" to "
        "INSTALLED_APPS." % CONFIG_FILE,
    )
