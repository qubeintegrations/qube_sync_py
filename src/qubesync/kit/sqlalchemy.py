"""The kit's tables as SQLAlchemy models, for Flask and FastAPI (SQLAlchemy 1.4 or later):
Connection, Run, QuickbooksRecord, Notification, SyncMark, QueuedRequest and RequestDelivery,
on their own MetaData (metadata), which your Alembic picks up:

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
    cast,
    func,
    inspect,
    select,
)
from sqlalchemy.exc import IntegrityError, NoInspectionAvailable
from sqlalchemy.orm import declarative_base, relationship, validates
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.types import TypeDecorator

from ._models import (
    ConnectionMixin,
    QueuedRequestMixin,
    QuickbooksRecordMixin,
    RunMixin,
    dump_json,
    family_for,
    load_json,
)
from ._settings import settings
from ._store import (
    CONNECTION,
    NOTIFICATION,
    QUEUED_REQUEST,
    QUICKBOOKS_RECORD,
    REQUEST_DELIVERY,
    RUN,
    SYNC_MARK,
    UTC,
    Store,
    import_path,
)

__all__ = [
    "metadata",
    "Base",
    "Connection",
    "Run",
    "QuickbooksRecord",
    "Notification",
    "SyncMark",
    "QueuedRequest",
    "RequestDelivery",
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

    # passive_deletes="all": disconnect deletes these itself, so deleting the row never nulls theirs.
    runs = relationship("Run", back_populates="connection", passive_deletes="all")
    quickbooks_records = relationship("QuickbooksRecord", back_populates="connection", passive_deletes="all")
    queued_requests = relationship("QueuedRequest", back_populates="connection", passive_deletes="all")

    def __repr__(self):
        return "<Connection %s qube_id=%r status=%r>" % (self.id, self.qube_id, self.status)


class Run(RunMixin, Base):
    __tablename__ = "qube_runs"
    __table_args__ = (
        Index("index_qube_runs_on_reference", "reference", unique=True),
        Index("index_qube_runs_on_connection_id", "connection_id"),
        Index("index_qube_runs_on_record_and_operation", "record_type", "record_id", "operation", "created_at"),
        # For SyncStatus and the connection's scopes.
        Index(
            "index_qube_runs_on_connection_record_and_state",
            "connection_id",
            "record_type",
            "record_id",
            "operation",
            "state",
        ),
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
        # A record's link on a connection whatever its kind: SyncStatus and the scopes.
        Index("index_qube_quickbooks_records_on_connection_and_record", "connection_id", "record_type", "record_id"),
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


class SyncMark(Base):
    """When a connection's last completed run of a workflow started (Connection.last_synced_at):
    a sync's next since, kept apart from qube_runs so pruning runs never loses it."""

    __tablename__ = "qube_sync_marks"
    __table_args__ = (
        Index("index_qube_sync_marks_on_connection_and_workflow", "connection_id", "workflow", unique=True),
    )

    id = Column(_ID, primary_key=True)
    connection_id = Column(BigInteger, ForeignKey("qube_connections.id", ondelete="CASCADE"), nullable=False)
    workflow = Column(String(100), nullable=False)
    started_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=_now)
    updated_at = Column(DateTime, nullable=False, default=_now, onupdate=_now)


class QueuedRequest(QueuedRequestMixin, Base):
    __tablename__ = "qube_requests"
    __table_args__ = (
        Index("index_qube_requests_on_reference", "reference", unique=True),
        Index(
            "index_qube_requests_on_connection_and_record",
            "connection_id",
            "record_type",
            "record_id",
            "operation",
            "created_at",
        ),
    )

    id = Column(_ID, primary_key=True)
    connection_id = Column(BigInteger, ForeignKey("qube_connections.id"), nullable=False)
    operation = Column(String(100), nullable=False)
    record_type = Column(String(100), nullable=False)
    record_id = Column(String(255), nullable=False)
    reference = Column(String(255), nullable=False)
    qube_id = Column(String(255))
    state = Column(String(50), nullable=False, default="queued")
    params = Column(JSONText)
    error = Column(JSONText)
    pages_answered = Column(Integer, nullable=False, default=0)
    last_page = Column(Integer)
    ended_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=_now)
    updated_at = Column(DateTime, nullable=False, default=_now, onupdate=_now)

    connection = relationship("Connection", back_populates="queued_requests")
    # Deleting a request deletes its deliveries (ON DELETE CASCADE too, where foreign keys are on).
    deliveries = relationship("RequestDelivery", cascade="all, delete-orphan")

    def __repr__(self):
        return "<QueuedRequest %s %s %r state=%r>" % (self.id, self.operation, self.reference, self.state)


