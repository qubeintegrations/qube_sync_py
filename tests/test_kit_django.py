"""What's Django's own in qubesync.django: the installed app (its migrations match its models,
the config module is imported, the store registered), login_required and CSRF on the routes
and not on the webhooks, the template tags, a template override, and the default queue's
thread. The routes' status codes are in test_kit_routes.py, on all three adapters."""
import pytest

pytest.importorskip("django")

import kit_django_setup  # noqa: E402,F401
from django.core.management import call_command  # noqa: E402
from django.template import engines  # noqa: E402
from django.test import Client, RequestFactory, override_settings  # noqa: E402
from django.urls import include, path, reverse  # noqa: E402

import qubesync.django as qube_django  # noqa: E402
import qubesync.kit as kit  # noqa: E402
from kit_support import DECISIONS, QUESTION, SEARCH, drain, kit_reset, run_body, sign  # noqa: E402,F401
from kit_worlds import CreateInvoice, make_driver  # noqa: E402


@pytest.fixture
def app(kit_reset):
    return make_driver("django")


@pytest.fixture
def world(app):
    return app[1]


@pytest.fixture
def account(world):
    return world.account()


def test_the_migrations_match_the_models():
    call_command("makemigrations", "qubesync", check=True, dry_run=True, verbosity=0)


def test_the_app_imports_the_config_module_and_registers_its_store():
    import kitapp.config
    from qubesync.django.store import STORE
    from qubesync.kit._store import current_store

    assert kitapp.config.LOADED
    assert current_store() is STORE


def test_the_tables_are_the_rails_engines():
    from qubesync.django.models import Connection, Notification, QuickbooksRecord, Run

    assert [m._meta.db_table for m in (Connection, Run, QuickbooksRecord, Notification)] == [
        "qube_connections",
        "qube_runs",
        "qube_quickbooks_records",
        "qube_notifications",
    ]
    names = {c.name for m in (Connection, Run, QuickbooksRecord, Notification) for c in m._meta.constraints}
    assert names == {
        "index_qube_connections_on_qube_id",
        "index_qube_runs_on_reference",
        "index_qube_quickbooks_records_on_qb_id",
        "index_qube_quickbooks_records_on_record",
        "index_qube_notifications_on_run_and_delivery",
    }


def test_the_routes_are_named_in_the_qubesync_namespace():
    assert reverse("qubesync:connections") == "/quickbooks/connections"
    assert reverse("qubesync:connection_onboarding", args=[3]) == "/quickbooks/connections/3/onboarding"
    assert reverse("qubesync:run_webhook", args=[3]) == "/webhooks/qube/runs/3"
    assert reverse("qubesync:connection_webhook", args=[3]) == "/webhooks/qube/connections/3"
    assert reverse("qubesync:question", args=[3]) == "/qube/questions/runs/3"
    assert reverse("qubesync:question_search", args=[3]) == "/qube/questions/runs/3/search"
    assert reverse("qubesync:retry_start", args=[3]) == "/qube/runs/3/retry_start"
    assert reverse("qubesync:redeliver", args=[3]) == "/qube/runs/3/redeliver"


def test_login_required_sends_a_signed_out_user_to_sign_in(app, world):
    response = Client().post("/quickbooks/connections")

    assert response.status_code == 302
    assert response["Location"].startswith("/login")
    assert world.count(world.Connection) == 0


def test_the_posts_are_csrf_checked_and_the_webhooks_arent(app, world, account):
    run = world.run(world.invoice(account), world.connection(account), question=QUESTION, links={"decisions": DECISIONS, "search": SEARCH})
    client = Client(enforce_csrf_checks=True)
    client.force_login(account.user)
    handed = []
    kit.configure(enqueue=lambda delivery: handed.append(delivery))

    assert client.post("/quickbooks/connections").status_code == 403
    assert client.post("/qube/questions/runs/%s" % run.id, {"choice": "use:1"}).status_code == 403
    assert client.post("/qube/runs/%s/retry_start" % run.id).status_code == 403

    body = run_body("workflow_run.completed", run)
    response = Client(enforce_csrf_checks=True).generic(
        "POST", "/webhooks/qube/runs/%s" % run.id, body, content_type="application/json", HTTP_X_QUBE_SIGNATURE=sign(body)
    )
    assert response.status_code == 200
    assert len(handed) == 1


def test_takes_a_webhook_over_djangos_upload_limit_up_to_5_mb(app, world, account):
    run = world.run(world.invoice(account), world.connection(account))
    handed = []
    kit.configure(enqueue=lambda delivery: handed.append(delivery))
    big = run_body("workflow_run.completed", run, {"output": {"pad": "x" * (3 * 1024 * 1024)}})

    with override_settings(DATA_UPLOAD_MAX_MEMORY_SIZE=1024):
        response = Client().generic(
            "POST", "/webhooks/qube/runs/%s" % run.id, big, content_type="application/x-www-form-urlencoded", HTTP_X_QUBE_SIGNATURE=sign(big)
        )

    assert response.status_code == 200
    assert handed[0]["body"] == big


def test_patterns_takes_another_sign_in():
    from qubesync.django import urls

    seen = []

    def staff_only(view):
        seen.append(view.__name__)
        return view

    urls.patterns(sign_in=staff_only)

    assert sorted(seen) == ["answer", "connect", "onboarding", "redeliver", "retry_start", "search"]


