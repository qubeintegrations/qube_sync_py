#!/usr/bin/env python3
"""
RequestBuilder Usage Examples

This file demonstrates various ways to use the RequestBuilder DSL
to create QuickBooks XML requests in JSON format.
"""

import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from qubesync import QubeSync, RequestBuilder, FluentRequestBuilder
import json


def example_new_module_usage():
    print("=== New Module Usage ===")
    
    # Clean imports - no more nested namespaces
    request = RequestBuilder(version="16.0")
    with request as r:
        with r.QBXML() as qbxml:
            with qbxml.QBXMLMsgsRq(onError='stopOnError') as msgs:
                with msgs.CustomerQueryRq(requestID='clean_import_example', iterator='Start') as query:
                    query.MaxReturned(30)
                    query.IncludeRetElement('ListID')
                    query.IncludeRetElement('Name')
                    query.IncludeRetElement('CompanyName')
    
    print("Using RequestBuilder (direct import):")
    print(json.dumps(request.as_json(), indent=2))
    
    # Fluent version
    fluent_request = FluentRequestBuilder(version="16.0")
    fluent_request.QBXML().QBXMLMsgsRq(onError='stopOnError').ItemQueryRq(
        requestID='clean_fluent'
    ).add_children([
        ('MaxReturned', 50),
        ('IncludeRetElement', 'ListID'),
        ('IncludeRetElement', 'Name'),
        ('IncludeRetElement', 'Type')
    ])
    
    print("\nUsing FluentRequestBuilder (direct import):")
    print(json.dumps(fluent_request.as_json(), indent=2))
    
    return request.as_json(), fluent_request.as_json()


def example_customer_query():
    """Example: Customer Query Request (Ruby equivalent)"""
    print("=== Customer Query Request ===")
    
    request_id = "customer_query_123"
    max_returned = 50
    
    # Context manager style (most Pythonic)
    request = RequestBuilder(version="16.0")
    with request as r:
        with r.QBXML() as qbxml:
            with qbxml.QBXMLMsgsRq(onError='stopOnError') as msgs:
                with msgs.CustomerQueryRq(requestID=request_id, iterator='Start') as query:
                    query.MaxReturned(max_returned)
                    query.IncludeRetElement('ListID')
                    query.IncludeRetElement('Name')
                    query.IncludeRetElement('FullName')
                    query.IncludeRetElement('IsActive')
                    query.IncludeRetElement('Email')
    
    print(json.dumps(request.as_json(), indent=2))
    return request.as_json()


def example_invoice_query():
    """Example: Invoice Query Request"""
    print("\n=== Invoice Query Request ===")
    
    # Ruby-like style (without context managers)
    request = RequestBuilder(version="16.0")
    qbxml = request.QBXML()
    msgs = qbxml.QBXMLMsgsRq(onError='stopOnError')
    query = msgs.InvoiceQueryRq(requestID='invoice_query_456', iterator='Start')
    query.MaxReturned(25)
    query.IncludeRetElement('TxnID')
    query.IncludeRetElement('TxnNumber')
    query.IncludeRetElement('CustomerRef')
    query.IncludeRetElement('TxnDate')
    query.IncludeRetElement('DueDate')
    query.IncludeRetElement('Subtotal')
    query.IncludeRetElement('AppliedAmount')
    query.IncludeRetElement('BalanceRemaining')
    
    print(json.dumps(request.as_json(), indent=2))
    return request.as_json()


def example_item_query():
    """Example: Item Query Request with filters"""
    print("\n=== Item Query Request with Filters ===")
    
    request = RequestBuilder(version="16.0")
    with request as r:
        with r.QBXML() as qbxml:
            with qbxml.QBXMLMsgsRq(onError='continueOnError') as msgs:
                with msgs.ItemQueryRq(requestID='item_query_789') as query:
                    query.MaxReturned(100)
                    # Date range filter
                    with query.ModifiedDateRangeFilter() as date_filter:
                        date_filter.FromModifiedDate('2024-01-01T00:00:00')
                        date_filter.ToModifiedDate('2024-12-31T23:59:59')
                    # Include elements
                    query.IncludeRetElement('ListID')
                    query.IncludeRetElement('Name')
                    query.IncludeRetElement('FullName')
                    query.IncludeRetElement('Type')
                    query.IncludeRetElement('SalePrice')
                    query.IncludeRetElement('QtyOnHand')
    
    print(json.dumps(request.as_json(), indent=2))
    return request.as_json()


