"""The kit's tables and what it does with them, on Django's ORM and on SQLAlchemy: connections
(link, move, list families, adoption), runs (every ending kept, the summary, looks_stuck),
operations (start and its reuse, retry_start, the job's checks), sync status and its scopes,
connection events, notification dedupe and the default queue's retries. With KIT_PG_URL set
(tests/README.md) they run on PostgreSQL."""
import datetime
import json
import logging
import os
import threading
import time

import pytest
import requests

import qubesync.kit as kit
from kit_support import (  # noqa: F401
    DELIVERY_ID,
    QUBE_ID,
    WEBHOOK_URL,
    api_error,
    drain,
    iso,
    kit_reset,
    run_body,
    timeout,
    vector_body,
)
from kit_worlds import ConnectionEvents, CreateInvoice, SyncCustomer, make_world
from qubesync import webhooks


@pytest.fixture(params=["django", "sqlalchemy"])
def world(request, kit_reset):
    return make_world(request.param)


@pytest.fixture
def account(world):
    return world.account()


@pytest.fixture
def connection(world, account):
    return world.connection(account)


@pytest.fixture
def invoice(world, account):
    return world.invoice(account)


@pytest.fixture
def customer(world, account):
    return world.customer(account)


@pytest.fixture
def run(world, invoice, connection):
    return world.run(invoice, connection)


@pytest.fixture
def client():
    return kit.settings().client


def deliver(world, kind, row, body):
    kit.run(kind, str(row.id), body)
    return world.reload(row)


# -- Connections -----------------------------------------------------------------------------


class TestConnection:
    def test_webhook_url_is_the_setting_and_its_own_id(self, connection):
        assert connection.webhook_url == "%s/connections/%s" % (WEBHOOK_URL, connection.id)

    def test_not_checking_in_only_when_stalled_for_that_reason(self, world, connection):
        connection = world.update(connection, status="stalled", stall_reason="not_checking_in")
        assert connection.not_checking_in()
        connection = world.update(connection, stall_reason="quickbooks_unavailable")
        assert not connection.not_checking_in()
        connection = world.update(connection, status="connected", stall_reason=None)
        assert not connection.not_checking_in()

    def test_links_a_record_by_kind_and_reads_it_back_both_ways(self, world, connection, customer):
        row = connection.link(customer, kind="customer", qb_id="80000001-1", edit_sequence="171", name="Riverbend Electric")

        assert (row.kind, row.list, row.qb_id, row.edit_sequence, row.name) == (
            "customer",
            "name",
            "80000001-1",
            "171",
            "Riverbend Electric",
        )
        assert row.record == customer
        assert connection.qb_id_for(customer, kind="customer") == "80000001-1"
        assert connection.qb_id_for(customer, kind="vendor") is None
        assert connection.find_linked("80000001-1", kind="customer") == customer
        assert connection.find_linked("nope", kind="customer") is None
        assert connection.quickbooks_record("80000001-1", kind="customer").id == row.id

    def test_replaces_a_records_id_for_the_same_kind(self, world, connection, customer):
        connection.link(customer, kind="customer", qb_id="80000001-1")
        connection.link(customer, kind="customer", qb_id="80000002-1", edit_sequence="9")

        assert connection.qb_id_for(customer, kind="customer") == "80000002-1"
        assert world.count(world.QuickbooksRecord) == 1

    def test_moves_a_qb_id_between_records_and_logs_it(self, world, account, connection, customer, caplog):
        other = world.customer(account, name="Riverbend (old)")
        connection.link(other, kind="customer", qb_id="80000001-1")
        connection.link(customer, kind="customer", qb_id="80000002-1")

        with caplog.at_level(logging.INFO, logger="qubesync.kit"):
            connection.link(customer, kind="customer", qb_id="80000001-1")

        assert connection.find_linked("80000001-1", kind="customer") == customer
        assert connection.qb_id_for(other, kind="customer") is None
        assert connection.qb_id_for(customer, kind="customer") == "80000001-1"
        assert world.count(world.QuickbooksRecord) == 1
        key = world.key(customer)
        assert "customer 80000001-1 moved from %s %s to %s %s" % (key, other.id, key, customer.id) in caplog.text

    def test_keeps_the_same_id_on_two_connections_apart(self, world, account, connection, customer):
        second = world.connection(account, qube_id="conn-q-2")
        other = world.customer(account, name="Other file's")
        connection.link(customer, kind="customer", qb_id="80000001-1")
        second.link(other, kind="customer", qb_id="80000001-1")

        assert connection.find_linked("80000001-1", kind="customer") == customer
        assert second.find_linked("80000001-1", kind="customer") == other

    def test_owned_by_lists_an_owners_connections(self, world, account, connection):
        second = world.connection(account, qube_id="conn-q-2")
        world.connection(world.account("Someone else"), qube_id="conn-q-3")

        assert sorted(c.id for c in world.Connection.owned_by(account)) == sorted([connection.id, second.id])
        assert connection.owner_id == str(account.id)
        assert connection.owner == account

    def test_refuses_a_link_without_a_qb_id(self, connection, customer):
        with pytest.raises(ValueError):
            connection.link(customer, kind="customer", qb_id=None)

    @pytest.mark.parametrize("inside", [False, True], ids=["alone", "inside_a_transaction"])
    def test_retries_a_unique_race_once_in_a_savepoint(self, world, connection, customer, monkeypatch, inside):
        # The first try finds nothing (as if another worker hadn't committed yet) and its insert
        # conflicts; the second finds the row and updates it.
        connection.link(customer, kind="customer", qb_id="80000001-1")
        store = world.Connection._kit_store
        first = store.first
        misses = []

        def missing_once(name, **kwargs):
            if name == "quickbooks_record" and not misses:
                if kwargs.get("qb_id") == "80000001-1":
                    misses.append(True)
                    return None
            if misses == [True] and kwargs.get("record_id") == str(customer.id):
                misses.append(True)
                return None
            return first(name, **kwargs)

        monkeypatch.setattr(store, "first", missing_once)
        if inside:
            # As in a handler, under the run row's lock: the savepoint keeps the outer
            # transaction usable after the conflict.
            with store.atomic():
                row = connection.link(customer, kind="customer", qb_id="80000001-1", edit_sequence="2")
                assert store.get("connection", connection.id) is not None
        else:
            row = connection.link(customer, kind="customer", qb_id="80000001-1", edit_sequence="2")

        assert len(misses) == 2
        assert row.edit_sequence == "2"
        assert world.count(world.QuickbooksRecord) == 1


