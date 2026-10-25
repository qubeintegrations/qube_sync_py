# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks sales tax return line operations (``client.sales_tax_return_line``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    Ref,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _SalesTaxReturnLineQueryParamsRequired(TypedDict):
    tax_agency_vendor_ref: List[Ref]


class SalesTaxReturnLineQueryParams(_SalesTaxReturnLineQueryParamsRequired, total=False):
    """Params for ``sales_tax_return_line.query`` (List sales tax return lines)."""
    #: Use the `meta_data` attribute to control whether query responses include counts. Options
    #: are NoMetaData (default), MetaDataOnly (count only), and MetaDataAndResponseData (count
    #: plus objects). Counts are approximate and may vary slightly if records are created or
    #: deleted during processing.
    meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class SalesTaxReturnLine:
    """QuickBooks sales tax return line operations: query.

    Get it from ``client.sales_tax_return_line``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def query(
        self,
        connection_id: str,
        params: Optional[SalesTaxReturnLineQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List sales tax return lines.

        Queues ``sales_tax_return_line.query``: GET /connections/{connection_id}/sales-tax-return-lines, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``SalesTaxReturnLineQueryParams``)::

            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            request_id: str
            tax_agency_vendor_ref: List[Ref] (required)
                full_name: str
                list_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/sales-tax-return-lines/list-sales-tax-return-lines
        """
        return self._client._queue_operation("sales_tax_return_line.query", connection_id, params, webhook_url, idempotency_key)
