"""QuBe Sync's integration kit for Django: an installed app with the kit's tables (models and
migrations), the routes, and the question and run status templates.

    pip install "qubesync[django]>=0.4.0"

    # settings.py
    INSTALLED_APPS += ["qubesync.django"]

    # urls.py
    urlpatterns += [path("", include("qubesync.django.urls"))]

    python manage.py migrate qubesync

    # quickbooks_desktop/config.py, imported when the apps are ready (the QUBESYNC_CONFIG
    # Django setting names another module)
    import qubesync.kit
    qubesync.kit.configure(
        operations={"create_invoice": "quickbooks_desktop.create_invoice.CreateInvoice"},
        connection_events="quickbooks_desktop.connection_events.ConnectionEvents",
        current_account=lambda request: request.user.account,
    )

The models are qubesync.django.models' Connection, Run, QuickbooksRecord and Notification
(tables qube_connections, qube_runs, qube_quickbooks_records and qube_notifications). The
routes, relative to where urls.py includes them, each named in the qubesync namespace:

    POST quickbooks/connections                   connections            behind login_required and CSRF
    POST quickbooks/connections/<id>/onboarding   connection_onboarding  behind login_required and CSRF
    POST webhooks/qube/runs/<id>                  run_webhook            no sign-in, no CSRF (signed)
    POST webhooks/qube/connections/<id>           connection_webhook     no sign-in, no CSRF (signed)
    POST qube/questions/runs/<id>                 question               behind login_required and CSRF
    GET  qube/questions/runs/<id>/search          question_search        behind login_required
    POST qube/runs/<id>/retry_start               retry_start            behind login_required and CSRF

On a record's page:

    {% load qubesync %}
    {% qube_run_status invoice "create_invoice" %}
    {% qube_question invoice "create_invoice" %}
"""
try:
    import django as _django  # noqa: F401
except ImportError as error:  # pragma: no cover
    raise ImportError('qubesync.django needs Django: pip install "qubesync[django]"') from error

from typing import Any, Dict

from ..kit import ConnectionEvents, Operation
from ..kit import question_context as _question_context
from ..kit import run_status_context as _run_status_context

__all__ = ["Operation", "ConnectionEvents", "question_context", "run_status_context"]


def question_context(record, operation):
    # type: (Any, str) -> Dict[str, Any]
    """What qubesync/question.html reads, for the record's page: the open question of record's
    latest run of operation (a slug), if it's asking, and where it's answered. The
    {% qube_question %} tag renders it; for your own markup:

        context = {"invoice": invoice, **qubesync.django.question_context(invoice, "create_invoice")}
    """
    from django.urls import reverse

    return _question_context(record, operation, lambda run: reverse("qubesync:question", args=[run.pk]))


def run_status_context(record, operation):
    # type: (Any, str) -> Dict[str, Any]
    """What qubesync/run_status.html reads: record's latest run of operation, its summary, a
    failure's detail, and where an unconfirmed start is sent again. The {% qube_run_status %}
    tag renders it."""
    from django.urls import reverse

    return _run_status_context(record, operation, lambda run: reverse("qubesync:retry_start", args=[run.pk]))
