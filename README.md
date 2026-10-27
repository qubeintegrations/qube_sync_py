# QubeSync Python Library

A Python library for QuickBooks Desktop integration through [QuBe Sync](https://docs.qubesync.com): a client for the v2 API, webhook verification, and (for v1) a DSL for building QuickBooks XML requests.

## Features

- 🔌 **v2 API client** - Connections, workflow runs and their questions, every QuickBooks operation as a typed method (`qube.customer.create`), with retries and idempotency
- 🧩 **Integration kit** - Connections, runs and QuickBooks ids in tables of its own, with onboarding, webhooks and questions for Django, Flask and FastAPI (`qubesync.kit`), so your app keeps only its own code
- 🔌 **v1 API client (legacy)** - Connect, queue requests, handle webhooks
- 🏗️ **Intuitive Request Builder DSL** - Build QBXML requests with Python syntax
- 🔒 **Webhook security** - Built-in signature verification for webhooks
- 🚀 **Multiple syntax styles** - Context managers, fluent chaining, or Ruby-like syntax
- ✅ **Fully tested** - comprehensive tests ensuring reliability
- 📦 **Clean imports** - Simple `from qubesync import ...` syntax

## Installation

```bash
pip install qubesync
```

Or install from source:

```bash
git clone https://github.com/qubeintegrations/qube_sync_py
cd qube_sync_py
pip install -e .
```

## v2 client

`qubesync.Client` calls the [QuBe Sync v2 API](https://docs.qubesync.com). It never reads the
environment: make one from your app's settings and pass the key in.

```python
import os
from qubesync import Client, APIError

qube = Client(api_key=os.environ["QUBE_API_KEY"])
```

`Client(api_key, *, base_url="https://qubesync.com", open_timeout=5, read_timeout=30, max_retries=2, total_timeout=60, on_retry=None)`.
Every method returns the response's `data` as plain dicts and lists. Methods that take a URL take
the link QuBe Sync gave you (a webhook's or run's `links`), or a path under `/api/v2`.

### Onboarding a customer

```python
connection = qube.create_connection(
    webhook_url="https://your-app.com/webhooks/qube",  # connection.* events
    name="Acme Ltd",                                    # optional
)
save(connection["id"])
redirect_to(connection["links"]["onboarding"])  # QuBe Sync walks your customer through setup

# Later: a fresh link, or a new webhook URL
qube.regenerate_onboarding(connection["id"])
qube.update_connection(connection["id"], webhook_url="https://your-app.com/webhooks/qube2")
```

`create_connection(webhook_url=..., type="simulated")` makes a connection to a simulated
QuickBooks company file instead, connected as it's made, for testing without a Windows computer.

Also `get_connection(id)`, `list_connections()`, `delete_connection(id)`, and for a setup
without hosted onboarding `set_password(id, password=None)` and `get_qwc(id)` (the QWC file's XML).

### Starting a run and answering its question

```python
run = qube.start_run(
    connection_id,
    "push_invoice",
    {"invoice": {...}},
    reference="invoice-1042",  # your record's id; also the Idempotency-Key
    webhook_url="https://your-app.com/webhooks/qube",
)

# In your webhook handler, for a workflow_run.awaiting_input event:
prompt = event.prompt
# ...show the prompt's choices to your user, then send the one they picked:
qube.answer(event.links["decisions"], choice="use:1")
qube.answer(event.links["decisions"], choice="create", data={"name": "Acme Ltd"})

# A choice whose field is searched: look records up as your user types
matches = qube.search(event.links["search"], field="customer", q="acm")

qube.get_run(event.links["run"])                  # or qube.get_run(connection_id, run_id)
qube.cancel_run(event.links["cancel"], reason="customer cancelled the order")
```

Also `list_runs(connection_id, reference=None, state=None, outcome=None)`,
`redeliver_run(connection_id, run_id)`, which has QuBe Sync send the run's latest event again
(after an outage longer than the webhook retries) and returns `{"run_id", "event", "revision",
"webhook_url"}` (a 409 `APIError` when it has nothing to send yet, 429 when asked again too
soon), and `run_events(connection_id, run_id, after=None, limit=None)`, which returns the whole
body (`{"data": [...], "next_after": ...}`) so you can page with `after=`.

### Typed workflow starts

`qubesync workflows` fetches your app's workflow input types (`GET /api/v2/workflows/types`) and
writes them as a Python module you check in: a start method per workflow, and per branch of its
input, whose operation bodies have the same TypedDicts and field docs as the operation methods
below.

```sh
QUBE_API_KEY=... qubesync workflows            # qube_workflows.py (or python -m qubesync workflows)
QUBE_API_KEY=... qubesync workflows --check    # in CI: exits 1 when the module is out of date
```

```python
import qube_workflows

qube_workflows.client = qube  # once, at boot

qube_workflows.add_transaction.invoice(
    connection_id,
    {
        "customer_ref": {"list_id": "80000001-1700000000"},
        "invoice_line_add": [{"item_ref": {"full_name": "Consulting"}, "amount": 100.0}],
    },
    adds=[{"kind": "customer", "add": {"name": "Acme Ltd"}}],
    reference="invoice-%s" % invoice.id,
    webhook_url="https://your-app.com/webhooks/qube",
)

# The input alone, for start or a qubesync.kit Operation's input:
qube_workflows.add_transaction.invoice_input(params, adds=adds)
```

- A workflow whose input has branches (add_transaction's `operation`, upsert's `kind`) gets one
  method per branch, named by the branch, and an input builder, `<branch>_input`: the
  discriminator is filled in and the inputs are keyword-only (required ones without defaults),
  except a workflow's one operation body (add_transaction's `params`), which every branch takes
  positionally; a workflow with two (upsert's `add` and `update`) takes both as keywords.
  `start(connection_id, input, ...)` takes any branch's input. A workflow without branches gets
  `start(connection_id, *, <inputs>, reference=, webhook_url=)` and `input(...)`. Each builder
  leaves out None values. `connection_id` may be anything with a `qube_id` (a qubesync.kit
  Connection). A name that's a Python keyword or a start's own takes a trailing underscore:
  upsert's `class` input is `class_=`, a `version` input `version_=`, a workflow or branch named
  `class` is `class_` (its builder `class_input`).
- Each start takes `reference=`, `webhook_url=`, `version=None` and `client=` (the module's
  `client` unless given), and returns the run as `start_run` does.
- Each input is a TypedDict: `AddTransactionInvoiceInput` for a branch's (`<Workflow><Branch>Input`),
  `AddTransactionInput` for any of the workflow's (`<Workflow>Input`, the union of its branches, or
  its one shape). An operation body is that operation's params TypedDict
  (`qubesync.operations.invoice.InvoiceCreateParams`) and a nested entry with branches (an `adds`
  item) a union of a TypedDict per branch. An operation newer than your qubesync is a plain
  `Dict[str, Any]`, with a warning when the served operations aren't the library's
  (`qubesync.operations.DIGEST`). A field the workflow sets itself (QuBe Sync lists them as
  `set_by_workflow`: upsert's `list_id` and `edit_sequence`) is optional in that body, which then
  gets a TypedDict of its own (`RecordPaymentPaymentBody`, `UpsertCustomerUpdateBody`), and its
  docs say a value given for it is overwritten. The module imports only qubesync and `typing`,
  runs on Python 3.8, and passes `mypy --strict`.
- QuBe Sync still checks every start: a field the operation doesn't take is a 422 at the call, its
  error's `path` the body (`input.params`) and its `message` naming the field (`unknown parameter:
  "customer_rf"`).
- `--drafts` types each workflow's draft where it has one, so you can build against a workflow
  before publishing it. The header records the digest and the flag, and `--check` fetches with the
  same flag. When QuBe Sync can't be reached or answers 5xx, `--check` warns and exits 0; a 401
  exits 1.
- `--output PATH` chooses the module; `QUBE_BASE_URL` another host (with or without `/api/v2`).
- In the integration kit, an operation's `input` can return a builder's input, typed as it
  (`def input(self) -> AddTransactionInvoiceInput`).

### Queueing an operation

Every QuickBooks operation is a method on its entity: `qube.<entity>.<action>(connection_id, params, webhook_url=...)`,
with actions `create`, `update`, `query`, `delete` and `execute`.

```python
HOOK = "https://your-app.com/webhooks/qube"  # where QuickBooks' answer goes

queued = qube.customer.create(connection_id, {
    "name": "Acme Ltd",
    "bill_address": {"addr1": "1 Main St", "city": "Austin", "state": "TX"},
}, webhook_url=HOOK)

qube.invoice.create(connection_id, {
    "customer_ref": {"full_name": "Acme Ltd"},
    "invoice_line_add": [{"item_ref": {"full_name": "Widget"}, "quantity": 2}],
}, webhook_url=HOOK)

# A query sends its params as the query string, nested filters included
qube.invoice.query(connection_id, {
    "modified_date_range_filter": {"from_modified_date": "2026-10-01"},
    "max_returned": 100,
}, webhook_url=HOOK)

qube.txn_void.execute(connection_id, {"txn_id": "1A2B-1234567890", "txn_void_type": "Invoice"}, webhook_url=HOOK)
qube.class_.query(connection_id, webhook_url=HOOK)  # `class` is `class_`

# qbXML as written
qube.queue_qbxml(connection_id, request_xml, webhook_url=HOOK)
```

Each method sends an Idempotency-Key (`idempotency_key=`, or a UUID made for the call and
reused on its retries) and returns the queued request. A query QuickBooks answers in pages
still makes one call: the pages come to `webhook_url`, one webhook each. An entity's module is
imported the first time you use it (`qube.customer`), so the other 123 cost nothing.

The params are `TypedDict`s with every field's description, in `qubesync.operations.<entity>`
(`from qubesync.operations.invoice import InvoiceCreateParams`) and, for the nested types
entities share, `qubesync.operations._types` (`Ref`, `Address`...). mypy, pyright and your
editor check them; a method's docstring lists its fields and links its API reference page.

The escape hatch takes the operation id: `qube.queue("customer.create", connection_id, params,
webhook_url=HOOK)` is `qube.customer.create(...)`. For an operation newer than your installed
version, pass `method=` and `path=` (the path after the connection):
`qube.queue("widget.create", connection_id, params, webhook_url=HOOK, method="post", path="widgets")`.

Query strings follow the API: a list repeats its key (`ref_number=A&ref_number=B`), a nested
dict brackets its keys (`name_range[from]=A&name_range[to]=M`, a list inside it as
`filter[list_id][]=a`), and booleans are `true`/`false`.

The answer arrives at `webhook_url` (see [Webhooks](#webhooks)). Also `get_request(connection_id, id)`,
`request_pages(connection_id, id)`, `discard_request(connection_id, id)`,
`list_requests(connection_id, page=None, page_size=None, state=None, ...)` (the whole body,
`{"data": [...], "meta": {"page": ..., "total_pages": ...}}`), and `iter_requests(connection_id, ...)`,
a generator over every page.

Anything else: `qube.request("GET", "/workflows", query={...})` returns the whole parsed body.

### Retries, idempotency and errors

- A GET, PUT or DELETE, or any request with an `Idempotency-Key`, is retried up to `max_retries`
  times (after 0.5 s, then 1 s) when the connection fails or times out, or QuBe Sync answers 429,
  502, 503 or 504. A 429 or 503's `Retry-After` is honoured, up to 30 s. Other POSTs
  (`create_connection`, `cancel_run`...) are sent once.
- A call returns or raises within `total_timeout` (60 s), retries and their waits included: each
  attempt's timeouts are cut to the time left, and a retry whose wait (backoff or `Retry-After`)
  would leave under a second isn't made, so the call raises what the last attempt got. Pass
  `max_retries=0` for calls made while a user waits on a page, if 60 s is too long.
- `answer` is retried when its decisions URL has a `prompt_token` (a run's `links.decisions`
  always does while it asks). A retry after a lost answer may raise a 409 `APIError` with code
  `prompt_changed`: the question has been answered, by the first attempt or by someone else.
  Without a `prompt_token` it's sent once, since an answer sent again could be taken for the
  run's next question.
- A retried DELETE (`delete_connection`, or `request("DELETE", ...)`) that gets a 404 returns
  `None`, as a 204 would, when an earlier attempt's answer was lost after it could have reached
  QuBe Sync (a read timeout, a connection reset or closed after opening, a 502 or 504): that
  attempt deleted it. Any other 404 raises, including a retry's 404 after a refused connection, a
  connect timeout, a 429 or a 503.
- `on_retry=` is called with a dict before each retry's wait: `attempt` (1, 2...),
  `max_retries`, `delay` and `elapsed` (seconds), `method`, `url` (without its query string),
  `status` (or `None`) and `error` (the `requests` exception, or `None`). It never gets the key,
  headers or body. It isn't called when no retry is made. An exception it raises stops the call
  and reaches your code.

  ```python
  qube = Client(api_key=key, on_retry=lambda r: log.warning("QuBe Sync retry %(attempt)d: %(method)s %(url)s %(status)s", r))
  ```
- `start_run` sends `reference` as the Idempotency-Key. `queue` and `queue_qbxml` send
  `idempotency_key=` when you pass one, or a UUID made for that call and reused on its retries,
  so a retry never queues a request twice.
- Any other non-2xx answer raises `APIError` (a `QubeSyncError`): `status`, `errors` (the body's
  `errors` as it came: a sentence, `{detail, code}`, fields, or a list of problems), `code`
  (`"prompt_changed"`, `"not_awaiting_input"`...), `message` (one line, safe to log), `body`, and
  `request_id` (send it to support). A connection that still fails after the retries raises the
  `requests` exception (`requests.ConnectionError`, `requests.Timeout`).
- A link on another host is refused with `ValueError` before anything is sent, so the API key
  only ever goes to `base_url`. The key never appears in `repr(client)` or an error.

```python
try:
    qube.answer(event.links["decisions"], choice="use:1")
except APIError as e:
    if e.code == "prompt_changed":
        refresh_question(run)
    else:
        log.error("%s (request %s)", e.message, e.request_id)
        raise
```

## Webhooks

`qubesync.webhooks` verifies a delivery's `X-QUBE-Signature` header and parses the body into a
typed event. It uses only the standard library, works with any framework, and never reads the
environment: pass your webhook secrets in.

```python
import os
from qubesync import webhooks

SECRETS = [os.environ["QUBE_WEBHOOK_SECRET"]]  # add the new one here while a secret rotates

def handle(raw_body, signature_header):
    """raw_body: the request body exactly as received (bytes or str), before any JSON parsing."""
    try:
        event = webhooks.verify(raw_body, signature_header, SECRETS)
    except webhooks.SignatureError as e:
        log.warning("webhook refused: %s", e)  # e.reason: missing, malformed, stale or mismatch
        return 401

    if event.dedupe_key and already_handled(event.dedupe_key):
        return 200  # a redelivery

    if event.type == "request":
        # One page of a request's answer, in one state.
        save_page(event.page_request_id, event.page, event.response_json, event.error)
    elif event.type == "workflow_run":
        run = find_run(event.reference)
        if event.newer_than(run.revision):  # older or equal revisions arrived late: skip them
            run.update(revision=event.revision, state=event.run_state, prompt=event.prompt)
    elif event.type == "notification":
        # Data a running workflow sent out. Never skip it by revision; dedupe_key is delivery_id.
        store_records(event.reference, event.name, event.data)
    elif event.type == "connection":
        conn = find_connection(event.connection_id)
        if event.newer_than(conn.revision):
            conn.update(revision=event.revision, status=event.event, stall_reason=event.stall_reason)
    elif event.type == "name_index":
        refresh_pickers(event.connection_id, event.name_index)
    # event.type == "unknown": a newer event this version doesn't know. Accept it (2xx).

    if event.dedupe_key:
        mark_handled(event.dedupe_key)
    return 200
```

- `webhooks.verify(raw_body, header, secrets, tolerance=300, now=None)` returns the event or
  raises `SignatureError`. `secrets` is a list (or one string); any of them may match. The
  timestamp must be within `tolerance` seconds of `now` (unix seconds or a `datetime`), either way.
  Passing a parsed dict raises `TypeError`, since the signature covers the exact bytes; an empty
  `secrets` list raises `ValueError`.
- `SignatureError.reason` is `"missing"`, `"malformed"`, `"stale"` or `"mismatch"`. Its message
  is safe to log: it never holds the secret, the signatures or the body.
- `webhooks.parse(raw_body)` builds the event without verifying, for tests or when you verified
  elsewhere.
- Every event has `type`, `event`, `timestamp`, `app_id`, `sandbox`, `dedupe_key`, `revision`,
  `reference`, the parsed `body` (also `to_dict()` and `get(key)`). Missing keys read as `None`.

| `type` | Event | Accessors | `dedupe_key` |
| --- | --- | --- | --- |
| `request` | no `event`, has `page_request_id` | `id`, `page_request_id`, `state`, `page`, `iteration_state`, `response_json`, `error` | `"<page_request_id>:<state>"` |
| `workflow_run` | `workflow_run.awaiting_input`, `.completed`, `.failed`, `.cancelled` | `run_id`, `reference`, `revision`, `run_state`, `workflow`, `connection_id`, `prompt`, `outcome`, `output`, `error`, `summary`, `cancel_reason`, `links`, `newer_than(rev)` | `None` |
| `notification` | `workflow_run.notification` | `run_id`, `reference`, `revision`, `delivery_id`, `seq`, `name`, `state`, `from_`, `data` | `delivery_id` |
| `connection` | `connection.*` | `delivery_id`, `revision`, `connection`, `connection_id`, `stall_reason`, `newer_than(rev)` | `delivery_id` |
| `name_index` | `name_index.*` | `connection_id`, `name_index` | `None` |
| `unknown` | anything else | `body`, `get(key)` | `None` |

`newer_than(stored_revision)` is true when nothing is stored yet (`None`) or the event's
revision is higher.

### Flask

```python
from flask import Flask, request
from qubesync import webhooks

app = Flask(__name__)

@app.post("/webhooks/qube")
def qube_webhook():
    try:
        event = webhooks.verify(
            request.get_data(),  # the raw bytes; not request.json
            request.headers.get(webhooks.HEADER),
            SECRETS,
        )
    except webhooks.SignatureError:
        return "", 401
    handle_event(event)  # route by event.type as above, ideally on a background job
    return "", 204
```

`QubeSync.verify_and_build_webhook(body, signature)` (0.1.x, reads `QUBE_WEBHOOK_SECRET`)
still works and returns a plain dict.

## Integration kit

The kit is the part of a QuBe Sync integration that's the same in every app, the Python port of
the [qube_rails](https://rubygems.org/gems/qube_rails) engine:

- tables of its own: your customers' **connections** (an account can have several, one per
  company file), the **runs** your app starts (and any plain **requests**), the **QuickBooks
  ids** it learns, each kept against its connection, the **notifications** each run has taken,
  and when each sync last completed;
- onboarding: make a connection for the signed-in account, send one of its connections back
  through QuBe Sync's setup, or disconnect one;
- the webhook endpoints (verify the signature, find the row, enqueue) and their job (check the
  event is that run's or that connection's, apply it, call your handler);
- the question routes (answer by choice, search a record field), the start retry, the
  redelivery of a stuck run's latest event, and the question and run status templates;
- each record's sync status with QuickBooks, derived from those tables, and list-page filters;
- `Operation`, `Request` and `ConnectionEvents`, the bases of your classes.

It ships in this package, so `pip install -U qubesync` updates it, and your app keeps only its
own code, which the kit never names. Your own tables need no QuBe columns:

```
quickbooks_desktop/
    config.py              qubesync.kit.configure(...): the one place the kit reads your app from
    create_invoice.py      an Operation subclass per way your app starts a workflow
    connection_events.py   a ConnectionEvents subclass, for a connection's own events
```

`qubesync.kit` imports no framework and no ORM. The adapters each come with an extra:

```bash
pip install "qubesync[django]>=0.4.0"    # or [flask], or [fastapi]
```

| | The kit's tables | Routes | Templates |
| --- | --- | --- | --- |
| Django 3.2+ | `qubesync.django.models`, from its migrations (`python manage.py migrate qubesync`) | `include("qubesync.django.urls")` | `{% load qubesync %}`, `{% qube_question %}`, `{% qube_run_status %}`, `{% qube_error %}` |
| Flask 2+ | `qubesync.kit.sqlalchemy` (SQLAlchemy 1.4+), through your session | `qubesync.flask.init_app(app)` | Jinja globals `qube_question`, `qube_run_status`, `qube_error` |
| FastAPI | `qubesync.kit.sqlalchemy`, through your session | `qubesync.fastapi.router()` | `qubesync.fastapi.add_templates(templates)` |

The tables are `qube_connections`, `qube_runs`, `qube_quickbooks_records`,
`qube_notifications`, `qube_sync_marks`, `qube_requests` and `qube_request_deliveries`, with the
same columns, unique keys and indexes as qube_rails' (Django
names two plain indexes more shortly, as it keeps index names to 30 characters). They work on
PostgreSQL, MySQL and SQLite: `qube_runs`' `input`, `error`, `question` and `links` are JSON kept
as text, so no database's JSON type or driver matters, and nothing queries inside them. The
polymorphic ids (`owner_id`, `record_id`) are strings, so integer and UUID keys both fit.

With SQLAlchemy, add the kit's metadata to your Alembic's and autogenerate a revision:

```python
# migrations/env.py
import qubesync.kit.sqlalchemy
target_metadata = [Base.metadata, qubesync.kit.sqlalchemy.metadata]
```

### Settings

`qubesync.kit.configure(...)` in `quickbooks_desktop/config.py`, the only place the kit reads
your app from:

```python
import qubesync.kit

qubesync.kit.configure(
    operations={"create_invoice": "quickbooks_desktop.create_invoice.CreateInvoice"},
    connection_events="quickbooks_desktop.connection_events.ConnectionEvents",
    current_account=lambda request: request.user.account,
    db_session=db.session,  # Flask and FastAPI only
)
```

| Setting | What it is | Default |
| --- | --- | --- |
| `operations` | slug -> operation class, or its dotted path (imported at first use) | none: raises |
| `connection_events` | your `ConnectionEvents` class, or its dotted path | none: raises |
| `current_account` | `(request) -> account`: the signed-in customer's account, which owns its connections. `None` answers 401 | none: raises |
| `authorize_question` | `(request, record, run) -> True` when the signed-in user may answer or search that run's question, or send its start again. The run carries its `operation` and its `connection` (whose `owner` connected it). Only `True` allows; anything else answers 404 (search: `[]` with 404), as for a missing run, and is logged | allows only when `current_account` owns the run's connection (compared by type and id, so a `None` or unsaved account never matches); raises `NotConfigured` while `current_account` isn't set |
| `enqueue` | `(delivery)`: hands `{"kind", "id", "body"}` (kind `"run"`, `"connection"` or `"request"`) to your queue, whose worker calls `qubesync.kit.run(kind, id, body)`. `False` or an exception answers 503 | a worker thread in this process, which retries, with a warning: a restart loses what hasn't run |
| `job_attempts` | how many times the default queue runs a delivery whose work raised, with a growing wait, before it logs an error | `10` |
| `dedupe` | where each run's taken notification delivery ids are kept: `once(run, delivery_id, fn)`, or `seen(key)` / `remember(key)` | `qubesync.kit.DatabaseDedupe`: the `qube_notifications` table, in the handler's transaction |
| `db_session` | `() -> Session`: your SQLAlchemy session for the request or job at hand (a `scoped_session`, or Flask-SQLAlchemy's `db.session`). Django needs none | none: raises (Flask, FastAPI) |
| `api_key` | | `QUBE_API_KEY` |
| `base_url` | | `QUBE_URL`, else `https://qubesync.com` |
| `webhook_secret` | a secret, or a list while one rotates | `QUBE_WEBHOOK_SECRET` |
| `webhook_url` | the base of every webhook URL | `QUBE_WEBHOOK_URL` |
| `client` | a `qubesync.Client` to use instead of the one made from `api_key` and `base_url` (tests) | |
| `production` | `True` where Connect must refuse `simulated=1` (404) | the adapter's guess: Django `not DEBUG`, Flask `not (app.debug or app.testing)`, FastAPI `not app.debug`; `True` elsewhere |
| `prune_runs_after` | a `datetime.timedelta` of a day or more: `qubesync.kit.prune_runs()` deletes ended runs and requests older than that ([Storage](#storage)) | `None`: kept |

A setting your app hasn't written raises `qubesync.kit.NotConfigured`, naming that file, the
first time it's needed, so nothing silently passes. The environment is read at first use.
Secrets are never logged, and `repr(qubesync.kit.settings())` hides them.

Set `authorize_question` only to change who may answer. The default lets the account that owns
the run's connection answer it, which is right for most apps. Set your own to check more (that
this user may see the record) or less (staff who act for any account):

```python
qubesync.kit.configure(
    authorize_question=lambda request, record, run: (
        run.connection.owner == request.user.account and request.user.can_edit(record)
    ),
)
```

A notification (one page of a sync, say) is taken once per run by its `delivery_id`. By default
the id goes in `qube_notifications` inside the run row's lock and the same transaction as your
`notification` handler: a redelivery finds the row and is skipped, and a handler that raises
rolls its row back with its own writes, so the retry runs it again.
`qubesync.kit.CacheDedupe(cache, expires_in=86400)` keeps the ids in a cache instead (anything
with `get(key)` and `set(key, value, timeout=)`, as Django's cache and Flask-Caching are); it
needs a cache your workers share, and it isn't transactional: a crash between the handler's
commit and the cache write runs the handler again.

With SQLAlchemy, give your `find_record` the same session as `db_session`, so a handler's writes
and the kit's commit together. The kit's own steps (applying an event under a run's row lock, a
start, a link outside a handler) commit that session when they end and roll it back when they
raise, as a Django `atomic` block would. On SQLite, use SQLAlchemy's [recipe for SQLite's
transactions](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#serializable-isolation-savepoints-transactional-ddl):
pysqlite's own handling breaks the savepoints a link uses.

### Background work

The endpoint verifies a delivery, answers 200 at once, and hands the work to the `enqueue`
setting. Its default runs `qubesync.kit.perform` on a worker thread in your process (with a
database connection of its own under Django, and an app context under Flask), and a delivery
whose work raised runs again after a growing wait (3 s, 18 s, 83 s ...), `job_attempts` times in
all, then logs an error ("QuBe Sync: gave up on a webhook ..."). It's fine for development; a
restart loses what it hasn't run, so before production set `enqueue` to a durable queue whose
worker calls `qubesync.kit.run`:

```python
# quickbooks_desktop/tasks.py (Celery)
@app.task(autoretry_for=(Exception,), retry_backoff=True, max_retries=9)
def qube_delivery(kind, id, body):
    qubesync.kit.run(kind, id, body)

# quickbooks_desktop/config.py
qubesync.kit.configure(enqueue=lambda d: qube_delivery.delay(d["kind"], d["id"], d["body"]))
```

Retries are then your queue's. QuBe Sync stops sending a delivery once your endpoint has
answered 200, so if the work fails later your queue is the only thing that will run it again.
The endpoint answers 200 only once `enqueue` has taken the delivery: when it returns `False` or
raises, it answers 503, logged without the body, and QuBe Sync sends it again.

`run` raises when it can't do the work (a handler of yours raised, the database is down, the
run's operation was taken out of `operations`: `UnknownOperation`, or a connection's event came
before the connection's id was saved: `NotReady`). One case isn't retried: a delivery whose run,
connection or record has been deleted since it arrived. The endpoint answers 404 unless the row
exists, and your app saves a record before starting its run, so a row that's missing by the
time the job runs was deleted. `run` logs a warning ("QuBe Sync: dropped ...") and returns.

### Routes

Relative to where your app mounts them:

| Route | What it does |
| --- | --- |
| `POST quickbooks/connections` | Connect, for the signed-in account (`current_account`). Sends its newest connection that has never connected (`pending` or `setup_cancelled`) back through setup, so clicking Connect again doesn't pile up connections. Makes a new one (the row, then QuBe Sync's connection with the row's webhook URL, then its `qube_id`, with an optional `name`) when the account has none, or with `new=1`. Redirects (303) to the setup. With `simulated=1`, outside production (the `production` setting), it makes a new connection to a simulated QuickBooks company file instead (`create_connection(type="simulated")`, connected as it's made), and redirects (303) back to the page: for testing with no Windows computer. In production that answers 404. |
| `POST quickbooks/connections/<id>/onboarding` | One of the signed-in account's connections, back through setup, with its webhook URL brought up to date (or made at QuBe Sync, for a row QuBe Sync never answered). Another account's connection answers 404. |
| `DELETE quickbooks/connections/<id>` | Disconnects one of the signed-in account's connections: QuBe Sync deletes its connection (already gone counts), then the row goes, with its runs, requests, QuickBooks links and sync marks (`connection.disconnect()`). 303 back; refused, with a message, while a run or request hasn't ended, or when QuBe Sync doesn't answer. Another account's connection answers 404. Behind your sign-in and CSRF. |
| `POST quickbooks/connections/<id>/disconnect` | The same, for an HTML form, which can't send `DELETE` (Django, Flask and FastAPI have no method override). |
| `POST webhooks/qube/runs/<id>` | A run's webhooks. |
| `POST webhooks/qube/connections/<id>` | A connection's webhooks. |
| `POST webhooks/qube/requests/<id>` | A plain request's webhooks ([Plain requests](#plain-requests)). |
| `POST qube/questions/runs/<id>` | Your user's answer to the run's question, from the template: 303 back to the page. Once QuBe Sync takes it, the run is `running` again (its sync status `sending`) until its next webhook, which waits on the Web Connector's next poll. With a message when it didn't go through (the question has changed: a 409, or any 400, from QuBe Sync, and it's forgotten; or QuBe Sync's words for a field it couldn't take, a 422). Behind your sign-in and CSRF. |
| `GET qube/questions/runs/<id>/search` | A record field's matches, as JSON (`q` of 2 to 100 characters and a `field`, else `[]`). Behind your sign-in. |
| `POST qube/runs/<id>/retry_start` | A start QuBe Sync never confirmed, sent again with the same reference, from the run status template: 303 back, with a message for a run that isn't `starting`. Behind your sign-in and CSRF, and `authorize_question`. |
| `POST qube/runs/<id>/redeliver` | A run that looks stuck (`run.looks_stuck()`: confirmed, not ended, and quiet for 10 minutes while running or waiting on a question this app never got): asks QuBe Sync to send its latest event again (`redeliver_run`), from the run status template's "Send its latest news again" button. 303 back, with a message when QuBe Sync has nothing to send yet (409), was asked a moment ago (429) or didn't answer, or the run isn't quiet. Behind your sign-in and CSRF, and `authorize_question`. |

The webhook routes verify the signature (401 if it doesn't check out), answer 404 when the row
isn't there, enqueue, and answer 200. No sign-in, no CSRF, the raw
body, any content type, up to 5 MB (413 beyond, unread). Each id in a URL is only a pointer: the
job checks the signed event's reference and connection id against the row (a request's event,
its id).

A refused webhook is logged with its reason, its path and what to check, never the secret, the
signature or the body: `mismatch` (it isn't signed with `QUBE_WEBHOOK_SECRET`: set that to the
app's webhook secret, which `qube env --write .env` writes, and restart; QuBe Sync sends it
again), `stale` (its time is over 5 minutes from this server's clock), `missing` or `malformed`
(no valid `X-Qube-Signature`: not from QuBe Sync).

Two buttons cover onboarding: Connect, for an account setting up its first company file (or
finishing a setup it started), and, once it has one, Connect another company file:

```html
<form method="post" action="/quickbooks/connections">{% csrf_token %}<button>Connect QuickBooks Desktop</button></form>
<form method="post" action="/quickbooks/connections">{% csrf_token %}
  <input type="hidden" name="new" value="1"><input type="hidden" name="name" value="Second file">
  <button>Connect another company file</button>
</form>
<!-- Disconnect: show its message with {% qube_error %} (Flask, FastAPI: qube_error) -->
<form method="post" action="/quickbooks/connections/{{ connection.id }}/disconnect">{% csrf_token %}<button>Disconnect</button></form>
<!-- Outside production only: -->
<form method="post" action="/quickbooks/connections">{% csrf_token %}
  <input type="hidden" name="simulated" value="1"><button>Connect a simulated QuickBooks (for testing)</button>
</form>
```

### Connections

A `Connection` is one company file: `owner` (your account), `qube_id` (QuBe Sync's id, `None`
until it answers), `name`, `status` (`pending`, `connected`, `setup_cancelled`, `stalled`),
`stall_reason` and `revision`. `Connection.owned_by(account)` lists an account's (Django's
`QuerySet`, SQLAlchemy's `Query`), `connection.connected()` and `connection.not_checking_in()`
say how it stands, and `connection.webhook_url` is where its events go.

Its own events (`QUBE_WEBHOOK_URL/connections/<id>`) update `status`, `stall_reason` and
`revision` when the event is for that connection (`qube_id`) and newer than the last one
applied, under the row's lock. Then your class runs, with `connection` and `owner`.

`connection.disconnect()` deletes the row with its runs (and their notifications), its plain
requests (and their deliveries), its QuickBooks links and its sync marks, in one transaction,
after your class's `disconnected()` (no event: the account disconnected it), where you delete
your own rows that point at it. The disconnect route calls it once QuBe Sync has deleted its
connection. `connection.last_synced_at("pull_changes")` is when its last completed run of that
workflow started ([Storage](#storage)).

An event can come before the row has its `qube_id`: a simulated connection sends
`connection.connected` as it's made, before `create_connection` has answered. Such an event
finds QuBe Sync's connection made with the row's webhook URL and keeps its id, or raises
`NotReady`, so the job tries again shortly. Connect does the same for a row left without an id
(a crash between the create and the save), so one row never gets two connections. Adopting
lists the app's connections and takes only the one with the row's webhook URL that has never
connected (or simulated, which is connected as it's made), was made at or after the row (its `created_at`, with five minutes allowed for clock
difference), and has the row's name when the row has one; if two qualify it takes neither, and
a connection with no `created_at` is never adopted.

```python
# quickbooks_desktop/connection_events.py
import qubesync.kit


class ConnectionEvents(qubesync.kit.ConnectionEvents):
    # QuickBooks is connected: start syncing.
    def connected(self, event):
        InitialImport.start(self.owner, self.connection)

    # They chose "Cancel setup": offer to set it up again.
    def setup_cancelled(self, event):
        self.log_event(event)

    # connection.stall_reason: "not_checking_in" (turn on the QuickBooks computer and check the
    # Web Connector runs) or "quickbooks_unavailable" (open QuickBooks with the company file).
    def stalled(self, event):
        send_stalled_email(self.owner, self.connection)

    def resumed(self, event):
        self.log_event(event)

    # The account disconnected it: your rows that point at it go in the same transaction.
    def disconnected(self):
        SyncSetting.objects.filter(connection_id=self.connection.id).delete()
```

#### QuickBooks ids

Every ListID and TxnID your app learns is kept against its connection and its list family.
QuickBooks gives out ListIDs from one counter per family, so an id is unique only within its
family of one company file: customers, vendors, employees and other names share one, every item
type shares another, each other list (accounts, classes, terms...) has its own
(`qubesync.kit.family_for(kind)`). TxnIDs are kept per transaction type.

```python
connection.link(customer, kind="customer", qb_id=list_id, edit_sequence="171", name="Riverbend Electric")
connection.qb_id_for(customer, kind="customer")      # "80000001-1738310400", or None
connection.find_linked(list_id, kind="customer")     # your Customer, or None
connection.find_linked(entity_ref_list_id)           # any family; raises ValueError if the id is in several
connection.quickbooks_record(list_id, kind="item")   # the row, with kind, edit_sequence and name
```

A record has one id per kind on a connection; linking it again replaces it. One contact can be
linked as a customer and as a vendor (two QuickBooks names, two ids). An id already linked in
that family to another of your records moves to this one, and that's logged; linked again with
another kind of the same family (an item converted from service to non-inventory), the row's
kind changes. `qb_id_for` finds an item linked as `item_service` when asked for `item` or
`item_non_inventory`, but never hands out a customer's id as a vendor's. A link takes a row lock
and runs in a savepoint, retried once when another worker links the same record at the same
moment.

### Writing an operation

One class per way your app starts a workflow, listed in `operations` by its `slug`:

```python
# quickbooks_desktop/create_invoice.py
import qubesync.kit


class CreateInvoice(qubesync.kit.Operation):
    workflow = "add_transaction"
    slug = "create_invoice"

    # Optional: your record, by the id its run keeps. Leave it out and the run finds the record
    # by its type; write it to load what the input reads.
    @classmethod
    def find_record(cls, id):
        return Invoice.objects.select_related("customer").filter(pk=id).first()

    # The run's input, from the record. without_nils leaves out a field your record doesn't
    # have yet rather than sending it as null.
    def input(self):
        customer = self.record.customer
        return self.without_nils({
            "operation": "invoice.create",
            "params": {
                # Its ListID on this connection when it's linked, otherwise its name.
                "customer_ref": self.quickbooks_ref(customer, kind="customer", name=customer and customer.name),
                "ref_number": self.record.number,
                "invoice_line_add": [
                    {"item_ref": self.quickbooks_ref(line.item, kind="item", name=line.item.name), "amount": float(line.total)}
                    for line in self.record.lines.all()
                ],
            },
        })

    # How the run ended: event.outcome says which, event.output holds the result. Keep the
    # QuickBooks ids it carries on the connection.
    def ended(self, event):
        lines = list(self.record.lines.all())

        # The records the add named, found or made, by the input's path: linked, so the next
        # run refers to them by id. A cancelled ending can carry some too.
        def record_for(path, entry):
            if path == "customer_ref":
                return self.record.customer
            match = re.match(r"\Ainvoice_line_add\.(\d+)\.item_ref\Z", path)
            return lines[int(match.group(1))].item if match else None

        self.link_references(event, record_for)
        if event.outcome != "added":
            return
        txn = (event.output or {}).get("record") or {}
        self.connection.link(self.record, kind="invoice", qb_id=txn["txn_id"],
                             edit_sequence=txn.get("edit_sequence"), name=txn.get("ref_number"))
        self.record.status = "sent"
        self.record.save()

    # A run that failed, or that your app cancelled.
    def failed(self, event):
        self.record.status = "failed"
        self.record.save()

    # What a running workflow sends along (a sync's pages): taken once per delivery_id.
    def notification(self, event):
        self.log_event(event)
```

```python
run = CreateInvoice.start(invoice, connection)
```

`start` takes a connection QuBe Sync has made (it raises `qubesync.kit.NotConnected` for one with
no `qube_id`). It writes the run's row first, with a new reference, its input and state
`starting`, since a webhook can come before it returns; starts the run with that reference as the
idempotency key and `QUBE_WEBHOOK_URL/runs/<run id>` as its webhook URL; keeps QuBe Sync's
`qube_run_id`, `state`, `run_url` and `cancel_url`; and returns the row.

One run at a time per record, operation and connection: while the record's latest run of that
operation on that connection hasn't ended, `start` starts nothing new and returns that run
(`run.reused` is `True`), first sending its start again, with the same reference and stored
input, when QuBe Sync hasn't confirmed it (no `qube_run_id`, still `starting`). The reference is
the idempotency key, so a double click gets the same run back from QuBe Sync, never a second
invoice. A new reference is made only once the last run has ended. The check and the new row
(its input worked out before it's written) happen under a lock on the connection's row
(`SELECT ... FOR UPDATE`), so two starts at once find the same row.

A start can fail two ways, and they're handled differently:

- **Refused** (QuBe Sync answered 4xx: bad input, a workflow that isn't published) or an input
  that raised: nothing was started. The row is marked `failed` and the error raised; start again.
  A 409 is the exception: the idempotency key is in use by another call still in flight (the
  other click of a double click), whose start may land, so the row stays `starting`.
- **No answer** (a timeout, a 5xx, a dropped connection): the run may have started. The row stays
  `starting`, with its reference and input, and the error is raised. Send it again with
  `run.retry_start()` (or `CreateInvoice.retry_start(run)`), never with a new `start`: a new
  reference would start a second run, and a second invoice.

`retry_start()` resends the same reference as the `Idempotency-Key`, with the same workflow, input
and webhook URL. QuBe Sync answers a repeat of a start it took with the run that start made (201,
`Idempotent-Replayed: true`) and starts nothing; a start it never took starts now. It returns a
run that already has its `qube_run_id` as it is, and refuses (`ValueError`) one that `failed`.

A `Run` keeps `operation`, `record`, `connection`, `reference`, `revision`, `state`, `outcome`,
`error`, `cancel_reason`, `ended_at`, and the open `question` and its `links`.
`Run.latest_for(record, "create_invoice")` is a record's newest. Each event is applied under the
run row's lock: one whose reference isn't the run's, or whose `connection_id` isn't its
connection's, is skipped and logged; a notification is taken once; anything else only when its
revision is newer than the last applied. Handlers see `self.record`, `self.run` and
`self.connection`. A handler you don't write logs.

### Plain requests

A workflow is the default: it finds or makes the records an invoice names, checks QuickBooks
before resending after a lost answer, and asks your user when something needs a choice. Use a
plain request (one v2 operation, `Client.queue`) for a one-off query, or a write your app
settles itself: you handle each answer, error and lost answer.

```python
# quickbooks_desktop/find_customer.py
import qubesync.kit


class FindCustomer(qubesync.kit.Request):
    operation = "customer.query"  # a v2 operation id
    slug = "find_customer"

    def params(self):
        return {"full_name": self.record.name}

    # Each answered page: event.response_json["data"], event.page.
    def answered(self, event):
        found = ((event.response_json or {}).get("data") or [None])[0]
        if found:
            self.connection.link(self.record, kind="customer", qb_id=found["list_id"], name=found["full_name"])

    # Every page 1..N is in. Optional.
    def done(self):
        pass

    # error or discarded: show event.error["user_message"].
    def failed(self, event):
        pass

    # QuBe Sync keeps trying (QuickBooks closed, a dialog open). Never resend. Default: logs.
    def retrying(self, event):
        pass

    # The answer never came back: QuickBooks may have applied it. Default: failed(event). A query
    # can be queued again; check a write before resending it.
    def timed_out(self, event):
        pass
```

List it in `operations` with your operations (`"find_customer":
"quickbooks_desktop.find_customer.FindCustomer"`), and queue it:

```python
row = FindCustomer.queue(customer, connection)  # a QueuedRequest
```

`queue` works as `start` does: under the connection row's lock, a request for the same record,
slug and connection that hasn't ended is returned (`row.reused`) rather than queued again, sent
again first, with the same params and `Idempotency-Key`, when QuBe Sync never confirmed it (no
`qube_id`). A new request, with a new key, is made only once the last has ended. The key is the
row's `reference`, saved before the call. A refusal (a 4xx but 409) marks the row `failed` and
raises; a timeout, a 5xx or a 409 leaves it `queued` and raises: queue again, or call
`row.retry_queue()`. `params` that raise mark the row `failed` before anything is sent.
`find_record` works as an operation's.

The request's webhook URL is `QUBE_WEBHOOK_URL/requests/<row id>`. Each delivery is taken once,
by `page_request_id` and `state` (in `qube_request_deliveries`, written in the handler's
transaction), under the row's lock. An event whose `id` isn't the row's `qube_id` is skipped and
logged (request webhooks carry no connection id; before the queue's answer is saved, the first
event's `id` is kept). Pages can come in any order: `done` is called once, when every page from 1
to the one whose `iteration_state` is `done` is in (`not_applicable` is one page). A `retryable`
isn't final, and one that arrives after its page's answer is skipped.

A `QueuedRequest` keeps `operation`, `record`, `connection`, `reference`, `qube_id`, `params`,
`state` (`queued`, `retryable`, `response_received`, `error`, `timed_out`, `discarded`, or
`failed` for a refused queue), `error` (the webhook's), `pages_answered`, `last_page` and
`ended_at` (`ended()`, `done()`). It never keeps a response body: your handler stores what it
needs. A delivery whose handler raises rolls back with it, so the job's retry runs it again.

### Run status

The kit keeps every ending on the run row before your handler runs, under the same lock:
`state`, `outcome`, a failure's `error` (as the event carried it: a sentence, or its code,
message and detail), a cancel's `cancel_reason`, and `ended_at`. `run.ended()`, `run.failed()` and
`run.cancelled()` say which (a run that completed on a `cancelled` outcome counts as cancelled),
and `run.summary_text` says it in a sentence: "Added to QuickBooks", "Done", "Failed:
<message>", "Cancelled: <reason>", "Waiting for your answer", "Starting", "Not confirmed by QuBe
Sync yet" or "Running" (`run.error_message` and `run.error_detail` are its parts).

A start QuBe Sync hasn't confirmed for a minute (`run.unconfirmed()`) reads "Not confirmed by
QuBe Sync yet", and the template offers a "Try the start again" button, posting to
`qube/runs/<id>/retry_start`.

A run QuBe Sync confirmed that has had no news for 10 minutes, running or waiting on a question
this app never received (`run.looks_stuck()`), may have lost a webhook (the app was down longer
than QuBe Sync's retries). The template then says "No news from QuBe Sync about it for a while."
(`.qube-run-quiet`) and offers "Send its latest news again" (`.qube-redeliver`), posting to
`qube/runs/<id>/redeliver`, which asks QuBe Sync to send the run's latest event again; it comes
back through the webhook route, and one already applied is skipped by its revision.

Show the record's status, and its question, on its page:

```django
{% load qubesync %}
{% qube_run_status invoice "create_invoice" %}
{% qube_run_status invoice "create_invoice" connection=connection %}   {# one company file #}
{% qube_question invoice "create_invoice" %}
```

```jinja
{{ qube_run_status(invoice, "create_invoice") }}     {# Flask; connection=... too #}
{{ qube_question(invoice, "create_invoice") }}
{{ qube_run_status(request, invoice, "create_invoice") }}   {# FastAPI, after add_templates #}
```

The status reads the record's [sync status](#sync-status) on `connection`, else on the connection
its latest run went out on, and shows its summary (`.qube-run-summary`, inside
`.qube-run-status.qube-sync-<status>.qube-run-<state>`, with `data-qube-sync-status`) and, for a
failure, the error's detail (`.qube-run-error-detail`); nothing before it's sent.

An answer, a start retry or a redelivery that can't go through goes back to the page with why,
which whichever template comes first shows once (`.qube-error`): Django keeps it in the session,
Flask in its session (so it needs a `SECRET_KEY`; without one the route answers the message as
text with its status, 409 or 422), and FastAPI in `request.session` with Starlette's
`SessionMiddleware`, else in a `qubesync_error` cookie that lasts 60 seconds and that the
template's script clears once it's shown. The question shows the open question of that record's latest run of that operation,
and nothing when that run isn't asking. Each choice is a form posting to the run's question
route with your CSRF token (Django's; Flask-WTF's `csrf_token()`; a `csrf_token` you pass
FastAPI's), and a record field's box searches through your app, so the API key never reaches
the browser. For other markup, put your own `qubesync/question.html` or
`qubesync/run_status.html` where your templates are found first. `question_context` and
`run_status_context` in each adapter give their context for an `{% include %}`.

### Sync status

Where one of your records stands with QuickBooks, per connection and operation, worked out from
the kit's own rows (the record's runs, its link in `qube_quickbooks_records`) and never stored, so
your tables need no status column:

```python
status = connection.sync_status(invoice, "create_invoice")   # a qubesync.kit.SyncStatus
status.status        # "not_sent", "sending", "needs_answer", "in_quickbooks", "done", "failed" or "cancelled"
status.qb_id         # its QuickBooks id on this connection, when it's linked
status.error         # a failed run's error
status.retry         # whether starting again makes sense (failed or cancelled, and not linked)
status.unconfirmed   # a start QuBe Sync hasn't confirmed: run.retry_start()
status.summary_text  # "In QuickBooks", "Waiting for your answer", "Failed: ...", or None
status.run, status.link
```

Per connection, since an invoice can be in one company file and not another.
`qubesync.kit.SyncStatus.latest(invoice, "create_invoice")` reads it on the connection the latest
run went out on, for a page that doesn't say which (`not_sent` with no run).

When the run and the link disagree, the newest word wins:
1. a latest run that hasn't ended: `sending` (an unconfirmed start too) or `needs_answer`;
2. a latest run that failed or was cancelled after the link was made, or with no link:
   `failed` or `cancelled`;
3. a link: `in_quickbooks`, always with its `qb_id`;
4. a latest run that completed and linked nothing (an operation that doesn't link its record):
   `done`, which a new start may follow;
5. otherwise `not_sent`.

For list pages and filters, the connection narrows a model of yours, or your ORM's query of one
(a Django `QuerySet`; a SQLAlchemy `Query` or `select()`), in one query each: an `EXISTS` on the
kit's tables, by your primary key as text, on indexes the kit's migrations add.

```python
connection.not_in_quickbooks(Invoice.objects.filter(account=account))
connection.in_quickbooks(Invoice)
connection.needing_answer(Invoice, "create_invoice")
connection.sending(Invoice, "create_invoice")   # starting or running
```

### Django

```python
# settings.py
INSTALLED_APPS += ["qubesync.django"]

# urls.py
urlpatterns += [path("", include("qubesync.django.urls"))]
```

```bash
python manage.py migrate qubesync
```

- `quickbooks_desktop/config.py` is imported when the apps are ready (or set `QUBESYNC_CONFIG`
  to another module's dotted path).
- Onboarding, the questions, the start retry and the redelivery are behind `login_required` and
  Django's CSRF middleware. With another sign-in, include `qubesync.django.urls.patterns(sign_in=your_decorator)`:
  `path("", include((qubesync.django.urls.patterns(sign_in=staff_only), "qubesync")))`. The
  routes are named in the `qubesync` namespace (`reverse("qubesync:connections")`).
- The webhook views are `csrf_exempt` and read the raw body from the request's stream, so
  `DATA_UPLOAD_MAX_MEMORY_SIZE` (2.5 MB by default) doesn't cap them.
- Each event is applied in `transaction.atomic` with the row read again under
  `select_for_update`. `record_type` keeps your model's label (`myapp.Invoice`).

### Flask

```python
# app.py
import quickbooks_desktop.config  # its qubesync.kit.configure(..., db_session=db.session)
import qubesync.flask
from flask_login import login_required

qubesync.flask.init_app(app, sign_in=login_required)
```

- `qubesync.flask.blueprints(sign_in=None, url_prefix=None)` returns the three blueprints
  (`webhooks`, `connections`, `questions`) to register yourself; `sign_in` goes on all but the
  webhooks.
- With Flask-WTF's `CSRFProtect` set up before the blueprints are registered, the webhooks
  blueprint is exempted; set up after, call `csrf.exempt(bps.webhooks)`. A `MAX_CONTENT_LENGTH`
  under 5 MB refuses large webhooks first.
- `record_type` keeps your model's module and class (`myapp.models.Invoice`), which the kit
  imports to find the row again.

### FastAPI

```python
# main.py
import quickbooks_desktop.config  # its qubesync.kit.configure(..., db_session=Session)
import qubesync.fastapi

app.include_router(qubesync.fastapi.router(dependencies=[Depends(signed_in)]))
# or qube = qubesync.fastapi.routers(), and include qube.webhooks, qube.connections and
# qube.questions where you like
```

- Your sign-in dependency puts the user where `current_account` reads it (`request.state.user`,
  say). FastAPI has no CSRF protection of its own: pass the templates a `csrf_token` for yours.
- `db_session` is a `scoped_session`. The database and the calls to QuBe Sync run on a worker
  thread, which removes its session when the route is done. Answers read a form
  (`python-multipart`, in the extra).

### Another framework

`qubesync.kit.receive`, `connect`, `onboarding`, `disconnect`, `answer`, `search`,
`retry_start` and `redeliver` do each route's work and return a `Reply` (`status`, and `text`, `json` or
`location`); an adapter reads the request, calls one, and writes the response. A `Reply` with an
`error` is a redirect back whose message the adapter keeps for the page (or, when it can't,
answers its `fallback` instead). `qubesync.kit.question_context` and `run_status_context` are the
templates' context, taking that message as `error`.

### What isn't ported

qube_rails tells a record's pages to refresh (Turbo 8 page refreshes over Action Cable) when an
event changes its run. Django, Flask and FastAPI have nothing that does that out of the box, so
the kit doesn't: a reload shows the next question or the ending.

### Storage

Rows go with their run: deleting a run deletes its notifications, and deleting a plain request
its deliveries. Disconnecting a connection deletes its runs and requests. Runs are kept until you
say otherwise. To prune ended ones, set `prune_runs_after` and schedule
`qubesync.kit.prune_runs()` once a day (cron, Celery beat):

```python
qubesync.kit.configure(prune_runs_after=datetime.timedelta(days=90))

@app.task
def prune_qube_runs():
    qubesync.kit.prune_runs()
```

It deletes only ended runs (`Run.prunable(older_than)`: completed, failed or cancelled, by
`ended_at`, or `updated_at` for a run that failed before it started) and ended plain requests
(`QueuedRequest.prunable(older_than)`), with their notifications and deliveries, in batches of
500, never within a day of their end: a webhook for a deleted row answers 404, which QuBe Sync
retries for hours. What a record's page shows stays right: `in_quickbooks` comes from
`qube_quickbooks_records`, which are never pruned, and a sync's next `since` from
`qube_sync_marks` (`connection.last_synced_at(workflow)`, or `self.last_synced_at()` in an
operation: when the connection's last completed run of that workflow started, aware UTC), which
each completed run moves forward, never back. A pruned run's record whose run had failed, or
completed without a link, shows `not_sent` again.

## v1 (legacy)

The `QubeSync` class calls the v1 API (`/api/v1`) and reads `QUBE_API_KEY`, `QUBE_URL` and
`QUBE_WEBHOOK_SECRET` from the environment. It still works, but use the [v2 client](#v2-client)
for new code.

### Quick Start

#### Environment Setup

Set your QubeSync credentials:

```bash
export QUBE_API_KEY="your_api_key_here"
export QUBE_WEBHOOK_SECRET="your_webhook_secret_here"
export QUBE_URL="https://qubesync.com/api/v1"  # Optional, defaults to this
```

#### Basic Usage

```python
from qubesync import QubeSync, RequestBuilder

# 1. Create a connection
connection = QubeSync.create_connection({
    "name": "My Customer Inc.", # optional (will populate from QuickBooks on first sync if blank)
    "redirect_url": "https://your-app.com/qbd-setup/callback"
})

# 2. Build a request using the DSL
request = RequestBuilder(version="16.0")
with request as r:
    with r.QBXML() as qbxml:
        with qbxml.QBXMLMsgsRq(onError='stopOnError') as msgs:
            with msgs.CustomerQueryRq(requestID='customer_123', iterator='Start') as query:
                query.MaxReturned(50)
                query.IncludeRetElement('ListID')
                query.IncludeRetElement('Name')
                query.IncludeRetElement('Email')

# 3. Queue the request
response = QubeSync.queue_request(connection['id'], {
    'request_json': request.as_json(),
    'webhook_url': 'https://your-app.com/webhooks/qb_response'
})

print(f"Request queued with ID: {response['id']}")
```

### API Client Reference

#### Connection Management

```python
from qubesync import QubeSync

# Create a new connection
connection = QubeSync.create_connection({
    "name": "My Customer Inc.", # optional (will populate from QuickBooks on first sync if blank)
    "redirect_url": "https://your-app.com/qbd-setup/callback"
})

# Get connection details
connection = QubeSync.get_connection(connection_id)

# Delete a connection
QubeSync.delete_connection(connection_id)

# Generate QWC file for QuickBooks
qwc_content = QubeSync.get_qwc(connection_id)

# Generate password for QuickBooks connection
password = QubeSync.generate_password(connection_id)
```

#### Request Management

```python
# Queue a request
request_data = {
    'request_json': {...},  # Built using RequestBuilder
    'webhook_url': 'https://your-app.com/webhook'
}
response = QubeSync.queue_request(connection_id, request_data)

# Get request status
request = QubeSync.get_request(request_id)

# Get all requests for a connection
requests = QubeSync.get_requests(connection_id)

# Delete a request
QubeSync.delete_request(request_id)
```

#### Webhook Handling

```python
# Verify and parse webhook payload
def handle_webhook(request):
    signature = request.headers.get('X-Qube-Signature')
    # The raw body, bytes or str, before anything parses it
    body = request.body

    try:
        webhook_data = QubeSync.verify_and_build_webhook(body, signature)
        # Process the verified webhook data in the background
        # to ensure a quick response
        print(f"Received response for request: {webhook_data['id']}")
        return {"status": "success"}
    except (StaleWebhookError, InvalidWebhookSignatureError) as e:
        print(f"Webhook verification failed: {e}")
        return {"status": "error"}, 401
```

The timestamp in `X-Qube-Signature` must be within 300 seconds (5 minutes) of now, either way,
or `verify_and_build_webhook` raises `StaleWebhookError`. Pass `max_age` (in seconds) for
another window. A bad, missing or malformed signature raises `InvalidWebhookSignatureError`.

### RequestBuilder DSL

The RequestBuilder provides an intuitive Python DSL for constructing QBXML requests that get converted to JSON format for the QubeSync API.

#### Context Manager Style (Recommended)

```python
from qubesync import RequestBuilder

request = RequestBuilder(version="16.0")
with request as r:
    with r.QBXML() as qbxml:
        with qbxml.QBXMLMsgsRq(onError='stopOnError') as msgs:
            with msgs.InvoiceQueryRq(requestID='inv_query_123') as query:
                query.MaxReturned(25)
                query.IncludeRetElement('TxnID')
                query.IncludeRetElement('TxnNumber')
                query.IncludeRetElement('CustomerRef')
                query.IncludeRetElement('TxnDate')
                query.IncludeRetElement('DueDate')
                query.IncludeRetElement('BalanceRemaining')

json_data = request.as_json()
```

#### Fluent Chaining Style

```python
from qubesync import FluentRequestBuilder

request = FluentRequestBuilder(version="16.0")
request.QBXML().QBXMLMsgsRq(onError='stopOnError').ItemQueryRq(
    requestID='item_query_456'
).add_children([
    ('MaxReturned', 100),
    ('IncludeRetElement', 'ListID'),
    ('IncludeRetElement', 'Name'),
    ('IncludeRetElement', 'Type'),
    ('IncludeRetElement', 'SalePrice')
])

json_data = request.as_json()
```

#### Ruby-like Style

```python
from qubesync import RequestBuilder

request = RequestBuilder(version="16.0")
qbxml = request.QBXML()
msgs = qbxml.QBXMLMsgsRq(onError='stopOnError')
query = msgs.CustomerQueryRq(requestID='customer_789', iterator='Start')
query.MaxReturned(30)
query.IncludeRetElement('ListID')
query.IncludeRetElement('Name')
query.IncludeRetElement('CompanyName')

json_data = request.as_json()
```

#### Handling Python Reserved Words

Use trailing underscores for Python reserved words:

```python
request = RequestBuilder(version="16.0")
with request as r:
    with r.QBXML() as qbxml:
        with qbxml.QBXMLMsgsRq(onError='stopOnError') as msgs:
            # Use trailing underscore for 'class', 'for', 'if', etc.
            with msgs.CustomQueryRq(class_='invoice', for_='reports') as query:
                query.MaxReturned(100)
```

#### Complex Nested Structures

```python
request = RequestBuilder(version="16.0")
with request as r:
    with r.QBXML() as qbxml:
        with qbxml.QBXMLMsgsRq(onError='stopOnError') as msgs:
            with msgs.InvoiceAddRq(requestID='invoice_add_999') as add_req:
                with add_req.InvoiceAdd() as invoice:
                    with invoice.CustomerRef() as customer_ref:
                        customer_ref.ListID('80000001-1234567890')
                    
                    invoice.TxnDate('2024-01-15')
                    invoice.RefNumber('INV-2024-001')
                    
                    with invoice.InvoiceLineAdd() as line:
                        with line.ItemRef() as item_ref:
                            item_ref.ListID('80000002-1234567890')
                        line.Desc('Professional Services')
                        line.Quantity(10)
                        line.Rate(150.00)
```

### Example Output

The RequestBuilder generates clean JSON that the QubeSync API processes:

```json
{
  "version": "16.0",
  "request": [
    {
      "name": "QBXML",
      "children": [
        {
          "name": "QBXMLMsgsRq",
          "attributes": {"onError": "stopOnError"},
          "children": [
            {
              "name": "CustomerQueryRq",
              "attributes": {"requestID": "customer_123", "iterator": "Start"},
              "children": [
                {"name": "MaxReturned", "text": 50},
                {"name": "IncludeRetElement", "text": "ListID"},
                {"name": "IncludeRetElement", "text": "Name"},
                {"name": "IncludeRetElement", "text": "Email"}
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

### Error Handling

```python
from qubesync import (
    QubeSync, 
    QubeSyncError, 
    ConfigError, 
    StaleWebhookError, 
    InvalidWebhookSignatureError
)

try:
    connection = QubeSync.create_connection({"name": "Test"})
except ConfigError as e:
    print(f"Configuration error: {e}")
except QubeSyncError as e:
    print(f"API error: {e}")

# Webhook verification
try:
    webhook_data = QubeSync.verify_and_build_webhook(body, signature)
except StaleWebhookError:
    print("Webhook is too old")
except InvalidWebhookSignatureError:
    print("Invalid webhook signature")
```

### Available Classes

#### API Client
- `QubeSync` - Main API client for all QubeSync operations
- `QubeSyncError` - Base exception class
- `ConfigError` - Configuration/environment variable errors
- `StaleWebhookError` - Webhook timestamp too old
- `InvalidWebhookSignatureError` - Webhook signature verification failed

#### Request Building
- `RequestBuilder` - Context manager style DSL (recommended)
- `FluentRequestBuilder` - Method chaining style DSL
- `RequestElement` - Individual request element (advanced usage)

## Development

### Running Tests

```bash
# Run all tests
python run_tests.py

# Run with verbose output
python run_tests.py --verbose

# Run specific test file
python run_tests.py tests/test_request_builder.py
```

### Running Examples

```bash
# Run all examples
python examples.py

# Use virtual environment
./bin/python examples.py
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`python run_tests.py`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- 📧 Email: support@qubesync.com
- 📖 Documentation: [QubeSync Docs](https://docs.qubesync.com)
- 🐛 Issues: [GitHub Issues](https://github.com/qubeintegrations/qube_sync_py/issues)

## Changelog

### v0.1.0
- Initial release
- Complete QubeSync API client
- RequestBuilder DSL with multiple syntax styles
- Comprehensive test suite
- Webhook security verification
- Clean module structure with intuitive imports