class TestListFamilies:
    """One ListID counter per family, verified on QuickBooks Enterprise 24.0."""

    def test_maps_kinds_to_families(self):
        family = kit.family_for
        assert {family(k) for k in ("customer", "vendor", "employee", "other_name")} == {"name"}
        assert {family(k) for k in ("item", "item_service", "item_non_inventory", "item_sales_tax", "item_group")} == {"item"}
        assert [family(k) for k in ("account", "class", "invoice", "bill", "made_up_kind")] == [
            "account",
            "class",
            "invoice",
            "bill",
            "made_up_kind",
        ]

    def test_one_contact_as_a_customer_and_a_vendor(self, world, connection, customer):
        connection.link(customer, kind="customer", qb_id="80000010-1")
        connection.link(customer, kind="vendor", qb_id="80000011-1")

        assert connection.qb_id_for(customer, kind="customer") == "80000010-1"
        assert connection.qb_id_for(customer, kind="vendor") == "80000011-1"
        assert {row.list for row in world.all(world.QuickbooksRecord)} == {"name"}

    def test_finds_an_entity_refs_id_with_no_kind(self, connection, customer):
        connection.link(customer, kind="vendor", qb_id="80000011-1")

        assert connection.find_linked("80000011-1") == customer
        assert connection.find_linked("80000011-1", kind="customer") == customer  # the same name family
        assert connection.quickbooks_record("80000011-1").kind == "vendor"

    def test_an_item_linked_as_item_service_answers_item_and_relinks_with_a_new_kind(self, world, connection, customer):
        connection.link(customer, kind="item_service", qb_id="80000003-1")

        assert connection.qb_id_for(customer, kind="item") == "80000003-1"
        assert connection.qb_id_for(customer, kind="item_non_inventory") == "80000003-1"
        assert connection.find_linked("80000003-1", kind="item") == customer

        connection.link(customer, kind="item_non_inventory", qb_id="80000003-1", edit_sequence="2")

        rows = world.all(world.QuickbooksRecord, list="item")
        assert [(row.kind, row.edit_sequence) for row in rows] == [("item_non_inventory", "2")]

    def test_the_same_id_in_two_families_links_two_records(self, world, account, connection, customer):
        contact = world.customer(account, name="Lone Star Supply")
        connection.link(contact, kind="customer", qb_id="80000003-1")
        connection.link(customer, kind="account", qb_id="80000003-1")

        assert connection.find_linked("80000003-1", kind="customer") == contact
        assert connection.find_linked("80000003-1", kind="account") == customer
        assert world.count(world.QuickbooksRecord) == 2

    def test_a_no_kind_lookup_in_several_families_raises(self, world, account, connection, customer):
        contact = world.customer(account, name="Lone Star Supply")
        connection.link(contact, kind="customer", qb_id="80000003-1")
        connection.link(customer, kind="class", qb_id="80000003-1")

        with pytest.raises(ValueError, match=r"more than one kind \(class, customer\): pass kind="):
            connection.find_linked("80000003-1")

    def test_never_hands_out_a_customers_id_as_a_vendors(self, connection, customer):
        connection.link(customer, kind="customer", qb_id="80000010-1")

        assert connection.qb_id_for(customer, kind="vendor") is None

    def test_qb_id_for_raises_when_the_family_has_several_and_none_is_that_kind(self, connection, customer):
        connection.link(customer, kind="item_service", qb_id="80000003-1")
        connection.link(customer, kind="item_inventory", qb_id="80000004-1")

        with pytest.raises(ValueError, match="pass kind"):
            connection.qb_id_for(customer, kind="item")


class TestTwoConnections:
    def test_each_has_its_own_runs_and_links(self, world, account, connection, invoice):
        second = world.connection(account, qube_id="conn-q-2")
        first_run = world.run(invoice, connection)
        second_run = world.run(invoice, second)

        for each, txn_id in ((first_run, "T-1"), (second_run, "T-2")):
            body = run_body("workflow_run.completed", each, {"revision": 1, "output": {"record": {"txn_id": txn_id}}})
            kit.run("run", str(each.id), body)

        assert [r.id for r in world.all(world.Run, connection_id=connection.id)] == [first_run.id]
        assert [r.id for r in world.all(world.Run, connection_id=second.id)] == [second_run.id]
        assert world.reload(connection).qb_id_for(invoice, kind="invoice") == "T-1"
        assert world.reload(second).qb_id_for(invoice, kind="invoice") == "T-2"


# -- Adoption --------------------------------------------------------------------------------


class TestAdoption:
    """Adopting QuBe Sync's connection for a row without a qube_id."""

    @pytest.fixture
    def row(self, world, account):
        return world.connection(account, qube_id=None, status="pending", name="Main file")

    def made_for(self, row, **changes):
        made = {
            "id": "conn-q-lost",
            "webhook_url": row.webhook_url,
            "last_connected_at": None,
            "name": row.name,
            "created_at": iso(row._kit_store.utc(row.created_at)),
        }
        made.update(changes)
        return made

    def listing(self, client, *connections):
        client.returns["list_connections"] = list(connections)

    def test_adopts_the_one_made_for_the_row(self, world, row, client):
        self.listing(client, self.made_for(row))

        assert row.adopt_qube_connection() == "conn-q-lost"
        assert world.reload(row).qube_id == "conn-q-lost"

    def test_skips_one_made_before_the_row(self, row, client):
        made_at = row._kit_store.utc(row.created_at) - datetime.timedelta(hours=1)
        self.listing(client, self.made_for(row, created_at=iso(made_at)))

        assert row.adopt_qube_connection() is None

    def test_allows_five_minutes_of_clock_difference(self, row, client):
        made_at = row._kit_store.utc(row.created_at) - datetime.timedelta(seconds=240)
        self.listing(client, self.made_for(row, created_at=iso(made_at)))

        assert row.adopt_qube_connection() == "conn-q-lost"

    def test_never_adopts_one_with_no_created_at_and_logs_it_once(self, row, client, caplog):
        self.listing(client, self.made_for(row, created_at=None), self.made_for(row, id="conn-q-2", created_at=None))

        assert row.adopt_qube_connection() is None
        assert caplog.text.count("carry no created_at") == 1

    def test_skips_one_that_has_connected(self, row, client):
        self.listing(client, self.made_for(row, last_connected_at=iso(datetime.datetime.now(datetime.timezone.utc))))

        assert row.adopt_qube_connection() is None

    def test_adopts_a_simulated_one_though_it_has_connected(self, world, row, client):
        # Connected from the moment it's made, but only the lost answer carried its setup link.
        connected = iso(datetime.datetime.now(datetime.timezone.utc))
        self.listing(client, self.made_for(row, type="simulated", last_connected_at=connected))

        assert row.adopt_qube_connection() == "conn-q-lost"
        assert world.reload(row).qube_id == "conn-q-lost"

    def test_skips_a_standard_one_that_has_connected(self, row, client):
        connected = iso(datetime.datetime.now(datetime.timezone.utc))
        self.listing(client, self.made_for(row, type="standard", last_connected_at=connected))

        assert row.adopt_qube_connection() is None

    def test_skips_one_whose_name_isnt_the_rows(self, row, client):
        self.listing(client, self.made_for(row, name="Another file"))

        assert row.adopt_qube_connection() is None

    def test_takes_any_name_when_the_row_has_none(self, world, row, client):
        row = world.update(row, name=None)
        self.listing(client, self.made_for(row, name="Riverbend Electric"))

        assert row.adopt_qube_connection() == "conn-q-lost"

    def test_skips_one_with_another_webhook_url(self, row, client):
        self.listing(client, self.made_for(row, webhook_url="https://elsewhere.example/webhooks/qube/connections/1"))

        assert row.adopt_qube_connection() is None

    def test_adopts_none_when_two_could_be_the_rows(self, row, client, caplog):
        self.listing(client, self.made_for(row), self.made_for(row, id="conn-q-2"))

        assert row.adopt_qube_connection() is None
        assert "2 of QuBe Sync's connections could be its; adopted none" in caplog.text


