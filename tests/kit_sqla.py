"""SQLAlchemy models for the Flask and FastAPI tests: an account that keeps its connection, and
an invoice that keeps its run. A file database, so each thread has a connection of its own."""
import os
import tempfile

from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

import qubesync.kit.sqlalchemy as qube_sqla

Base = declarative_base()
engine = create_engine("sqlite:///" + os.path.join(tempfile.mkdtemp(), "kit.sqlite3"))
Session = scoped_session(sessionmaker(bind=engine))


class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    user = Column(String(40))
    qube_connection_id = Column(String(64))
    qube_connection_revision = Column(Integer)
    connected = Column(Boolean, default=False)


class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    qube_reference = Column(String(200))
    qube_revision = Column(Integer)
    qube_question = Column(JSON)
    qube_links = Column(JSON)
    status = Column(String(20), default="new")


def reset():
    Session.remove()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def make_classes(base_operation=qube_sqla.Operation, base_connection=qube_sqla.ConnectionEvents, on_find=None):
    class CreateInvoice(base_operation):
        workflow = "add_transaction"
        slug = "create_invoice"

        @classmethod
        def find_record(cls, record_id):
            if on_find:
                on_find()
            return Session().get(Invoice, int(record_id))

        def input(self):
            return {"operation": "invoice.create", "params": {"ref_number": str(self.record.id)}}

        def ended(self, event):
            self.record.status = "sent"
            self.save_record(["status"])

    class Connection(base_connection):
        @classmethod
        def find_record(cls, record_id):
            return Session().get(Account, int(record_id))

        def connected(self, event):
            self.account.connected = True
            self.save_record(["connected"])

    return CreateInvoice, Connection


def add(row):
    session = Session()
    session.add(row)
    session.commit()
    return row