def test_the_template_tags_render_with_the_pages_csrf_token(app, world, account):
    invoice = world.invoice(account)
    run = world.run(invoice, world.connection(account), question=QUESTION, links={"decisions": DECISIONS, "search": SEARCH})
    client = Client()
    client.force_login(account.user)

    page = client.get("/invoices/%s" % invoice.id).content.decode()

    assert 'name="csrfmiddlewaretoken"' in page
    assert 'action="/qube/questions/runs/%s"' % run.id in page
    assert '<p class="qube-run-summary">Running</p>' in page


def test_question_context_for_an_include(app, world, account):
    invoice = world.invoice(account)
    run = world.run(invoice, world.connection(account), question=QUESTION, links={"decisions": DECISIONS})

    context = qube_django.question_context(invoice, "create_invoice")

    assert context["question"] == QUESTION
    assert context["action"] == "/qube/questions/runs/%s" % run.id
    assert qube_django.run_status_context(invoice, "create_invoice")["summary"] == "Running"


def test_the_app_overrides_a_template_by_path(app, world, account, tmp_path):
    (tmp_path / "qubesync").mkdir()
    (tmp_path / "qubesync" / "question.html").write_text('<div class="app-own">{{ question.message }}</div>')
    invoice = world.invoice(account)
    world.run(invoice, world.connection(account), question=QUESTION, links={"decisions": DECISIONS})
    templates = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [str(tmp_path)],
            "APP_DIRS": True,
            "OPTIONS": {"context_processors": ["django.template.context_processors.request"]},
        }
    ]

    with override_settings(TEMPLATES=templates):
        page = engines["django"].from_string("{% load qubesync %}{% qube_question invoice 'create_invoice' %}")
        shown = page.render({"invoice": invoice}, RequestFactory().get("/"))

    assert shown.strip() == '<div class="app-own">Which customer?</div>'


def test_the_default_queue_runs_the_job_and_closes_its_connection(app, world, account, monkeypatch):
    run = world.run(world.invoice(account), world.connection(account))
    closed = []
    monkeypatch.setattr("qubesync.django.store.close_old_connections", lambda: closed.append(True))
    body = run_body("workflow_run.completed", run)

    response = Client().generic("POST", "/webhooks/qube/runs/%s" % run.id, body, content_type="application/json", HTTP_X_QUBE_SIGNATURE=sign(body))
    drain()

    assert response.status_code == 200
    assert world.reload(run).state == "completed"
    assert CreateInvoice.calls[0][0] == "ended"
    assert closed


def test_includes_under_a_prefix():
    from django.urls import resolve

    with override_settings(ROOT_URLCONF=__name__):
        assert resolve("/qube-sync/webhooks/qube/runs/1").url_name == "run_webhook"


urlpatterns = [path("qube-sync/", include("qubesync.django.urls"))]


def test_simulated_connect_follows_debug_unless_production_is_set(app, world, account):
    client = Client()
    client.force_login(account.user)

    assert client.post("/quickbooks/connections", {"simulated": "1"}).status_code == 404  # DEBUG is off
    with override_settings(DEBUG=True):
        response = client.post("/quickbooks/connections", {"simulated": "1"}, HTTP_REFERER="/account")
    assert (response.status_code, response["Location"]) == (303, "/account")
    kit.configure(production=True)
    with override_settings(DEBUG=True):
        assert client.post("/quickbooks/connections", {"simulated": "1"}).status_code == 404


def test_the_run_status_tag_takes_a_connection(app, world, account):
    invoice = world.invoice(account)
    connection = world.connection(account)
    connection.link(invoice, kind="invoice", qb_id="TXN-1")
    page = engines["django"].from_string("{% load qubesync %}{% qube_run_status invoice 'create_invoice' connection=connection %}")

    shown = page.render({"invoice": invoice, "connection": connection}, RequestFactory().get("/"))

    assert 'data-qube-sync-status="in_quickbooks"' in shown


def test_without_a_session_an_answer_that_cant_go_through_answers_as_text(app, world, account):
    invoice = world.invoice(account)
    run = world.run(invoice, world.connection(account), question=QUESTION, links={"decisions": DECISIONS})
    request = RequestFactory().post("/qube/questions/runs/%s" % run.id, {"choice": "nope"})
    request.user = account.user
    request._dont_enforce_csrf_checks = True

    from qubesync.django import views

    response = views.answer(request, str(run.id))

    assert (response.status_code, response.content.decode()) == (409, kit.CHANGED)


def test_redirect_back_goes_back_with_the_message_for_the_page():
    request = RequestFactory().post("/start", HTTP_REFERER="/invoices/1")
    request.session = {}
    response = qube_django.redirect_back(request, "Connect first.")
    assert (response.status_code, response["Location"]) == (303, "/invoices/1")
    assert qube_django.take_error(request) == "Connect first."

    request = RequestFactory().post("/start", HTTP_REFERER="https://elsewhere.example/x")
    request.session = {}
    response = qube_django.redirect_back(request)
    assert (response.status_code, response["Location"], request.session) == (303, "/", {})
