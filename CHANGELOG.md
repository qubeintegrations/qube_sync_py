# Changelog

All notable changes to the QubeSync Python library will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
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
