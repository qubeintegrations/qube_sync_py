"""Plain v2 requests (qubesync.kit.Request), sync marks, run pruning and Connection.disconnect,
on Django's ORM and on SQLAlchemy."""
import datetime
import json

import pytest

import qubesync.kit as kit
from kit_support import QUBE_ID, REQUEST_ID, WEBHOOK_URL, api_error, kit_reset, run_body, timeout, vector_body  # noqa: F401
from kit_worlds import ConnectionEvents, CreateInvoice, FindCustomer, make_world
from qubesync.kit._store import utc


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
def customer(world, account):
    return world.customer(account, name="Northwind Builders")


@pytest.fixture
def client():
    return kit.settings().client


@pytest.fixture
def row(world, customer, connection):
    return world.request(customer, connection)


def deliver(world, row, name, changes=None):
    body = json.loads(vector_body(name))
    body.update(changes or {})
    kit.run("request", str(row.id), json.dumps(body))
    return world.reload(row)


def page(number, iteration_state, state="response_received"):
    return {"page": number, "page_request_id": "pr-%s" % number, "iteration_state": iteration_state, "state": state}


def days_ago(world, days):
    return world.Run._kit_store.now() - datetime.timedelta(days=days)


# -- Request.queue ---------------------------------------------------------------------------


class TestQueue:
    def test_writes_the_row_first_and_queues_with_its_reference_as_the_key_and_its_webhook_url(self, world, customer, connection, client):
        queued = FindCustomer.queue(customer, connection)

        row = world.reload(queued)
        assert (row.operation, row.qube_id, row.state, row.params, row.ended_at) == (
            "find_customer", "req-q-1", "queued", {"full_name": "Northwind Builders"}, None
        )
        assert row.reference.startswith("find_customer-%s-" % customer.id)
        assert row.webhook_url == "%s/requests/%s" % (WEBHOOK_URL, row.id)
        assert row.record == customer and row.connection.id == connection.id
        assert client.called("queue") == [
            ("queue", ("customer.query", QUBE_ID, {"full_name": "Northwind Builders"}),
             {"webhook_url": row.webhook_url, "idempotency_key": row.reference})
        ]
        assert queued.reused is False

    def test_returns_the_records_request_that_hasnt_ended_and_a_new_one_once_it_has(self, world, customer, connection, client):
        first = FindCustomer.queue(customer, connection)
        world.update(first, state="retryable")

        again = FindCustomer.queue(customer, connection)
        assert (again.id, again.reused) == (first.id, True)
        assert len(client.called("queue")) == 1

        world.update(first, state="response_received", ended_at=world.Run._kit_store.now())
        later = FindCustomer.queue(customer, connection)
        assert later.id != first.id
        assert later.reference != first.reference

    def test_sends_an_unconfirmed_queue_again_with_its_own_reference_and_params(self, world, customer, connection, client):
        client.raises["queue"] = timeout()
        with pytest.raises(kit.NETWORK_ERRORS):
            FindCustomer.queue(customer, connection)
        first = world.all(world.QueuedRequest)[0]
        assert (first.state, first.qube_id) == ("queued", None)

        customer.name = "Renamed since"  # the resend still sends what the first did
        world.write(customer)
        del client.raises["queue"]
        again = FindCustomer.queue(customer, connection)

        assert (again.id, again.reused, world.reload(again).qube_id) == (first.id, True, "req-q-1")
        sent = client.called("queue")[-1]
        assert sent[1][2] == {"full_name": "Northwind Builders"}
        assert sent[2]["idempotency_key"] == first.reference

        world.reload(first).retry_queue()  # confirmed now: nothing is sent
        assert len(client.called("queue")) == 2

    def test_marks_the_row_failed_and_raises_when_quickbooks_sync_refuses_it(self, world, customer, connection, client):
        client.raises["queue"] = api_error(422, {"detail": "bad params"})

        with pytest.raises(kit.APIError):
            FindCustomer.queue(customer, connection)
        row = world.all(world.QueuedRequest)[0]
        assert (row.state, row.qube_id) == ("failed", None)
        assert row.ended_at is not None

    def test_leaves_a_queue_answered_409_queued(self, world, customer, connection, client):
        client.raises["queue"] = api_error(409, "in use")

        with pytest.raises(kit.APIError):
            FindCustomer.queue(customer, connection)
        row = world.all(world.QueuedRequest)[0]
        assert (row.state, row.ended_at) == ("queued", None)

    def test_marks_the_row_failed_when_its_params_raise_before_anything_is_sent(self, world, customer, connection, client, monkeypatch):
        def broken(self):
            raise ValueError("no name")

        monkeypatch.setattr(FindCustomer, "params", broken)

        with pytest.raises(ValueError, match="no name"):
            FindCustomer.queue(customer, connection)
        row = world.all(world.QueuedRequest)[0]
        assert row.state == "failed" and row.ended_at is not None
        assert client.called("queue") == []

    def test_refuses_a_connection_quickbooks_sync_hasnt_made(self, world, account, customer):
        pending = world.connection(account, qube_id=None, status="pending")

        with pytest.raises(kit.NotConnected):
            FindCustomer.queue(customer, pending)


