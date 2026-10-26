"""Every route and its status codes, through Django's, Flask's and FastAPI's test clients:
onboarding, the webhooks, the questions, the start retry and the templates on a record's page,
each scoped to the signed-in account."""
import json
import logging
import re
import time

import pytest

import qubesync.kit as kit
from kit_support import (  # noqa: F401
    DECISIONS,
    ONBOARDING,
    QUBE_ID,
    QUESTION,
    SEARCH,
    SECRET,
    VECTORS,
    api_error,
    drain,
    kit_reset,
    run_body,
    sign,
    timeout,
    vector,
    vector_body,
    vector_prompt,
)
from kit_worlds import CreateInvoice, SyncCustomer, make_driver


@pytest.fixture(params=["django", "flask", "fastapi"])
def app(request, kit_reset):
    return make_driver(request.param)


@pytest.fixture
def http(app):
    return app[0]


@pytest.fixture
def world(app):
    return app[1]


@pytest.fixture
def account(world):
    return world.account()


@pytest.fixture
def client():
    return kit.settings().client


@pytest.fixture
def queued():
    handed = []
    kit.configure(enqueue=lambda delivery: handed.append(delivery))
    return handed


def signed_out(http, response):
    assert response.status in http.signed_out


# -- Onboarding ------------------------------------------------------------------------------


