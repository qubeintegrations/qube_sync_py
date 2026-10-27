# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks item sites operations (``client.item_sites``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    CurrencyFilter,
    EntityFilter,
)

if TYPE_CHECKING:
    from ..v2 import Client


class ItemSiteFilter(TypedDict, total=False):
    #: Filters according to the item name or ID. You can use an ItemQuery request to get
    #: information about all the items that are set up in the QuickBooks file. “Items” are line
    #: items used for fast entry on sales and purchase forms. They include services and goods
    #: that a business buys and sells, as well as special items that perform calculations–for
    #: example, subtotal, discount, and sales-tax items.
    item_filter: EntityFilter
    #: Allows you to report on Sites.
    site_filter: CurrencyFilter


class ItemSitesQueryParams(TypedDict, total=False):
    """Params for ``item_sites.query`` (List item sites)."""
    #: Used in filters to select list objects based on whether or not they are currently enabled
    #: for use by QuickBooks. The default value is asActiveOnly, which selects only list objects
    #: that are active.
    active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
    include_ret_element: List[Literal["AssemblyBuildPoint", "EditSequence", "InventorySiteLocationRef", "InventorySiteRef", "ItemInventoryAssemblyRef", "ItemInventoryRef", "ListID", "QuantityOnHand", "QuantityOnPendingTransfers", "QuantityOnPurchaseOrders", "QuantityOnSalesOrders", "QuantityRequiredByPendingBuildTxns", "QuantityToBeBuiltByPendingBuildTxns", "ReorderLevel", "TimeCreated", "TimeModified"]]
    #: Allows you to report on Item Sites.
    #:
    #: Choose at most one of: `list_id`, or the set (`item_site_filter`, `item_type_filter`).
    #: Members of a set combine with each other, not with the other choices.
    item_site_filter: ItemSiteFilter
    #: Allows you to report on a specific item type.
    #:
    #: Choose at most one of: `list_id`, or the set (`item_site_filter`, `item_type_filter`).
    #: Members of a set combine with each other, not with the other choices.
    item_type_filter: Literal["AllExceptFixedAsset", "Assembly", "Discount", "FixedAsset", "Inventory", "InventoryAndAssembly", "NonInventory", "OtherCharge", "Payment", "Sales", "SalesTax", "Service"]
    #: Page through every match: QuBe Sync asks QuickBooks for each page in turn and sends each
    #: to your `webhook_url` as it arrives, all with the same `id`. On by default, with pages of
    #: 100 records; send `iterator=true` with `max_returned` for another size. Off when you send
    #: `iterator=false` (every match in one answer) or `max_returned` alone (at most that many,
    #: in one answer).
    iterator: bool
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list family, not across the
    #: company file: customers, vendors, employees and other names share one sequence, every
    #: item type shares another, and each other list has its own.
    #:
    #: Choose at most one of: `list_id`, or the set (`item_site_filter`, `item_type_filter`).
    #: Members of a set combine with each other, not with the other choices.
    list_id: List[str]
    #: Limits the number of objects that a query returns. (To get a count of how many objects
    #: could possibly be returned, use the `meta_data` query attribute.) If you include a
    #: `max_returned` value, it must be at least 1.
    #:
    #: The page size, with `iterator=true`. Sent without `iterator`, or with `iterator=false`,
    #: it's a cap instead: at most this many records come back, in one answer, and QuickBooks
    #: doesn't say whether more matched.
    max_returned: int
    #: Use the `meta_data` attribute to control whether query responses include counts. Options
    #: are NoMetaData (default), MetaDataOnly (count only), and MetaDataAndResponseData (count
    #: plus objects). Counts are approximate and may vary slightly if records are created or
    #: deleted during processing.
    meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class ItemSites:
    """QuickBooks item sites operations: query.

    Get it from ``client.item_sites``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def query(
        self,
        connection_id: str,
        params: Optional[ItemSitesQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List item sites.

        Queues ``item_sites.query``: GET /connections/{connection_id}/item-sites, params in the query string.
        QuickBooks answers in pages: each page comes to ``webhook_url`` as its own webhook.
        Returns the queued request.

        Params (``ItemSitesQueryParams``)::

            active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
            include_ret_element: List[Literal[...] (one of 16 values)]
            item_site_filter: ItemSiteFilter
                item_filter: EntityFilter
                    full_name: List[str]
                    full_name_with_children: str
                    list_id: List[str]
                    list_id_with_children: str
                site_filter: CurrencyFilter
                    full_name: List[str]
                    list_id: List[str]
            item_type_filter: Literal[...] (one of 12 values)
            iterator: bool
            list_id: List[str]
            max_returned: int
            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/item-sites/list-item-sites
        """
        return self._client._queue_operation("item_sites.query", connection_id, params, webhook_url, idempotency_key)