# -- The job ---------------------------------------------------------------------------------


class TestRequestJob:
    def test_hands_an_answer_to_answered_then_done_and_ends_the_row(self, world, row):
        row = deliver(world, row, "request: an answer")

        assert FindCustomer.calls == [("answered", 1), ("done", 1)]
        assert (row.state, row.pages_answered, row.last_page, row.error) == ("response_received", 1, 1, None)
        assert row.done()

    def test_takes_a_delivery_once_by_page_request_id_and_state(self, world, row):
        deliver(world, row, "request: an answer")
        deliver(world, row, "request: an answer")

        assert FindCustomer.calls == [("answered", 1), ("done", 1)]
        assert world.count(world.RequestDelivery, request_id=row.id) == 1

    def test_calls_done_once_every_page_is_in_whatever_order_they_come_in(self, world, row):
        deliver(world, row, "request: a page of a paginated query", page(3, "done"))
        row = deliver(world, row, "request: a page of a paginated query", page(1, "continue"))
        assert not row.ended()
        assert (row.pages_answered, row.last_page, row.state) == (2, 3, "response_received")

        deliver(world, row, "request: a page of a paginated query", page(2, "continue"))
        row = deliver(world, row, "request: a page of a paginated query", page(2, "continue"))  # a retry

        assert FindCustomer.calls == [("answered", 3), ("answered", 1), ("answered", 2), ("done", 3)]
        assert row.done()

    def test_keeps_a_retryable_not_final_and_skips_one_after_its_pages_answer(self, world, row):
        row = deliver(world, row, "request: QuickBooks refused it", page(1, "not_applicable", state="retryable"))
        assert (row.state, row.ended_at) == ("retryable", None)
        assert "user_message" in row.error

        deliver(world, row, "request: an answer", page(1, "not_applicable"))
        late = dict(page(1, "not_applicable", state="retryable"), page_request_id="pr-1-late")
        row = deliver(world, row, "request: QuickBooks refused it", late)

        assert FindCustomer.calls == [("retrying", 1), ("answered", 1), ("done", 1)]
        assert row.state == "response_received"

    def test_ends_the_row_on_an_error_keeping_it_and_hands_it_to_failed(self, world, row):
        row = deliver(world, row, "request: QuickBooks refused it")

        assert FindCustomer.calls == [("failed", "error")]
        assert row.state == "error" and row.ended()
        assert row.error["error_code"] == 3100

    def test_hands_a_timed_out_to_failed_by_default(self, world, row):
        row = deliver(world, row, "request: an answer that never came back")

        assert FindCustomer.calls == [("failed", "timed_out")]
        assert row.state == "timed_out" and row.ended()

    def test_skips_an_event_whose_id_isnt_the_rows(self, world, row, caplog):
        row = deliver(world, row, "request: an answer", {"id": "someone-elses"})

        assert FindCustomer.calls == []
        assert row.state == "queued"
        assert "skipped request 'someone-elses': not this request" in caplog.text

    def test_skips_an_event_that_isnt_a_requests(self, world, row, caplog):
        kit.run("request", str(row.id), vector_body("workflow_run.completed"))

        assert FindCustomer.calls == []
        assert "not this request" in caplog.text

    def test_takes_the_id_from_the_first_event_before_the_queues_answer_is_saved(self, world, customer, connection):
        unconfirmed = world.request(customer, connection, qube_id=None)

        unconfirmed = deliver(world, unconfirmed, "request: an answer")

        assert (unconfirmed.qube_id, unconfirmed.state) == (REQUEST_ID, "response_received")

    def test_drops_a_deleted_request_and_raises_for_a_slug_taken_out(self, world, row, caplog):
        kit.run("request", "0", vector_body("request: an answer"))
        assert "request 0 isn't there" in caplog.text

        kit.configure(operations={"create_invoice": CreateInvoice})
        with pytest.raises(kit.UnknownOperation):
            kit.run("request", str(row.id), vector_body("request: an answer"))

    def test_keeps_no_response_body_on_the_row(self, world):
        if world.name == "django":
            names = [f.name for f in world.QueuedRequest._meta.concrete_fields]
        else:
            names = list(world.QueuedRequest.__table__.c.keys())
        assert "response_json" not in names and "response_xml" not in names


