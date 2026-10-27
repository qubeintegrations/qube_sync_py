"""The routes' views. urls.py mounts them; each hands the request to qubesync.kit and turns
its Reply into a response."""
from typing import Optional

from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .. import kit

__all__ = [
    "connect",
    "onboarding",
    "disconnect",
    "disconnect_form",
    "run_webhook",
    "connection_webhook",
    "request_webhook",
    "answer",
    "search",
    "retry_start",
    "redeliver",
    "storyboard",
    "storyboard_search",
    "storyboard_answer",
    "response",
]


def response(reply, request=None):
    # type: (kit.Reply, Optional[HttpRequest]) -> HttpResponse
    if reply.error is not None:
        if not _keep_error(request, reply.error):
            return response(reply.fallback)
    if reply.location is not None:
        redirect = HttpResponseRedirect(reply.location)
        redirect.status_code = reply.status
        return redirect
    if reply.json is not None:
        return JsonResponse(reply.json, status=reply.status, safe=False)
    if reply.text is not None:
        return HttpResponse(reply.text, status=reply.status, content_type="text/plain; charset=utf-8")
    return HttpResponse(status=reply.status)


def _keep_error(request, message):
    # type: (Optional[HttpRequest], str) -> bool
    # In the session, for the templates to show once.
    session = getattr(request, "session", None)
    if session is None:
        return False
    session[kit.ERROR_KEY] = message
    return True


@require_POST
def connect(request):
    # type: (HttpRequest) -> HttpResponse
    """POST quickbooks/connections: qubesync.kit.connect."""
    from django.conf import settings

    referer = request.headers.get("Referer")
    reply = kit.connect(request, request.POST, referer, request.get_host(), production=not settings.DEBUG)
    return response(reply)


@require_POST
def onboarding(request, id):
    # type: (HttpRequest, str) -> HttpResponse
    """POST quickbooks/connections/<id>/onboarding: qubesync.kit.onboarding."""
    return response(kit.onboarding(request, id))


@require_http_methods(["DELETE"])
def disconnect(request, id):
    # type: (HttpRequest, str) -> HttpResponse
    """DELETE quickbooks/connections/<id>: qubesync.kit.disconnect."""
    return _disconnect(request, id)


@require_POST
def disconnect_form(request, id):
    # type: (HttpRequest, str) -> HttpResponse
    """POST quickbooks/connections/<id>/disconnect: the same, from a form, which can't send DELETE."""
    return _disconnect(request, id)


def _disconnect(request, id):
    # type: (HttpRequest, str) -> HttpResponse
    referer = request.headers.get("Referer")
    return response(kit.disconnect(request, id, referer, request.get_host()), request)


@csrf_exempt  # QuBe Sync signs its webhooks instead
@require_POST
def run_webhook(request, id):
    # type: (HttpRequest, str) -> HttpResponse
    """POST webhooks/qube/runs/<id>: qubesync.kit.receive."""
    return _receive(request, "run", id)


@csrf_exempt
@require_POST
def connection_webhook(request, id):
    # type: (HttpRequest, str) -> HttpResponse
    """POST webhooks/qube/connections/<id>: qubesync.kit.receive."""
    return _receive(request, "connection", id)


@csrf_exempt
@require_POST
def request_webhook(request, id):
    # type: (HttpRequest, str) -> HttpResponse
    """POST webhooks/qube/requests/<id>: qubesync.kit.receive."""
    return _receive(request, "request", id)


def _receive(request, kind, id):
    # type: (HttpRequest, str, str) -> HttpResponse
    signature = request.headers.get(kit.SIGNATURE_HEADER)
    body = _raw_body(request)  # the raw bytes the signature is over
    # The enqueue setting's default is the kit's worker thread, which closes its database
    # connection after each job, as a request does.
    return response(kit.receive(kind, id, body, signature, path=request.path))


def _raw_body(request):
    # type: (HttpRequest) -> Optional[bytes]
    """The body, read from the request's stream rather than request.body, so Django's
    DATA_UPLOAD_MAX_MEMORY_SIZE (2.5 MB by default) doesn't refuse a webhook the kit takes (up
    to MAX_WEBHOOK_BODY, 5 MB), whatever its content type. None when it's over that: a 413."""
    try:
        length = int(request.META.get("CONTENT_LENGTH") or 0)
    except ValueError:
        length = 0
    if length > kit.MAX_WEBHOOK_BODY:
        return None
    return request.read(kit.MAX_WEBHOOK_BODY + 1)


@require_POST
def answer(request, id):
    # type: (HttpRequest, str) -> HttpResponse
    """POST qube/questions/runs/<id>: qubesync.kit.answer. Django's CSRF middleware checks the
    token the question template writes in each form."""
    referer = request.headers.get("Referer")
    return response(kit.answer(request, id, request.POST, referer, request.get_host()), request)


@require_GET
def search(request, id):
    # type: (HttpRequest, str) -> HttpResponse
    """GET qube/questions/runs/<id>/search: qubesync.kit.search."""
    return response(kit.search(request, id, request.GET))


@require_POST
def retry_start(request, id):
    # type: (HttpRequest, str) -> HttpResponse
    """POST qube/runs/<id>/retry_start: qubesync.kit.retry_start."""
    referer = request.headers.get("Referer")
    return response(kit.retry_start(request, id, referer, request.get_host()), request)


@require_POST
def redeliver(request, id):
    # type: (HttpRequest, str) -> HttpResponse
    """POST qube/runs/<id>/redeliver: qubesync.kit.redeliver."""
    referer = request.headers.get("Referer")
    return response(kit.redeliver(request, id, referer, request.get_host()), request)


# -- The storyboard: every screen with sample data, while the storyboard setting is on --------


def _storyboard_on():
    # type: () -> bool
    from django.conf import settings

    return kit.storyboard_on(bool(settings.DEBUG))


def _storyboard_url(name, key):
    # type: (str, Optional[str]) -> str
    from django.urls import reverse

    if name == "index":
        return reverse("qubesync:storyboard")
    return reverse("qubesync:storyboard_%s" % name, args=[key])


@require_GET
def storyboard(request, screen=None):
    # type: (HttpRequest, Optional[str]) -> HttpResponse
    """GET qube/storyboard and qube/storyboard/<screen>: every screen (or one) from sample
    data, in the storyboard_layout setting's template (its block content)."""
    from django.shortcuts import render

    if not _storyboard_on():
        raise Http404("The storyboard is off (the storyboard setting).")
    page = kit.storyboard_page(screen, _storyboard_url, notice="sent" in request.GET)
    if page is None:
        raise Http404("No such screen.")
    layout = kit.settings().storyboard_layout or "qubesync/storyboard/page.html"
    return render(request, "qubesync/storyboard.html", {"storyboard": page, "layout": layout})


@require_GET
def storyboard_search(request, screen):
    # type: (HttpRequest, str) -> HttpResponse
    """GET qube/storyboard/<screen>/search: matches from the samples."""
    if not _storyboard_on():
        return response(kit.Reply(404, json=[]))
    return response(kit.storyboard_search(screen, request.GET))


@require_POST
def storyboard_answer(request, screen):
    # type: (HttpRequest, str) -> HttpResponse
    """POST qube/storyboard/<screen>/answer: sends nothing, and says so."""
    if not _storyboard_on() or kit.storyboard_page(screen, _storyboard_url) is None:
        raise Http404("No such screen.")
    return response(kit.storyboard_answer(screen, _storyboard_url("screen", screen)))
