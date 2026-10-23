"""
QubeSync - Python library for QuickBooks integration via QubeSync API

This package provides:
- QubeSync: Main API client for interacting with QubeSync service
- RequestBuilder: DSL for building QuickBooks XML requests
- webhooks: verify a webhook delivery and parse it into a typed event
- Exception classes for error handling

Usage:
    from qubesync import QubeSync, RequestBuilder
    
    # API operations
    connection = QubeSync.create_connection(options)
    
    # Request building
    request = RequestBuilder(version="16.0")
    with request as r:
        with r.QBXML() as qbxml:
            # ... build request
"""

# Import main classes for convenient access
from .client import (
    QubeSync,
    QubeSyncError,
    StaleWebhookError, 
    InvalidWebhookSignatureError,
    ConfigError
)

from .request_builder import (
    RequestBuilder,
    RequestElement,
    FluentRequestBuilder
)

from . import webhooks
from .webhooks import SignatureError

# Version info
__version__ = "0.2.0"

# Public API
__all__ = [
    # Main API client
    "QubeSync",
    
    # Request builders
    "RequestBuilder", 
    "RequestElement",
    "FluentRequestBuilder",
    
    # Webhooks
    "webhooks",
    "SignatureError",

    # Exceptions
    "QubeSyncError",
    "StaleWebhookError",
    "InvalidWebhookSignatureError", 
    "ConfigError",
    
    # Version
    "__version__"
]
