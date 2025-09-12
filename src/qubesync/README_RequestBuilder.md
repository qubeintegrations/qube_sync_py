# RequestBuilder - Python DSL for QuickBooks XML Requests

A Python Domain Specific Language (DSL) for building QuickBooks XML requests that can be serialized to JSON format for API consumption. This library provides a fluent, Ruby-like interface for constructing complex QuickBooks requests.

## Features

- ✅ **Context manager support** - Pythonic with-statement syntax  
- ✅ **Method chaining** - Fluent interface for streamlined building
- ✅ **Flat DSL syntax** - Simple and intuitive
- ✅ **Nested structures** - Full support for complex XML hierarchies
- ✅ **Python reserved word handling** - Use trailing underscore for `class_`, `for_`, etc.
- ✅ **JSON serialization** - Direct conversion to QubeSync-compatible format
- ✅ **Multiple syntax styles** - Choose the style that fits your needs

## Installation

The RequestBuilder is included in the QubeSync Python library. Make sure you have the src directory in your Python path:

```python
import sys
sys.path.insert(0, 'src')
from request_builder import QubeSync
```

## Basic Usage

### Context Manager Style (Recommended for Python)

```python
from request_builder import QubeSync

request = QubeSync.RequestBuilder(version="16.0")
with request as r:
    with r.QBXML() as qbxml:
        with qbxml.QBXMLMsgsRq(onError='stopOnError') as msgs:
            with msgs.CustomerQueryRq(requestID='test123', iterator='Start') as query:
                query.MaxReturned(20)
                query.IncludeRetElement('ListID')
                query.IncludeRetElement('Name')
                query.IncludeRetElement('FullName')

json_data = request.as_json()
```

### Ruby-like Style

```python
from request_builder import QubeSync

request = QubeSync.RequestBuilder(version="16.0")
qbxml = request.QBXML()
msgs = qbxml.QBXMLMsgsRq(onError='stopOnError')
query = msgs.CustomerQueryRq(requestID='test123', iterator='Start')
query.MaxReturned(20)
query.IncludeRetElement('ListID')
query.IncludeRetElement('Name')
query.IncludeRetElement('FullName')

json_data = request.as_json()
```

### Fluent Chaining Style

```python
from request_builder import QubeSync

request = QubeSync.FluentRequestBuilder(version="16.0")
request.QBXML().QBXMLMsgsRq(onError='stopOnError').CustomerQueryRq(
    requestID='test123', iterator='Start'
).add_children([
    ('MaxReturned', 20),
    ('IncludeRetElement', 'ListID'),
    ('IncludeRetElement', 'Name'),
    ('IncludeRetElement', 'FullName')
])

json_data = request.as_json()
```

## Output Format

