# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks sales tax payable operations (``client.sales_tax_payable``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict


if TYPE_CHECKING:
    from ..v2 import Client


class SalesTaxPayableQueryParams(TypedDict, total=False):
    """Params for ``sales_tax_payable.query`` (List sales tax payables)."""
    #: The date when the exchange rate was last changed.
    as_of_date: str
    include_ret_element: List[Literal["Amount", "PayeeEntityRef", "SalesTaxPayableLineRet"]]
    #: Use the `meta_data` attribute to control whether query responses include counts. Options
    #: are NoMetaData (default), MetaDataOnly (count only), and MetaDataAndResponseData (count
    #: plus objects). Counts are approximate and may vary slightly if records are created or
    #: deleted during processing.
    meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class SalesTaxPayable:
    """QuickBooks sales tax payable operations: query.

    Get it from ``client.sales_tax_payable``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def query(
        self,
        connection_id: str,
        params: Optional[SalesTaxPayableQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List sales tax payables.

        Queues ``sales_tax_payable.query``: GET /connections/{connection_id}/sales-tax-payables, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``SalesTaxPayableQueryParams``)::

            as_of_date: str
            include_ret_element: List[Literal["Amount", "PayeeEntityRef", "SalesTaxPayableLineRet"]]
            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/sales-tax-payables/list-sales-tax-payables
        """
        return self._client._queue_operation("sales_tax_payable.query", connection_id, params, webhook_url, idempotency_key)