# -- Sync marks ------------------------------------------------------------------------------


class TestSyncMarks:
    def test_a_completed_run_moves_its_workflows_mark_to_when_the_run_started(self, world, connection, account):
        invoice = world.invoice(account)
        run = world.ago(world.run(invoice, connection), 300)
        assert connection.last_synced_at("add_transaction") is None

        deliver_run(world, run, "workflow_run.completed")

        started = utc(world.Run._kit_store.utc(run.created_at))
        assert world.reload(connection).last_synced_at("add_transaction") == started
        assert world.reload(connection).last_synced_at("add_transaction").tzinfo is not None
        assert CreateInvoice(invoice, world.reload(run)).last_synced_at() == started

    def test_never_moves_it_back_when_an_older_run_completes_later(self, world, connection, account):
        newer = world.run(world.invoice(account, "1"), connection)
        older = world.ago(world.run(world.invoice(account, "2"), connection), 3600)

        deliver_run(world, newer, "workflow_run.completed")
        deliver_run(world, older, "workflow_run.completed")

        assert connection.last_synced_at("add_transaction") == world.Run._kit_store.utc(newer.created_at)
        assert world.count(world.SyncMark) == 1

    def test_a_failed_run_leaves_it_alone(self, world, connection, account):
        deliver_run(world, world.run(world.invoice(account), connection), "workflow_run.failed")

        assert connection.last_synced_at("add_transaction") is None


def deliver_run(world, run, name):
    kit.run("run", str(run.id), run_body(name, run, {"revision": 5}))
    return world.reload(run)


# -- Pruning ---------------------------------------------------------------------------------


