# Changelog

All notable changes to the QubeSync Python library will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Typed workflow starts: `qubesync workflows [--drafts] [--check] [--output qube_workflows.py]`
  (a console script, and `python -m qubesync workflows`) fetches your app's workflow input types
  with `QUBE_API_KEY` (from `QUBE_BASE_URL`, with or without `/api/v2`) and writes one module to
  check in: per workflow a namespace (`add_transaction`) with a start method and an input builder
  per branch of its input (`invoice`, `invoice_input`), or `start` and `input`, and a TypedDict
  per input (`AddTransactionInvoiceInput`, `AddTransactionInput`) whose operation bodies are the
  operations' params TypedDicts. A field the workflow sets itself (`set_by_workflow`) is optional
  in that body's own TypedDict. `--check` sends the module's digest as `If-None-Match` and exits 1
  when it's out of date (naming the workflows that changed), on a 401 or without a header, and 0
  with a warning when QuBe Sync can't be reached. The renderer is `qubesync.workflow_types`.
- `Client.workflow_types(include_drafts=False, etag=None)`: GET /workflows/types, returning
  `qubesync.v2.NOT_MODIFIED` on a 304.
- `qubesync.operations.DIGEST`, the sha256 of the operations manifest the library was generated
  from, compared with a workflow types document's `operations_digest`; and
  `qubesync.operations._fields`, each operation's params fields, for the renderer only.

### Changed
- `qubesync.kit.Operation.input` is typed as returning a `Mapping[str, Any]` (was a `Dict`), so
  an override can return a generated input TypedDict. Its behaviour is unchanged.

## [0.4.0] - 2026-10-25

