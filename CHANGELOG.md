# Changelog

All notable changes to the QubeSync Python library will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2026-10-25

### Added
- `qubesync.Client`, a client for the v2 API (`/api/v2`): `Client(api_key, base_url=..., open_timeout=5,
  read_timeout=30, max_retries=2)`. It never reads the environment. Methods for connections
  (`create_connection`, `get_connection`, `list_connections`, `update_connection`,
  `delete_connection`, `regenerate_onboarding`, `set_password`, `get_qwc`), workflow runs
  (`start_run`, `get_run`, `list_runs`, `cancel_run`, `run_events`), questions (`answer`,
  `search`), queued requests (`queue`, `queue_qbxml`, `get_request`, `request_pages`,
  `list_requests`, `iter_requests`, `discard_request`) and `request` for anything else. Each
  returns the response's `data` as plain dicts and lists.
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
