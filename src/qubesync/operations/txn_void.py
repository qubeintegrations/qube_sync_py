# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks txn void operations (``client.txn_void``)."""

from typing import Any, Dict, Literal, Optional, TYPE_CHECKING, TypedDict


if TYPE_CHECKING:
    from ..v2 import Client


class _TxnVoidExecuteParamsRequired(TypedDict):
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    txn_id: str
    #: The type of transaction being voided.
    txn_void_type: Literal["ARRefundCreditCard", "Bill", "BillPaymentCheck", "BillPaymentCreditCard", "Charge", "Check", "CreditCardCharge", "CreditCardCredit", "CreditMemo", "Deposit", "InventoryAdjustment", "Invoice", "ItemReceipt", "JournalEntry", "SalesReceipt", "VendorCredit"]


class TxnVoidExecuteParams(_TxnVoidExecuteParamsRequired, total=False):
    """Params for ``txn_void.execute`` (Execute txn void)."""
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class TxnVoid:
    """QuickBooks txn void operations: execute.

    Get it from ``client.txn_void``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def execute(
        self,
        connection_id: str,
        params: Optional[TxnVoidExecuteParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute txn void.

        Queues ``txn_void.execute``: POST /connections/{connection_id}/txn-void, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``TxnVoidExecuteParams``)::

            request_id: str
            txn_id: str (required)
            txn_void_type: Literal[...] (one of 16 values) (required)

        Docs: https://docs.qubesync.com/api-reference/v2/txn-void/execute-txn-void
        """
        return self._client._queue_operation("txn_void.execute", connection_id, params, webhook_url, idempotency_key)