### Added
- `qubesync.kit`, the integration kit: the Python port of the qube_rails engine. It imports no
  framework and no ORM.
  - Tables of its own: `qube_connections` (an account can have several, one per company file),
    `qube_runs`, `qube_quickbooks_records` and `qube_notifications`, with qube_rails' columns,
    unique keys and indexes. Django gets them as `qubesync.django.models` with a migration;
    Flask and FastAPI as SQLAlchemy models in `qubesync.kit.sqlalchemy` (its own `metadata`, for
    an app's Alembic). JSON is kept as text, the same on PostgreSQL, MySQL and SQLite. Your own
    tables need no QuBe columns.
  - `Connection`: `owned_by(owner)`, `link(record, kind=, qb_id=, edit_sequence=None,
    name=None)` (an id linked to another record moves, and that's logged; a row lock and a
    savepoint retry on a unique race), `qb_id_for(record, kind=)`, `find_linked(qb_id,
    kind=None)`, `quickbooks_record(qb_id, kind=None)`, `connected()`, `not_checking_in()`,
    `webhook_url`, `owner`, and `adopt_qube_connection()` for a create whose id was never
    saved (QuBe Sync's one connection with the row's webhook URL and name, made since the row,
    never connected (or simulated)). QuickBooks ids are unique per list family (`family_for`).
  - `Run`: `latest_for(record, operation)`, `retry_start()` (the same reference as the
    Idempotency-Key), `summary_text`, `error_message`, `error_detail`, `open_question`,
    `ended()`, `failed()`, `cancelled()`, `unconfirmed()`, `record`, `webhook_url`.
  - `Operation`: `start(record, connection)` (the run row first; a 4xx or a raised input marks
    it failed, no answer leaves it starting), `retry_start(run)`, `find_record`, `input`, the
    handlers (`question`, `ended`, `failed`, `notification`), `quickbooks_ref`,
    `link_references(event, fn)`, `answered(token)`, `without_nils`, `log_event`. Events are
    checked against the run's reference and connection, applied by revision under the run
    row's lock, and every ending is kept on the run.
  - `ConnectionEvents`: `connected`, `setup_cancelled`, `stalled` and `resumed`, with
    `connection` and `owner`; an event before the row has its qube_id adopts it or raises
    `NotReady` for a retry.
  - `configure(**settings)`: `operations`, `connection_events`, `current_account`,
    `authorize_question` (default: the signed-in account owns the run's connection),
    `enqueue`, `job_attempts` (10), `dedupe` (default `DatabaseDedupe`, the
    `qube_notifications` table in the handler's transaction, or `CacheDedupe`), `db_session`
    (SQLAlchemy), `api_key`, `base_url`, `webhook_secret`, `webhook_url`, `client`. An unset one
    raises `NotConfigured` naming `quickbooks_desktop/config.py`; `repr` hides the secrets.
  - The job, `run(kind, id, body)`, and the default queue (`perform`): a worker thread that
    runs a delivery whose work raised again after a growing wait, `job_attempts` times.
  - The routes' work, returning a `Reply`: `connect`, `onboarding`, `receive`, `answer`,
    `search`, `retry_start`; and `question_context` and `run_status_context`.
- The routes, in each adapter: `POST quickbooks/connections` (reuses the account's
  never-connected connection unless `new=1`), `POST quickbooks/connections/<id>/onboarding`
  (404 unless the signed-in account owns it), `POST webhooks/qube/runs/<id>` and
  `POST webhooks/qube/connections/<id>` (401, 404, 413, 200, or 503 when the enqueue fails),
  `POST qube/questions/runs/<id>` and `GET .../search` (404 when refused, 409 when the question
  changed; an unset `current_account` raises `NotConfigured` there, as on connect), and
  `POST qube/runs/<id>/retry_start`.
- `qubesync.django` (extra `django`): an installed app with the models and migration,
  `qubesync.django.urls`, the templates and `{% load qubesync %}` (`{% qube_question %}`,
  `{% qube_run_status %}`).
- `qubesync.flask` (extra `flask`): `blueprints()` / `init_app()`, the Jinja templates and
  globals (`qube_question`, `qube_run_status`).
- `qubesync.fastapi` (extra `fastapi`): `routers()` / `router()`, `add_templates`,
  `question_html` and `run_status_html`.

## [0.3.0] - 2026-10-25

### Added
- `qubesync.Client`, a client for the v2 API (`/api/v2`): `Client(api_key, base_url=..., open_timeout=5,
  read_timeout=30, max_retries=2)`. It never reads the environment. Methods for connections
  (`create_connection`, `get_connection`, `list_connections`, `update_connection`,
  `delete_connection`, `regenerate_onboarding`, `set_password`, `get_qwc`), workflow runs
  (`start_run`, `get_run`, `list_runs`, `cancel_run`, `run_events`), questions (`answer`,
  `search`), queued requests (`queue_qbxml`, `get_request`, `request_pages`,
  `list_requests`, `iter_requests`, `discard_request`) and `request` for anything else. Each
  returns the response's `data` as plain dicts and lists.
- A method per QuickBooks operation, on its entity: `client.customer.create(connection_id, params,
  webhook_url=..., idempotency_key=None)`, `client.invoice.query(...)`, `client.txn_void.execute(...)`
  (`class` is `client.class_`): 261 operations on 124 entities. Each entity's module
  (`qubesync.operations.<entity>`) is imported on first use. Params are `TypedDict`s with every
  field's description; nested types more than one entity uses are in `qubesync.operations._types`.
  The package ships `py.typed`.
- The methods are generated by `python scripts/generate_operations.py [--check]` from
  `tests/fixtures/operations.json`, a copy of https://qubesync.com/libraries/operations.json; CI
  fails when the generated files are stale or the copy differs from the served one.
- `queue(operation_id, connection_id, params=None, *, webhook_url, idempotency_key=None,
  method=None, path=None)` queues by operation id; an id this version doesn't know needs `method`
  and `path`.
- Query strings repeat a list's key (`ref_number=A&ref_number=B`) and bracket nested dicts
  (`name_range[from]=A`, `filter[list_id][]=a`), as the API reads them.
- Links from webhooks and runs are accepted only on the client's own scheme, host and port;
  anything else raises `ValueError` before a request is made.
- Retries (0.5 s, then 1 s; `Retry-After` honoured up to 30 s) on a failed connection, a
  timeout, 429, 502, 503 and 504, for GET, PUT, DELETE and any request with an
  Idempotency-Key. `start_run` sends `reference` as the key; `queue` and `queue_qbxml` send the
  given `idempotency_key` or a UUID reused on that call's retries.
- `total_timeout=60`: every call returns or raises within it, retries and their waits included.
  Each attempt's timeouts are cut to the time left, and a retry whose wait would leave under a
  second isn't made (a `Retry-After` is never shortened).
- `on_retry=`: called before each retry's wait with `attempt`, `max_retries`, `delay`,
  `elapsed`, `method`, `url` (no query string), `status` and `error`; never the key, headers or
  body. An exception it raises stops the call.
- `answer` is retried when its decisions URL has a `prompt_token`; a retry after a lost answer
  may raise a 409 with code `prompt_changed`.
- A retried DELETE that gets a 404 after an earlier attempt's answer was lost (a read timeout,
  a reset or closed connection, a 502 or 504) returns `None`, as a 204 would.
- `qubesync.APIError(QubeSyncError)` for any non-2xx answer: `status`, `errors`, `code`,
  `message`, `body`, `request_id`. The API key never appears in an error or `repr(client)`.

### Changed
- The README leads with the v2 client; the `QubeSync` class (v1) is documented under
  "v1 (legacy)" and is unchanged.
- Releases publish through PyPI trusted publishing, from `release.yml`'s OIDC token; no API
  token is stored.

## [0.2.0] - 2026-10-23

### Added
- `qubesync.webhooks`: `verify(raw_body, header, secrets, tolerance=300, now=None)` checks a
  delivery's `X-QUBE-Signature` and returns a typed event (`request`, `workflow_run`,
  `notification`, `connection`, `name_index` or `unknown`) with `dedupe_key`, `revision`,
  `reference` and `newer_than(rev)` where they apply. `parse(raw_body)` builds the event
  without verifying. Standard library only, and it never reads the environment.
- `SignatureError(QubeSyncError)`, whose `reason` is `missing`, `malformed`, `stale` or
  `mismatch`. Its message never holds the secret, the signatures or the body.
- Tests drive every case of the server's test vectors (`tests/fixtures/test_vectors.json`).

### Changed
- `QubeSyncError` lives in `qubesync.errors` (still importable from `qubesync` and
  `qubesync.client`).

`QubeSync.verify_and_build_webhook` is unchanged and still works.

## [0.1.2] - 2026-10-22

Security fixes for webhook verification. Upgrading needs no code change.

### Fixed
- `verify_and_build_webhook` no longer prints the timestamp and signatures of every webhook.
- The timestamp must be within 300 seconds of now, either way. It was 500 seconds old, and any
  timestamp in the future passed. `max_age` (seconds) still sets the window.
- A malformed header (a part without `=`, a non-numeric `t`, a blank `v1`) raises
  `InvalidWebhookSignatureError` instead of `ValueError`, and a non-ASCII signature no longer
  raises `TypeError`.

### Changed
- `verify_and_build_webhook` and `sign_payload` take the raw body as `bytes` or `str`.
- `requires-python = ">=3.8"`.
- Tests run against a delivery signed by the QuBe Sync server (`tests/fixtures/webhook_vectors.json`).

## [0.1.0] - 2025-09-12

### Added
- **Complete QubeSync API client** with full CRUD operations for connections and requests
- **RequestBuilder DSL** with multiple syntax styles:
  - Context manager style (recommended Python approach)
  - Fluent chaining style (method chaining)
  - Ruby-like style (direct method calls)
- **Webhook security verification** with HMAC signature validation
- **Comprehensive test suite** with 59 tests covering all functionality
- **Clean module structure** with intuitive imports (`from qubesync import ...`)
- **Multiple request building patterns** for different developer preferences
- **Python reserved word handling** with trailing underscore convention
- **Complex nested structure support** for advanced QBXML requests
- **Error handling** with specific exception classes for different error types
- **Environment variable configuration** for API keys and secrets
- **Request queuing and management** with full lifecycle support
- **QWC file generation** for QuickBooks connection setup
- **Password generation** for QuickBooks connections

### Features
- 🔌 Full QubeSync API integration
- 🏗️ Intuitive DSL for building QBXML requests in JSON format
- 🔒 Built-in webhook security with signature verification
- 🚀 Multiple syntax styles to match developer preferences
- ✅ Comprehensive test coverage with pytest
- 📦 Clean, professional module structure
- 🔧 Easy configuration via environment variables

### API Client Capabilities
- Connection management (create, read, delete)
- Request queuing and management
- Webhook payload verification
- QWC file generation for QuickBooks
- Password generation for connections
- Comprehensive error handling

### RequestBuilder Features
- Context manager syntax for Pythonic code
- Fluent chaining syntax
- Automatic handling of Python reserved words
- Support for complex nested structures
- Clean JSON output compatible with QubeSync API
- Multiple element types (text, attributes, children)

### Technical Details
- **Python Support**: 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
- **Dependencies**: requests
- **Package Structure**: Clean module organization under `src/qubesync/`
- **Testing**: pytest with comprehensive coverage
- **Distribution**: Ready for PyPI with proper `pyproject.toml`

### Documentation
- Comprehensive README with examples
- Getting Started guide
- RequestBuilder-specific documentation
- Inline code documentation with examples
- Complete API reference

[0.1.0]: https://github.com/qubeintegrations/qube_sync_py/releases/tag/v0.1.0
