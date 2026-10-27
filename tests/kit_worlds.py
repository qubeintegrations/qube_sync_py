"""The kit's behaviour tests run on both ORMs: a World makes an app's records and the kit's rows
on Django or on SQLAlchemy, and the operation and connection classes the tests configure work
on either. A Driver sends HTTP requests to one adapter (Django, Flask or FastAPI), signed in as
an account or not, so the route tests run on all three."""
import datetime
import json
import uuid

import pytest

import qubesync.kit as kit
from kit_support import API_KEY, QUBE_ID, REQUEST_ID, SECRET, WEBHOOK_URL, FakeClient

# The world the current test runs in, for the operation classes' find_record and handlers.
CURRENT = []


def world():
    return CURRENT[0]


class CreateInvoice(kit.Operation):
    workflow = "add_transaction"
    slug = "create_invoice"
    calls = []

    @classmethod
    def find_record(cls, id):
        return world().find(world().Invoice, id)

    def input(self):
        return self.without_nils({"operation": "invoice.create", "params": {"ref_number": self.record.number, "memo": None}})

    def notification(self, event):
        CreateInvoice.calls.append(("notification", event.delivery_id))

    def ended(self, event):
        CreateInvoice.calls.append(("ended", event.outcome, self.run.id, self.connection.id))
        self.record.status = "sent"
        world().write(self.record)
        txn = (event.get("output") or {}).get("record") or {}
        if txn.get("txn_id"):
            self.connection.link(self.record, kind="invoice", qb_id=txn["txn_id"], name=txn.get("ref_number"))

    def failed(self, event):
        CreateInvoice.calls.append(("failed", event.event))
        self.record.status = "failed"
        world().write(self.record)


class SyncCustomer(kit.Operation):
    """An operation with no find_record: its record comes from the run's record_type."""

    workflow = "ensure_customer"
    slug = "sync_customer"
    calls = []

    def input(self):
        return {"name": self.record.name}

    def ended(self, event):
        SyncCustomer.calls.append(("ended", self.record))


class FindCustomer(kit.Request):
    """A plain request, with no find_record: its record comes from the row's record_type."""

    operation = "customer.query"
    slug = "find_customer"
    calls = []

    def params(self):
        return {"full_name": self.record.name}

    def answered(self, event):
        FindCustomer.calls.append(("answered", event.page))

    def done(self):
        FindCustomer.calls.append(("done", self.queued_request.last_page))

    def failed(self, event):
        FindCustomer.calls.append(("failed", event.state))

    def retrying(self, event):
        FindCustomer.calls.append(("retrying", event.page))


class ConnectionEvents(kit.ConnectionEvents):
    calls = []

    def disconnected(self):
        # Its runs are still there: the hook runs before they go.
        runs_left = self.connection._kit_store.exists("run", connection_id=self.connection.id)
        ConnectionEvents.calls.append(("disconnected", self.connection.id, runs_left))

    def connected(self, event):
        ConnectionEvents.calls.append(("connected", self.connection.id, self.owner.id, self.connection.status))

    def setup_cancelled(self, event):
        ConnectionEvents.calls.append(("setup_cancelled", self.connection.id, self.owner.id, self.connection.status))

    def stalled(self, event):
        ConnectionEvents.calls.append(("stalled", self.connection.id, self.owner.id, self.connection.stall_reason))

    def resumed(self, event):
        ConnectionEvents.calls.append(("resumed", self.connection.id, self.owner.id, self.connection.stall_reason))


OPERATIONS = {"create_invoice": CreateInvoice, "sync_customer": SyncCustomer, "find_customer": FindCustomer}


def clear_calls():
    for cls in (CreateInvoice, SyncCustomer, FindCustomer, ConnectionEvents):
        del cls.calls[:]


