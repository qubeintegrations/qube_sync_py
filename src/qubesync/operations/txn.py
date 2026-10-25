# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks txn operations (``client.txn``)."""

from typing import Any, Dict, Literal, Optional, TYPE_CHECKING, TypedDict


if TYPE_CHECKING:
    from ..v2 import Client


class _TxnDeleteParamsRequired(TypedDict):
    #: The type of transaction to be deleted.
    txn_del_type: Literal["ARRefundCreditCard", "Bill", "BillPaymentCheck", "BillPaymentCreditCard", "BuildAssembly", "Charge", "Check", "CreditCardCharge", "CreditCardCredit", "CreditMemo", "Deposit", "Estimate", "InventoryAdjustment", "Invoice", "ItemReceipt", "JournalEntry", "PurchaseOrder", "ReceivePayment", "SalesOrder", "SalesReceipt", "SalesTaxPaymentCheck", "TimeTracking", "TransferInventory", "VehicleMileage", "VendorCredit"]
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    txn_id: str


class TxnDeleteParams(_TxnDeleteParamsRequired, total=False):
    """Params for ``txn.delete`` (Delete txn)."""
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class Txn:
    """QuickBooks txn operations: delete.

    Get it from ``client.txn``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def delete(
        self,
        connection_id: str,
        params: Optional[TxnDeleteParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Delete txn.

        Queues ``txn.delete``: DELETE /connections/{connection_id}/txns, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``TxnDeleteParams``)::

            request_id: str
            txn_del_type: Literal[...] (one of 25 values) (required)
            txn_id: str (required)

        Docs: https://docs.qubesync.com/api-reference/v2/txns/delete-txn
        """
        return self._client._queue_operation("txn.delete", connection_id, params, webhook_url, idempotency_key)