# -- Runs ------------------------------------------------------------------------------------


class TestRun:
    def test_keeps_a_completed_ending_before_the_handler_runs(self, world, run, monkeypatch):
        seen = []

        def ended(operation, event):
            seen.append((operation.run.state, operation.run.outcome, operation.run.ended_at is None))

        monkeypatch.setattr(CreateInvoice, "ended", ended)
        run = deliver(world, "run", run, run_body("workflow_run.completed", run, {"revision": 2, "outcome": "added"}))

        assert seen == [("completed", "added", False)]
        assert (run.state, run.outcome) == ("completed", "added")
        assert run.ended_at is not None
        assert run.ended()
        assert run.summary_text == "Added to QuickBooks"

    def test_keeps_a_failed_runs_error_as_the_event_carried_it(self, world, run):
        error = {
            "code": "no_such_customer",
            "message": "No customer named Riverbend",
            "detail": "Add the customer, then start again.",
        }
        run = deliver(world, "run", run, run_body("workflow_run.failed", run, {"revision": 2, "error": error}))

        assert run.failed()
        assert run.error == error
        assert run.summary_text == "Failed: No customer named Riverbend"
        assert run.error_detail == "Add the customer, then start again."

    def test_takes_an_error_thats_a_sentence(self, world, run):
        run = deliver(world, "run", run, run_body("workflow_run.failed", run, {"revision": 2}))

        assert run.summary_text.startswith("Failed: Five renames were tried")
        assert run.error_detail is None

    def test_keeps_a_cancelled_runs_reason(self, world, run):
        run = deliver(world, "run", run, run_body("workflow_run.cancelled", run, {"revision": 2}))

        assert run.cancelled()
        assert run.cancel_reason == "The customer was merged in our CRM."
        assert run.summary_text == "Cancelled: The customer was merged in our CRM."

    def test_keeps_an_ending_when_the_handler_writes_nothing(self, world, run, monkeypatch):
        monkeypatch.setattr(CreateInvoice, "failed", lambda operation, event: None)
        run = deliver(world, "run", run, run_body("workflow_run.failed", run, {"revision": 2}))

        assert (run.state, run.outcome) == ("failed", "renames_exhausted")

    def test_says_where_it_stands_in_a_sentence(self, world, run):
        assert run.summary_text == "Running"
        assert world.update(run, state="awaiting_input").summary_text == "Waiting for your answer"
        assert world.update(run, state="completed", outcome="completed").summary_text == "Done"
        assert world.update(run, state="completed", outcome="used_existing").summary_text == "Done: Used existing"
        failed = world.update(run, state="failed", outcome=None, ended_at=None, error=None)
        assert failed.summary_text == "Failed: it couldn't be started"
        assert world.update(run, state="cancelled", cancel_reason=None).summary_text == "Cancelled: your app chose to stop"

    def test_a_completed_run_whose_outcome_is_cancelled_is_cancelled(self, world, run):
        run = world.update(run, state="completed", outcome="cancelled")

        assert run.cancelled() and run.ended() and not run.failed()
        assert run.summary_text == "Cancelled: your app chose to stop"
        assert world.update(run, cancel_reason="Merged in the CRM").summary_text == "Cancelled: Merged in the CRM"

    def test_an_unconfirmed_start_is_one_a_minute_old(self, world, invoice, connection):
        fresh = world.run(invoice, connection, state="starting")
        assert fresh.summary_text == "Starting"
        assert not fresh.unconfirmed()

        old = world.ago(world.run(invoice, connection, state="starting"), 120)
        assert old.summary_text == "Not confirmed by QuBe Sync yet"
        assert old.unconfirmed()

    def test_latest_for_is_the_records_newest_run_of_that_operation(self, world, invoice, connection):
        older = world.ago(world.run(invoice, connection), 3600)
        newer = world.run(invoice, connection)
        world.run(invoice, connection, operation="sync_customer")

        assert world.Run.latest_for(invoice, "create_invoice").id == newer.id
        assert older.id != newer.id
        assert world.Run.latest_for(world.invoice(invoice_account(world, invoice)), "create_invoice") is None

    def test_keeps_json_columns_as_text_and_reads_them_back(self, world, run):
        run = world.update(run, question={"token": "t", "choices": []}, links={"decisions": "d"}, error="a sentence")

        assert run.open_question == {"token": "t", "choices": []}
        assert run.links == {"decisions": "d"}
        assert run.error == "a sentence"


def invoice_account(world, invoice):
    return world.find(world.Account, invoice.account_id)


# -- Operations: the job ---------------------------------------------------------------------


