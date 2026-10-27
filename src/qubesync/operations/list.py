# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks list operations (``client.list``)."""

from typing import Any, Dict, Literal, Optional, TYPE_CHECKING, TypedDict


if TYPE_CHECKING:
    from ..v2 import Client


class _ListDeleteParamsRequired(TypedDict):
    #: The type of list from which a list member is being deleted.
    list_del_type: Literal["Account", "BillingRate", "Class", "Currency", "Customer", "CustomerMsg", "CustomerType", "DateDrivenTerms", "Employee", "InventorySite", "ItemDiscount", "ItemFixedAsset", "ItemGroup", "ItemInventory", "ItemInventoryAssembly", "ItemNonInventory", "ItemOtherCharge", "ItemPayment", "ItemSalesTax", "ItemSalesTaxGroup", "ItemService", "ItemSubtotal", "JobType", "OtherName", "PaymentMethod", "PayrollItemNonWage", "PayrollItemWage", "PriceLevel", "SalesRep", "SalesTaxCode", "ShipMethod", "StandardTerms", "ToDo", "UnitOfMeasureSet", "Vehicle", "Vendor", "VendorType", "WorkersCompCode"]
    #: `list_id` and FullName both identify a list object. QuickBooks assigns `list_id` when the
    #: object is created. `list_id` values are unique within a list family, not across the
    #: company file: customers, vendors, employees and other names share one sequence, every
    #: item type shares another, and each other list has its own.
    list_id: str


class ListDeleteParams(_ListDeleteParamsRequired, total=False):
    """Params for ``list.delete`` (Delete list)."""
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class ListOperations:
    """QuickBooks list operations: delete.

    Get it from ``client.list``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def delete(
        self,
        connection_id: str,
        params: Optional[ListDeleteParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Delete list.

        Queues ``list.delete``: DELETE /connections/{connection_id}/lists, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``ListDeleteParams``)::

            list_del_type: Literal[...] (one of 38 values) (required)
            list_id: str (required)
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/lists/delete-list
        """
        return self._client._queue_operation("list.delete", connection_id, params, webhook_url, idempotency_key)
