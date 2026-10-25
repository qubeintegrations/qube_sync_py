# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks txn deleted operations (``client.txn_deleted``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    DeletedDateRangeFilter,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _TxnDeletedQueryParamsRequired(TypedDict):
    #: The type of transaction to be deleted.
    txn_del_type: List[Literal["ARRefundCreditCard", "Bill", "BillPaymentCheck", "BillPaymentCreditCard", "BuildAssembly", "Charge", "Check", "CreditCardCharge", "CreditCardCredit", "CreditMemo", "Deposit", "Estimate", "InventoryAdjustment", "Invoice", "ItemReceipt", "JournalEntry", "PurchaseOrder", "ReceivePayment", "SalesOrder", "SalesReceipt", "SalesTaxPaymentCheck", "TimeTracking", "TransferInventory", "VehicleMileage", "VendorCredit"]]


class TxnDeletedQueryParams(_TxnDeletedQueryParamsRequired, total=False):
    """Params for ``txn_deleted.query`` (List txn deleteds)."""
    #: Filters according to delete dates (within the last 90 days).
    deleted_date_range_filter: DeletedDateRangeFilter
    include_ret_element: List[Literal["RefNumber", "TimeCreated", "TimeDeleted", "TxnDelType", "TxnID"]]
    #: Use the `meta_data` attribute to control whether query responses include counts. Options
    #: are NoMetaData (default), MetaDataOnly (count only), and MetaDataAndResponseData (count
    #: plus objects). Counts are approximate and may vary slightly if records are created or
    #: deleted during processing.
    meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class TxnDeleted:
    """QuickBooks txn deleted operations: query.

    Get it from ``client.txn_deleted``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def query(
        self,
        connection_id: str,
        params: Optional[TxnDeletedQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List txn deleteds.

        Queues ``txn_deleted.query``: GET /connections/{connection_id}/txn-deleteds, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``TxnDeletedQueryParams``)::

            deleted_date_range_filter: DeletedDateRangeFilter
                from_deleted_date: str
                to_deleted_date: str
            include_ret_element: List[Literal["RefNumber", "TimeCreated", "TimeDeleted", "TxnDelType", "TxnID"]]
            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            request_id: str
            txn_del_type: List[Literal[...] (one of 25 values)] (required)

        Docs: https://docs.qubesync.com/api-reference/v2/txn-deleteds/list-txn-deleteds
        """
        return self._client._queue_operation("txn_deleted.query", connection_id, params, webhook_url, idempotency_key)
