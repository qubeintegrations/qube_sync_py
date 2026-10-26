from django.http import HttpResponse
from django.template import engines
from django.urls import include, path

from .models import Invoice

PAGE = engines["django"].from_string(
    "{% load qubesync %}<main>{% qube_run_status invoice 'create_invoice' %}"
    "{% qube_question invoice 'create_invoice' %}</main>"
)


def invoice_page(request, id):
    """Stands in for an app's invoice page, with the run status and the question on it."""
    return HttpResponse(PAGE.render({"invoice": Invoice.objects.get(pk=id)}, request))


urlpatterns = [
    path("login", lambda request: HttpResponse("sign in")),
    path("invoices/<int:id>", invoice_page),
    path("", include("qubesync.django.urls")),
]
