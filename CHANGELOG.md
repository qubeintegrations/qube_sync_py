# Changelog

All notable changes to the QubeSync Python library will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
