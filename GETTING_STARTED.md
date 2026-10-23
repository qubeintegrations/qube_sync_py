# Getting Started with QubeSync Python

## 1. Installation

```bash
pip install qubesync
```

## 2. Set Up Environment Variables

```bash
export QUBE_API_KEY="your_api_key_here"
export QUBE_WEBHOOK_SECRET="your_webhook_secret_here"
```

## 3. Your First QubeSync Request

```python
from qubesync import QubeSync, RequestBuilder

# Create a connection
connection = QubeSync.create_connection({
    "name": "My First Connection"
})

# Build a customer query
request = RequestBuilder(version="16.0")
with request as r:
    with r.QBXML() as qbxml:
        with qbxml.QBXMLMsgsRq(onError='stopOnError') as msgs:
            with msgs.CustomerQueryRq(requestID='first_query') as query:
                query.MaxReturned(10)
                query.IncludeRetElement('Name')

# Queue the request
response = QubeSync.queue_request(connection['id'], {
    'request_json': request.as_json(),
    'webhook_url': 'https://your-app.com/webhook'
})

print(f"✅ Request queued: {response['id']}")
```

## 4. Handle the Response

```python
def webhook_handler(request):
    signature = request.headers.get('X-Qube-Signature')
    body = request.body  # raw bytes, before anything parses them

    webhook_data = QubeSync.verify_and_build_webhook(body, signature)
    print(f"Received QuickBooks data: {webhook_data}")
    
    return {"status": "success"}
```

## 5. Next Steps

- Check out the full [README.md](README.md) for complete documentation
- Explore [examples.py](examples.py) for more usage patterns
- Read about [Request Builder DSL](src/qubesync/README_RequestBuilder.md)

## Common Patterns

### Customer Operations
```python
# Query customers
with msgs.CustomerQueryRq(requestID='customers') as query:
    query.MaxReturned(100)
    query.IncludeRetElement('ListID')
    query.IncludeRetElement('Name')
    query.IncludeRetElement('Email')
```

### Invoice Operations
```python
# Query invoices
with msgs.InvoiceQueryRq(requestID='invoices') as query:
    query.MaxReturned(50)
    query.IncludeRetElement('TxnID')
    query.IncludeRetElement('TxnNumber')
    query.IncludeRetElement('CustomerRef')
    query.IncludeRetElement('BalanceRemaining')
```

### Item Operations
```python
# Query items
with msgs.ItemQueryRq(requestID='items') as query:
    query.MaxReturned(200)
    query.IncludeRetElement('ListID')
    query.IncludeRetElement('Name')
    query.IncludeRetElement('Type')
    query.IncludeRetElement('SalePrice')
```

Happy coding! 🚀
