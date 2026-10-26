"""The kit's tables as SQLAlchemy models, for Flask and FastAPI (SQLAlchemy 1.4 or later):
Connection, Run, QuickbooksRecord and Notification, on their own MetaData (metadata), which
your Alembic picks up:

    # migrations/env.py
    import qubesync.kit.sqlalchemy
    target_metadata = [Base.metadata, qubesync.kit.sqlalchemy.metadata]

then `alembic revision --autogenerate -m "QuBe Sync's tables"`. Or, without Alembic,
qubesync.kit.sqlalchemy.metadata.create_all(engine).

The kit reads and writes them through your session, the db_session setting: a function that
returns the session of the request or job at hand (a scoped_session, or Flask-SQLAlchemy's
db.session). Give your find_record the same session, so a handler's writes and the kit's
commit together. The kit's own steps (applying an event under a run's row lock, a start, a
link outside a handler) commit that session when they end, and roll it back when they raise,
as a Django atomic block would.

The polymorphic columns (owner_type, record_type) keep your model's module and class name
(myapp.models.Invoice), which the kit imports to find the row again; owner_id and record_id
are strings, so integer and UUID keys both fit. input, error, question and links are JSON kept
as text (qubesync.kit._models.dump_json says why).
"""
try:
    import sqlalchemy as _sqlalchemy  # noqa: F401
except ImportError as error:  # pragma: no cover
    raise ImportError('qubesync.kit.sqlalchemy needs SQLAlchemy: pip install "qubesync[flask]" or "qubesync[fastapi]"') from error

import contextlib
import datetime
import uuid
from typing import Any, Dict, Iterator, List, Optional, Tuple

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    Text,
    inspect,
)
from sqlalchemy.exc import IntegrityError, NoInspectionAvailable
from sqlalchemy.orm import declarative_base, relationship, validates
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.types import TypeDecorator

from ._models import ConnectionMixin, QuickbooksRecordMixin, RunMixin, dump_json, family_for, load_json
from ._settings import settings
from ._store import CONNECTION, NOTIFICATION, QUICKBOOKS_RECORD, RUN, UTC, Store, import_path

__all__ = [
    "metadata",
    "Base",
    "Connection",
    "Run",
    "QuickbooksRecord",
    "Notification",
    "JSONText",
    "SQLAlchemyStore",
    "STORE",
]

metadata = MetaData()
Base = declarative_base(metadata=metadata)

# Ids are big integers, as Rails' are; SQLite only autoincrements an INTEGER PRIMARY KEY.
_ID = BigInteger().with_variant(Integer, "sqlite")


def _now():
    # type: () -> datetime.datetime
    # Naive UTC, in a timestamp without a time zone, as Rails keeps them.
    return datetime.datetime.now(UTC).replace(tzinfo=None)


