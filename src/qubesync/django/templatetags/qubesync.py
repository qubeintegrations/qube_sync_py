"""{% load qubesync %}: the question and run status templates for a record's page, as the
Rails engine's partials are rendered:

    {% qube_run_status invoice "create_invoice" %}
    {% qube_run_status invoice "create_invoice" connection=connection %}
    {% qube_question invoice "create_invoice" %}
    {% qube_sync_status invoice "create_invoice" as sync %}{% if sync.status != "in_quickbooks" %}...
    {% qube_error %}  (a route's message, on a page without the other two: a disconnect's)

Each takes the record and its operation's slug, and passes the page's CSRF token and request
on to the template (qubesync/question.html, qubesync/run_status.html). Whichever comes first
shows the message a question or run route left in the session.
"""
from django import template

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
    return {"error": take_error(context.get("request"))}
