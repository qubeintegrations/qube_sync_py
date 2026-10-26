"""{% load qubesync %}: the question and run status templates for a record's page, as the
Rails engine's partials are rendered:

    {% qube_run_status invoice "create_invoice" %}
    {% qube_question invoice "create_invoice" %}

Each takes the record and its operation's slug, and passes the page's CSRF token and request
on to the template (qubesync/question.html, qubesync/run_status.html).
"""
from django import template

from .. import question_context, run_status_context

register = template.Library()


def _with_page(context, values):
    values["csrf_token"] = context.get("csrf_token")
    values["request"] = context.get("request")
    return values


@register.inclusion_tag("qubesync/question.html", takes_context=True)
def qube_question(context, record, operation):
    """The open question of record's latest run of operation, with a form per choice, or
    nothing when it isn't asking."""
    return _with_page(context, question_context(record, operation))


@register.inclusion_tag("qubesync/run_status.html", takes_context=True)
def qube_run_status(context, record, operation):
    """Where record's latest run of operation stands, or nothing when it has no runs."""
    return _with_page(context, run_status_context(record, operation))
