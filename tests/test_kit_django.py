"""qubesync.django: the installed app's routes, through Django's test client, its bases on real
models, and the question template."""
import json
import logging
import os
import tempfile

import pytest

django = pytest.importorskip("django")

from django.conf import settings  # noqa: E402

if not settings.configured:
    settings.configure(
        DEBUG=False,
        SECRET_KEY="kit-tests",
        ALLOWED_HOSTS=["testserver", "app.example"],
        ROOT_URLCONF="kitapp.urls",
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "django.contrib.sessions",
            "qubesync.django",
            "kitapp",
        ],
        MIDDLEWARE=[
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": os.path.join(tempfile.mkdtemp(), "kit.sqlite3"),
            }
        },
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "APP_DIRS": True,
                "OPTIONS": {"context_processors": ["django.template.context_processors.request"]},
            }
        ],
        LOGIN_URL="/login",
        USE_TZ=True,
        DEFAULT_AUTO_FIELD="django.db.models.AutoField",
        QUBESYNC_CONFIG="kitapp.config",
    )
    django.setup()
    from django.core.management import call_command

    call_command("migrate", run_syncdb=True, verbosity=0)

from django.contrib.auth.models import User  # noqa: E402
from django.template.loader import render_to_string  # noqa: E402
from django.test import Client, RequestFactory, override_settings  # noqa: E402

import qubesync.django as qube_django  # noqa: E402
import qubesync.kit as kit  # noqa: E402
from kit_support import (  # noqa: E402,F401
    DECISIONS,
    PROMPT,
    SEARCH,
    SECRET,
    WEBHOOK_URL,
    FakeClient,
    api_error,
    connection_event,
    drain,
    kit_reset,
    notification,
    run_event,
    sign,
)
from kitapp.models import Account, Invoice  # noqa: E402


class CreateInvoice(qube_django.Operation):
    workflow = "add_transaction"
    slug = "create_invoice"
    ended_with = []

    @classmethod
    def find_record(cls, record_id):
        return Invoice.objects.filter(pk=record_id).first()

    def input(self):
        return {"operation": "invoice.create", "params": {"ref_number": str(self.record.id)}}

    def ended(self, event):
        type(self).ended_with.append(event.outcome)
        self.record.status = "sent"
        self.save_record(["status"])


class Connection(qube_django.ConnectionEvents):
    @classmethod
    def find_record(cls, record_id):
        return Account.objects.get(pk=record_id)

    def connected(self, event):
        self.account.connected = True
        self.save_record(["connected"])


@pytest.fixture(autouse=True)
def app(kit_reset):
    Invoice.objects.all().delete()
    Account.objects.all().delete()
    User.objects.all().delete()
    CreateInvoice.ended_with = []
    fake = FakeClient()
    queued = []
    kit.configure(
        operations={"create_invoice": CreateInvoice},
        connection=Connection,
        webhook_secret=SECRET,
        webhook_url=WEBHOOK_URL,
        client=fake,
        enqueue=lambda *job: queued.append(job),
        current_account=lambda request: Account.objects.get(user=request.user),
    )
    user = User.objects.create(username="pat")
    account = Account.objects.create(user=user)
    return {"client": fake, "queued": queued, "user": user, "account": account}


def signed_in(user):
    client = Client()
    client.force_login(user)
    return client


def invoice(account, **fields):
    defaults = {"qube_reference": "ref-1", "qube_revision": 0}
    defaults.update(fields)
    return Invoice.objects.create(account=account, **defaults)


def post_webhook(path, body, header=None, client=None):
    client = client or Client(enforce_csrf_checks=True)
    return client.post(
        path, data=body, content_type="application/json", HTTP_X_QUBE_SIGNATURE=header or sign(body)
    )


# -- The app ---------------------------------------------------------------------------------


def test_the_app_config_imports_the_config_module():
    import sys

    assert sys.modules["kitapp.config"].LOADED is True


# -- Webhooks --------------------------------------------------------------------------------


def test_a_signed_webhook_is_enqueued_without_csrf_or_sign_in(app):
    body = run_event()
    response = post_webhook("/webhooks/qube/create_invoice/42", body)
    assert response.status_code == 200
    assert app["queued"] == [("create_invoice", "42", body)]


def test_a_bad_signature_is_401_and_only_its_reason_is_logged(app, caplog):
    body = run_event()
    with caplog.at_level(logging.WARNING, logger="qubesync.kit"):
        response = post_webhook("/webhooks/qube/create_invoice/42", body, sign(body, secret="whsec_wrong"))
    assert response.status_code == 401
    assert app["queued"] == []
    assert "QuBe Sync: refused a webhook: mismatch" in caplog.messages
    assert SECRET not in caplog.text and body not in caplog.text