class World(object):
    """What a test makes and reads, on one ORM."""

    name = ""

    def settings(self):
        """The kit's settings every test starts from (a fake client, the test webhook secret,
        current_account as the driver signs in)."""
        return dict(
            operations=OPERATIONS,
            connection_events=ConnectionEvents,
            api_key=API_KEY,
            webhook_secret=SECRET,
            webhook_url=WEBHOOK_URL,
            client=FakeClient(),
        )

    def connection(self, owner, qube_id=QUBE_ID, status="connected", name=None):
        return self.create(self.Connection, owner=owner, qube_id=qube_id, status=status, name=name)

    def run(self, record, connection, operation="create_invoice", reference=None, revision=0, state="running", **fields):
        return self.create(
            self.Run,
            connection_id=connection.id,
            operation=operation,
            record=record,
            reference=reference or "%s-%s-%s" % (operation, record.id, uuid.uuid4()),
            state=state,
            revision=revision,
            **fields
        )

    def request(self, record, connection, state="queued", qube_id=REQUEST_ID, **fields):
        return self.create(
            self.QueuedRequest,
            connection_id=connection.id,
            operation="find_customer",
            record=record,
            reference="find_customer-%s-%s" % (record.id, uuid.uuid4()),
            state=state,
            qube_id=qube_id,
            params={"full_name": record.name},
            pages_answered=0,
            **fields
        )

    def ago(self, row, seconds):
        """row as if made seconds ago."""
        moment = self.Run._kit_store.now() - datetime.timedelta(seconds=seconds)
        return self.update(row, created_at=moment)

    def quiet(self, row, seconds):
        """row as if last updated seconds ago."""
        moment = self.Run._kit_store.now() - datetime.timedelta(seconds=seconds)
        return self.update(row, updated_at=moment)


class DjangoWorld(World):
    name = "django"

    def __init__(self):
        import kit_django_setup  # noqa: F401
        from django.contrib.auth.models import User

        from kitapp.models import Account, Customer, Invoice
        from qubesync.django.models import (
            Connection,
            Notification,
            QueuedRequest,
            QuickbooksRecord,
            RequestDelivery,
            Run,
            SyncMark,
        )

        self.User = User
        self.Account, self.Invoice, self.Customer = Account, Invoice, Customer
        self.Connection, self.Run, self.QuickbooksRecord, self.Notification = Connection, Run, QuickbooksRecord, Notification
        self.SyncMark, self.QueuedRequest, self.RequestDelivery = SyncMark, QueuedRequest, RequestDelivery

    def clean(self):
        for model in (self.RequestDelivery, self.QueuedRequest, self.SyncMark, self.Notification, self.QuickbooksRecord, self.Run, self.Connection, self.Invoice, self.Customer, self.Account, self.User):
            model.objects.all().delete()

    def account(self, name="Riverbend"):
        user = self.User.objects.create(username="%s-%s" % (name, uuid.uuid4().hex[:8]))
        return self.Account.objects.create(name=name, user=user)

    def unsaved_account(self):
        return self.Account(name="Unsaved")

    def invoice(self, account, number="1001"):
        return self.Invoice.objects.create(account=account, number=number)

    def customer(self, account, name="Riverbend Electric"):
        return self.Customer.objects.create(account=account, name=name)

    def create(self, model, **fields):
        row = model(**fields)
        row.save()
        return row

    def update(self, row, **fields):
        type(row)._base_manager.filter(pk=row.pk).update(**fields)
        return self.reload(row)

    def reload(self, row):
        return type(row)._base_manager.get(pk=row.pk)

    def find(self, model, id):
        return model.objects.filter(pk=id).first()

    def write(self, record):
        record.save()

    def destroy(self, row):
        row.delete()

    def count(self, model, **filters):
        return model._base_manager.filter(**filters).count()

    def all(self, model, **filters):
        return list(model._base_manager.filter(**filters).order_by("id"))

    def key(self, record):
        return record._meta.label

    def release(self):
        """After work on another thread: its database connection closed."""
        from django.db import connection

        connection.close()


class SQLAlchemyWorld(World):
    name = "sqlalchemy"

    def __init__(self):
        import kit_sqla
        import qubesync.kit.sqlalchemy as tables

        self.module = kit_sqla
        self.Session = kit_sqla.Session
        self.Account, self.Invoice, self.Customer = kit_sqla.Account, kit_sqla.Invoice, kit_sqla.Customer
        self.Connection, self.Run, self.QuickbooksRecord, self.Notification = (
            tables.Connection,
            tables.Run,
            tables.QuickbooksRecord,
            tables.Notification,
        )
        self.SyncMark, self.QueuedRequest, self.RequestDelivery = tables.SyncMark, tables.QueuedRequest, tables.RequestDelivery

    def settings(self):
        values = World.settings(self)
        values["db_session"] = self.Session
        return values

    def clean(self):
        self.module.reset()

    def account(self, name="Riverbend"):
        return self.create(self.Account, name=name, user="%s-%s" % (name, uuid.uuid4().hex[:8]))

    def unsaved_account(self):
        return self.Account(name="Unsaved", user="nobody")

    def invoice(self, account, number="1001"):
        return self.create(self.Invoice, account_id=account.id, number=number)

    def customer(self, account, name="Riverbend Electric"):
        return self.create(self.Customer, account_id=account.id, name=name)

    def create(self, model, **fields):
        session = self.Session()
        row = model(**fields)
        session.add(row)
        session.commit()
        return row

    def update(self, row, **fields):
        session = self.Session()
        row = self.reload(row)
        for name, value in fields.items():
            setattr(row, name, value)
        session.commit()
        return row

    def reload(self, row):
        # A new transaction, so what another thread committed shows. The row's id from its
        # identity, which a detached row (its session removed) still has.
        from sqlalchemy import inspect

        session = self.Session()
        session.commit()
        return session.get(type(row), inspect(row).identity[0], populate_existing=True)

    def find(self, model, id):
        return self.Session().get(model, int(id))

    def write(self, record):
        # Inside the kit's transaction, which commits it with the run.
        self.Session().add(record)

    def destroy(self, row):
        session = self.Session()
        session.delete(self.reload(row))
        session.commit()

    def count(self, model, **filters):
        self.Session().commit()
        return self.Session().query(model).filter_by(**filters).count()

    def all(self, model, **filters):
        self.Session().commit()
        return self.Session().query(model).filter_by(**filters).order_by(model.id).all()

    def key(self, record):
        return "kit_sqla.%s" % type(record).__name__

    def release(self):
        self.Session.remove()


