"""QuBe Sync's integration kit, without a framework: the code that's the same for every app,
so your app keeps only its own (a configure call, an operation class per workflow it starts,
and a connection class) and updates the rest with `pip install -U qubesync`.

Your app's code lives in quickbooks_desktop/:

    quickbooks_desktop/config.py          qubesync.kit.configure(...): the one place the kit
                                          reads your app from
    quickbooks_desktop/create_invoice.py  an Operation subclass per way it starts a workflow
    quickbooks_desktop/connection.py      a ConnectionEvents subclass: the account, and the
                                          connection's four handlers

The routes come from your framework's adapter: qubesync.django, qubesync.flask or
qubesync.fastapi (pip install "qubesync[django]", say). Nothing here names an operation, a
workflow or a model, and nothing imports a framework.
"""
from ..v2 import APIError, Client
from . import mapping
from ._bases import ConnectionEvents, Event, Operation, connection_webhook_url
from ._defaults import InProcessQueue, MemoryDedupe, client
from ._job import operation_class, run
from ._settings import CONFIG_FILE, NotConfigured, Settings, configure, reset, settings
from ._web import (
    CHANGED,
    SIGNATURE_HEADER,
    MAX_WEBHOOK_BODY,
    Reply,
    answer,
    answer_data,
    back,
    choice,
    connect,
    find_question,
    number,
    question_context,
    receive,
    refusal,
    search,
)
from .mapping import as_date, as_integer, as_number, as_string, dig, get, rows, without_nils

__all__ = [
    # settings
    "configure",
    "settings",
    "reset",
    "Settings",
    "NotConfigured",
    "CONFIG_FILE",
    # the bases
    "Operation",
    "ConnectionEvents",
    "Event",
    "connection_webhook_url",
    # the client
    "client",
    "Client",
    "APIError",
    # the job, and the defaults of enqueue and dedupe
    "run",
    "operation_class",
    "InProcessQueue",
    "MemoryDedupe",
    # the routes' work
    "Reply",
    "receive",
    "connect",
    "answer",
    "search",
    "find_question",
    "question_context",
    "CHANGED",
    "SIGNATURE_HEADER",
    "MAX_WEBHOOK_BODY",
    # the answer's parts
    "choice",
    "answer_data",
    "number",
    "refusal",
    "back",
    # mapping helpers
    "mapping",
    "get",
    "rows",
    "dig",
    "as_string",
    "as_number",
    "as_integer",
    "as_date",
    "without_nils",
]