class TestJob:
    def test_hands_a_completed_run_to_ended_with_the_record_run_and_connection(self, world, run, invoice, connection):
        run = deliver(world, "run", run, run_body("workflow_run.completed", run, {"revision": 4}))

        assert CreateInvoice.calls == [("ended", "used_existing", run.id, connection.id)]
        assert world.reload(invoice).status == "sent"
        assert (run.revision, run.state, run.outcome) == (4, "completed", "used_existing")

    def test_hands_a_failed_or_cancelled_run_to_failed(self, world, run):
        deliver(world, "run", run, run_body("workflow_run.failed", run, {"revision": 2}))
        run = deliver(world, "run", run, run_body("workflow_run.cancelled", run, {"revision": 3}))

        assert CreateInvoice.calls == [("failed", "workflow_run.failed"), ("failed", "workflow_run.cancelled")]
        assert run.state == "cancelled"

    def test_skips_an_event_whose_reference_isnt_the_runs(self, world, run, caplog):
        run = deliver(world, "run", run, run_body("workflow_run.completed", run, {"reference": "create_invoice-1-earlier", "revision": 9}))

        assert CreateInvoice.calls == []
        assert run.revision == 0
        assert "skipped workflow_run.completed for 'create_invoice-1-earlier'" in caplog.text
        assert "not this run" in caplog.text

    def test_skips_an_event_whose_connection_id_isnt_the_runs_connections(self, world, run, caplog):
        run = deliver(world, "run", run, run_body("workflow_run.completed", run, {"connection_id": "someone-elses", "revision": 9}))

        assert CreateInvoice.calls == []
        assert run.revision == 0
        assert "on 'someone-elses': not this run" in caplog.text

    def test_skips_an_event_with_no_reference(self, world, run):
        deliver(world, "run", run, vector_body("connection.connected", {"reference": None}))

        assert CreateInvoice.calls == []

    def test_applies_an_event_only_when_its_newer(self, world, run):
        deliver(world, "run", run, run_body("workflow_run.failed", run, {"revision": 5}))
        deliver(world, "run", run, run_body("workflow_run.completed", run, {"revision": 3}))  # older, late
        run = deliver(world, "run", run, run_body("workflow_run.failed", run, {"revision": 5}))  # a retry

        assert CreateInvoice.calls == [("failed", "workflow_run.failed")]
        assert run.revision == 5

    def test_takes_a_notification_once_by_delivery_id_whatever_its_revision(self, world, run):
        deliver(world, "run", run, run_body("workflow_run.notification", run, {"revision": 2}))
        deliver(world, "run", run, run_body("workflow_run.notification", run, {"revision": 2}))  # a retry
        run = deliver(world, "run", run, run_body("workflow_run.notification", run, {"revision": 1, "delivery_id": "d-2"}))

        assert CreateInvoice.calls == [("notification", DELIVERY_ID), ("notification", "d-2")]
        assert run.revision == 0

    def test_uses_the_dedupe_setting(self, world, run):
        class Store(object):
            def __init__(self):
                self.keys = []

            def seen(self, key):
                return key in self.keys

            def remember(self, key):
                self.keys.append(key)

        store = Store()
        kit.configure(dedupe=store)
        deliver(world, "run", run, run_body("workflow_run.notification", run))

        assert store.keys == ["qube-sync/delivery/%s" % DELIVERY_ID]

    def test_keeps_a_question_with_its_links_and_a_newer_event_forgets_it(self, world, run):
        run = deliver(world, "run", run, run_body("workflow_run.awaiting_input", run, {"revision": 6}))

        assert {"token", "choices", "message"} <= set(run.question)
        assert sorted(run.links) == ["decisions", "search"]
        assert (run.revision, run.state) == (6, "awaiting_input")

        run = deliver(world, "run", run, run_body("workflow_run.completed", run, {"revision": 7}))

        assert run.question is None and run.links is None

    def test_leaves_the_question_alone_for_a_retry_with_no_prompt(self, world, run):
        deliver(world, "run", run, run_body("workflow_run.awaiting_input", run, {"revision": 6}))
        run = deliver(world, "run", run, run_body("workflow_run.awaiting_input", run, {"revision": 7, "prompt": None}))

        assert run.question is not None

    def test_finds_the_record_by_record_type_without_find_record(self, world, customer, connection):
        sync = world.run(customer, connection, operation="sync_customer")
        deliver(world, "run", sync, run_body("workflow_run.completed", sync, {"revision": 1}))

        assert SyncCustomer.calls == [("ended", customer)]

    def test_drops_a_delivery_whose_record_was_deleted(self, world, run, invoice, caplog):
        key = (world.key(invoice), invoice.id)
        world.destroy(invoice)

        kit.run("run", str(run.id), run_body("workflow_run.completed", run))

        assert CreateInvoice.calls == []
        assert "dropped workflow_run.completed: run %s's %s %s isn't there" % ((run.id,) + key) in caplog.text

    def test_drops_one_whose_find_record_raises_not_found(self, world, run, monkeypatch, caplog):
        store = world.Run._kit_store

        def missing(cls, id):
            raise store.not_found_errors[0]()

        monkeypatch.setattr(CreateInvoice, "find_record", classmethod(missing))
        kit.run("run", str(run.id), run_body("workflow_run.completed", run))

        assert "dropped workflow_run.completed" in caplog.text

    def test_drops_a_deleted_run_or_connection_and_raises_for_an_operation_taken_out(self, run, caplog):
        kit.run("run", "0", vector_body("workflow_run.completed"))
        kit.run("connection", "0", vector_body("connection.connected"))
        assert "run 0 isn't there" in caplog.text
        assert "connection 0 isn't there" in caplog.text

        kit.configure(operations={"sync_customer": SyncCustomer})
        with pytest.raises(kit.UnknownOperation):
            kit.run("run", str(run.id), run_body("workflow_run.completed", run))

    def test_keeps_nothing_on_the_apps_record(self, world):
        if world.name == "django":
            names = [f.name for f in world.Invoice._meta.concrete_fields]
        else:
            names = list(world.Invoice.__table__.c.keys())
        assert names == ["id", "account", "number", "status"] or names == ["id", "account_id", "number", "status"]


# -- Operations: starting --------------------------------------------------------------------