WORLDS = {"django": (DjangoWorld, "django"), "sqlalchemy": (SQLAlchemyWorld, "sqlalchemy")}
_made = {}


def make_world(name):
    cls, module = WORLDS[name]
    pytest.importorskip(module)
    if name not in _made:
        _made[name] = cls()
    made = _made[name]
    made.clean()
    clear_calls()
    CURRENT[:] = [made]
    kit.configure(**made.settings())
    return made


# -- HTTP drivers ----------------------------------------------------------------------------


class Response(object):
    def __init__(self, status, text, headers):
        self.status = status
        self.text = text
        self.headers = headers

    @property
    def location(self):
        return self.headers.get("Location") or self.headers.get("location")

    def json(self):
        return json.loads(self.text)


class Driver(object):
    """Sends requests to one adapter. account signs in as that account (None: signed out)."""

    def reset(self):
        """Before each test: forget what the last one signed in or kept."""

    world_name = "sqlalchemy"
    # What the adapter answers a signed-out request: Django's login_required redirects.
    signed_out = (401,)

    def current_account(self, request):
        raise NotImplementedError


class DjangoDriver(Driver):
    world_name = "django"
    signed_out = (302,)

    def __init__(self, world):
        from django.test import Client

        self.world = world
        self.Client = Client
        self._signed_in = None

    def current_account(self, request):
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            return None
        return self.world.Account.objects.filter(user=user).first()

    def _client(self, account):
        # One client per signed-in account, so its session lasts from a POST to the next page.
        if account is None:
            return self.Client()
        if self._signed_in is None or self._signed_in[0] != account.pk:
            client = self.Client()
            client.force_login(account.user)
            self._signed_in = (account.pk, client)
        return self._signed_in[1]

    def reset(self):
        self._signed_in = None

    def _headers(self, headers):
        meta = {}
        for name, value in (headers or {}).items():
            meta["HTTP_" + name.upper().replace("-", "_")] = value
        return meta

    def post(self, path, data=None, account=None, headers=None, body=None, content_type="application/json"):
        client = self._client(account)
        if body is not None:
            response = client.generic("POST", path, body, content_type=content_type, **self._headers(headers))
        else:
            response = client.post(path, data or {}, **self._headers(headers))
        return self._wrap(response)

    def get(self, path, params=None, account=None, headers=None):
        return self._wrap(self._client(account).get(path, params or {}, **self._headers(headers)))

    def delete(self, path, account=None, headers=None):
        return self._wrap(self._client(account).delete(path, **self._headers(headers)))

    def _wrap(self, response):
        return Response(response.status_code, response.content.decode("utf-8"), dict(response.items()))


