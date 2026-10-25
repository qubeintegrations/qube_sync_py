# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks txn display operations (``client.txn_display``)."""

from typing import Any, Dict, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    Ref,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _TxnDisplayCreateParamsRequired(TypedDict):
    #: Specifies the type of QuickBooks transaction for which to open an edit form in the
    #: QuickBooks UI. Notice that some transaction types don’t support the entity reference that
    #: “prefills” the form because it would make no sense to do this for certain forms.
    txn_display_add_type: Literal["Bill", "BillPayment", "BuildAssembly", "Charge", "Check", "CreditCardCharge", "CreditCardCredit", "CreditMemo", "Deposit", "Estimate", "InventoryAdjustment", "Invoice", "ItemReceipt", "JournalEntry", "PurchaseOrder", "ReceivePayment", "SalesOrder", "SalesReceipt", "SalesTaxPaymentCheck", "VendorCredit"]


class TxnDisplayCreateParams(_TxnDisplayCreateParamsRequired, total=False):
    """Params for ``txn_display.create`` (Create txn display)."""
    #: A QuickBooks “entity” is a customer, vendor, employee, or person on the QuickBooks “other
    #: names” list. Special cases to note: In a BillToPayQuery message, `entity_ref` refers to
    #: the vendor name. In JournalCreditLine and JournalDebitLine messages for A/R accounts,
    #: `entity_ref` must refer to a customer, or else the transaction won’t be recorded.
    entity_ref: Ref
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class _TxnDisplayUpdateParamsRequired(TypedDict):
    #: The type of QuickBooks transaction to open for modification in the QuickBooks UI.
    #: (`txn_id` specifies the particular transaction.)
    txn_display_mod_type: Literal["Bill", "BillPaymentCheck", "BillPaymentCreditCard", "BuildAssembly", "Charge", "Check", "CreditCardCharge", "CreditCardCredit", "CreditMemo", "Deposit", "Estimate", "InventoryAdjustment", "Invoice", "ItemReceipt", "JournalEntry", "PurchaseOrder", "ReceivePayment", "SalesOrder", "SalesReceipt", "SalesTaxPaymentCheck", "VendorCredit"]
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    txn_id: str


class TxnDisplayUpdateParams(_TxnDisplayUpdateParamsRequired, total=False):
    """Params for ``txn_display.update`` (Update txn display)."""
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class TxnDisplay:
    """QuickBooks txn display operations: create, update.

    Get it from ``client.txn_display``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[TxnDisplayCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create txn display.

        Queues ``txn_display.create``: POST /connections/{connection_id}/txn-displays, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``TxnDisplayCreateParams``)::

            entity_ref: Ref
                full_name: str
                list_id: str
            request_id: str
            txn_display_add_type: Literal[...] (one of 20 values) (required)

        Docs: https://docs.qubesync.com/api-reference/v2/txn-displays/create-txn-display
        """
        return self._client._queue_operation("txn_display.create", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[TxnDisplayUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update txn display.

        Queues ``txn_display.update``: PUT /connections/{connection_id}/txn-displays, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``TxnDisplayUpdateParams``)::

            request_id: str
            txn_display_mod_type: Literal[...] (one of 21 values) (required)
            txn_id: str (required)

        Docs: https://docs.qubesync.com/api-reference/v2/txn-displays/update-txn-display
        """
        return self._client._queue_operation("txn_display.update", connection_id, params, webhook_url, idempotency_key)
