# QubeSync Test Suite

This directory contains comprehensive tests for the QubeSync Python library.

## Test Coverage

The test suite covers all major functionality of the QubeSync library:

### Configuration & Environment
- ✅ `test_base_url_default` - Default API base URL
- ✅ `test_base_url_custom` - Custom API base URL via environment variable
- ✅ `test_default_headers` - Default HTTP headers
- ✅ `test_api_key_success` - API key retrieval
- ✅ `test_api_key_missing` - API key missing error handling
- ✅ `test_api_secret_success` - Webhook secret retrieval
- ✅ `test_api_secret_missing` - Webhook secret missing error handling

### HTTP Client Functionality
- ✅ `test_connection` - HTTP session creation with authentication
- ✅ `test_get_success` - Successful GET requests
- ✅ `test_get_error` - GET request error handling
- ✅ `test_post_success` - Successful POST requests
- ✅ `test_delete_success` - Successful DELETE requests

### Connection Management
- ✅ `test_create_connection_success` - Creating new connections
- ✅ `test_create_connection_no_id` - Error handling when connection creation fails
- ✅ `test_delete_connection` - Deleting connections
- ✅ `test_get_connection` - Retrieving connection details

### Request Queue Management
- ✅ `test_queue_request_with_json` - Queuing requests with JSON payload
- ✅ `test_queue_request_with_xml` - Queuing requests with XML payload
- ✅ `test_queue_request_missing_request_data` - Error handling for invalid requests
- ✅ `test_get_request` - Retrieving individual queued requests
- ✅ `test_get_requests` - Retrieving all queued requests for a connection
- ✅ `test_delete_request` - Deleting queued requests

### Utility Functions
- ✅ `test_get_qwc` - Getting QuickBooks Web Connector file
- ✅ `test_generate_password_success` - Password generation
- ✅ `test_generate_password_no_password` - Password generation error handling

### Webhook Security
- ✅ `test_extract_signature_meta_valid` - Parsing webhook signature headers
- ✅ `test_extract_signature_meta_missing_timestamp` - Missing timestamp error
- ✅ `test_extract_signature_meta_missing_signature` - Missing signature error
- ✅ `test_extract_signature_meta_with_equals_in_signature` - Signatures containing equals signs
- ✅ `test_sign_payload` - Payload signing functionality
- ✅ `test_verify_and_build_webhook_success` - Successful webhook verification
- ✅ `test_verify_and_build_webhook_stale` - Stale webhook rejection
- ✅ `test_verify_and_build_webhook_invalid_signature` - Invalid signature rejection
- ✅ `test_verify_and_build_webhook_custom_max_age` - Custom age validation

## Running the Tests

### Option 1: Using the Test Runner Script
```bash
# Run all tests with verbose output
python3 run_tests.py --verbose

# Run a specific test
python3 run_tests.py --specific-test test_create_connection

# Show help and list all available tests
python3 run_tests.py --help
```

### Option 2: Direct pytest execution
```bash
# Run all tests
./bin/python -m pytest tests/test_qube_sync.py -v

# Run a specific test class
./bin/python -m pytest tests/test_qube_sync.py::TestQubeSync -v

# Run a specific test method
./bin/python -m pytest tests/test_qube_sync.py::TestQubeSync::test_verify_and_build_webhook_success -v
```

## Environment Variables

The tests require these environment variables to be set:

- `QUBE_API_KEY` - API key for authentication (default: "test_api_key")
- `QUBE_WEBHOOK_SECRET` - Secret for webhook signature verification (default: "supersecret")
- `QUBE_URL` - Custom API base URL (optional, defaults to "https://qubesync.com/api/v1")

These are automatically set by the test runner script for convenience.

## Test Structure

All tests are organized in the `TestQubeSync` class and use pytest fixtures and mocking to isolate functionality:

- **Setup**: Each test method has environment variables properly configured
- **Mocking**: HTTP requests are mocked to avoid external dependencies
- **Assertions**: Comprehensive assertions verify both successful operations and error conditions
- **Cleanup**: Environment variables are restored after tests that modify them

## Coverage Statistics

- **34 tests** covering all public methods
- **100% pass rate**
- **Mocked HTTP requests** for reliable testing
- **Error condition testing** for robust error handling
- **Security testing** for webhook verification

## Dependencies

- `pytest` - Testing framework
- `unittest.mock` - Mocking HTTP requests and external dependencies

The test suite uses the existing virtual environment and installs only necessary testing dependencies.

## The kit's tests on PostgreSQL

The kit's tests run on SQLite by default. With `KIT_PG_URL=postgresql://user:password@host:5432`
they run on PostgreSQL instead, in its `kit_django` and `kit_sqla` databases (create both first),
which the sync status scopes' SQL and the start's row lock need (`test_two_starts_at_once_make_one_run`
runs only there). `psycopg2-binary` is needed.
