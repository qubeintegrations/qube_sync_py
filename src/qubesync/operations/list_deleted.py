# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks list deleted operations (``client.list_deleted``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    DeletedDateRangeFilter,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _ListDeletedQueryParamsRequired(TypedDict):
    #: The type of list from which a list member is being deleted.
    list_del_type: List[Literal["Account", "BillingRate", "Class", "Currency", "Customer", "CustomerMsg", "CustomerType", "DateDrivenTerms", "Employee", "InventorySite", "ItemDiscount", "ItemFixedAsset", "ItemGroup", "ItemInventory", "ItemInventoryAssembly", "ItemNonInventory", "ItemOtherCharge", "ItemPayment", "ItemSalesTax", "ItemSalesTaxGroup", "ItemService", "ItemSubtotal", "JobType", "OtherName", "PaymentMethod", "PayrollItemNonWage", "PayrollItemWage", "PriceLevel", "SalesRep", "SalesTaxCode", "ShipMethod", "StandardTerms", "ToDo", "UnitOfMeasureSet", "Vehicle", "Vendor", "VendorType", "WorkersCompCode"]]


class ListDeletedQueryParams(_ListDeletedQueryParamsRequired, total=False):
    """Params for ``list_deleted.query`` (List list deleteds)."""
    #: Filters according to delete dates (within the last 90 days).
    deleted_date_range_filter: DeletedDateRangeFilter
    include_ret_element: List[Literal["FullName", "ListDelType", "ListID", "TimeCreated", "TimeDeleted"]]
    #: Use the `meta_data` attribute to control whether query responses include counts. Options
    #: are NoMetaData (default), MetaDataOnly (count only), and MetaDataAndResponseData (count
    #: plus objects). Counts are approximate and may vary slightly if records are created or
    #: deleted during processing.
    meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class ListDeleted:
    """QuickBooks list deleted operations: query.

    Get it from ``client.list_deleted``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def query(
        self,
        connection_id: str,
        params: Optional[ListDeletedQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List list deleteds.

        Queues ``list_deleted.query``: GET /connections/{connection_id}/list-deleteds, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``ListDeletedQueryParams``)::

            deleted_date_range_filter: DeletedDateRangeFilter
                from_deleted_date: str
                to_deleted_date: str
            include_ret_element: List[Literal["FullName", "ListDelType", "ListID", "TimeCreated", "TimeDeleted"]]
            list_del_type: List[Literal[...] (one of 38 values)] (required)
            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/list-deleteds/list-list-deleteds
        """
        return self._client._queue_operation("list_deleted.query", connection_id, params, webhook_url, idempotency_key)
