# QubeSync Python Library

A Python library for QuickBooks Desktop integration through [QuBe Sync](https://docs.qubesync.com): a client for the v2 API, webhook verification, and (for v1) a DSL for building QuickBooks XML requests.

## Features

- 🔌 **v2 API client** - Connections, workflow runs and their questions, every QuickBooks operation as a typed method (`qube.customer.create`), with retries and idempotency
- 🧩 **Integration kit** - Webhooks, onboarding and questions for Django, Flask and FastAPI (`qubesync.kit`), so your app keeps only its own code
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

Also `list_runs(connection_id, reference=None, state=None, outcome=None)` and
`run_events(connection_id, run_id, after=None, limit=None)`, which returns the whole body
(`{"data": [...], "next_after": ...}`) so you can page with `after=`.

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

The kit is the part of a QuBe Sync integration that's the same for every app: the webhook
endpoint and its job, onboarding, the question routes and their template, and the `Operation`
and `ConnectionEvents` bases with their reference, revision and delivery-id checks. It ships in
this package, so `pip install -U qubesync` updates it, and your app keeps only its own code:

```
quickbooks_desktop/
    config.py          qubesync.kit.configure(...): the one place the kit reads your app from
    create_invoice.py  an Operation subclass per way your app starts a workflow
    connection.py      a ConnectionEvents subclass: the account, and the connection's handlers
```

`qubesync.kit` is framework-free. The adapters, `qubesync.django`, `qubesync.flask` and
`qubesync.fastapi`, each come with an extra that installs the framework:

```bash
pip install "qubesync[django]>=0.4.0"    # or [flask], or [fastapi]
```

### Settings

`qubesync.kit.configure(...)` in `quickbooks_desktop/config.py`. A setting your app hasn't
written raises `qubesync.kit.NotConfigured` the first time it's needed, naming that file, so
nothing silently passes. `repr(qubesync.kit.settings())` never shows the API key or the secret.

| Setting | What it is | Default |
| --- | --- | --- |
| `operations` | `{"create_invoice": CreateInvoice}`: each operation by the slug in its webhook URL (a class, or its dotted path, imported at first use) | none: raises |
| `connection` | your `ConnectionEvents` subclass (or its dotted path). `connection` is its slug in webhook URLs, never an operation's | none: raises |
| `current_account` | `(request) -> account`: the signed-in customer's account. `None` answers onboarding 401 | none: raises |
| `authorize_question` | `(request, record, operation) -> True` when the signed-in user may answer or search that record's question. Only `True` allows | none: every answer and search is refused (403), and logged |
| `enqueue` | `(operation, record_id, body)`: hands a verified webhook to your queue, whose job calls `qubesync.kit.run(operation, record_id, body)` | one worker thread in this process (FastAPI: background tasks, one at a time), with a warning: a restart loses what hasn't run |
| `dedupe` | an object with `seen(key)` and `remember(key)`, for notification delivery ids | in memory, with a warning |
| `api_key`, `base_url`, `webhook_secret`, `webhook_url` | | `QUBE_API_KEY`, `QUBE_URL` (`https://qubesync.com`), `QUBE_WEBHOOK_SECRET`, `QUBE_WEBHOOK_URL`, read at first use. `webhook_secret` may be a list while a secret rotates |
| `client` | a `qubesync.Client` to use instead of the one made from `api_key` and `base_url` (tests) | |
| `render_question` | `(context) -> HTML`, instead of the packaged question template (Flask and FastAPI's `question_html`) | |

`qube env --write .env` writes `QUBE_URL`, `QUBE_API_KEY` and `QUBE_WEBHOOK_SECRET`.
`QUBE_WEBHOOK_URL` is the base of each run's and each connection's webhook URL: `qube listen
--write-env .env` writes it in development, and in production it's your app's
`https://<your app>/webhooks/qube`.

Write `authorize_question` first: the record's id comes from the URL, so it's all that keeps one
customer's users off another's records.

Before production, point `enqueue` at a durable queue and `dedupe` at your database or cache.
With Celery:

```python
# quickbooks_desktop/tasks.py
@app.task
def qube_webhook(operation, record_id, body):
    qubesync.kit.run(operation, record_id, body)  # raises: Celery retries

# quickbooks_desktop/config.py
qubesync.kit.configure(enqueue=lambda *job: qube_webhook.delay(*job), dedupe=DeliveryStore())
```

QuBe Sync had its 2xx when the event was handed on, so a job that raises is your queue's to
retry. `run` raises when `find_record` returns `None`.

### Routes

Relative to where your app mounts them:

| | |
| --- | --- |
| `POST quickbooks/connect` | onboarding: creates the account's connection (or reuses it, with its webhook URL brought up to date and a fresh link), and redirects (303) to QuBe Sync's setup. Behind your sign-in |
| `POST webhooks/qube/<operation>/<record_id>` | verifies the signature (401, logging only the reason), 404 for an unknown slug, 413 over 5 MB, enqueues, 200. Any content type. No sign-in, no CSRF |
| `POST qube/questions/<operation>/<record_id>` | your user's choice, with its fields as their types: 303 back to the page, 409 when the question changed (a 409, or any 400, from QuBe Sync: it's forgotten), 422 with QuBe Sync's words. Behind sign-in and CSRF |
| `GET qube/questions/<operation>/<record_id>/search` | a record field's matches, as JSON (`q` of 2 to 100 characters and a `field`, else `[]`). Behind sign-in |

### Your operation class

The same in every framework, apart from the base you import:

```python
# quickbooks_desktop/create_invoice.py
from qubesync.django import Operation      # or qubesync.flask / qubesync.fastapi
from qubesync.kit import mapping as m


class CreateInvoice(Operation):
    workflow = "add_transaction"
    slug = "create_invoice"

    @classmethod
    def find_record(cls, record_id):
        return Invoice.objects.filter(pk=record_id).first()  # SQLAlchemy: session.get(Invoice, record_id)

    def input(self):
        return m.without_nils({
            "operation": "invoice.create",
            "params": {
                "customer_ref": {"full_name": m.get(self.record, "customer", "name")},
                "ref_number": m.as_string(self.record.number),
                "txn_date": m.as_date(self.record.issued_on),
            },
        })

    def ended(self, event):
        if event.outcome == "added":
            self.record.txn_id = m.dig(event, "output", "record", "txn_id")
            self.save_record(["txn_id"])

    def failed(self, event):
        ...  # event.outcome, event.error, event.cancel_reason

# Elsewhere: CreateInvoice.start(invoice, account.qube_connection_id)
```

The record keeps `qube_reference` (a string), `qube_revision` (an integer) and, for a workflow
that asks, `qube_question` and `qube_links` (JSON). Override `saved_reference` /
`save_reference`, `saved_revision` / `save_revision`, `saved_question` / `saved_links` /
`save_question`, or `save_record`, to keep them elsewhere. Handlers you don't write log.

```python
# quickbooks_desktop/connection.py
from qubesync.django import ConnectionEvents


class Connection(ConnectionEvents):
    @classmethod
    def find_record(cls, record_id):
        return Account.objects.get(pk=record_id)

    def connected(self, event): ...        # QuickBooks is connected
    def setup_cancelled(self, event): ...  # offer Connect again
    def stalled(self, event): ...          # event.stall_reason: not_checking_in, quickbooks_unavailable
    def resumed(self, event): ...          # clear what stalled showed
```

The account keeps `qube_connection_id` and `qube_connection_revision`; a new connection's id
clears the revision. Override `saved_connection_id` / `save_connection_id` and `saved_revision`
/ `save_revision` to keep them elsewhere.

### Django

```python
# settings.py
INSTALLED_APPS += ["qubesync.django"]

# urls.py
urlpatterns += [path("", include("qubesync.django.urls"))]

# quickbooks_desktop/config.py: imported when the apps are ready (or set QUBESYNC_CONFIG to
# another module's dotted path)
import qubesync.kit

qubesync.kit.configure(
    operations={"create_invoice": "quickbooks_desktop.create_invoice.CreateInvoice"},
    connection="quickbooks_desktop.connection.Connection",
    current_account=lambda request: request.user.account,
    authorize_question=lambda request, record, operation: record.account_id == request.user.account_id,
)
```

- Onboarding and the question routes are behind `login_required`. With another sign-in,
  include `qubesync.django.urls.patterns(sign_in=your_decorator)`:
  `path("", include((qubesync.django.urls.patterns(sign_in=staff_only), "qubesync")))`.
- The webhook view is `csrf_exempt` and reads the raw body from the request's stream, so
  `DATA_UPLOAD_MAX_MEMORY_SIZE` (2.5 MB by default) doesn't cap it; the kit takes up to 5 MB.
- `qubesync.django.Operation` and `ConnectionEvents` save with `save(update_fields=...)` and
  apply each event inside `transaction.atomic`, with the row read again under
  `select_for_update` (override `lock_record`), so two workers never apply one record's events
  at once and a handler that raises leaves the record as it was.
- The default queue gives its thread a database connection of its own (`close_old_connections`).

The question template, on the record's page:

```python
context = {"invoice": invoice, **qubesync.django.question_context("create_invoice", invoice)}
return render(request, "invoice.html", context)
```

```django
{% include "qubesync/question.html" %}
```

It writes a form per choice with its CSRF token, a search box for a record field, and `qube-`
classes for your CSS (with django-csp, the search script carries `request.csp_nonce`). For
other markup, put your own at `templates/qubesync/question.html` in a directory Django searches
first (`DIRS`, or an app above `qubesync.django` in `INSTALLED_APPS`); it reads `question`
(`message`, `details`, `choices` with their `fields`, `token`) and `action`.

### Flask

```python
# app.py
import quickbooks_desktop.config  # its qubesync.kit.configure(...), as above
import qubesync.flask
from flask_login import login_required

qubesync.flask.init_app(app, sign_in=login_required)
```

- `qubesync.flask.blueprints(sign_in=None, url_prefix=None)` returns the three blueprints
  (`webhooks`, `connect`, `questions`) to register yourself; `sign_in` (a view decorator) goes
  on onboarding and the question routes, or put your own `before_request` on those two.
- With Flask-WTF's `CSRFProtect` set up before the blueprints are registered, the webhooks
  blueprint is exempted; set up after, call `csrf.exempt(bps.webhooks)`. A `MAX_CONTENT_LENGTH`
  under 5 MB refuses large webhooks first.
- `qubesync.flask.Operation` and `ConnectionEvents` save by committing the SQLAlchemy session
  the record belongs to, so `find_record` returns a record from your session. Take the row lock
  as you find it (`select(Invoice).where(Invoice.id == record_id).with_for_update()`); override
  `save_record` for another ORM.
- The default queue runs each job in an app context of your app's.

The question template: `render_template("invoice.html", invoice=invoice,
**qubesync.flask.question_context("create_invoice", invoice))` with `{% include
"qubesync/question.html" %}` in `invoice.html` (it writes Flask-WTF's `csrf_token()` when it's
there, and a `csp_nonce` from the context), or pass the page
`qubesync.flask.question_html("create_invoice", invoice)` from the view. Your own `templates/qubesync/question.html` is found first, or set
`render_question`.

### FastAPI

```python
# main.py
import quickbooks_desktop.config  # its qubesync.kit.configure(...), as above
import qubesync.fastapi

qube = qubesync.fastapi.routers()
app.include_router(qube.webhooks)
app.include_router(qube.connect, dependencies=[Depends(signed_in)])
app.include_router(qube.questions, dependencies=[Depends(signed_in)])
# or: app.include_router(qubesync.fastapi.router(dependencies=[Depends(signed_in)]))
```

- Your sign-in dependency puts the user where `current_account` and `authorize_question` read
  it (`request.state.user`, say).
- The webhook reads the raw body from `request.stream()`, capped at 5 MB. Without
  an `enqueue` setting, each job is a background task, one at a time. Answers read a form
  (`python-multipart`, in the extra); the record and the calls to QuBe Sync run on a worker
  thread.
- `qubesync.fastapi.Operation` and `ConnectionEvents` save through SQLAlchemy, as Flask's do.

The question template: `qubesync.fastapi.add_templates(templates)` lets your `Jinja2Templates`
find `qubesync/question.html` after your own directories (so yours, at
`templates/qubesync/question.html`, wins); then pass
`qubesync.fastapi.question_context(request, "create_invoice", invoice)` to the page and
`{% include "qubesync/question.html" %}`, or render it with
`qubesync.fastapi.question_html(request, "create_invoice", invoice, templates=templates,
csrf_token=...)`. Set `render_question` for other markup.

### Another framework

`qubesync.kit.receive`, `connect`, `answer` and `search` do each route's work and return a
`Reply` (`status`, and `text`, `json` or `location`); an adapter reads the request, calls one,
and writes the response. `qubesync.kit.question_context(operation, record, action)` is the
template's context.

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
