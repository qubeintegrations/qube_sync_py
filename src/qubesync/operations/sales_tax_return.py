# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks sales tax return operations (``client.sales_tax_return``)."""

from typing import Any, Dict, Literal, Optional, TYPE_CHECKING, TypedDict


if TYPE_CHECKING:
    from ..v2 import Client


class SalesTaxReturnQueryParams(TypedDict, total=False):
    """Params for ``sales_tax_return.query`` (List sales tax returns)."""
    #: Use the `meta_data` attribute to control whether query responses include counts. Options
    #: are NoMetaData (default), MetaDataOnly (count only), and MetaDataAndResponseData (count
    #: plus objects). Counts are approximate and may vary slightly if records are created or
    #: deleted during processing.
    meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class SalesTaxReturn:
    """QuickBooks sales tax return operations: query.

    Get it from ``client.sales_tax_return``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def query(
        self,
        connection_id: str,
        params: Optional[SalesTaxReturnQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List sales tax returns.

        Queues ``sales_tax_return.query``: GET /connections/{connection_id}/sales-tax-returns, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``SalesTaxReturnQueryParams``)::

            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/sales-tax-returns/list-sales-tax-returns
        """
        return self._client._queue_operation("sales_tax_return.query", connection_id, params, webhook_url, idempotency_key)
