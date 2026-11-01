# Changelog

All notable changes to the QubeSync Python library will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `RequestEvent.perhaps_applied`: true for a `timed_out` request and for an `error` with
  `error_type` `outcome_unknown`, QuBe Sync's type for a write the Web Connector reported an error
  on mid-request. QuickBooks may have applied either, so look before sending a write again.
  `RequestEvent.error_type` reads `error["error_type"]`.
- A request webhook whose body would be over 1 MB comes with `response_xml` None,
  `response_xml_omitted` true and `links.self`. `RequestEvent.response_xml`, `.response_xml_omitted`,
  `.links` and `.self_link` read them, and `Client.response_xml_for(event)` returns the event's
  `response_xml`, fetching it from `links.self` when it was omitted.
- `Client.get_request(link)` takes a request's URL (such as `links.self`), as `get_run` does.
  `get_request(connection_id, id)` works as before.

## [0.4.0] - 2026-10-27

Adds the integration kit (`qubesync.kit`, with Django, Flask and FastAPI adapters), typed
workflow starts, simulated connections and resending a run's latest event. Nothing existing
changes: the 0.3.0 client and the v1 `QubeSync` class work as they did.

### Added

**Client**
- Typed workflow starts: `qubesync workflows [--drafts] [--check] [--output qube_workflows.py]`
  (a console script, and `python -m qubesync workflows`) fetches your app's workflow input types
  with `QUBE_API_KEY` (and `QUBE_BASE_URL`, with or without `/api/v2`) and writes one module to
  check in: per workflow a namespace (`add_transaction`) with a start method and an input builder
  per branch of its input (`invoice`, `invoice_input`), or `start` and `input`, and a TypedDict
  per input (`AddTransactionInvoiceInput`, `AddTransactionInput`) whose operation bodies are the
  operations' params TypedDicts. A field the workflow sets itself (`set_by_workflow`) is optional
  in that body. `--check` exits 1 when the module is out of date (naming the workflows that
  changed) or the key is refused, and 0 with a warning when QuBe Sync can't be reached. The
  renderer is `qubesync.workflow_types`.
- `Client.workflow_types(include_drafts=False, etag=None)`: `GET /workflows/types`, returning
  `qubesync.v2.NOT_MODIFIED` on a 304.
- `Client.create_connection(webhook_url=, name=None, type=None)`: `type="simulated"` makes a
  connection to a simulated QuickBooks company file, connected as soon as it's made, for trying
  an integration without QuickBooks Desktop.
- `Client.redeliver_run(connection_id, run_id)`: `POST .../workflow-runs/{run_id}/redeliver` has
  QuBe Sync send the run's latest event to your webhook again, for when your endpoint was down
  longer than QuBe Sync's retries. It returns `{run_id, event, revision, webhook_url}`, raises
  `APIError` 409 (`nothing_to_redeliver`) or 429, and isn't retried.
- `Client.search(..., row=None)`: `row` names the row of a question's rows field, for a search
  whose kind depends on that row (the missing-records question's per-record search).
- `qubesync.operations.DIGEST`: the sha256 of the QuickBooks operations manifest this version
  was generated from. `qubesync workflows` warns when QuBe Sync's operations differ from it.

**Integration kit**
- `qubesync.kit`: the Python port of the qube_rails engine, holding the code QuBe Sync's
  integration kit used to generate into every app, so your app keeps only its own operations,
  connection events and configuration. It imports no framework and no ORM.
- Tables of its own: `qube_connections` (an account can have several, one per company file),
  `qube_runs`, `qube_quickbooks_records` and `qube_notifications`. Django gets them as
  `qubesync.django.models` with migrations (`0002_sync_status_indexes` adds the sync status
  indexes); Flask and FastAPI as SQLAlchemy models in `qubesync.kit.sqlalchemy` (its own
  `metadata`, for your Alembic). JSON is kept as text, the same on PostgreSQL, MySQL and SQLite.
  Your own tables need no QuBe Sync columns.
- `Connection`: `owned_by(owner)`, `link(record, kind=, qb_id=, edit_sequence=None, name=None)`,
  `qb_id_for(record, kind=)`, `find_linked(qb_id, kind=None)`, `quickbooks_record(qb_id,
  kind=None)`, `connected()`, `not_checking_in()`, `webhook_url`, `owner`, and
  `adopt_qube_connection()` for a connection whose QuBe Sync id was never saved. QuickBooks ids
  are kept per connection and list family (`family_for`).
- `Run`: `latest_for(record, operation)`, `retry_start()`, `looks_stuck()`, `summary_text`,
  `error_message`, `error_detail`, `open_question`, `ended()`, `failed()`, `cancelled()`,
  `unconfirmed()`, `record`, `webhook_url`. Every ending is kept on the run.
- `Operation`: `start(record, connection)`, `retry_start(run)`, `find_record`, `input` (typed as
  returning a `Mapping`, so it can return a generated input TypedDict), the handlers
  (`question`, `ended`, `failed`, `notification`), `quickbooks_ref`, `link_references(event,
  fn)`, `answered(token)`, `without_nils`, `log_event`. A start returns the record's run that
  hasn't ended on that connection (`run.reused`) rather than starting another, so a double click
  can't add an invoice twice; an unconfirmed one is sent again with the same reference (the
  Idempotency-Key) and input. No answer leaves a run `starting`; only a 4xx or an input that
  raised marks it failed. Events are checked against the run's reference and connection and
  applied by revision under the run row's lock.
