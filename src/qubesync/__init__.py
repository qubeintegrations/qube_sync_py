"""
QubeSync - Python library for QuickBooks integration via QubeSync API

This package provides:
- Client: the v2 API client (APIError for a refused request)
- QubeSync: Main API client for interacting with QubeSync service
- RequestBuilder: DSL for building QuickBooks XML requests
- webhooks: verify a webhook delivery and parse it into a typed event
- Exception classes for error handling

Usage:
    from qubesync import Client

    client = Client(api_key=os.environ["QUBE_API_KEY"])
    connection = client.create_connection(webhook_url="https://your-app.com/webhooks/qube")

v1 (legacy):
    from qubesync import QubeSync, RequestBuilder
    
    # API operations
    connection = QubeSync.create_connection(options)
    
    # Request building
    request = RequestBuilder(version="16.0")
    with request as r:
        with r.QBXML() as qbxml:
            # ... build request
"""

from ._version import __version__

# The v2 API client
from .v2 import Client, APIError

# v1 (legacy)
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

# Public API
__all__ = [
    # v2 API client
    "Client",
    "APIError",

    # v1 API client (legacy)
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