class TestConnect:
    def test_writes_a_row_makes_quickbooks_with_its_webhook_url_and_sends_them_to_setup(self, http, world, account, client):
        response = http.post("/quickbooks/connections", {"name": " Main file "}, account=account)

        made = world.all(world.Connection)[-1]
        assert response.status == 303
        assert response.location == ONBOARDING
        name, args, kwargs = client.called("create_connection")[0]
        assert kwargs == {"webhook_url": made.webhook_url, "name": "Main file"}
        assert re.match(r"\Ahttps://app\.example/webhooks/qube/connections/\d+\Z", made.webhook_url)
        assert (made.owner.id, made.qube_id, made.status, made.name) == (account.id, "conn-q-1", "pending", "Main file")

    def test_makes_a_new_one_when_the_accounts_only_one_is_connected(self, http, world, account, client):
        world.connection(account)
        client.returns["create_connection"] = {"id": "conn-q-2", "links": {"onboarding": ONBOARDING}}

        http.post("/quickbooks/connections", account=account)

        assert sorted(c.qube_id for c in world.all(world.Connection)) == sorted([QUBE_ID, "conn-q-2"])

    def test_sends_the_newest_never_connected_one_back_through_setup(self, http, world, account, client):
        world.ago(world.connection(account, qube_id="conn-q-old", status="pending"), 3600)
        world.connection(account, qube_id="conn-q-new", status="setup_cancelled")

        response = http.post("/quickbooks/connections", account=account)

        assert response.location == ONBOARDING
        assert world.count(world.Connection) == 2
        assert client.called("create_connection") == []
        assert [c[1] for c in client.called("update_connection")] == [("conn-q-new",)]
        assert [c[1] for c in client.called("regenerate_onboarding")] == [("conn-q-new",)]

    def test_makes_another_with_new_1(self, http, world, account, client):
        world.connection(account, qube_id="conn-q-pending", status="pending")
        client.returns["create_connection"] = {"id": "conn-q-2", "links": {"onboarding": ONBOARDING}}

        http.post("/quickbooks/connections", {"new": "1"}, account=account)

        assert world.count(world.Connection) == 2

    def test_leaves_the_row_without_a_qube_id_when_theres_no_answer_and_the_next_click_picks_it_up(self, http, world, account, client):
        client.raises["create_connection"] = api_error(500)
        with pytest.raises(kit.APIError):
            http.post("/quickbooks/connections", account=account)
        row = world.all(world.Connection)[-1]
        assert (row.qube_id, row.status) == (None, "pending")

        del client.raises["create_connection"]
        http.post("/quickbooks/connections", account=account)

        assert world.count(world.Connection) == 1
        assert world.reload(row).qube_id == "conn-q-1"
        assert client.names().count("list_connections") == 1

    def test_adopts_a_connection_whose_id_was_never_saved(self, http, world, account, client):
        row = world.connection(account, qube_id=None, status="pending")
        client.returns["list_connections"] = [
            {
                "id": "conn-q-lost",
                "webhook_url": row.webhook_url,
                "last_connected_at": None,
                "name": None,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
        ]

        response = http.post("/quickbooks/connections", account=account)

        assert world.reload(row).qube_id == "conn-q-lost"
        assert client.called("create_connection") == []
        assert response.location == ONBOARDING

    def test_is_behind_the_apps_sign_in(self, http, world):
        signed_out(http, http.post("/quickbooks/connections"))
        assert world.count(world.Connection) == 0

    def test_answers_401_when_current_account_finds_no_account(self, http, world, account, caplog):
        kit.configure(current_account=lambda request: None)

        response = http.post("/quickbooks/connections", account=account)

        assert response.status == 401
        assert "current_account found no signed-in account" in caplog.text

    def test_raises_naming_the_config_file_when_current_account_isnt_set(self, http, account):
        kit.configure(current_account=None)

        with pytest.raises(kit.NotConfigured, match=r"current_account.*quickbooks_desktop/config\.py"):
            http.post("/quickbooks/connections", account=account)


class TestOnboarding:
    @pytest.fixture
    def connection(self, world, account):
        return world.connection(account)

    def test_brings_the_webhook_url_up_to_date_and_sends_them_back_through_setup(self, http, account, connection, client):
        response = http.post("/quickbooks/connections/%s/onboarding" % connection.id, account=account)

        assert client.called("update_connection") == [("update_connection", (QUBE_ID,), {"webhook_url": connection.webhook_url})]
        assert client.called("regenerate_onboarding") == [("regenerate_onboarding", (QUBE_ID,), {})]
        assert (response.status, response.location) == (303, ONBOARDING)

    def test_makes_quickbooks_connection_for_a_row_left_without_one(self, http, world, account, connection, client):
        connection = world.update(connection, qube_id=None)
        client.returns["create_connection"] = {"id": "conn-q-9", "links": {"onboarding": ONBOARDING}}

        response = http.post("/quickbooks/connections/%s/onboarding" % connection.id, account=account)

        assert world.reload(connection).qube_id == "conn-q-9"
        assert response.location == ONBOARDING

    def test_answers_404_for_another_accounts_connection_and_asks_nothing(self, http, world, connection, client):
        response = http.post("/quickbooks/connections/%s/onboarding" % connection.id, account=world.account("Someone else"))

        assert response.status == 404
        assert client.calls == []

    def test_answers_404_for_a_connection_that_isnt_there(self, http, account):
        assert http.post("/quickbooks/connections/0/onboarding", account=account).status == 404
        assert http.post("/quickbooks/connections/nope/onboarding", account=account).status == 404

    def test_is_behind_the_apps_sign_in(self, http, connection, client):
        signed_out(http, http.post("/quickbooks/connections/%s/onboarding" % connection.id))
        assert client.calls == []


# -- Webhooks --------------------------------------------------------------------------------


class TestRunWebhook:
    @pytest.fixture
    def run(self, world, account):
        return world.run(world.invoice(account), world.connection(account))

    @pytest.fixture
    def body(self, run):
        return run_body("workflow_run.completed", run)

    def deliver(self, http, path, body, header, content_type="application/json"):
        headers = {"X-QUBE-Signature": header} if header else {}
        return http.post(path, body=body, headers=headers, content_type=content_type)

    def test_verifies_enqueues_the_raw_body_and_answers_200(self, http, run, body, queued):
        response = self.deliver(http, "/webhooks/qube/runs/%s" % run.id, body, sign(body))

        assert response.status == 200
        assert queued == [{"kind": "run", "id": str(run.id), "body": body}]

    def test_answers_404_for_a_run_that_isnt_there_once_the_signature_checks_out(self, http, body, queued):
        assert self.deliver(http, "/webhooks/qube/runs/0", body, sign(body)).status == 404
        assert self.deliver(http, "/webhooks/qube/runs/nope", body, sign(body)).status == 404
        assert queued == []

    def test_checks_the_signature_before_the_row(self, http, body, queued):
        assert self.deliver(http, "/webhooks/qube/runs/0", body, None).status == 401

    def test_verifies_the_servers_own_test_vector_at_its_timestamp(self, http, run, queued, monkeypatch):
        entry = vector("workflow_run.completed")
        kit.configure(webhook_secret=VECTORS["secrets"])
        monkeypatch.setattr("qubesync.webhooks.time.time", lambda: VECTORS["timestamp"])

        assert self.deliver(http, "/webhooks/qube/runs/%s" % run.id, entry["body"], entry["header"]).status == 200

    def test_takes_a_list_of_secrets_while_one_rotates(self, http, run, body, queued):
        kit.configure(webhook_secret=["whsec_new", SECRET])

        assert self.deliver(http, "/webhooks/qube/runs/%s" % run.id, body, sign(body)).status == 200

    def test_answers_503_logged_without_the_body_when_the_enqueue_returns_false(self, http, run, body, caplog):
        kit.configure(enqueue=lambda delivery: False)

        response = self.deliver(http, "/webhooks/qube/runs/%s" % run.id, body, sign(body))

        assert response.status == 503
        assert "couldn't enqueue a webhook for run %s" % run.id in caplog.text
        assert run.reference not in caplog.text

    def test_answers_503_logged_without_the_body_or_message_when_the_enqueue_raises(self, http, run, body, caplog):
        def broken(delivery):
            raise IOError("redis is down: %s" % delivery["body"])

        kit.configure(enqueue=broken)

        response = self.deliver(http, "/webhooks/qube/runs/%s" % run.id, body, sign(body))

        assert response.status == 503
        assert "(OSError)" in caplog.text
        assert run.reference not in caplog.text

    @pytest.mark.parametrize(
        "reason,header",
        [
            ("mismatch", lambda body: sign(body, secret="whsec_other")),
            ("missing", lambda body: None),
            ("malformed", lambda body: "v1=abc"),
            ("stale", lambda body: sign(body, timestamp=int(time.time()) - 301)),
        ],
    )
    def test_refuses_a_bad_signature_with_401_logging_only_the_reason(self, http, run, body, queued, caplog, reason, header):
        sent = header(body)

        response = self.deliver(http, "/webhooks/qube/runs/%s" % run.id, body, sent)

        assert response.status == 401
        assert queued == []
        assert "QuBe Sync: refused a webhook: %s" % reason in caplog.text
        assert SECRET not in caplog.text
        assert run.reference not in caplog.text
        if sent and "v1=" in sent:
            assert sent.split("v1=")[-1] not in caplog.text

    def test_refuses_a_tampered_body(self, http, run, body, queued):
        header = sign(body)

        assert self.deliver(http, "/webhooks/qube/runs/%s" % run.id, body.replace(run.reference, "other-ref"), header).status == 401

    def test_answers_400_for_a_signed_body_thats_not_a_json_object(self, http, run, queued):
        assert self.deliver(http, "/webhooks/qube/runs/%s" % run.id, "[1, 2]", sign("[1, 2]")).status == 400

    def test_takes_any_content_type_and_a_body_of_up_to_5_mb(self, http, run, queued):
        big = run_body("workflow_run.completed", run, {"output": {"pad": "x" * (4 * 1024 * 1024)}})

        response = self.deliver(http, "/webhooks/qube/runs/%s" % run.id, big, sign(big), content_type="text/plain")

        assert response.status == 200
        assert queued[0]["body"] == big

    def test_answers_413_for_a_body_over_5_mb_unread(self, http, run, queued, caplog):
        huge = "x" * (5 * 1024 * 1024 + 1)

        assert self.deliver(http, "/webhooks/qube/runs/%s" % run.id, huge, sign(huge)).status == 413
        assert "refused a webhook: its body is over 5242880 bytes" in caplog.text

    def test_needs_no_sign_in_or_csrf(self, http, run, body, queued):
        # The driver sends no sign-in; Django's test client enforces nothing, see test_kit_django.
        assert self.deliver(http, "/webhooks/qube/runs/%s" % run.id, body, sign(body)).status == 200

    def test_raises_naming_the_config_file_when_the_secret_isnt_set(self, http, run, body):
        kit.configure(webhook_secret=None)

        with pytest.raises(kit.NotConfigured, match=r"QUBE_WEBHOOK_SECRET.*quickbooks_desktop/config\.py"):
            self.deliver(http, "/webhooks/qube/runs/%s" % run.id, body, sign(body))

    def test_the_default_queue_runs_the_delivery_after_the_response(self, http, world, run, body):
        response = self.deliver(http, "/webhooks/qube/runs/%s" % run.id, body, sign(body))
        drain()

        assert response.status == 200
        assert world.reload(run).state == "completed"
        assert CreateInvoice.calls[0][0] == "ended"

    def test_has_no_route_for_the_old_urls(self, http, world, account, body, queued):
        assert self.deliver(http, "/webhooks/qube/create_invoice/1", body, sign(body)).status in (404, 405)
        assert self.deliver(http, "/webhooks/qube/connection/%s" % account.id, body, sign(body)).status in (404, 405)


class TestConnectionWebhook:
    def test_verifies_enqueues_and_answers_200(self, http, world, account, queued):
        connection = world.connection(account)
        body = vector_body("connection.connected")

        response = http.post("/webhooks/qube/connections/%s" % connection.id, body=body, headers={"X-QUBE-Signature": sign(body)})

        assert response.status == 200
        assert queued == [{"kind": "connection", "id": str(connection.id), "body": body}]

    def test_answers_404_for_a_connection_that_isnt_there(self, http, queued):
        body = vector_body("connection.connected")

        assert http.post("/webhooks/qube/connections/0", body=body, headers={"X-QUBE-Signature": sign(body)}).status == 404

    def test_refuses_a_bad_signature_with_401(self, http, world, account, queued):
        connection = world.connection(account)
        body = vector_body("connection.connected")
        header = sign(body, secret="whsec_no")

        assert http.post("/webhooks/qube/connections/%s" % connection.id, body=body, headers={"X-QUBE-Signature": header}).status == 401

    def test_retries_a_connection_with_no_qube_id_yet_until_its_adopted(self, http, world, account, client, monkeypatch):
        monkeypatch.setattr("qubesync.kit._job.retry_delay", lambda attempt: 0)
        connection = world.connection(account, qube_id=None, status="pending")
        listings = [[]]

        def listed():
            if listings:
                return listings.pop()
            return [
                {
                    "id": QUBE_ID,
                    "webhook_url": connection.webhook_url,
                    "last_connected_at": None,
                    "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }
            ]

        client.returns["list_connections"] = listed
        body = vector_body("connection.connected")

        response = http.post("/webhooks/qube/connections/%s" % connection.id, body=body, headers={"X-QUBE-Signature": sign(body)})
        drain()

        assert response.status == 200
        connection = world.reload(connection)
        assert (connection.qube_id, connection.status) == (QUBE_ID, "connected")


# -- Questions -------------------------------------------------------------------------------


class TestAnswer:
    @pytest.fixture
    def invoice(self, world, account):
        return world.invoice(account)

    @pytest.fixture
    def run(self, world, account, invoice):
        return world.run(invoice, world.connection(account), revision=6, question=QUESTION, links={"decisions": DECISIONS, "search": SEARCH})

    def answer(self, http, run, data, account, invoice):
        return http.post("/qube/questions/runs/%s" % run.id, data, account=account, headers={"Referer": "/invoices/%s" % invoice.id})

    def test_posts_the_choice_with_its_fields_as_their_types_forgets_the_question_and_goes_back(self, http, world, account, invoice, run, client):
        form = {"choice": "add", "data[name]": " Lone Star ", "data[count]": "3", "data[rate]": "1.5", "data[taxable]": "true", "data[note]": ""}

        response = self.answer(http, run, form, account, invoice)

        assert client.called("answer") == [
            ("answer", (DECISIONS,), {"choice": "add", "data": {"name": "Lone Star", "count": 3, "rate": 1.5, "taxable": True}})
        ]
        assert (response.status, response.location) == (303, "/invoices/%s" % invoice.id)
        assert world.reload(run).question is None

    def test_sends_an_unticked_checkbox_as_false_and_a_number_it_cant_read_as_typed(self, http, account, invoice, run, client):
        self.answer(http, run, {"choice": "add", "data[count]": "three"}, account, invoice)

        assert client.called("answer")[0][2]["data"] == {"count": "three", "taxable": False}

    def test_answers_409_for_a_choice_the_question_doesnt_have(self, http, account, invoice, run, client):
        response = self.answer(http, run, {"choice": "delete_everything"}, account, invoice)

        assert (response.status, response.text) == (409, "This question has changed; reload.")
        assert client.called("answer") == []

    @pytest.mark.parametrize("status,code", [(409, "prompt_changed"), (400, "not_awaiting_input"), (400, "bad_request")])
    def test_forgets_the_question_and_answers_409_when_quickbooks_says_it_changed(self, http, world, account, invoice, run, client, status, code):
        client.raises["answer"] = api_error(status, {"code": code})

        response = self.answer(http, run, {"choice": "use:1"}, account, invoice)

        assert response.status == 409
        assert world.reload(run).question is None

    def test_keeps_the_question_and_says_why_for_a_422(self, http, world, account, invoice, run, client):
        client.raises["answer"] = api_error(422, {"detail": "count must be a whole number"})

        response = self.answer(http, run, {"choice": "add", "data[count]": "3"}, account, invoice)

        assert (response.status, response.text) == (422, "QuBe Sync couldn't take that answer: count must be a whole number")
        assert world.reload(run).question == QUESTION

    def test_raises_for_anything_else_quickbooks_answers(self, http, account, invoice, run, client):
        client.raises["answer"] = api_error(500, "boom")

        with pytest.raises(kit.APIError):
            self.answer(http, run, {"choice": "use:1"}, account, invoice)

    def test_by_default_lets_the_account_that_owns_the_runs_connection_answer(self, http, account, invoice, run):
        assert self.answer(http, run, {"choice": "use:1"}, account, invoice).status == 303

    def test_by_default_refuses_when_current_account_finds_no_account(self, http, account, invoice, run):
        kit.configure(current_account=lambda request: None)

        assert self.answer(http, run, {"choice": "use:1"}, account, invoice).status == 404

    def test_by_default_never_matches_an_unsaved_account(self, http, world, account, invoice, run):
        kit.configure(current_account=lambda request: world.unsaved_account())

        assert self.answer(http, run, {"choice": "use:1"}, account, invoice).status == 404

    def test_by_default_answers_404_for_another_accounts_run_logged(self, http, world, invoice, run, client, caplog):
        response = self.answer(http, run, {"choice": "use:1"}, world.account("Someone else"), invoice)

        assert response.status == 404
        assert "refused an answer or search for run %s: authorize_question said no" % run.id in caplog.text
        assert client.called("answer") == []

    def test_uses_an_authorize_question_the_app_sets(self, http, world, invoice, run):
        kit.configure(authorize_question=lambda request, record, asked: record.number == "1001")

        assert self.answer(http, run, {"choice": "use:1"}, world.account("Staff"), invoice).status == 303

    def test_passes_the_request_record_and_run_to_authorize_question(self, http, account, invoice, run):
        seen = []

        def authorize(request, record, asked):
            seen.append((type(record).__name__, record.id, asked.id, request is not None))
            return False

        kit.configure(authorize_question=authorize)
        self.answer(http, run, {"choice": "use:1"}, account, invoice)

        assert seen == [("Invoice", invoice.id, run.id, True)]

    def test_lets_only_true_through(self, http, account, invoice, run, client):
        kit.configure(authorize_question=lambda request, record, asked: record)

        assert self.answer(http, run, {"choice": "use:1"}, account, invoice).status == 404
        assert client.called("answer") == []

    def test_answers_403_while_neither_authorize_question_nor_current_account_is_set(self, http, account, invoice, run, client, caplog):
        kit.configure(current_account=None)

        response = self.answer(http, run, {"choice": "use:1"}, account, invoice)

        assert response.status == 403
        assert "neither authorize_question nor current_account is set" in caplog.text
        assert client.called("answer") == []

    def test_answers_404_when_find_record_returns_none(self, http, account, invoice, run, monkeypatch):
        monkeypatch.setattr(CreateInvoice, "find_record", classmethod(lambda cls, id: None))

        assert self.answer(http, run, {"choice": "use:1"}, account, invoice).status == 404

    def test_answers_404_when_find_record_raises_not_found(self, http, world, account, invoice, run, monkeypatch):
        error = world.Run._kit_store.not_found_errors[0]

        def missing(cls, id):
            raise error()

        monkeypatch.setattr(CreateInvoice, "find_record", classmethod(missing))

        assert self.answer(http, run, {"choice": "use:1"}, account, invoice).status == 404

    def test_answers_409_for_a_run_that_has_stopped_asking(self, http, world, account, invoice, run):
        run = world.update(run, question=None, links=None)

        assert self.answer(http, run, {"choice": "use:1"}, account, invoice).status == 409

    def test_answers_404_for_a_run_that_isnt_there_or_whose_operation_isnt_configured(self, http, account, invoice, run):
        assert http.post("/qube/questions/runs/0", {"choice": "x"}, account=account).status == 404

        kit.configure(operations={"sync_customer": SyncCustomer})
        assert self.answer(http, run, {"choice": "use:1"}, account, invoice).status == 404

    def test_goes_back_to_this_app_only(self, http, account, run):
        response = http.post("/qube/questions/runs/%s" % run.id, {"choice": "use:1"}, account=account, headers={"Referer": "https://evil.example/x"})

        assert response.location.endswith("/") and "evil" not in response.location

    def test_is_behind_the_apps_sign_in(self, http, run, client):
        signed_out(http, http.post("/qube/questions/runs/%s" % run.id, {"choice": "use:1"}))
        assert client.called("answer") == []


class TestSearch:
    @pytest.fixture
    def run(self, world, account):
        return world.run(world.invoice(account), world.connection(account), question=QUESTION, links={"decisions": DECISIONS, "search": SEARCH})

    def search(self, http, run, q, account, field="list_id"):
        return http.get("/qube/questions/runs/%s/search" % run.id, {"field": field, "q": q}, account=account)

    def test_returns_the_matches_from_links_search(self, http, account, run, client):
        matches = [{"value": "80000001-1", "label": "Riverbend Electric", "detail": None}]
        client.returns["search"] = matches

        response = self.search(http, run, " river ", account)

        assert (response.status, response.json()) == (200, matches)
        assert client.called("search") == [("search", (SEARCH,), {"field": "list_id", "q": "river"})]

    def test_asks_nothing_for_too_short_or_too_long(self, http, account, run, client):
        for q, field in (("r", "list_id"), ("r" * 101, "list_id"), ("river", ""), ("river", "f" * 101)):
            response = self.search(http, run, q, account, field=field)
            assert (response.status, response.json()) == (200, [])
        assert client.called("search") == []

    def test_answers_409_when_the_question_has_no_search_link(self, http, world, account, run):
        run = world.update(run, links={"decisions": DECISIONS})

        assert self.search(http, run, "river", account).status == 409

    def test_passes_quickbooks_4xx_on_with_no_matches(self, http, account, run, client):
        client.raises["search"] = api_error(409, {"code": "prompt_changed"})

        response = self.search(http, run, "river", account)

        assert (response.status, response.json()) == (409, [])

    def test_answers_empty_with_404_when_authorize_question_says_no(self, http, account, run, client):
        kit.configure(authorize_question=lambda request, record, asked: False)

        response = self.search(http, run, "river", account)

        assert (response.status, response.json()) == (404, [])
        assert client.called("search") == []

    def test_by_default_answers_empty_with_404_for_another_accounts_run(self, http, world, run, client):
        response = self.search(http, run, "river", world.account("Someone else"))

        assert (response.status, response.json()) == (404, [])
        assert client.called("search") == []

    def test_answers_403_while_neither_is_set(self, http, account, run):
        kit.configure(current_account=None)

        response = self.search(http, run, "river", account)

        assert (response.status, response.json()) == (403, [])

    def test_is_behind_the_apps_sign_in(self, http, run, client):
        signed_out(http, http.get("/qube/questions/runs/%s/search" % run.id, {"field": "list_id", "q": "river"}))
        assert client.called("search") == []


# -- The start retry -------------------------------------------------------------------------


class TestRetryStart:
    @pytest.fixture
    def invoice(self, world, account):
        return world.invoice(account)

    @pytest.fixture
    def run(self, world, account, invoice):
        made = world.run(invoice, world.connection(account), state="starting", input={"operation": "invoice.create"})
        return world.ago(made, 120)

    def retry(self, http, run, account, invoice):
        return http.post("/qube/runs/%s/retry_start" % run.id, account=account, headers={"Referer": "/invoices/%s" % invoice.id})

    def test_resends_the_start_with_its_reference_keeps_the_answer_and_goes_back(self, http, world, account, invoice, run, client):
        client.returns["start_run"] = {"id": "run-q-1", "state": "running"}

        response = self.retry(http, run, account, invoice)

        assert client.called("start_run")[0][2]["reference"] == run.reference
        assert (response.status, response.location) == (303, "/invoices/%s" % invoice.id)
        run = world.reload(run)
        assert (run.qube_run_id, run.state) == ("run-q-1", "running")

    def test_goes_back_still_unconfirmed_without_an_answer_and_failed_when_refused(self, http, world, account, invoice, run, client):
        client.raises["start_run"] = timeout()
        assert self.retry(http, run, account, invoice).status == 303
        assert world.reload(run).state == "starting"

        client.raises["start_run"] = api_error(422, {"detail": "bad"})
        assert self.retry(http, run, account, invoice).status == 303
        assert world.reload(run).state == "failed"

    def test_answers_409_for_a_run_that_isnt_starting(self, http, world, account, invoice, run, client):
        run = world.update(run, state="running")

        assert self.retry(http, run, account, invoice).status == 409
        assert client.called("start_run") == []

    def test_answers_404_for_another_accounts_run_logged_and_sends_nothing(self, http, world, invoice, run, client, caplog):
        response = self.retry(http, run, world.account("Someone else"), invoice)

        assert response.status == 404
        assert "refused a start retry for run %s" % run.id in caplog.text
        assert client.called("start_run") == []

    def test_answers_404_for_a_run_that_isnt_there(self, http, account):
        assert http.post("/qube/runs/0/retry_start", account=account).status == 404

    def test_is_behind_the_apps_sign_in(self, http, run, client):
        signed_out(http, http.post("/qube/runs/%s/retry_start" % run.id))
        assert client.called("start_run") == []


# -- The templates ---------------------------------------------------------------------------


class TestQuestionTemplate:
    @pytest.fixture
    def invoice(self, world, account):
        return world.invoice(account)

    @pytest.fixture
    def connection(self, world, account):
        return world.connection(account)

    def page(self, http, invoice, account):
        response = http.get("/invoices/%s" % invoice.id, account=account)
        assert response.status == 200
        return response.text

    def asking(self, world, run, question=None):
        return world.update(run, question=question or vector_prompt(), links={"decisions": "d", "search": "s"})

    def test_shows_the_latest_runs_question_with_a_form_per_choice_posting_to_its_route(self, http, world, account, invoice, connection):
        older = self.asking(world, world.run(invoice, connection), dict(vector_prompt(), message="An older question"))
        world.ago(older, 3600)
        latest = self.asking(world, world.run(invoice, connection))
        action = "/qube/questions/runs/%s" % latest.id

        shown = self.page(http, invoice, account)

        assert shown.count('class="qube-question"') == 1
        assert "An older question" not in shown
        assert "No record has exactly that name" in shown
        assert set(re.findall(r'<form class="qube-choice" method="post" action="([^"]+)"', shown)) == {action}
        assert re.findall(r'name="choice" value="([^"]+)"', shown) == ["use:1", "use", "none", "cancel"]
        assert 'data-qube-search="%s/search"' % action in shown
        assert 'data-qube-field="list_id"' in shown
        assert 'name="data[list_id]"' in shown

    def test_shows_nothing_when_the_latest_run_has_stopped_asking(self, http, world, account, invoice, connection):
        world.ago(self.asking(world, world.run(invoice, connection)), 3600)
        world.run(invoice, connection)

        assert "qube-question" not in self.page(http, invoice, account)

    def test_escapes_what_it_prints(self, http, world, account, invoice, connection):
        self.asking(world, world.run(invoice, connection), dict(vector_prompt(), message="<script>alert(1)</script>"))

        shown = self.page(http, invoice, account)

        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in shown
        assert "<script>alert(1)" not in shown

    def test_shows_nothing_for_a_record_with_no_runs(self, http, account, invoice):
        assert "qube-question" not in self.page(http, invoice, account)


class TestRunStatusTemplate:
    @pytest.fixture
    def invoice(self, world, account):
        return world.invoice(account)

    @pytest.fixture
    def connection(self, world, account):
        return world.connection(account)

    def page(self, http, invoice, account):
        response = http.get("/invoices/%s" % invoice.id, account=account)
        assert response.status == 200
        return response.text

    def test_shows_the_latest_runs_summary_and_a_failures_detail(self, http, world, account, invoice, connection):
        world.ago(world.run(invoice, connection, state="completed", outcome="added"), 3600)
        world.run(
            invoice,
            connection,
            state="failed",
            ended_at=world.Run._kit_store.now(),
            error={"message": "No customer <b>named</b> Riverbend", "detail": "Add the customer first."},
        )

        shown = self.page(http, invoice, account)

        assert 'class="qube-run-status qube-run-failed"' in shown
        assert '<p class="qube-run-summary">Failed: No customer &lt;b&gt;named&lt;/b&gt; Riverbend</p>' in shown
        assert '<p class="qube-run-error-detail">Add the customer first.</p>' in shown

    def test_shows_a_completed_run_without_a_detail(self, http, world, account, invoice, connection):
        world.run(invoice, connection, state="completed", outcome="added")

        shown = self.page(http, invoice, account)

        assert '<p class="qube-run-summary">Added to QuickBooks</p>' in shown
        assert "qube-run-error-detail" not in shown

    def test_offers_to_try_an_unconfirmed_start_again_and_only_then(self, http, world, account, invoice, connection):
        old = world.ago(world.run(invoice, connection, state="starting"), 120)
        shown = self.page(http, invoice, account)

        assert '<p class="qube-run-summary">Not confirmed by QuBe Sync yet</p>' in shown
        assert 'action="/qube/runs/%s/retry_start"' % old.id in shown
        assert 'class="qube-retry-start"' in shown

        world.run(invoice, connection, state="starting")  # a younger one, now the latest
        shown = self.page(http, invoice, account)
        assert '<p class="qube-run-summary">Starting</p>' in shown
        assert "qube-retry-start-form" not in shown

    def test_shows_nothing_for_a_record_with_no_runs(self, http, account, invoice):
        assert "qube-run-status" not in self.page(http, invoice, account)

    def test_raises_for_a_slug_no_operation_has(self, world, invoice):
        with pytest.raises(ValueError, match="no operation has the slug 'nope'"):
            kit.run_status_context(invoice, "nope", lambda run: "")