class TestStart:
    def test_writes_the_run_first_starts_it_and_keeps_the_answer(self, world, invoice, connection, client):
        client.returns["start_run"] = {
            "id": "run-q-1",
            "state": "running",
            "links": {"run": "https://qubesync.com/r/1", "cancel": "https://qubesync.com/r/1/cancel"},
        }

        started = CreateInvoice.start(invoice, connection)

        started = world.reload(started)
        assert (started.operation, started.record, started.connection_id) == ("create_invoice", invoice, connection.id)
        assert (started.qube_run_id, started.state, started.run_url, started.cancel_url) == (
            "run-q-1",
            "running",
            "https://qubesync.com/r/1",
            "https://qubesync.com/r/1/cancel",
        )
        assert started.reference.startswith("create_invoice-%s-" % invoice.id)
        name, args, kwargs = client.called("start_run")[0]
        assert args == (QUBE_ID, "add_transaction", {"operation": "invoice.create", "params": {"ref_number": "1001"}})
        assert kwargs == {"reference": started.reference, "webhook_url": "%s/runs/%s" % (WEBHOOK_URL, started.id)}

    def test_keeps_a_state_a_webhook_wrote_before_the_answer(self, world, invoice, connection, client):
        def webhook_first(*args, **kwargs):
            row = world.all(world.Run)[-1]
            world.update(row, state="awaiting_input", revision=2)
            return {"id": "run-q-1", "state": "running"}

        client.returns["start_run"] = webhook_first

        started = world.reload(CreateInvoice.start(invoice, connection))

        assert (started.state, started.qube_run_id, started.revision) == ("awaiting_input", "run-q-1", 2)

    def test_refuses_a_connection_quickbooks_hasnt_made(self, world, account, invoice):
        pending = world.connection(account, qube_id=None, status="pending")

        with pytest.raises(kit.NotConnected, match="qube_id"):
            CreateInvoice.start(invoice, pending)
        assert world.count(world.Run) == 0

    def test_marks_the_run_failed_when_quickbooks_refuses_it(self, world, invoice, connection, client):
        client.raises["start_run"] = api_error(422, {"detail": "bad input"})

        with pytest.raises(kit.APIError):
            CreateInvoice.start(invoice, connection)
        row = world.all(world.Run)[-1]
        assert (row.state, row.qube_run_id) == ("failed", None)

    def test_raises_realtime_required_and_marks_the_run_failed_on_a_standard_connection(self, world, invoice, connection, client):
        client.raises["start_run"] = api_error(422, {"code": "realtime_required", "detail": "Upgrade it to realtime."})

        with pytest.raises(kit.RealtimeRequired, match="Upgrade it to realtime."):
            CreateInvoice.start(invoice, connection)
        assert world.all(world.Run)[-1].state == "failed"

    def test_realtime_required_without_a_detail_says_why(self, world, invoice, connection, client):
        client.raises["start_run"] = api_error(422, {"code": "realtime_required"})

        with pytest.raises(kit.RealtimeRequired, match="realtime connections"):
            CreateInvoice.start(invoice, connection)

    def test_a_retried_start_refused_for_realtime_raises_realtime_required(self, world, invoice, connection, client):
        client.raises["start_run"] = timeout()
        with pytest.raises(requests.Timeout):
            CreateInvoice.start(invoice, connection)
        client.raises["start_run"] = api_error(422, {"code": "realtime_required", "detail": "Upgrade it."})

        row = world.all(world.Run)[-1]
        with pytest.raises(kit.RealtimeRequired, match="Upgrade it."):
            row.retry_start()
        assert world.reload(row).state == "failed"

    def test_marks_the_run_failed_when_its_input_raises(self, world, invoice, connection, client, monkeypatch):
        def broken(operation):
            raise NotImplementedError("not yet")

        monkeypatch.setattr(CreateInvoice, "input", broken)

        with pytest.raises(NotImplementedError):
            CreateInvoice.start(invoice, connection)
        assert world.all(world.Run)[-1].state == "failed"
        assert client.called("start_run") == []

    def test_leaves_the_run_starting_with_its_input_when_theres_no_answer(self, world, invoice, connection, client):
        client.raises["start_run"] = timeout()

        with pytest.raises(requests.Timeout):
            CreateInvoice.start(invoice, connection)
        row = world.all(world.Run)[-1]
        assert (row.state, row.qube_run_id) == ("starting", None)
        assert row.input == {"operation": "invoice.create", "params": {"ref_number": "1001"}}

    def test_leaves_the_run_starting_on_a_5xx(self, world, invoice, connection, client):
        client.raises["start_run"] = api_error(500)

        with pytest.raises(kit.APIError):
            CreateInvoice.start(invoice, connection)
        assert world.all(world.Run)[-1].state == "starting"


    def test_leaves_the_run_starting_on_a_409_the_other_clicks_call_in_flight(self, world, invoice, connection, client):
        client.raises["start_run"] = api_error(409, "Idempotency-Key is being used by another call: try again")

        with pytest.raises(kit.APIError):
            CreateInvoice.start(invoice, connection)
        assert world.all(world.Run)[-1].state == "starting"

    def test_returns_the_records_run_that_hasnt_ended_rather_than_starting_another(self, world, invoice, connection, client):
        first = CreateInvoice.start(invoice, connection)
        assert first.reused is False

        again = CreateInvoice.start(invoice, connection)

        assert (again.id, again.reused) == (first.id, True)
        assert len(client.called("start_run")) == 1
        assert world.count(world.Run) == 1

    def test_resends_an_unconfirmed_start_with_its_reference_and_stored_input(self, world, invoice, connection, client):
        client.raises["start_run"] = timeout()
        with pytest.raises(requests.Timeout):
            CreateInvoice.start(invoice, connection)
        invoice.number = "changed since"
        world.write(invoice)
        del client.raises["start_run"]

        again = CreateInvoice.start(invoice, connection)

        first, second = client.called("start_run")
        assert second[2]["reference"] == first[2]["reference"] == again.reference
        assert second[1][2] == {"operation": "invoice.create", "params": {"ref_number": "1001"}}
        again = world.reload(again)
        assert (again.qube_run_id, again.state, world.count(world.Run)) == ("run-q-1", "running", 1)

    def test_makes_a_new_reference_once_the_last_run_has_ended(self, world, invoice, connection, client):
        first = CreateInvoice.start(invoice, connection)
        world.update(first, state="failed")

        second = CreateInvoice.start(invoice, connection)

        assert second.id != first.id and second.reference != first.reference and not second.reused

    def test_keeps_each_connections_and_operations_runs_apart(self, world, account, invoice, connection, client):
        first = CreateInvoice.start(invoice, connection)
        client.returns["start_run"] = {"id": "run-q-2", "state": "running"}
        other = CreateInvoice.start(invoice, world.connection(account, qube_id="conn-q-other"))

        assert other.id != first.id and not other.reused

    def test_an_input_that_raises_leaves_one_failed_row_and_raises(self, world, invoice, connection, client, monkeypatch):
        def broken(operation):
            raise ValueError("no customer")

        monkeypatch.setattr(CreateInvoice, "input", broken)

        with pytest.raises(ValueError, match="no customer"):
            CreateInvoice.start(invoice, connection)
        rows = world.all(world.Run)
        assert [(row.state, row.input) for row in rows] == [("failed", None)]

    @pytest.mark.skipif(not os.environ.get("KIT_PG_URL"), reason="row locks need PostgreSQL (KIT_PG_URL)")
    def test_two_starts_at_once_make_one_run(self, world, invoice, connection, client):
        gate = threading.Barrier(2)
        started = []

        def slow_start(*args, **kwargs):
            time.sleep(0.2)
            return {"id": "run-q-1", "state": "running"}

        client.returns["start_run"] = slow_start

        def click():
            gate.wait()
            try:
                started.append(CreateInvoice.start(invoice, world.reload(connection)).id)
            finally:
                world.release()

        threads = [threading.Thread(target=click) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert len(started) == 2 and len(set(started)) == 1
        assert world.count(world.Run) == 1


class TestRetryStart:
    def test_resends_the_same_reference_workflow_input_and_webhook_url(self, world, invoice, connection, client):
        client.raises["start_run"] = timeout()
        with pytest.raises(requests.Timeout):
            CreateInvoice.start(invoice, connection)
        started = world.all(world.Run)[-1]
        invoice.number = "changed since"  # the input it resends is the first one's
        world.write(invoice)

        del client.raises["start_run"]
        client.returns["start_run"] = {"id": "run-q-1", "state": "running"}
        retried = started.retry_start()

        assert retried.id == started.id
        name, args, kwargs = client.called("start_run")[-1]
        assert args == (QUBE_ID, "add_transaction", {"operation": "invoice.create", "params": {"ref_number": "1001"}})
        assert kwargs == {"reference": started.reference, "webhook_url": started.webhook_url}
        started = world.reload(started)
        assert (started.qube_run_id, started.state) == ("run-q-1", "running")

    def test_returns_a_run_already_answered_and_refuses_one_that_failed(self, world, invoice, connection, client):
        answered = world.run(invoice, connection, qube_run_id="run-q-9")
        assert answered.retry_start() is answered
        assert client.called("start_run") == []

        failed = world.run(invoice, connection, state="failed")
        with pytest.raises(ValueError, match="only a start that got no answer"):
            failed.retry_start()

    def test_sends_the_reference_as_the_idempotency_key(self, world, invoice, connection):
        # Through the real client, to the wire: the reference is the Idempotency-Key header.
        sent = []

        class Session(object):
            def request(self, method, url, data=None, headers=None, auth=None, timeout=None):
                sent.append((method, url, json.loads(data), headers))
                response = requests.Response()
                response.status_code = 201
                response._content = json.dumps({"data": {"id": "run-q-1", "state": "running"}}).encode()
                response.headers["Content-Type"] = "application/json"
                return response

        kit.configure(client=kit.Client("key", base_url="https://qube.example", session=Session()))
        started = world.run(invoice, connection, state="starting", input={"operation": "invoice.create"})

        started.retry_start()

        method, url, body, headers = sent[0]
        assert (method, url) == ("POST", "https://qube.example/api/v2/connections/%s/workflow-runs" % QUBE_ID)
        assert headers["Idempotency-Key"] == started.reference
        assert body["reference"] == started.reference
        assert body["input"] == {"operation": "invoice.create"}


# -- Operations: the instance helpers --------------------------------------------------------


class TestOperationHelpers:
    def test_answered_forgets_the_question_only_for_its_token(self, world, run, invoice):
        run = world.update(run, question={"token": "t-1"}, links={"decisions": "x"})
        operation = CreateInvoice(invoice, run)

        operation.answered("t-0")
        assert world.reload(run).question == {"token": "t-1"}

        operation.answered("t-1")
        assert world.reload(run).question is None

    def test_quickbooks_ref_by_list_id_when_linked_else_by_name_else_none(self, world, run, invoice, customer, connection):
        operation = CreateInvoice(invoice, run)

        assert operation.quickbooks_ref(customer, kind="customer", name="Riverbend Electric") == {"full_name": "Riverbend Electric"}
        assert operation.quickbooks_ref(None, kind="customer", name=None) is None

        connection.link(customer, kind="customer", qb_id="80000001-1")
        assert operation.quickbooks_ref(customer, kind="customer", name="Riverbend Electric") == {"list_id": "80000001-1"}

    def test_quickbooks_ref_never_uses_another_connections_link(self, world, account, run, invoice, customer):
        world.connection(account, qube_id="conn-q-2").link(customer, kind="customer", qb_id="80000001-1")

        assert CreateInvoice(invoice, run).quickbooks_ref(customer, kind="customer", name="R") == {"full_name": "R"}

    REFERENCES = {
        "customer_ref": {
            "kind": "customer",
            "outcome": "found",
            "record": {"type": "customer", "list_id": "80000001-1", "edit_sequence": "17", "full_name": "Riverbend Electric"},
        },
        "invoice_line_add.0.item_ref": {
            "kind": "item",
            "outcome": "created",
            "record": {"type": "item_service", "list_id": "80000002-1", "full_name": "Widget"},
        },
        "invoice_line_add.1.item_ref": {"kind": "item", "outcome": "not_found", "record": None},
        "class_ref": {"kind": "class", "outcome": "found", "record": {"list_id": "80000003-1"}},
    }

    def event_with(self, name, run, output):
        return webhooks.parse(run_body(name, run, {"output": output}))

    def test_link_references_links_each_to_the_record_fn_returns(self, world, account, run, invoice, customer, connection):
        widget = world.customer(account, name="Widget (an item, here)")
        operation = CreateInvoice(invoice, run)
        seen = []
        records = {"customer_ref": customer, "invoice_line_add.0.item_ref": widget, "class_ref": invoice}

        def pick(path, entry):
            seen.append((path, entry["outcome"]))
            return records.get(path)

        linked = operation.link_references(self.event_with("workflow_run.completed", run, {"references": self.REFERENCES}), pick)

        assert seen == [("customer_ref", "found"), ("invoice_line_add.0.item_ref", "created"), ("class_ref", "found")]
        assert len(linked) == 3
        found = connection.quickbooks_record("80000001-1", kind="customer")
        assert (found.record, found.edit_sequence, found.name) == (customer, "17", "Riverbend Electric")
        item = connection.quickbooks_record("80000002-1", kind="item")
        assert (item.kind, item.record) == ("item_service", widget)
        klass = connection.quickbooks_record("80000003-1", kind="class")
        assert (klass.kind, klass.record) == ("class", invoice)

    def test_link_references_skips_none_and_works_on_a_cancelled_ending(self, run, invoice, customer):
        operation = CreateInvoice(invoice, run)
        cancelled = self.event_with("workflow_run.cancelled", run, {"references": {"customer_ref": self.REFERENCES["customer_ref"]}, "record": None})

        assert len(operation.link_references(cancelled, lambda path, entry: customer)) == 1
        assert operation.link_references(cancelled, lambda path, entry: None) == []
        assert operation.link_references(self.event_with("workflow_run.completed", run, None), lambda p, e: customer) == []

    def test_without_nils_at_every_depth(self, run, invoice):
        value = {"a": 1, "b": None, "c": {"d": None, "e": [1, None, {"f": None, "g": False}]}}

        assert CreateInvoice(invoice, run).without_nils(value) == {"a": 1, "c": {"e": [1, {"g": False}]}}

    def test_the_base_handlers_log_until_written(self, run, invoice, caplog):
        class Plain(kit.Operation):
            slug = "plain"

        event = webhooks.parse(vector_body("workflow_run.failed", {"reference": "r-1"}))
        with caplog.at_level(logging.INFO, logger="qubesync.kit"):
            Plain(invoice, run).failed(event)

        record = caplog.records[-1]
        assert record.levelname == "WARNING"
        assert record.getMessage() == "QuBe Sync: Plain %s (run %s): workflow_run.failed renames_exhausted (r-1)" % (invoice.id, run.id)
        with pytest.raises(NotImplementedError, match="record_type"):
            Plain.find_record("1")
        with pytest.raises(NotImplementedError):
            Plain(invoice, run).input()


# -- Notification dedupe ---------------------------------------------------------------------


class TestNotificationDedupe:
    def test_keeps_taken_ids_in_qube_notifications_by_default(self):
        assert isinstance(kit.settings().dedupe, kit.DatabaseDedupe)

    def test_runs_a_notification_delivered_twice_once(self, world, run):
        deliver(world, "run", run, run_body("workflow_run.notification", run))
        deliver(world, "run", run, run_body("workflow_run.notification", run))

        assert CreateInvoice.calls == [("notification", DELIVERY_ID)]
        assert [n.delivery_id for n in world.all(world.Notification, run_id=run.id)] == [DELIVERY_ID]

    def test_leaves_no_row_when_the_handler_raises_so_the_redelivery_runs_it(self, world, account, run, monkeypatch):
        calls = []

        def notification(operation, event):
            calls.append(1)
            world.write(world.Customer(account_id=account.id, name="written by the handler"))
            if len(calls) == 1:
                raise RuntimeError("app bug")

        monkeypatch.setattr(CreateInvoice, "notification", notification)

        with pytest.raises(RuntimeError, match="app bug"):
            kit.run("run", str(run.id), run_body("workflow_run.notification", run))
        assert world.count(world.Notification) == 0
        assert world.count(world.Customer) == 0  # the handler's writes rolled back with it

        kit.run("run", str(run.id), run_body("workflow_run.notification", run))
        assert len(calls) == 2
        assert world.count(world.Notification) == 1
        assert world.count(world.Customer) == 1

    def test_keeps_two_runs_ids_apart(self, world, run, invoice, connection):
        other = world.run(invoice, connection)
        deliver(world, "run", run, run_body("workflow_run.notification", run))
        deliver(world, "run", other, run_body("workflow_run.notification", other))

        assert len(CreateInvoice.calls) == 2

    def test_skips_on_a_unique_violation_without_aborting_the_transaction(self, world, run, monkeypatch):
        store = world.Run._kit_store
        ran = []
        with store.atomic():
            store.save(store.new("notification", run_id=run.id, delivery_id="d-1"))
            # The check finds nothing (as if another worker hadn't committed yet); the insert
            # conflicts.
            monkeypatch.setattr(store, "exists", lambda name, **filters: False)
            assert kit.DatabaseDedupe().once(run, "d-1", lambda: ran.append(1)) is False
            assert store.get("run", run.id) is not None  # the transaction still works
        assert ran == []

    def test_deletes_a_runs_rows_with_the_run(self, world, run):
        deliver(world, "run", run, run_body("workflow_run.notification", run))
        world.destroy(run)

        assert world.count(world.Notification) == 0

    def test_takes_a_cache_dedupe(self, world, run):
        class Cache(object):
            def __init__(self):
                self.values = {}

            def get(self, key):
                return self.values.get(key)

            def set(self, key, value, timeout=None):
                self.values[key] = value

        kit.configure(dedupe=kit.CacheDedupe(Cache()))
        deliver(world, "run", run, run_body("workflow_run.notification", run))
        deliver(world, "run", run, run_body("workflow_run.notification", run))

        assert len(CreateInvoice.calls) == 1
        assert world.count(world.Notification) == 0


# -- Connection events -----------------------------------------------------------------------


class TestConnectionEvents:
    @pytest.fixture
    def connection(self, world, account):
        return world.connection(account, status="pending")

    def test_applies_each_of_the_four_then_hands_it_on_with_its_owner(self, world, account, connection):
        connection = deliver(world, "connection", connection, vector_body("connection.connected"))
        assert (connection.status, connection.revision) == ("connected", 1)

        connection = deliver(world, "connection", connection, vector_body("connection.setup_cancelled"))
        assert connection.status == "setup_cancelled"

        connection = deliver(world, "connection", connection, vector_body("connection.stalled"))
        assert (connection.status, connection.stall_reason, connection.revision) == ("stalled", "not_checking_in", 3)

        connection = deliver(world, "connection", connection, vector_body("connection.resumed"))
        assert (connection.status, connection.stall_reason, connection.revision) == ("connected", None, 4)

        id = connection.id
        assert ConnectionEvents.calls == [
            ("connected", id, account.id, "connected"),
            ("setup_cancelled", id, account.id, "setup_cancelled"),
            ("stalled", id, account.id, "not_checking_in"),
            ("resumed", id, account.id, None),
        ]

    def test_skips_an_event_for_another_connection(self, world, connection, caplog):
        connection = deliver(world, "connection", connection, vector_body("connection.connected", {"connection": {"id": "someone-elses"}}))

        assert ConnectionEvents.calls == []
        assert (connection.status, connection.revision) == ("pending", None)
        assert "connection %s skipped connection.connected for 'someone-elses': not this connection" % connection.id in caplog.text

    def test_skips_an_event_that_isnt_a_connections(self, world, connection, caplog):
        deliver(world, "connection", connection, vector_body("workflow_run.completed"))

        assert ConnectionEvents.calls == []
        assert "skipped workflow_run.completed for None: not this connection" in caplog.text

    def test_applies_an_event_only_when_its_newer(self, world, connection):
        deliver(world, "connection", connection, vector_body("connection.resumed"))  # revision 4
        connection = deliver(world, "connection", connection, vector_body("connection.stalled"))  # 3, late

        assert [call[0] for call in ConnectionEvents.calls] == ["resumed"]
        assert (connection.status, connection.revision) == ("connected", 4)

    def test_keeps_two_connections_on_one_account_apart(self, world, account, connection):
        other = world.connection(account, qube_id="conn-q-2", status="pending")
        connection = deliver(world, "connection", connection, vector_body("connection.connected"))
        other = deliver(world, "connection", other, vector_body("connection.connected"))  # the first's id

        assert connection.status == "connected"
        assert other.status == "pending"

    def test_raises_naming_the_config_file_when_connection_events_isnt_set(self, connection):
        kit.configure(connection_events=None)

        with pytest.raises(kit.NotConfigured, match=r"connection_events.*quickbooks_desktop/config\.py"):
            kit.run("connection", str(connection.id), vector_body("connection.connected"))

    def test_the_base_handlers_log_a_stall_as_a_warning(self, connection, caplog):
        event = webhooks.parse(vector_body("connection.stalled"))
        kit.ConnectionEvents(connection).stalled(event)

        record = caplog.records[-1]
        assert record.levelname == "WARNING"
        assert record.getMessage() == "QuBe Sync: connection %s: connection.stalled (revision 3)" % connection.id

    class TestWithNoQubeIdYet:
        @pytest.fixture
        def connection(self, world, account):
            return world.connection(account, qube_id=None, status="pending")

        def test_raises_not_ready_when_quickbooks_has_none_for_the_row(self, connection, client):
            client.returns["list_connections"] = [{"id": "other", "webhook_url": "https://elsewhere"}]

            with pytest.raises(kit.NotReady, match="no qube_id yet"):
                kit.run("connection", str(connection.id), vector_body("connection.connected"))
            assert ConnectionEvents.calls == []

        def test_adopts_the_connection_made_with_its_webhook_url_then_applies_the_event(self, world, connection, client, caplog):
            client.returns["list_connections"] = [
                {
                    "id": QUBE_ID,
                    "webhook_url": connection.webhook_url,
                    "last_connected_at": None,
                    "name": None,
                    "created_at": iso(datetime.datetime.now(datetime.timezone.utc)),
                }
            ]
            with caplog.at_level(logging.INFO, logger="qubesync.kit"):
                connection = deliver(world, "connection", connection, vector_body("connection.connected"))

            assert (connection.qube_id, connection.status) == (QUBE_ID, "connected")
            assert "adopted QuBe Sync's connection" in caplog.text


# -- The default queue -----------------------------------------------------------------------


class TestDefaultQueue:
    @pytest.fixture(autouse=True)
    def no_waits(self, monkeypatch):
        monkeypatch.setattr("qubesync.kit._job.retry_delay", lambda attempt: 0)

    def test_retries_a_delivery_whose_work_raised(self, world, run, monkeypatch):
        tries = []

        def ended(operation, event):
            tries.append(1)
            if len(tries) < 3:
                raise RuntimeError("app bug")
            CreateInvoice.calls.append(("ended",))

        monkeypatch.setattr(CreateInvoice, "ended", ended)
        kit.perform({"kind": "run", "id": str(run.id), "body": run_body("workflow_run.completed", run)})
        drain()

        assert len(tries) == 3
        assert world.reload(run).state == "completed"

    def test_retries_not_ready_until_the_connection_has_its_id(self, world, account, client):
        row = world.connection(account, qube_id=None, status="pending")
        listings = [[], []]

        def listed():
            if listings:
                return listings.pop()
            return [{"id": QUBE_ID, "webhook_url": row.webhook_url, "last_connected_at": None, "created_at": iso(datetime.datetime.now(datetime.timezone.utc))}]

        client.returns["list_connections"] = listed
        kit.perform({"kind": "connection", "id": str(row.id), "body": vector_body("connection.connected")})
        drain()

        assert world.reload(row).status == "connected"

    def test_logs_an_error_when_the_attempts_run_out(self, world, run, monkeypatch, caplog):
        tries = []

        def ended(operation, event):
            tries.append(1)
            raise RuntimeError("app bug")

        monkeypatch.setattr(CreateInvoice, "ended", ended)
        kit.configure(job_attempts=3)
        run_id = run.id
        kit.perform({"kind": "run", "id": str(run_id), "body": run_body("workflow_run.completed", run)})
        drain()

        assert len(tries) == 3
        assert "QuBe Sync: gave up on a webhook for run %s after 3 attempts: RuntimeError: app bug" % run_id in caplog.text
        assert world.reload(run).state == "running"  # each attempt rolled back


# -- Sync status -----------------------------------------------------------------------------


def ended(world, run, state="completed", seconds_ago=0, **fields):
    moment = world.Run._kit_store.now() - datetime.timedelta(seconds=seconds_ago)
    return world.update(run, state=state, ended_at=moment, updated_at=moment, **fields)


def linked(world, connection, invoice, seconds_ago=0):
    row = connection.link(invoice, kind="invoice", qb_id="TXN-1")
    moment = world.Run._kit_store.now() - datetime.timedelta(seconds=seconds_ago)
    return world.update(row, updated_at=moment)


class TestSyncStatus:
    def status(self, connection, invoice):
        return connection.sync_status(invoice, "create_invoice")

    def test_not_sent_with_no_run_and_no_link(self, connection, invoice):
        status = self.status(connection, invoice)

        assert (status.status, status.qb_id, status.error, status.retry, status.unconfirmed) == ("not_sent", None, None, False, False)
        assert status.summary_text is None

    @pytest.mark.parametrize("state,expected", [("starting", "sending"), ("running", "sending"), ("awaiting_input", "needs_answer")])
    def test_a_run_that_hasnt_ended_wins_over_a_link(self, world, connection, invoice, state, expected):
        linked(world, connection, invoice)
        world.run(invoice, connection, state=state)

        status = self.status(connection, invoice)

        assert (status.status, status.qb_id, status.retry) == (expected, "TXN-1", False)

    def test_an_unconfirmed_start_is_sending_and_unconfirmed(self, world, connection, invoice):
        world.ago(world.run(invoice, connection, state="starting"), 120)

        status = self.status(connection, invoice)

        assert (status.status, status.unconfirmed, status.summary_text) == ("sending", True, "Not confirmed by QuBe Sync yet")

    def test_failed_with_its_error_and_retry_when_not_linked(self, world, connection, invoice):
        error = {"message": "No customer named Riverbend"}
        ended(world, world.run(invoice, connection), state="failed", error=error)

        status = self.status(connection, invoice)

        assert (status.status, status.error, status.retry) == ("failed", error, True)
        assert status.summary_text == "Failed: No customer named Riverbend"

    def test_a_failure_after_the_link_wins_without_a_retry(self, world, connection, invoice):
        linked(world, connection, invoice, seconds_ago=3600)
        ended(world, world.run(invoice, connection), state="failed")

        status = self.status(connection, invoice)

        assert (status.status, status.qb_id, status.retry) == ("failed", "TXN-1", False)

    def test_a_link_after_the_failure_is_in_quickbooks(self, world, connection, invoice):
        ended(world, world.run(invoice, connection), state="failed", seconds_ago=3600)
        linked(world, connection, invoice)

        status = self.status(connection, invoice)

        assert (status.status, status.qb_id, status.error, status.summary_text) == ("in_quickbooks", "TXN-1", None, "In QuickBooks")

    def test_cancelled_including_a_chart_that_chose_to_stop(self, world, connection, invoice):
        ended(world, world.run(invoice, connection), state="completed", outcome="cancelled")

        status = self.status(connection, invoice)

        assert (status.status, status.retry) == ("cancelled", True)

    def test_a_completed_run_with_its_link_is_in_quickbooks_in_its_words(self, world, connection, invoice):
        ended(world, world.run(invoice, connection), outcome="added", seconds_ago=10)
        linked(world, connection, invoice)

        status = self.status(connection, invoice)

        assert (status.status, status.summary_text) == ("in_quickbooks", "Added to QuickBooks")

    def test_a_completed_run_that_linked_nothing_is_done(self, world, connection, invoice):
        ended(world, world.run(invoice, connection), outcome="completed")

        status = self.status(connection, invoice)

        assert (status.status, status.qb_id, status.retry, status.summary_text) == ("done", None, False, "Done")

    def test_is_per_connection_and_operation(self, world, account, connection, invoice):
        other = world.connection(account, qube_id="conn-q-other")
        world.run(invoice, connection, state="running")
        linked(world, other, invoice)

        assert self.status(connection, invoice).status == "sending"
        assert self.status(other, invoice).status == "in_quickbooks"
        assert connection.sync_status(invoice, "sync_customer").status == "not_sent"

    def test_latest_reads_it_on_the_latest_runs_connection(self, world, account, connection, invoice):
        assert kit.SyncStatus.latest(invoice, "create_invoice").status == "not_sent"
        other = world.connection(account, qube_id="conn-q-other")
        world.ago(world.run(invoice, connection, state="running"), 60)
        ended(world, world.run(invoice, other), state="failed")

        assert kit.SyncStatus.latest(invoice, "create_invoice").status == "failed"


class TestSyncStatusScopes:
    @pytest.fixture
    def invoices(self, world, account):
        return [world.invoice(account, number=str(1000 + n)) for n in range(4)]

    def ids(self, world, rows):
        return sorted(row.id for row in rows)

    def query(self, world):
        if world.name == "django":
            return world.Invoice.objects.filter(number__startswith="10")
        return world.Session().query(world.Invoice).filter(world.Invoice.number.like("10%"))

    def test_in_and_not_in_quickbooks_by_this_connections_links(self, world, account, connection, invoices):
        connection.link(invoices[0], kind="invoice", qb_id="TXN-0")
        connection.link(invoices[1], kind="invoice_copy", qb_id="TXN-1")
        world.connection(account, qube_id="conn-q-other").link(invoices[2], kind="invoice", qb_id="TXN-2")

        assert self.ids(world, connection.in_quickbooks(world.Invoice)) == self.ids(world, invoices[:2])
        assert self.ids(world, connection.not_in_quickbooks(self.query(world))) == self.ids(world, invoices[2:])

    def test_needing_answer_and_sending_by_this_connections_runs_of_that_operation(self, world, account, connection, invoices):
        world.run(invoices[0], connection, state="awaiting_input")
        world.run(invoices[1], connection, state="starting")
        world.run(invoices[2], connection, state="running")
        world.run(invoices[3], connection, state="completed")
        world.run(invoices[3], world.connection(account, qube_id="conn-q-other"), state="awaiting_input")
        world.run(invoices[3], connection, operation="sync_customer", state="awaiting_input")

        assert self.ids(world, connection.needing_answer(world.Invoice, "create_invoice")) == self.ids(world, invoices[:1])
        assert self.ids(world, connection.sending(self.query(world), "create_invoice")) == self.ids(world, invoices[1:3])

    def test_takes_a_select_on_sqlalchemy(self, world, connection, invoices):
        if world.name != "sqlalchemy":
            pytest.skip("SQLAlchemy's select()")
        from sqlalchemy import select

        connection.link(invoices[0], kind="invoice", qb_id="TXN-0")

        found = world.Session().execute(connection.in_quickbooks(select(world.Invoice))).scalars().all()

        assert self.ids(world, found) == self.ids(world, invoices[:1])


class TestLooksStuck:
    def test_a_confirmed_run_quiet_for_ten_minutes_while_running(self, world, invoice, connection):
        run = world.run(invoice, connection, state="running", qube_run_id="run-q-7")
        assert not run.looks_stuck()

        assert world.quiet(run, 11 * 60).looks_stuck()

    def test_waiting_on_a_question_it_never_received(self, world, invoice, connection):
        run = world.quiet(world.run(invoice, connection, state="awaiting_input", qube_run_id="run-q-7"), 11 * 60)
        assert run.looks_stuck()

        asked = world.quiet(world.update(run, question={"token": "t"}), 11 * 60)
        assert not asked.looks_stuck()

    @pytest.mark.parametrize("fields", [{"qube_run_id": None, "state": "running"}, {"qube_run_id": "q", "state": "completed"}, {"qube_run_id": "q", "state": "starting"}])
    def test_never_an_unconfirmed_ended_or_starting_run(self, world, invoice, connection, fields):
        run = world.quiet(world.run(invoice, connection, **fields), 11 * 60)

        assert not run.looks_stuck()