class JSONText(TypeDecorator):
    """JSON kept as text: the same on PostgreSQL, MySQL and SQLite."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return dump_json(value)

    def process_result_value(self, value, dialect):
        return load_json(value)


class Connection(ConnectionMixin, Base):
    __tablename__ = "qube_connections"
    __table_args__ = (
        Index("index_qube_connections_on_qube_id", "qube_id", unique=True),
        Index("index_qube_connections_on_owner", "owner_type", "owner_id"),
    )

    id = Column(_ID, primary_key=True)
    owner_type = Column(String(100), nullable=False)
    owner_id = Column(String(255), nullable=False)
    qube_id = Column(String(255))
    name = Column(String(255))
    status = Column(String(255), nullable=False, default="pending")
    stall_reason = Column(String(255))
    revision = Column(Integer)
    created_at = Column(DateTime, nullable=False, default=_now)
    updated_at = Column(DateTime, nullable=False, default=_now, onupdate=_now)

    runs = relationship("Run", back_populates="connection")
    quickbooks_records = relationship("QuickbooksRecord", back_populates="connection")

    def __repr__(self):
        return "<Connection %s qube_id=%r status=%r>" % (self.id, self.qube_id, self.status)


class Run(RunMixin, Base):
    __tablename__ = "qube_runs"
    __table_args__ = (
        Index("index_qube_runs_on_reference", "reference", unique=True),
        Index("index_qube_runs_on_connection_id", "connection_id"),
        Index("index_qube_runs_on_record_and_operation", "record_type", "record_id", "operation", "created_at"),
    )

    id = Column(_ID, primary_key=True)
    connection_id = Column(BigInteger, ForeignKey("qube_connections.id"), nullable=False)
    operation = Column(String(100), nullable=False)
    record_type = Column(String(100), nullable=False)
    record_id = Column(String(255), nullable=False)
    reference = Column(String(255), nullable=False)
    qube_run_id = Column(String(255))
    input = Column(JSONText)
    revision = Column(Integer, nullable=False, default=0)
    state = Column(String(255), nullable=False, default="starting")
    outcome = Column(String(255))
    error = Column(JSONText)
    cancel_reason = Column(Text)
    ended_at = Column(DateTime)
    question = Column(JSONText)
    links = Column(JSONText)
    run_url = Column(String(255))
    cancel_url = Column(String(255))
    created_at = Column(DateTime, nullable=False, default=_now)
    updated_at = Column(DateTime, nullable=False, default=_now, onupdate=_now)

    connection = relationship("Connection", back_populates="runs")
    # Deleting a run deletes its notifications (ON DELETE CASCADE too, where foreign keys are on).
    notifications = relationship("Notification", cascade="all, delete-orphan")

    def __repr__(self):
        return "<Run %s %s %r state=%r>" % (self.id, self.operation, self.reference, self.state)


class Notification(Base):
    """A notification a run's handler has taken, by its delivery_id: DatabaseDedupe writes it in
    the same transaction as the handler, so a redelivery is skipped and a handler that raised
    runs again. Deleted with its run."""

    __tablename__ = "qube_notifications"
    __table_args__ = (Index("index_qube_notifications_on_run_and_delivery", "run_id", "delivery_id", unique=True),)

    id = Column(_ID, primary_key=True)
    run_id = Column(BigInteger, ForeignKey("qube_runs.id", ondelete="CASCADE"), nullable=False)
    delivery_id = Column(String(100), nullable=False)
    created_at = Column(DateTime, nullable=False, default=_now)


class QuickbooksRecord(QuickbooksRecordMixin, Base):
    __tablename__ = "qube_quickbooks_records"
    # A ListID is unique within its list family (family_for), not within one kind: every item
    # type shares a counter, and so do customers, vendors, employees and other names.
    __table_args__ = (
        Index("index_qube_quickbooks_records_on_qb_id", "connection_id", "list", "qb_id", unique=True),
        Index(
            "index_qube_quickbooks_records_on_record",
            "connection_id",
            "kind",
            "record_type",
            "record_id",
            unique=True,
        ),
    )

    id = Column(_ID, primary_key=True)
    connection_id = Column(BigInteger, ForeignKey("qube_connections.id"), nullable=False)
    kind = Column(String(100), nullable=False)
    list = Column(String(100), nullable=False)
    qb_id = Column(String(100), nullable=False)
    edit_sequence = Column(String(255))
    name = Column(String(255))
    record_type = Column(String(100))
    record_id = Column(String(255))
    created_at = Column(DateTime, nullable=False, default=_now)
    updated_at = Column(DateTime, nullable=False, default=_now, onupdate=_now)

    connection = relationship("Connection", back_populates="quickbooks_records")

    @validates("kind")
    def _family(self, _key, kind):
        self.list = family_for(kind)
        return kind

    def __repr__(self):
        return "<QuickbooksRecord %s %s %s>" % (self.id, self.kind, self.qb_id)


_MODELS = {
    CONNECTION: Connection,
    RUN: Run,
    QUICKBOOKS_RECORD: QuickbooksRecord,
    NOTIFICATION: Notification,
}

# How deep the kit's own transactions are, kept on the session (Session.info).
_DEPTH = "qubesync.depth"


class SQLAlchemyStore(Store):
    """The kit's tables through your SQLAlchemy session (the db_session setting)."""

    integrity_errors = (IntegrityError,)
    not_found_errors = (NoResultFound,)

    def session(self):
        # type: () -> Any
        return settings().db_session()

    def model(self, model_name):
        # type: (str) -> Any
        return _MODELS[model_name]

    def get(self, model_name, id):
        # type: (str, Any) -> Any
        try:
            key = int(str(id))
        except (TypeError, ValueError):
            return None
        return self.session().get(self.model(model_name), key, populate_existing=True)

    def filter(self, model_name, order=None, limit=None, lock=False, **filters):
        # type: (str, Optional[List[str]], Optional[int], bool, **Any) -> List[Any]
        query = self.query(model_name, **filters)
        cls = self.model(model_name)
        for column in order or []:
            descending = column.startswith("-")
            attribute = getattr(cls, column.lstrip("-"))
            query = query.order_by(attribute.desc() if descending else attribute)
        if lock:
            query = query.with_for_update().populate_existing()
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    def query(self, model_name, **filters):
        # type: (str, **Any) -> Any
        cls = self.model(model_name)
        query = self.session().query(cls)
        for column, value in filters.items():
            attribute = getattr(cls, column)
            query = query.filter(attribute.in_(value) if isinstance(value, (list, tuple)) else attribute == value)
        return query

    def save(self, row, fields=None):
        # type: (Any, Optional[List[str]]) -> None
        # A session writes only the columns that changed, so fields needs nothing more.
        session = self.session()
        session.add(row)
        if session.info.get(_DEPTH, 0):
            session.flush()
        else:
            session.commit()

    def delete(self, row):
        # type: (Any) -> None
        session = self.session()
        session.delete(row)
        if session.info.get(_DEPTH, 0):
            session.flush()
        else:
            session.commit()

    @contextlib.contextmanager
    def atomic(self, savepoint=False):
        # type: (bool) -> Iterator[None]
        session = self.session()
        depth = session.info.get(_DEPTH, 0)
        session.info[_DEPTH] = depth + 1
        try:
            if depth == 0:
                try:
                    yield
                    session.commit()
                except BaseException:
                    session.rollback()
                    raise
            elif savepoint:
                with session.begin_nested():
                    yield
            else:
                yield
        finally:
            session.info[_DEPTH] = depth

    @contextlib.contextmanager
    def locked(self, row):
        # type: (Any) -> Iterator[Any]
        cls = type(row)
        with self.atomic():
            fresh = self.session().query(cls).filter(cls.id == row.id).with_for_update().populate_existing().one()
            yield fresh

    def key_for(self, obj):
        # type: (Any) -> Tuple[str, str]
        try:
            mapper = inspect(obj).mapper
        except NoInspectionAvailable:
            cls = type(obj)
            id = getattr(obj, "id", None)
        else:
            # The base of a mapped hierarchy, as Rails keeps an STI model's base class.
            cls = mapper.base_mapper.class_
            id = mapper.primary_key_from_instance(obj)[0]
        return "%s.%s" % (cls.__module__, cls.__qualname__), "" if id is None else str(id)

    def resolve(self, type_name, id):
        # type: (Optional[str], Optional[str]) -> Any
        cls = import_path(type_name) if type_name else None
        if cls is None or id is None:
            return None
        try:
            key = _typed_key(cls, id)
        except (TypeError, ValueError):
            return None
        return self.session().get(cls, key)

    def persisted(self, obj):
        # type: (Any) -> bool
        try:
            return bool(inspect(obj).has_identity)
        except NoInspectionAvailable:
            return getattr(obj, "id", None) is not None

    def now(self):
        # type: () -> datetime.datetime
        return _now()

    def cleanup(self):
        # type: () -> None
        remove = getattr(settings().get("db_session"), "remove", None)
        if callable(remove):
            remove()


def _typed_key(cls, id):
    # type: (Any, str) -> Any
    # The id as the model's primary key takes it: an int, a UUID, or the string.
    column = inspect(cls).primary_key[0]
    try:
        python_type = column.type.python_type
    except NotImplementedError:
        return id
    if python_type is int:
        return int(id)
    if python_type is uuid.UUID:
        return uuid.UUID(id)
    return id


STORE = SQLAlchemyStore()
for _model in (Connection, Run, QuickbooksRecord):
    _model._kit_store = STORE