- Onboarding makes realtime connections (the `connection_type` setting, `"realtime"` by default,
  or `"standard"`), since workflows run only on realtime connections. A start QuBe Sync refuses
  as `realtime_required` marks the run failed and raises `qubesync.kit.RealtimeRequired`, whose
  message says how to upgrade.
- `qubesync.kit.MissingReference`, raised from `input` when a reference QuickBooks requires has
  no link and no name, so the start fails before anything is sent.
- `ConnectionEvents`: `connected`, `setup_cancelled`, `stalled` and `resumed`, with
  `connection` and `owner`; an event before the row has its QuBe Sync id adopts the connection
  or raises `NotReady` for a retry.
- `configure(**settings)`: `operations`, `connection_events`, `current_account`,
  `authorize_question` (default: the signed-in account owns the run's connection), `enqueue`,
  `job_attempts` (10), `dedupe` (default `DatabaseDedupe`, the `qube_notifications` table in the
  handler's transaction, or `CacheDedupe`), `db_session` (SQLAlchemy), `api_key`, `base_url`,
  `webhook_secret`, `webhook_url`, `client` and `production`. An unset one raises `NotConfigured`
  naming `quickbooks_desktop/config.py`; `repr` hides the secrets.
- The job, `run(kind, id, body)`, and the default queue: a worker thread that retries a delivery
  whose work raised, after a growing wait, `job_attempts` times.
- Sync status, derived and never stored: `connection.sync_status(record, operation)` returns a
  `qubesync.kit.SyncStatus` (`not_sent`, `sending`, `needs_answer`, `in_quickbooks`, `done`,
  `failed` or `cancelled`, with `qb_id`, `error`, `retry`, `unconfirmed`, `summary_text`, `run`
  and `link`), `SyncStatus.latest(record, operation)`, and the connection's
  `in_quickbooks(query)`, `not_in_quickbooks(query)`, `needing_answer(query, operation)` and
  `sending(query, operation)`, each one `EXISTS` query.
- The routes, in each adapter: `POST quickbooks/connections` (Connect: reuses the account's
  never-connected connection unless `new=1`; with `simulated=1`, outside production, makes a
  simulated connection and redirects back), `POST quickbooks/connections/<id>/onboarding`,
  `POST webhooks/qube/runs/<id>` and `POST webhooks/qube/connections/<id>` (401, 404, 413, 200,
  or 503 when the enqueue fails), `POST qube/questions/runs/<id>` and `GET .../search` (404 when
  refused), `POST qube/runs/<id>/retry_start` and `POST qube/runs/<id>/redeliver`. An answer,
  retry or redelivery that can't go through goes back to the page with why, shown once
  (`.qube-error`); an answer to a question that changed since the page showed it isn't sent.
  A refused webhook's log line names its path and what to check (the webhook secret, the clock,
  or a sender that isn't QuBe Sync).
- An answer QuBe Sync took puts the run back to `running` at once (`Operation.answered(token,
  taken=True)`), rather than waiting for the Web Connector's next poll.
- Disconnect: `DELETE quickbooks/connections/<id>`, and `POST .../<id>/disconnect` for an HTML
  form (`qubesync.kit.disconnect`). QuBe Sync deletes its connection first, then
  `connection.disconnect()` deletes the row with its runs, requests, links and sync marks, after
  `ConnectionEvents.disconnected()`, where your app deletes its own rows that point at it. It's
  refused while a run or request hasn't ended. `{% qube_error %}` (Django) and the `qube_error`
  Jinja global show a route's message on a page without the run status or question.
- Plain v2 requests: `qubesync.kit.Request` (`operation`, `slug`, `params()`, and the handlers
  `answered`, `done`, `failed`, `retrying`, `timed_out`). `Request.queue(record, connection)`
  returns a `QueuedRequest` (one at a time per record, slug and connection; its reference is the
  Idempotency-Key; `retry_queue()`), and their webhooks arrive at
  `POST webhooks/qube/requests/<id>`. Each delivery is taken once by `page_request_id:state`,
  and `done` fires once every page is in.
- Opt-in pruning: the `prune_runs_after` setting (a day or more) and `qubesync.kit.prune_runs()`
  delete ended runs and requests, never within a day of their end; links stay. Sync marks
  (`qube_sync_marks`, `connection.last_synced_at(workflow)`, `Operation.last_synced_at()`) keep
  when each connection's last completed run of a workflow started, so a sync's next `since`
  outlives pruned runs. Django's migration `0003_sync_marks_and_requests` adds these tables;
  with SQLAlchemy, autogenerate an Alembic revision.
- The templates: the question, and the run status, which reads the sync status. The status is a
  few words for a pill ("Sending to QuickBooks", "Needs your answer", "Couldn't sync"...) with
  why below it, "Try sending again" for an unconfirmed start, "Check for updates" for a run that
  looks stuck, and "Waiting for QuickBooks", with why and what to do, while the connection is
  stalled. `qube_sync_status` (a Django tag, and a Flask and FastAPI Jinja global) lets a page
  show its start button only while it makes sense, and `redirect_back` with
  `qubesync.kit.NETWORK_ERRORS` lets your own views, such as a start button's, go back with a
  message the page shows once.
- Styling: the question and run status templates render small pieces (`qubesync/question/*`,
  `qubesync/run_status/*`, `qubesync/error.html`, the same paths in Django and Jinja), each from
  a view-model (`QuestionView`, `ChoiceView`, `FieldView`, `RowsView`, `RowView`, `CellView`,
  `RunStatusView`); your app replaces a piece by putting its own at that path. The `ui_classes`
  setting adds your CSS framework's classes by piece. `{% qube_assets %}` / `qube_assets()`
  writes the behaviour script (`qubesync/question.js`) and, opt-in, the stylesheet
  (`qubesync/qubesync.css`, themed by `--qube-*` variables) into your layout.
- A question's choices show by kind: suggested records as option rows ending "Use this one", a
  form per section with the one filled button, and the exits in a footer. A rows field (the
  missing-records question) is a block per record: its choice as a segmented control, only the
  fields that choice needs, and "Set all to" and "Use for all N". It never scrolls sideways. A
  fixed list shows as a select.
- Wording: everything the screens say comes from `qubesync.kit.MESSAGES` (English, never naming
  QuBe Sync), reworded by the `messages` setting and read with `qubesync.kit.t`.
- The storyboard: `GET qube/storyboard` and `qube/storyboard/<screen>` show every screen from
  sample data in your layout, with each screen's override files. Its searches answer from the
  samples and nothing is sent. On by default in development, behind your app's sign-in.
- `qubesync.django` (extra `django`): an installed app with the models and migrations,
  `qubesync.django.urls`, the templates and `{% load qubesync %}` (`{% qube_question %}`,
  `{% qube_run_status %}`, `{% qube_sync_status %}`).
- `qubesync.flask` (extra `flask`): `blueprints()` / `init_app()`, the Jinja templates and
  globals.
- `qubesync.fastapi` (extra `fastapi`): `routers()` / `router()`, `add_templates`,
  `question_html` and `run_status_html`.

### Changed
- The operation docstrings now say a QuickBooks `list_id` is unique within a list family, not
  across the company file: customers, vendors, employees and other names share one sequence,
  every item type shares another, and each other list has its own. Key stored ids by connection
  and record kind, never by `list_id` alone.

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
