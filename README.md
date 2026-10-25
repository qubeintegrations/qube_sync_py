# QubeSync Python Library

A Python library for QuickBooks Desktop integration through [QuBe Sync](https://docs.qubesync.com): a client for the v2 API, webhook verification, and (for v1) a DSL for building QuickBooks XML requests.

## Features

- 🔌 **v2 API client** - Connections, workflow runs and their questions, queued requests, with retries and idempotency
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

`Client(api_key, *, base_url="https://qubesync.com", open_timeout=5, read_timeout=30, max_retries=2)`.
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

```python
queued = qube.queue(
    connection_id,
    "customers",                      # the operation's path after the connection
    {"name": "Acme Ltd"},
    webhook_url="https://your-app.com/webhooks/qube",  # where the answer goes
)

# A query: method="get" sends the params as the query string
qube.queue(connection_id, "txn-deleteds", {"txn_del_type": ["Invoice"]},
           webhook_url="https://your-app.com/webhooks/qube", method="get")

# qbXML as written
qube.queue_qbxml(connection_id, request_xml, webhook_url="https://your-app.com/webhooks/qube")
```

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
  (`create_connection`, `answer`, `cancel_run`...) are sent once.
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
