"""{% load qubesync %}: the question and run status templates for a record's page, as the
Rails engine's partials are rendered:

    {% qube_run_status invoice "create_invoice" %}
    {% qube_run_status invoice "create_invoice" connection=connection %}
    {% qube_question invoice "create_invoice" %}
    {% qube_sync_status invoice "create_invoice" as sync %}{% if sync.status != "in_quickbooks" %}...
    {% qube_error %}  (a route's message, on a page without the other two: a disconnect's)
    {% qube_assets stylesheet=True %}  (in your base template's <head>: the behaviour script,
                                        and the opt-in stylesheet)

The pieces use {% qube_classes piece "qube-..." %} (their qube- classes and the ui_classes
setting's), {% qube_t "status.running" %} (the messages setting's words) and
{% qube_capture as control %}...{% endqube_capture %} (a field's control, for its wrapper).

Each takes the record and its operation's slug, and passes the page's CSRF token and request
on to the template (qubesync/question.html, qubesync/run_status.html). Whichever comes first
shows the message a question or run route left in the session.
"""
from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from ... import kit
from ...kit import SyncStatus
from .. import question_context, run_status_context, take_error

register = template.Library()


def _with_page(context, values):
    values["csrf_token"] = context.get("csrf_token")
    values["request"] = context.get("request")
    return values


@register.inclusion_tag("qubesync/question.html", takes_context=True)
def qube_question(context, record, operation):
    """The open question of record's latest run of operation, with a form per choice, or
    nothing when it isn't asking."""
    return _with_page(context, question_context(record, operation, request=context.get("request")))


@register.inclusion_tag("qubesync/run_status.html", takes_context=True)
def qube_run_status(context, record, operation, connection=None):
    """Where record stands with QuickBooks for operation (on connection, else on its latest
    run's), or nothing before it's sent."""
    return _with_page(context, run_status_context(record, operation, connection, request=context.get("request")))


@register.simple_tag
def qube_sync_status(record, operation, connection=None):
    """record's SyncStatus for operation (on connection, else on its latest run's), for a page
    that shows a start button only while it makes sense."""
    if connection is not None:
        return SyncStatus.of(connection, record, operation)
    return SyncStatus.latest(record, operation)


@register.inclusion_tag("qubesync/error.html", takes_context=True)
def qube_error(context):
    """The message a route left in the session (a disconnect refused, say), once."""
    return {"message": take_error(context.get("request"))}


@register.simple_tag
def qube_classes(piece, *base):
    """A piece's classes: its qube- classes, then the ui_classes setting's for it."""
    return kit.qube_classes(piece, *base)


@register.simple_tag
def qube_t(key, **values):
    """A message the screens say (qubesync.kit.t), the messages setting's words over English."""
    return kit.t(key, **values)


@register.simple_tag(takes_context=True)
def qube_assets(context, stylesheet=False):
    """The behaviour script's tag (deferred, with request.csp_nonce when django-csp sets one)
    and, with stylesheet=True, the opt-in stylesheet's, from your static files."""
    from django.templatetags.static import static

    request = context.get("request")
    nonce = getattr(request, "csp_nonce", None) if request is not None else None
    tags = []
    if stylesheet:
        tags.append(format_html('<link rel="stylesheet" href="{}" media="all">', static("qubesync/qubesync.css")))
    if nonce:
        tags.append(format_html('<script src="{}" defer nonce="{}"></script>', static("qubesync/question.js"), nonce))
    else:
        tags.append(format_html('<script src="{}" defer></script>', static("qubesync/question.js")))
    return mark_safe("\n".join(tags))


class _CaptureNode(template.Node):
    def __init__(self, nodelist, name):
        self.nodelist = nodelist
        self.name = name

    def render(self, context):
        context[self.name] = mark_safe(self.nodelist.render(context))
        return ""


@register.tag
def qube_capture(parser, token):
    """{% qube_capture as control %}...{% endqube_capture %}: what's inside, rendered, as
    control (safe HTML), for the field wrapper a field piece includes."""
    bits = token.split_contents()
    if len(bits) != 3 or bits[1] != "as":
        raise template.TemplateSyntaxError("qube_capture takes 'as <name>'")
    nodelist = parser.parse(("endqube_capture",))
    parser.delete_first_token()
    return _CaptureNode(nodelist, bits[2])