class TestPruning:
    def test_is_off_until_prune_runs_after_is_set(self, world, account, connection):
        run = world.run(world.invoice(account), connection, state="completed", ended_at=days_ago(world, 400))

        kit.prune_runs()

        assert world.count(world.Run, id=run.id) == 1

    @pytest.mark.parametrize("value", [datetime.timedelta(hours=23), 90, "90 days"])
    def test_takes_only_a_timedelta_of_a_day_or_more(self, value):
        with pytest.raises(TypeError, match="prune_runs_after"):
            kit.configure(prune_runs_after=value)

    def test_deletes_ended_runs_and_requests_past_the_setting_and_keeps_the_rest(self, world, account, connection, customer):
        kit.configure(prune_runs_after=datetime.timedelta(days=30))
        invoice = world.invoice(account)
        old_done = world.run(invoice, connection, state="completed", ended_at=days_ago(world, 40))
        world.create(world.Notification, run_id=old_done.id, delivery_id="d-1")
        failed_at_start = world.update(world.run(invoice, connection, state="failed"), updated_at=days_ago(world, 40))
        old_going = world.update(world.run(invoice, connection, state="running"), updated_at=days_ago(world, 40))
        recent = world.run(invoice, connection, state="failed", ended_at=days_ago(world, 2))
        connection.link(invoice, kind="invoice", qb_id="T-1")
        synced = deliver_run(world, world.run(invoice, connection), "workflow_run.completed")  # a sync mark

        old_request = world.request(customer, connection, state="response_received", ended_at=days_ago(world, 40))
        world.create(world.RequestDelivery, request_id=old_request.id, dedupe_key="pr-1:response_received", page=1, state="response_received")
        going_request = world.update(world.request(customer, connection, state="retryable"), updated_at=days_ago(world, 40))

        kit.prune_runs()

        assert sorted(r.id for r in world.all(world.Run)) == sorted([old_going.id, recent.id, synced.id])
        assert failed_at_start.id != synced.id
        assert world.count(world.Notification) == 0
        assert [r.id for r in world.all(world.QueuedRequest)] == [going_request.id]
        assert world.count(world.RequestDelivery) == 0
        assert world.count(world.QuickbooksRecord) == 1
        assert world.count(world.SyncMark) == 1

    def test_never_prunes_what_ended_within_a_day(self, world, account, connection):
        hours_ago = world.Run._kit_store.now() - datetime.timedelta(hours=3)
        run = world.run(world.invoice(account), connection, state="completed", ended_at=hours_ago)

        assert world.Run.prunable(datetime.timedelta(hours=1)).count() == 0
        assert world.Run.prunable(datetime.timedelta(0)).count() == 0
        assert world.count(world.Run, id=run.id) == 1


# -- Disconnect ------------------------------------------------------------------------------


class TestDisconnect:
    def test_deletes_the_row_with_its_runs_requests_links_and_marks_after_the_hook(self, world, account, connection, customer):
        other = world.connection(world.account("Someone else"), qube_id="other-q")
        invoice = world.invoice(account)
        run = world.run(invoice, connection)
        world.create(world.Notification, run_id=run.id, delivery_id="d-1")
        deliver_run(world, world.run(invoice, connection), "workflow_run.completed")
        connection.link(invoice, kind="invoice", qb_id="T-1")
        deliver(world, world.request(customer, connection), "request: an answer")
        kept = world.run(world.invoice(account, "2"), other)

        world.reload(connection).disconnect()

        assert ConnectionEvents.calls == [("disconnected", connection.id, True)]
        assert world.count(world.Connection, id=connection.id) == 0
        assert [r.id for r in world.all(world.Run)] == [kept.id]
        for model in (world.Notification, world.QueuedRequest, world.RequestDelivery, world.QuickbooksRecord, world.SyncMark):
            assert world.count(model) == 0, model

    def test_rolls_everything_back_when_the_hook_raises(self, world, account, connection, monkeypatch):
        run = world.run(world.invoice(account), connection)

        def broken(self):
            raise RuntimeError("the app's rows")

        monkeypatch.setattr(ConnectionEvents, "disconnected", broken)

        with pytest.raises(RuntimeError):
            world.reload(connection).disconnect()
        assert world.count(world.Connection, id=connection.id) == 1
        assert world.count(world.Run, id=run.id) == 1


# -- An answer QuBe Sync took ----------------------------------------------------------------


class TestAnswered:
    def test_taken_puts_the_run_back_to_running_while_its_token_is_the_questions(self, world, account, connection):
        question = {"token": "tok", "choices": []}
        run = world.run(world.invoice(account), connection, state="awaiting_input", question=question, links={"decisions": "d"})

        CreateInvoice(None, run).answered("other-token", taken=True)
        assert world.reload(run).state == "awaiting_input"

        CreateInvoice(None, run).answered("tok", taken=True)
        run = world.reload(run)
        assert (run.state, run.question) == ("running", None)

    def test_not_taken_leaves_the_state_alone(self, world, account, connection):
        run = world.run(world.invoice(account), connection, state="awaiting_input", question={"token": "tok"})

        CreateInvoice(None, run).answered("tok")

        assert world.reload(run).state == "awaiting_input"
