"""The routes' views. urls.py mounts them; each hands the request to qubesync.kit and turns
its Reply into a response."""
from typing import Any

from django.db import close_old_connections
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .. import kit
from ..kit import _defaults

__all__ = ["webhook", "connect", "answer", "search", "response"]


def response(reply):
    # type: (kit.Reply) -> HttpResponse
    if reply.location is not None:
        redirect = HttpResponseRedirect(reply.location)
        redirect.status_code = reply.status
        return redirect
    if reply.json is not None:
        return JsonResponse(reply.json, status=reply.status, safe=False)
    if reply.text is not None:
        return HttpResponse(reply.text, status=reply.status, content_type="text/plain; charset=utf-8")
    return HttpResponse(status=reply.status)


def _in_process(operation, record_id, body):
    # type: (str, str, str) -> None
    """The enqueue setting's default under Django: the kit's worker thread, with a database
    connection of its own, as a request would have."""
    _defaults.default_queue().submit(_job, operation, record_id, body)


def _job(operation, record_id, body):
    # type: (str, str, str) -> None
    close_old_connections()
    try:
        kit.run(operation, record_id, body)
    finally:
        close_old_connections()


@csrf_exempt  # QuBe Sync signs its webhooks instead
@require_POST
def webhook(request, operation, record_id):
    # type: (HttpRequest, str, str) -> HttpResponse
    """POST webhooks/qube/<operation>/<record id>: qubesync.kit.receive."""
    enqueue = None if kit.settings().is_set("enqueue") else _in_process
    signature = request.headers.get(kit.SIGNATURE_HEADER)
    body = _raw_body(request)  # the raw bytes the signature is over
    return response(kit.receive(operation, record_id, body, signature, enqueue=enqueue))


def _raw_body(request):
    # type: (HttpRequest) -> Any
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
def connect(request):
    # type: (HttpRequest) -> HttpResponse
    """POST quickbooks/connect: qubesync.kit.connect, for the current_account setting's
    account."""
    return response(kit.connect(request))


@require_POST
def answer(request, operation, record_id):
    # type: (HttpRequest, str, str) -> HttpResponse
    """POST qube/questions/<operation>/<record id>: qubesync.kit.answer. Django's CSRF
    middleware checks the token the question template writes in each form."""
    referer = request.headers.get("Referer")
    reply = kit.answer(request, operation, record_id, request.POST, referer, request.get_host())
    return response(reply)


@require_GET
def search(request, operation, record_id):
    # type: (HttpRequest, str, str) -> Any
    """GET qube/questions/<operation>/<record id>/search: qubesync.kit.search."""
    return response(kit.search(request, operation, record_id, request.GET))