class FlaskDriver(Driver):
    def __init__(self, world):
        from flask import Flask, abort, request

        import qubesync.flask as qube_flask

        self.world = world

        def require_user(view):
            """Stands in for flask_login's login_required."""
            import functools

            @functools.wraps(view)
            def wrapped(*args, **kwargs):
                if not request.headers.get("X-User"):
                    abort(401)
                return view(*args, **kwargs)

            return wrapped

        app = Flask("kit_flask_test")
        app.config["TESTING"] = True
        app.secret_key = "kit-tests"  # Flask's session keeps a route's message for the page
        qube_flask.init_app(app, sign_in=require_user)

        @app.teardown_appcontext
        def remove_session(error=None):
            world.Session.remove()

        @app.route("/invoices/<int:id>")
        def invoice_page(id):
            invoice = world.find(world.Invoice, id)
            return "<main>%s%s</main>" % (
                qube_flask.run_status_html(invoice, "create_invoice"),
                qube_flask.question_html(invoice, "create_invoice"),
            )

        @app.route("/connections")
        def connections_page():
            return "<main>%s</main>" % qube_flask.error_html()

        self.app = app
        self.reset()

    def reset(self):
        # A fresh cookie jar (Flask's session) for each test.
        self.client = self.app.test_client()

    def current_account(self, request):
        user = request.headers.get("X-User")
        return self.world.Session().query(self.world.Account).filter_by(user=user).first() if user else None

    def _headers(self, account, headers):
        merged = dict(headers or {})
        if account is not None:
            merged["X-User"] = account.user
        return merged

    def post(self, path, data=None, account=None, headers=None, body=None, content_type="application/json"):
        if body is not None:
            response = self.client.post(path, data=body, headers=self._headers(account, headers), content_type=content_type)
        else:
            response = self.client.post(path, data=data or {}, headers=self._headers(account, headers))
        return self._wrap(response)

    def get(self, path, params=None, account=None, headers=None):
        return self._wrap(self.client.get(path, query_string=params or {}, headers=self._headers(account, headers)))

    def delete(self, path, account=None, headers=None):
        return self._wrap(self.client.delete(path, headers=self._headers(account, headers)))

    def _wrap(self, response):
        return Response(response.status_code, response.get_data(as_text=True), dict(response.headers))


class FastAPIDriver(Driver):
    def __init__(self, world):
        from fastapi import Depends, FastAPI, HTTPException, Request
        from fastapi.responses import HTMLResponse
        from fastapi.testclient import TestClient

        import qubesync.fastapi as qube_fastapi

        self.world = world

        def signed_in(request: Request) -> None:
            """Stands in for the app's sign-in dependency: it puts the user on request.state."""
            user = request.headers.get("x-user")
            if not user:
                raise HTTPException(status_code=401)
            request.state.user = user

        app = FastAPI()
        app.include_router(qube_fastapi.router(dependencies=[Depends(signed_in)]))

        @app.get("/invoices/{id}", response_class=HTMLResponse)
        def invoice_page(id: int, request: Request):
            invoice = world.find(world.Invoice, id)
            try:
                return "<main>%s%s</main>" % (
                    qube_fastapi.run_status_html(request, invoice, "create_invoice"),
                    qube_fastapi.question_html(request, invoice, "create_invoice"),
                )
            finally:
                world.Session.remove()

        @app.get("/connections", response_class=HTMLResponse)
        def connections_page(request: Request):
            return "<main>%s</main>" % qube_fastapi.error_html(request)

        self.app = app
        self.client = TestClient(app)

    def reset(self):
        self.client.cookies.clear()

    def current_account(self, request):
        user = getattr(request.state, "user", None)
        return self.world.Session().query(self.world.Account).filter_by(user=user).first() if user else None

    def _headers(self, account, headers):
        merged = dict(headers or {})
        if account is not None:
            merged["x-user"] = account.user
        return merged

    def post(self, path, data=None, account=None, headers=None, body=None, content_type="application/json"):
        merged = self._headers(account, headers)
        if body is not None:
            merged["content-type"] = content_type
            response = self.client.post(path, content=body, headers=merged, follow_redirects=False)
        else:
            response = self.client.post(path, data=data or {}, headers=merged, follow_redirects=False)
        return self._wrap(response)

    def get(self, path, params=None, account=None, headers=None):
        response = self._wrap(self.client.get(path, params=params or {}, headers=self._headers(account, headers), follow_redirects=False))
        if 'document.cookie = "%s=; Max-Age=0' % kit.ERROR_KEY in response.text:
            self.client.cookies.delete(kit.ERROR_KEY)  # what the template's script does in a browser
        return response

    def delete(self, path, account=None, headers=None):
        response = self.client.delete(path, headers=self._headers(account, headers), follow_redirects=False)
        return self._wrap(response)

    def _wrap(self, response):
        return Response(response.status_code, response.text, dict(response.headers))


DRIVERS = {
    "django": (DjangoDriver, "django"),
    "flask": (FlaskDriver, "flask"),
    "fastapi": (FastAPIDriver, "fastapi"),
}
_drivers = {}


def make_driver(name):
    cls, module = DRIVERS[name]
    pytest.importorskip(module)
    if name in ("flask", "fastapi"):
        pytest.importorskip("sqlalchemy")
    if name == "fastapi":
        pytest.importorskip("httpx")
    made = make_world(cls.world_name)
    if name not in _drivers:
        _drivers[name] = cls(made)
    driver = _drivers[name]
    driver.reset()
    kit.configure(current_account=driver.current_account)
    return driver, made
