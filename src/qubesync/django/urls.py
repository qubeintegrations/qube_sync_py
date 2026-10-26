"""The kit's routes, for your urls.py:

    urlpatterns += [path("", include("qubesync.django.urls"))]

Onboarding, the questions, the start retry and the redelivery are behind Django's login_required (LOGIN_URL),
and the POSTs behind Django's CSRF middleware. With another sign-in, include
patterns(sign_in=your_decorator) instead:

    urlpatterns += [path("", include((qubesync.django.urls.patterns(sign_in=staff_only), "qubesync")))]

current_account and authorize_question (qubesync.kit.configure) decide the rest. The webhooks
are never behind sign-in or CSRF: QuBe Sync signs them. Each route is named in the qubesync
namespace (reverse("qubesync:connections")).
"""
from typing import Any, Callable, List, Optional

from django.urls import path

from . import views

app_name = "qubesync"


def patterns(sign_in=None):
    # type: (Optional[Callable[[Any], Any]]) -> List[Any]
    """The routes, with sign_in (a view decorator; login_required when None) on all but the
    webhooks."""
    if sign_in is None:
        from django.contrib.auth.decorators import login_required

        sign_in = login_required
    return [
        # A "Connect QuickBooks Desktop" button posts here (with an optional name), and a
        # connection's "Set up again" to its onboarding. QuBe Sync's setup doesn't come back to
        # your app: it tells the connection by webhook.
        path("quickbooks/connections", sign_in(views.connect), name="connections"),
        path("quickbooks/connections/<str:id>/onboarding", sign_in(views.onboarding), name="connection_onboarding"),
        # Each run's webhook URL is QUBE_WEBHOOK_URL/runs/<run id>, and a connection's is
        # QUBE_WEBHOOK_URL/connections/<connection id>.
        path("webhooks/qube/runs/<str:id>", views.run_webhook, name="run_webhook"),
        path("webhooks/qube/connections/<str:id>", views.connection_webhook, name="connection_webhook"),
        # A start QuBe Sync never confirmed, sent again, from the run status template.
        path("qube/runs/<str:id>/retry_start", sign_in(views.retry_start), name="retry_start"),
        # A run that looks stuck, its latest event sent again, from the run status template.
        path("qube/runs/<str:id>/redeliver", sign_in(views.redeliver), name="redeliver"),
        # Your user's answer to a run's question, from the question template, and a record
        # field's search.
        path("qube/questions/runs/<str:id>", sign_in(views.answer), name="question"),
        path("qube/questions/runs/<str:id>/search", sign_in(views.search), name="question_search"),
    ]


urlpatterns = patterns()
