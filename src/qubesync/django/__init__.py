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

The models are qubesync.django.models' Connection, Run, QuickbooksRecord, Notification,
SyncMark, QueuedRequest and RequestDelivery (tables qube_connections, qube_runs,
qube_quickbooks_records, qube_notifications, qube_sync_marks, qube_requests and
qube_request_deliveries). The routes, relative to where urls.py includes them, each named in
the qubesync namespace:

    POST quickbooks/connections                   connections            behind login_required and CSRF
    POST quickbooks/connections/<id>/onboarding   connection_onboarding  behind login_required and CSRF
    DELETE quickbooks/connections/<id>            connection             behind login_required and CSRF
    POST quickbooks/connections/<id>/disconnect   connection_disconnect  the same, for a form
    POST webhooks/qube/runs/<id>                  run_webhook            no sign-in, no CSRF (signed)
    POST webhooks/qube/connections/<id>           connection_webhook     no sign-in, no CSRF (signed)
    POST webhooks/qube/requests/<id>              request_webhook        no sign-in, no CSRF (signed)
    POST qube/questions/runs/<id>                 question               behind login_required and CSRF
    GET  qube/questions/runs/<id>/search          question_search        behind login_required
    POST qube/runs/<id>/retry_start               retry_start            behind login_required and CSRF
    POST qube/runs/<id>/redeliver                 redeliver              behind login_required and CSRF

On a record's page:

    {% load qubesync %}
    {% qube_run_status invoice "create_invoice" %}   {# connection=... for one company file #}
    {% qube_question invoice "create_invoice" %}
    {% qube_error %}   {# a route's message on a page without those two: a disconnect's #}
"""
try:
    import django as _django  # noqa: F401
except ImportError as error:  # pragma: no cover
    raise ImportError('qubesync.django needs Django: pip install "qubesync[django]"') from error

from typing import Any, Dict

from ..kit import ERROR_KEY, ConnectionEvents, Operation
from ..kit import question_context as _question_context
from ..kit import run_status_context as _run_status_context

__all__ = [
    "Operation",
    "ConnectionEvents",
    "question_context",
    "run_status_context",
    "take_error",
    "redirect_back",
]


def question_context(record, operation, request=None):
    # type: (Any, str, Any) -> Dict[str, Any]
    """What qubesync/question.html reads, for the record's page: the open question of record's
    latest run of operation (a slug), if it's asking, where it's answered, and the error the
    last answer left in request's session (taken, so it shows once). The {% qube_question %}
    tag renders it; for your own markup:

        context = {"invoice": invoice, **qubesync.django.question_context(invoice, "create_invoice", request)}
    """
    from django.urls import reverse

    return _question_context(
        record, operation, lambda run: reverse("qubesync:question", args=[run.pk]), error=take_error(request)
    )


def run_status_context(record, operation, connection=None, request=None):
    # type: (Any, str, Any, Any) -> Dict[str, Any]
    """What qubesync/run_status.html reads: record's sync status for operation (on connection,
    else on its latest run's), its run's summary and failure detail, the retry and redelivery
    routes when they apply, and the error left in request's session. The {% qube_run_status %}
    tag renders it."""
    from django.urls import reverse

    return _run_status_context(
        record,
        operation,
        lambda run: reverse("qubesync:retry_start", args=[run.pk]),
        lambda run: reverse("qubesync:redeliver", args=[run.pk]),
        connection=connection,
        error=take_error(request),
    )


def take_error(request):
    # type: (Any) -> Any
    """The message a route left in request's session, removed: shown once."""
    session = getattr(request, "session", None)
    if session is None:
        return None
    return session.pop(ERROR_KEY, None)


def redirect_back(request, error=None):
    # type: (Any, Any) -> Any
    """Back to the page the request came from (303), with error, if any, for the templates to
    show once: for your own views, such as a start button's."""
    from .. import kit
    from .views import response

    referer = request.headers.get("Referer")
    if error is None:
        return response(kit.Reply(303, location=kit.back(referer, request.get_host())), request)
    return response(kit.back_with_error(error, 422, referer, request.get_host()), request)
