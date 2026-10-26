"""QuBe Sync's integration kit, without a framework: the part of an integration that's the
same in every app, so your app keeps only its own code and updates the rest with
`pip install -U qubesync`.

It keeps tables of its own: your customers' connections (an account can have several, one
per company file), the runs your app starts, the QuickBooks ids it learns, each against its
connection, and the notifications each run has taken. Django gets them as qubesync.django's
models and migrations; Flask and FastAPI as the SQLAlchemy models in qubesync.kit.sqlalchemy.
Your own tables need no QuBe columns.

Your app's code lives in quickbooks_desktop/:

    quickbooks_desktop/config.py              qubesync.kit.configure(...): the one place the
                                              kit reads your app from
    quickbooks_desktop/create_invoice.py      an Operation subclass per way it starts a workflow
    quickbooks_desktop/connection_events.py   a ConnectionEvents subclass, for a connection's
                                              connected, setup_cancelled, stalled and resumed

The routes come from your framework's adapter: qubesync.django, qubesync.flask or
qubesync.fastapi (pip install "qubesync[django]", say). Nothing here imports a framework.
"""
from ..v2 import APIError, Client
from . import mapping
from ._connection_events import ConnectionEvents
from ._defaults import CacheDedupe, DatabaseDedupe, InProcessQueue, client, log_retry
from ._errors import (
    CONFIG_FILE,
    MissingReference,
    NotConfigured,
    NotConnected,
    NotReady,
    UnknownOperation,
)
from ._job import perform, retry_delay, run
from ._models import family_for
from ._operation import Operation, without_nils
from ._settings import Settings, configure, reset, settings
from ._sync_status import SyncStatus
from ._web import (
    CHANGED,
    ERROR_KEY,
    MAX_WEBHOOK_BODY,
    NO_ANSWER,
    NOT_QUIET,
    NOT_STARTING,
    REDELIVERY_REFUSED,
    SIGNATURE_HEADER,
    SIGNATURE_HINTS,
    Reply,
    answer,
    answer_data,
    authorized_run,
    back,
    back_with_error,
    choice,
    connect,
    number,
    onboarding,
    owner_answers,
    question_context,
    receive,
    redeliver,
    refusal,
    retry_start,
    run_status_context,
    search,
)
from .mapping import as_date, as_integer, as_number, as_string, dig, get, rows

__all__ = [
    # settings
    "configure",
    "settings",
    "reset",
    "Settings",
    "CONFIG_FILE",
    # errors
    "NotConfigured",
    "NotReady",
    "MissingReference",
    "NotConnected",
    "UnknownOperation",
    # the bases
    "Operation",
    "ConnectionEvents",
    "SyncStatus",
    "family_for",
    # the client
    "client",
    "log_retry",
    "Client",
    "APIError",
    # the job, the default queue and the dedupe stores
    "run",
    "perform",
    "retry_delay",
    "InProcessQueue",
    "DatabaseDedupe",
    "CacheDedupe",
    # the routes' work
    "Reply",
    "receive",
    "connect",
    "onboarding",
    "answer",
    "search",
    "retry_start",
    "redeliver",
    "authorized_run",
    "owner_answers",
    "question_context",
    "run_status_context",
    "CHANGED",
    "NOT_STARTING",
    "NOT_QUIET",
    "REDELIVERY_REFUSED",
    "NO_ANSWER",
    "ERROR_KEY",
    "SIGNATURE_HEADER",
    "SIGNATURE_HINTS",
    "MAX_WEBHOOK_BODY",
    # the answer's parts
    "choice",
    "answer_data",
    "number",
    "refusal",
    "back",
    "back_with_error",
    # mapping helpers
    "mapping",
    "without_nils",
    "get",
    "rows",
    "dig",
    "as_string",
    "as_number",
    "as_integer",
    "as_date",
]