All styles produce the same JSON structure:

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
              "attributes": {"requestID": "test123", "iterator": "Start"},
              "children": [
                {"name": "MaxReturned", "text": 20},
                {"name": "IncludeRetElement", "text": "ListID"},
                {"name": "IncludeRetElement", "text": "Name"},
                {"name": "IncludeRetElement", "text": "FullName"}
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

## Advanced Examples

### Complex Nested Structure

```python
request = QubeSync.RequestBuilder(version="16.0")
with request as r:
    with r.QBXML() as qbxml:
        with qbxml.QBXMLMsgsRq(onError='stopOnError') as msgs:
            with msgs.InvoiceAddRq(requestID='invoice_001') as add_req:
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

### Date Range Filters

```python
request = QubeSync.RequestBuilder(version="16.0")
with request as r:
    with r.QBXML() as qbxml:
        with qbxml.QBXMLMsgsRq(onError='continueOnError') as msgs:
            with msgs.ItemQueryRq(requestID='item_query') as query:
                with query.ModifiedDateRangeFilter() as date_filter:
                    date_filter.FromModifiedDate('2024-01-01T00:00:00')
                    date_filter.ToModifiedDate('2024-12-31T23:59:59')
                query.MaxReturned(100)
```

### Python Reserved Words

Use trailing underscores for Python reserved words:

```python
request = QubeSync.RequestBuilder(version="16.0")
element = request.TestElement(class_='test-class', for_='test-for', if_='active')
# Produces: {"name": "TestElement", "attributes": {"class": "test-class", "for": "test-for", "if": "active"}}
```

## Integration with QubeSync

The RequestBuilder integrates seamlessly with QubeSync:

```python
from request_builder import QubeSync
# from qubesync import QubeSync as QubeSyncAPI  # Uncomment when using QubeSync

# Build the request
request = QubeSync.RequestBuilder(version="16.0")
with request as r:
    with r.QBXML() as qbxml:
        with qbxml.QBXMLMsgsRq(onError='stopOnError') as msgs:
            with msgs.CustomerQueryRq(requestID='customer_sync', iterator='Start') as query:
                query.MaxReturned(50)
                query.IncludeRetElement('ListID')
                query.IncludeRetElement('Name')

# Prepare for QubeSync
request_data = {
    'request_json': request.as_json(),
    'webhook_url': 'https://your-app.com/webhooks/customer_query'
}

# Queue the request
# response = QubeSyncAPI.queue_request(connection_id, request_data)
```

## Common QuickBooks Request Types

### Customer Query
```python
with msgs.CustomerQueryRq(requestID='customers', iterator='Start') as query:
    query.MaxReturned(100)
    query.IncludeRetElement('ListID')
    query.IncludeRetElement('Name')
    query.IncludeRetElement('FullName')
    query.IncludeRetElement('CompanyName')
    query.IncludeRetElement('Email')
    query.IncludeRetElement('Phone')
```

### Invoice Query
```python
with msgs.InvoiceQueryRq(requestID='invoices', iterator='Start') as query:
    query.MaxReturned(50)
    query.IncludeRetElement('TxnID')
    query.IncludeRetElement('TxnNumber')
    query.IncludeRetElement('CustomerRef')
    query.IncludeRetElement('TxnDate')
    query.IncludeRetElement('DueDate')
    query.IncludeRetElement('Subtotal')
    query.IncludeRetElement('BalanceRemaining')
```

### Item Query
```python
with msgs.ItemQueryRq(requestID='items') as query:
    query.MaxReturned(200)
    query.IncludeRetElement('ListID')
    query.IncludeRetElement('Name')
    query.IncludeRetElement('FullName')
    query.IncludeRetElement('Type')
    query.IncludeRetElement('SalePrice')
    query.IncludeRetElement('QtyOnHand')
```

## API Reference

### QubeSync.RequestBuilder

- **`__init__(version="16.0")`** - Create a new request builder
- **`as_json()`** - Convert to JSON format
- **`as_dict()`** - Alias for `as_json()`

### QubeSync.RequestElement

- **`__init__(name, attributes=None, text=None, parent=None)`** - Create an element
- **`as_dict()`** - Convert element to dictionary

### QubeSync.FluentRequestBuilder

- **`add_children(children_data)`** - Add multiple children at once
- **`parent()`** - Move back to parent element  
- **`root()`** - Return to root level

## Testing

Run the comprehensive test suite:

```bash
# All tests
python3 run_tests.py --verbose

# RequestBuilder tests only
python3 run_tests.py --request-builder-only --verbose

# Direct pytest
./bin/python -m pytest tests/test_request_builder.py -v
```

## Examples

See `examples.py` for comprehensive usage examples:

```bash
python3 examples.py
```

## Original Ruby Inspiration

This Python implementation is based on the Ruby QubeSync RequestBuilder:

```ruby
# Ruby version
request = QubeSync::RequestBuilder.new(version: "16.0") do |r|
  r.QBXML {
    r.QBXMLMsgsRq('onError' => 'stopOnError') {
      r.CustomerQueryRq('requestID' => 'test123', 'iterator' => 'Start') {
        r.MaxReturned 20
        r.IncludeRetElement 'ListID'
        r.IncludeRetElement 'Name'
      }
    }
  }
end
```

The Python version provides multiple syntax options to accommodate different coding styles while maintaining the same powerful DSL capabilities.