def test_a_webhook_over_djangos_upload_limit_is_taken_up_to_5_mb(app):
    # DATA_UPLOAD_MAX_MEMORY_SIZE is 2.5 MB by default; the webhook reads its stream instead.
    body = run_event(pad="a" * (3 * 1024 * 1024))
    client = Client()
    response = client.post(
        "/webhooks/qube/create_invoice/1", data=body, content_type="text/plain", HTTP_X_QUBE_SIGNATURE=sign(body)
    )
    assert response.status_code == 200
    assert app["queued"][0][2] == body
    huge = run_event(pad="a" * (5 * 1024 * 1024))
    response = client.post(
        "/webhooks/qube/create_invoice/1", data=huge, content_type="application/json", HTTP_X_QUBE_SIGNATURE=sign(huge)
    )
    assert response.status_code == 413


def test_an_unknown_slug_is_404(app):
    body = run_event()
    assert post_webhook("/webhooks/qube/nope/42", body).status_code == 404
    assert Client().get("/webhooks/qube/create_invoice/42").status_code == 405


def test_the_default_queue_runs_the_job_under_a_row_lock(app):
    kit.configure(enqueue=None)
    record = invoice(app["account"])
    body = run_event("workflow_run.completed", revision=2, outcome="added")
    assert post_webhook("/webhooks/qube/create_invoice/%d" % record.pk, body).status_code == 200
    drain()
    record.refresh_from_db()
    assert (record.status, record.qube_revision) == ("sent", 2)
    assert CreateInvoice.ended_with == ["added"]


# -- The bases on Django models --------------------------------------------------------------


def test_operation_saves_with_update_fields_and_forgets_the_question(app):
    record = invoice(app["account"])
    kit.run("create_invoice", str(record.pk), run_event("workflow_run.awaiting_input", revision=1))
    record.refresh_from_db()
    assert record.qube_question == PROMPT
    assert record.qube_links == {"decisions": DECISIONS, "search": SEARCH}
    kit.run("create_invoice", str(record.pk), run_event("workflow_run.completed", revision=3, outcome="added"))
    kit.run("create_invoice", str(record.pk), run_event("workflow_run.failed", revision=2))
    record.refresh_from_db()
    assert record.qube_question is None and record.qube_revision == 3 and record.status == "sent"


def test_a_handler_that_raises_leaves_the_record_as_it_was(app):
    class Breaking(CreateInvoice):
        def ended(self, event):
            self.save_question({"token": "x"}, {})
            raise RuntimeError("boom")

    kit.configure(operations={"create_invoice": Breaking})
    record = invoice(app["account"])
    with pytest.raises(RuntimeError):
        kit.run("create_invoice", str(record.pk), run_event("workflow_run.completed", revision=1))
    record.refresh_from_db()
    assert record.qube_question is None and record.qube_revision == 0


def test_start_saves_the_reference_on_the_model(app):
    record = invoice(app["account"], qube_reference=None)
    CreateInvoice.start(record, "c1")
    record.refresh_from_db()
    assert record.qube_reference.startswith("create_invoice-%d-" % record.pk)
    assert app["client"].calls[0][2]["webhook_url"] == "%s/create_invoice/%d" % (WEBHOOK_URL, record.pk)


def test_notifications_are_taken_once(app):
    taken = []

    class Paging(CreateInvoice):
        def notification(self, event):
            taken.append(event.delivery_id)

    kit.configure(operations={"create_invoice": Paging})
    record = invoice(app["account"])
    for delivery in ("d1", "d1", "d2"):
        kit.run("create_invoice", str(record.pk), notification(delivery_id=delivery))
    assert taken == ["d1", "d2"]


def test_connection_events_on_the_account(app):
    account = app["account"]
    account.qube_connection_id = "c1"
    account.save()
    kit.run("connection", str(account.pk), connection_event("connection.connected", connection_id="c-other"))
    account.refresh_from_db()
    assert account.connected is False
    kit.run("connection", str(account.pk), connection_event("connection.connected", revision=1))
    account.refresh_from_db()
    assert account.connected is True and account.qube_connection_revision == 1


# -- Onboarding ------------------------------------------------------------------------------


def test_connect_is_behind_sign_in(app):
    response = Client().post("/quickbooks/connect")
    assert response.status_code == 302 and response["Location"].startswith("/login")
    assert app["client"].calls == []


def test_connect_creates_then_reuses_the_connection(app):
    client = signed_in(app["user"])
    response = client.post("/quickbooks/connect")
    assert (response.status_code, response["Location"]) == (303, "https://qubesync.com/onboard/new")
    account = Account.objects.get(pk=app["account"].pk)
    assert (account.qube_connection_id, account.qube_connection_revision) == ("c-new", None)
    assert app["client"].calls[0] == (
        "create_connection",
        (),
        {"webhook_url": "%s/connection/%d" % (WEBHOOK_URL, account.pk)},
    )
    response = client.post("/quickbooks/connect")
    assert response["Location"] == "https://qubesync.com/onboard/again"
    assert app["client"].names() == ["create_connection", "update_connection", "regenerate_onboarding"]


# -- Questions -------------------------------------------------------------------------------