class RequestDelivery(Base):
    """A request webhook its handler has taken, by page_request_id:state, written in the
    handler's transaction. Deleted with its request."""

    __tablename__ = "qube_request_deliveries"
    __table_args__ = (
        Index("index_qube_request_deliveries_on_request_and_key", "request_id", "dedupe_key", unique=True),
    )

    id = Column(_ID, primary_key=True)
    request_id = Column(BigInteger, ForeignKey("qube_requests.id", ondelete="CASCADE"), nullable=False)
    dedupe_key = Column(String(200), nullable=False)
    page = Column(Integer)
    state = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False, default=_now)


_MODELS = {
    CONNECTION: Connection,
    RUN: Run,
    QUICKBOOKS_RECORD: QuickbooksRecord,
    NOTIFICATION: Notification,
    SYNC_MARK: SyncMark,
    QUEUED_REQUEST: QueuedRequest,
    REQUEST_DELIVERY: RequestDelivery,
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
            negated = column.endswith("__not")
            attribute = getattr(cls, column[: -len("__not")] if negated else column)
            condition = attribute.in_(value) if isinstance(value, (list, tuple)) else attribute == value
            query = query.filter(~condition if negated else condition)
        return query

    def prunable(self, model_name, cutoff, states=None):
        # type: (str, datetime.datetime, Optional[Tuple[str, ...]]) -> Any
        cls = self.model(model_name)
        query = self.session().query(cls)
        if states is None:
            return query.filter(cls.ended_at < cutoff)
        return query.filter(func.coalesce(cls.ended_at, cls.updated_at) < cutoff, cls.state.in_(list(states)))

    def ids(self, query, limit):
        # type: (Any, int) -> List[Any]
        cls = query.column_descriptions[0]["entity"]
        return [row[0] for row in query.with_entities(cls.id).order_by(cls.id).limit(limit)]

    def delete_all(self, model_name, **filters):
        # type: (str, **Any) -> int
        # "fetch": the deleted rows leave the session too, so none is read back stale.
        session = self.session()
        count = self.query(model_name, **filters).delete(synchronize_session="fetch")
        if not session.info.get(_DEPTH, 0):
            session.commit()
        return count

    def with_link(self, query, connection_id, linked):
        # type: (Any, Any, bool) -> Any
        query, model = self._query_of(query)
        found = self._exists(QuickbooksRecord, model, connection_id=connection_id)
        return _where(query, found if linked else ~found)

    def with_run(self, query, connection_id, operation, states):
        # type: (Any, Any, str, Tuple[str, ...]) -> Any
        query, model = self._query_of(query)
        found = self._exists(Run, model, Run.state.in_(list(states)), connection_id=connection_id, operation=operation)
        return _where(query, found)

    def _query_of(self, query):
        # type: (Any) -> Tuple[Any, Any]
        # A model class, a Query or a Select, and the model it's of.
        if isinstance(query, type):
            return self.session().query(query), query
        return query, query.column_descriptions[0]["entity"]

    def _exists(self, table, model, *conditions, **columns):
        # type: (Any, Any, *Any, **Any) -> Any
        mapper = inspect(model)
        base = mapper.base_mapper.class_
        type_name = "%s.%s" % (base.__module__, base.__qualname__)
        id_as_text = cast(mapper.primary_key[0], String(255))
        matches = [getattr(table, name) == value for name, value in columns.items()]
        return (
            select(table.id)
            .where(table.record_type == type_name, table.record_id == id_as_text, *(matches + list(conditions)))
            .exists()
        )

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


def _where(query, condition):
    # type: (Any, Any) -> Any
    return query.filter(condition) if hasattr(query, "filter") else query.where(condition)


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
for _model in (Connection, Run, QuickbooksRecord, QueuedRequest):
    _model._kit_store = STORE