def example_fluent_chaining():
    """Example: Using FluentRequestBuilder for method chaining"""
    print("\n=== Fluent Chaining Style ===")
    
    request = FluentRequestBuilder(version="16.0")
    request.QBXML().QBXMLMsgsRq(onError='stopOnError').CustomerQueryRq(
        requestID='fluent_customer_123', iterator='Start'
    ).add_children([
        ('MaxReturned', 30),
        ('IncludeRetElement', 'ListID'),
        ('IncludeRetElement', 'Name'),
        ('IncludeRetElement', 'CompanyName'),
        ('IncludeRetElement', 'Phone'),
        ('IncludeRetElement', 'Email')
    ])
    
    print(json.dumps(request.as_json(), indent=2))
    return request.as_json()


def example_complex_nested():
    """Example: Complex nested structure"""
    print("\n=== Complex Nested Structure ===")
    
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
                        invoice.BillAddress('123 Main St\\nAnytown, CA 12345')
                        invoice.ShipAddress('123 Main St\\nAnytown, CA 12345')
                        
                        with invoice.InvoiceLineAdd() as line1:
                            with line1.ItemRef() as item_ref:
                                item_ref.ListID('80000002-1234567890')
                            line1.Desc('Professional Services')
                            line1.Quantity(10)
                            line1.Rate(150.00)
                        
                        with invoice.InvoiceLineAdd() as line2:
                            with line2.ItemRef() as item_ref:
                                item_ref.ListID('80000003-1234567890')
                            line2.Desc('Materials')
                            line2.Quantity(5)
                            line2.Rate(25.00)
    
    print(json.dumps(request.as_json(), indent=2))
    return request.as_json()


def example_python_reserved_words():
    """Example: Handling Python reserved words with trailing underscore"""
    print("\n=== Python Reserved Words Handling ===")
    
    request = RequestBuilder(version="16.0")
    with request as r:
        with r.QBXML() as qbxml:
            with qbxml.QBXMLMsgsRq(onError='stopOnError') as msgs:
                # Using trailing underscores for Python reserved words
                with msgs.CustomQueryRq(class_='invoice', for_='reports', if_='active') as query:
                    query.MaxReturned(100)
                    query.IncludeRetElement('ListID')
    
    print(json.dumps(request.as_json(), indent=2))
    return request.as_json()


def demonstrate_integration_with_qubesync():
    """Example: How to use RequestBuilder with QubeSync"""
    print("\n=== Integration with QubeSync ===")
    
    # Build the request using RequestBuilder
    request = RequestBuilder(version="16.0")
    with request as r:
        with r.QBXML() as qbxml:
            with qbxml.QBXMLMsgsRq(onError='stopOnError') as msgs:
                with msgs.CustomerQueryRq(requestID='integration_test', iterator='Start') as query:
                    query.MaxReturned(20)
                    query.IncludeRetElement('ListID')
                    query.IncludeRetElement('Name')
    
    # Convert to format expected by QubeSync
    request_data = {
        'request_json': request.as_json(),
        'webhook_url': 'https://your-app.com/webhooks/customer_query'
    }
    
    print("Request data for QubeSync.queue_request():")
    print(json.dumps(request_data, indent=2))
    
    # This would be used like:
    # connection_id = "your_connection_id"  
    # response = QubeSync.queue_request(connection_id, request_data)
    
    return request_data


if __name__ == "__main__":
    print("RequestBuilder Usage Examples")
    print("=" * 50)
    
    # Run new module examples first
    example_new_module_usage()
    
    # Run all original examples
    example_customer_query()
    example_invoice_query()
    example_item_query()
    example_fluent_chaining()
    example_complex_nested()
    example_python_reserved_words()
    demonstrate_integration_with_qubesync()
    
    print("\n" + "=" * 50)
    print("All examples completed successfully!")