def asking(app):
    return invoice(app["account"], qube_question=PROMPT, qube_links={"decisions": DECISIONS, "search": SEARCH})


def mine(request, record, operation):
    return record.account.user_id == request.user.id


def test_answers_are_refused_while_authorize_question_isnt_set(app, caplog):
    record = asking(app)
    with caplog.at_level(logging.WARNING, logger="qubesync.kit"):
        response = signed_in(app["user"]).post("/qube/questions/create_invoice/%d" % record.pk, {"choice": "skip"})
        search = signed_in(app["user"]).get("/qube/questions/create_invoice/%d/search?q=river" % record.pk)
    assert response.status_code == 403 and search.status_code == 403
    assert "authorize_question isn't set" in caplog.text
    assert app["client"].calls == []


def test_another_customers_record_is_404(app):
    kit.configure(authorize_question=mine)
    other = User.objects.create(username="sam")
    Account.objects.create(user=other)
    record = asking(app)
    response = signed_in(other).post("/qube/questions/create_invoice/%d" % record.pk, {"choice": "skip"})
    assert response.status_code == 404
    assert app["client"].calls == []


def test_an_answer_is_csrf_checked(app):
    kit.configure(authorize_question=mine)
    record = asking(app)
    client = Client(enforce_csrf_checks=True)
    client.force_login(app["user"])
    assert client.post("/qube/questions/create_invoice/%d" % record.pk, {"choice": "skip"}).status_code == 403


def test_an_answer_posts_typed_data_and_goes_back(app):
    kit.configure(authorize_question=mine)
    record = asking(app)
    response = signed_in(app["user"]).post(
        "/qube/questions/create_invoice/%d" % record.pk,
        {"choice": "use", "data[customer]": "80000001-1", "data[amount]": "3", "data[notify]": "true"},
        HTTP_REFERER="http://testserver/invoices/%d" % record.pk,
    )
    assert (response.status_code, response["Location"]) == (303, "http://testserver/invoices/%d" % record.pk)
    assert app["client"].calls[0][2]["data"] == {"customer": "80000001-1", "amount": 3, "notify": True}
    record.refresh_from_db()
    assert record.qube_question is None


def test_a_stale_answer_forgets_the_question_and_is_409(app):
    kit.configure(authorize_question=mine)
    record = asking(app)
    app["client"].raises["answer"] = api_error(400, {"code": "not_awaiting_input"})
    response = signed_in(app["user"]).post("/qube/questions/create_invoice/%d" % record.pk, {"choice": "skip"})
    assert (response.status_code, response.content.decode()) == (409, kit.CHANGED)
    record.refresh_from_db()
    assert record.qube_question is None


def test_a_refused_answer_is_422(app):
    kit.configure(authorize_question=mine)
    record = asking(app)
    app["client"].raises["answer"] = api_error(422, {"detail": "customer is required"})
    response = signed_in(app["user"]).post("/qube/questions/create_invoice/%d" % record.pk, {"choice": "skip"})
    assert response.status_code == 422
    assert response.content.decode() == "QuBe Sync couldn't take that answer: customer is required"


def test_search_is_bounded_and_answers_json(app):
    kit.configure(authorize_question=mine)
    record = asking(app)
    client = signed_in(app["user"])
    url = "/qube/questions/create_invoice/%d/search" % record.pk
    assert json.loads(client.get(url, {"q": "r", "field": "customer"}).content) == []
    response = client.get(url, {"q": "river", "field": "customer"})
    assert response.status_code == 200 and json.loads(response.content)[0]["value"] == "80000001-1"
    assert app["client"].names() == ["search"]


# -- The question template -------------------------------------------------------------------


def test_the_template_renders_the_question_with_csrf_and_the_action(app):
    record = asking(app)
    request = RequestFactory().get("/invoices/%d" % record.pk)
    context = qube_django.question_context("create_invoice", record)
    assert context["action"] == "/qube/questions/create_invoice/%d" % record.pk
    html = render_to_string("qubesync/question.html", context, request=request)
    assert 'class="qube-question"' in html
    assert "csrfmiddlewaretoken" in html
    assert 'action="/qube/questions/create_invoice/%d"' % record.pk in html
    assert 'data-qube-search="/qube/questions/create_invoice/%d/search"' % record.pk in html
    assert "Riverbend Electric isn&#x27;t in QuickBooks yet." in html


def test_the_template_shows_nothing_without_a_question(app):
    record = invoice(app["account"])
    html = render_to_string("qubesync/question.html", qube_django.question_context("create_invoice", record))
    assert html.strip() == ""


def test_the_app_overrides_the_template_by_path(app):
    here = os.path.dirname(os.path.abspath(__file__))
    templates = [dict(settings.TEMPLATES[0], DIRS=[os.path.join(here, "kit_templates", "override")])]
    record = asking(app)
    with override_settings(TEMPLATES=templates):
        html = render_to_string("qubesync/question.html", qube_django.question_context("create_invoice", record))
    assert 'class="app-own-question"' in html
