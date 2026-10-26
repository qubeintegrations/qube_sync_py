"""SQLAlchemy models for the Flask and FastAPI tests: an account, its invoices and its
customers, none with a QuBe column, on a SQLite file (so each thread has a connection of its
own), in WAL mode with SQLAlchemy's recipe for SQLite's transactions (pysqlite's own handling
breaks SAVEPOINT)."""
import os
import tempfile

from sqlalchemy import Column, ForeignKey, Integer, String, create_engine, event
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

import qubesync.kit.sqlalchemy as qube_tables

Base = declarative_base()
engine = create_engine(
    "sqlite:///" + os.path.join(tempfile.mkdtemp(), "kit.sqlite3"), connect_args={"check_same_thread": False}
)


@event.listens_for(engine, "connect")
def _connect(dbapi_connection, record):
    dbapi_connection.isolation_level = None
    dbapi_connection.execute("PRAGMA journal_mode=WAL")
    dbapi_connection.execute("PRAGMA busy_timeout=5000")


@event.listens_for(engine, "begin")
def _begin(connection):
    connection.exec_driver_sql("BEGIN")


Session = scoped_session(sessionmaker(bind=engine, expire_on_commit=False))


class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    user = Column(String(40))
    name = Column(String(100))


class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    number = Column(String(20))
    status = Column(String(20), default="new")


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    name = Column(String(100))


def reset():
    Session.remove()
    qube_tables.metadata.drop_all(engine)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    qube_tables.metadata.create_all(engine)
