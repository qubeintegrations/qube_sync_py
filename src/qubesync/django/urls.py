"""The kit's routes, for your urls.py:

    urlpatterns += [path("", include("qubesync.django.urls"))]

connect, answer and search are behind Django's login_required (LOGIN_URL). With another
sign-in, include patterns(sign_in=your_decorator) instead:

    urlpatterns += [path("", include((qubesync.django.urls.patterns(sign_in=staff_only), "qubesync")))]

current_account and authorize_question (qubesync.kit.configure) decide the rest. The webhook
is never behind sign-in: QuBe Sync signs it.
"""
from typing import Any, Callable, List, Optional

from django.urls import path

from . import views

app_name = "qubesync"


def patterns(sign_in=None):
    # type: (Optional[Callable[[Any], Any]]) -> List[Any]
    """The routes, with sign_in (a view decorator; login_required when None) on connect,
    answer and search."""
    if sign_in is None:
        from django.contrib.auth.decorators import login_required

        sign_in = login_required
    return [
        path("webhooks/qube/<str:operation>/<str:record_id>", views.webhook, name="webhook"),
        path("quickbooks/connect", sign_in(views.connect), name="connect"),
        path("qube/questions/<str:operation>/<str:record_id>", sign_in(views.answer), name="answer"),
        path(
            "qube/questions/<str:operation>/<str:record_id>/search",
            sign_in(views.search),
            name="search",
        ),
    ]


urlpatterns = patterns()
