# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks item inventory operations (``client.item_inventory``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    EntityFilter,
    ItemDiscountBarCode,
    NameFilter,
    NameRangeFilter,
    Ref,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _ItemInventoryCreateParamsRequired(TypedDict):
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because `full_name` remains distinct.
    name: str


class ItemInventoryCreateParams(_ItemInventoryCreateParamsRequired, total=False):
    """Params for ``item_inventory.create`` (Create item inventory)."""
    #: Refers to the account QuickBooks uses to track the current value of the company’s
    #: inventory. (The AccountType of this account will be FixedAsset, OtherAsset, or
    #: OtherCurrentAsset.) In a request, if an `asset_account_ref` aggregate includes both
    #: `full_name` and `list_id`, `full_name` will be ignored.
    asset_account_ref: Ref
    #: Barcode reference information.
    bar_code: ItemDiscountBarCode
    #: Use classes to categorize transactions (for example, by department, location, or work
    #: type). Class tracking is off by default in QuickBooks. A `class_ref` points to one class;
    #: if both `full_name` and `list_id` are provided, `full_name` is ignored. In InvoiceAdd, a
    #: header-level `class_ref` is applied to line items unless you override or clear it on
    #: individual lines.
    class_ref: Ref
    #: Refers to the account that QuickBooks uses to track the original cost of goods that are
    #: eventually sold. (The AccountType of this account will be CostOfGoodsSold.) In a request,
    #: if a `cogs_account_ref` aggregate includes both `full_name` and `list_id`, `full_name`
    #: will be ignored.
    cogs_account_ref: Ref
    #: Allows for the attachment of a user defined GUID value.
    external_guid: str
    include_ret_element: List[Literal["AssetAccountRef", "AverageCost", "BarCodeValue", "COGSAccountRef", "ClassRef", "DataExtRet", "EditSequence", "ExternalGUID", "FullName", "IncomeAccountRef", "IsActive", "IsTaxIncluded", "ListID", "ManufacturerPartNumber", "Max", "Name", "OwnerID", "ParentRef", "PrefVendorRef", "PurchaseCost", "PurchaseDesc", "PurchaseTaxCodeRef", "QuantityOnHand", "QuantityOnOrder", "QuantityOnSalesOrder", "ReorderPoint", "SalesDesc", "SalesPrice", "SalesTaxCodeRef", "Sublevel", "TimeCreated", "TimeModified", "TxnID", "TxnNumber", "UnitOfMeasureSetRef"]]
    #: Refers to an income account. If an `income_account_ref` aggregate includes both
    #: `full_name` and `list_id`, `full_name` will be ignored.
    income_account_ref: Ref
    #: The date when an item was converted into an inventory item from some other type of item.
    inventory_date: str
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: For future use with international versions of QuickBooks.
    is_tax_included: bool
    #: The part number used by the manufacturer of the item.
    manufacturer_part_number: str
    #: Maximum number of items in inventory.
    max: float
    #: A reference to the list object that is one level above this one. For example, an
    #: inventory item with the `full_name` of GermanCars:Mercedes-Benz:CL500I99AA might have a
    #: parent object with the `full_name` of GermanCars:Mercedes-Benz. In a request, if a
    #: `parent_ref` aggregate includes both `full_name` and `list_id`, `full_name` will be
    #: ignored.
    parent_ref: Ref
    #: The preferred vendor for this item. If a `pref_vendor_ref` aggregate includes both
    #: `full_name` and `list_id`, `full_name` will be ignored.
    pref_vendor_ref: Ref
    #: Amount that the QuickBooks user expects to pay when ordering or buying this item, or the
    #: amount that was actually paid for this item.
    purchase_cost: float
    #: Appears in the Description column of checks, bills, credit card charges, and item
    #: receipts when this item is reordered.
    purchase_desc: str
    #: Account used for taxes on purchases in CA or UK.
    purchase_tax_code_ref: Ref
    #: The number of these items in inventory. `quantity_on_hand` times `average_cost` is
    #: `total_value` in an inventory item list. To change the `quantity_on_hand` for an item,
    #: you would have to use InventoryAdjustmentAdd not an ItemInventoryMod.
    quantity_on_hand: float
    #: Quantity at which QuickBooks will remind the user to reorder this inventory item.
    reorder_point: float
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: Appears in the Description column of a sales form when the QuickBooks user sells this
    #: item. For a fixed asset, describes the sale of the asset (for accounting purposes).
    sales_desc: str
    #: Price charged for this item.
    sales_price: float
    #: `sales_tax_code_ref` points to the sales-tax code used for an item or customer context.
    #: QuickBooks includes default TAX and NON codes, and a code can be deleted only when
    #: nothing references it. If sales tax is disabled, QuickBooks assigns the default
    #: non-taxable code. If both `full_name` and `list_id` are provided in `sales_tax_code_ref`,
    #: `full_name` is ignored.
    sales_tax_code_ref: Ref
    #: The total value of this inventory. If `total_value` is included, `quantity_on_hand` must
    #: also be included and must be greater than zero. If both `quantity_on_hand` and
    #: `purchase_cost` are included, then `total_value` will be set to `quantity_on_hand` times
    #: `purchase_cost`, regardless of what `total_value` is explicitly set to.
    total_value: float
    #: The unit of measure set consists of a base unit and 0-n related units.
    unit_of_measure_set_ref: Ref


class ItemInventoryQueryParams(TypedDict, total=False):
    """Params for ``item_inventory.query`` (List item inventories)."""
    #: Used in filters to select list objects based on whether or not they are currently enabled
    #: for use by QuickBooks. The default value is asActiveOnly, which selects only list objects
    #: that are active.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
    #: Filters according to the object’s class.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    class_filter: EntityFilter
    #: Filters results to objects modified on or after this timestamp. QuickBooks Desktop
    #: accepts 1970-01-01 through 2038-01-19T03:14:07. If only a date is provided, time defaults
    #: to 00:00:00.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    from_modified_date: str
    #: `full_name` (along with `list_id`) is a way to identify a list object. The `full_name` is
    #: the name prefixed by the names of each ancestor, for example Jones:Kitchen:Cabinets.
    #: `full_name` values aren’t case-sensitive.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    full_name: List[str]
    include_ret_element: List[Literal["AssetAccountRef", "AverageCost", "BarCodeValue", "COGSAccountRef", "ClassRef", "DataExtRet", "EditSequence", "ExternalGUID", "FullName", "IncomeAccountRef", "IsActive", "IsTaxIncluded", "ListID", "ManufacturerPartNumber", "Max", "Name", "ParentRef", "PrefVendorRef", "PurchaseCost", "PurchaseDesc", "PurchaseTaxCodeRef", "QuantityOnHand", "QuantityOnOrder", "QuantityOnSalesOrder", "ReorderPoint", "SalesDesc", "SalesPrice", "SalesTaxCodeRef", "Sublevel", "TimeCreated", "TimeModified", "UnitOfMeasureSetRef"]]
    #: Page through every match: QuBe Sync asks QuickBooks for each page in turn and sends each
    #: to your `webhook_url` as it arrives, all with the same `id`. On by default, with pages of
    #: 100 records; send `iterator=true` with `max_returned` for another size. Off when you send
    #: `iterator=false` (every match in one answer) or `max_returned` alone (at most that many,
    #: in one answer). It pages a filtered query only: with `full_name` or `list_id` every match
    #: comes back in one answer, so leave `iterator` out.
    iterator: bool
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list type, not globally
    #: across all lists. If both `full_name` and `list_id` are supplied in a request, QuickBooks
    #: uses `list_id` and ignores `full_name`.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    list_id: List[str]
    #: Limits the number of objects that a query returns. (To get a count of how many objects
    #: could possibly be returned, use the `meta_data` query attribute.) If you include a
    #: `max_returned` value, it must be at least 1.
    #:
    #: The page size, with `iterator=true`. Sent without `iterator`, or with `iterator=false`,
    #: it's a cap instead: at most this many records come back, in one answer, and QuickBooks
    #: doesn't say whether more matched.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    max_returned: int
    #: Use the `meta_data` attribute to control whether query responses include counts. Options
    #: are NoMetaData (default), MetaDataOnly (count only), and MetaDataAndResponseData (count
    #: plus objects). Counts are approximate and may vary slightly if records are created or
    #: deleted during processing.
    meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
    #: Filters according to the object’s Name.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    name_filter: NameFilter
    #: Filters according to the object’s Name.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    name_range_filter: NameRangeFilter
    #: `owner_id` identifies who owns the data extension. Use 0 for QuickBooks custom fields
    #: that appear in the UI, or use a GUID for private extensions owned by an app. Keep private
    #: GUIDs confidential unless you intentionally share extensions across apps. If you do share
    #: them, both apps must use the same `owner_id` and `data_ext_name`, because that pair
    #: uniquely identifies the extension.
    owner_id: List[str]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: Filters results to objects modified on or before this timestamp. QuickBooks Desktop
    #: accepts 1970-01-01 through 2038-01-19T03:14:07. If only a date is provided, time defaults
    #: to end-of-day (23:59:59).
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    to_modified_date: str


class _ItemInventoryUpdateParamsRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list type, not globally
    #: across all lists. If both `full_name` and `list_id` are supplied in a request, QuickBooks
    #: uses `list_id` and ignores `full_name`.
    list_id: str


class ItemInventoryUpdateParams(_ItemInventoryUpdateParamsRequired, total=False):
    """Params for ``item_inventory.update`` (Update item inventory)."""
    #: Effectively suppresses the UI prompt that is displayed upon a COGS account change when
    #: existing transactions use the account.
    apply_cogs_account_ref_to_existing_txns: bool
    #: Used to support changing the AccountRef in the Mod request. When you do this, the
    #: QuickBooks UI normally displays a prompt asking whether the change should apply to
    #: existing transactions or not. Specifying False basically dismisses this with a “No”
    #: answer; specifying True dismisses it with a “Yes” answer and then changes the existing
    #: transactions that use the item with that AccountRef.
    apply_income_account_ref_to_existing_txns: bool
    #: Refers to the account QuickBooks uses to track the current value of the company’s
    #: inventory. (The AccountType of this account will be FixedAsset, OtherAsset, or
    #: OtherCurrentAsset.) In a request, if an `asset_account_ref` aggregate includes both
    #: `full_name` and `list_id`, `full_name` will be ignored.
    asset_account_ref: Ref
    #: Barcode reference information.
    bar_code: ItemDiscountBarCode
    #: Use classes to categorize transactions (for example, by department, location, or work
    #: type). Class tracking is off by default in QuickBooks. A `class_ref` points to one class;
    #: if both `full_name` and `list_id` are provided, `full_name` is ignored. In InvoiceAdd, a
    #: header-level `class_ref` is applied to line items unless you override or clear it on
    #: individual lines.
    class_ref: Ref
    #: Refers to the account that QuickBooks uses to track the original cost of goods that are
    #: eventually sold. (The AccountType of this account will be CostOfGoodsSold.) In a request,
    #: if a `cogs_account_ref` aggregate includes both `full_name` and `list_id`, `full_name`
    #: will be ignored.
    cogs_account_ref: Ref
    #: By Default `force_uom_change` is false. However, in item Mod requests, you need to set
    #: the `force_uom_change` field to True if you are changing the UOM set and the base unit of
    #: the new set doesn’t match the base unit of the UOM set currently assigned to the item.
    #: This does the same thing as the user accepting the warning prompt in the UI.
    force_uom_change: bool
    include_ret_element: List[Literal["AssetAccountRef", "AverageCost", "BarCodeValue", "COGSAccountRef", "ClassRef", "DataExtRet", "EditSequence", "ExternalGUID", "FullName", "IncomeAccountRef", "IsActive", "IsTaxIncluded", "ListID", "ManufacturerPartNumber", "Max", "Name", "OwnerID", "ParentRef", "PrefVendorRef", "PurchaseCost", "PurchaseDesc", "PurchaseTaxCodeRef", "QuantityOnHand", "QuantityOnOrder", "QuantityOnSalesOrder", "ReorderPoint", "SalesDesc", "SalesPrice", "SalesTaxCodeRef", "Sublevel", "TimeCreated", "TimeModified", "TxnID", "TxnNumber", "UnitOfMeasureSetRef"]]
    #: Refers to an income account. If an `income_account_ref` aggregate includes both
    #: `full_name` and `list_id`, `full_name` will be ignored.
    income_account_ref: Ref
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: For future use with international versions of QuickBooks.
    is_tax_included: bool
    #: The part number used by the manufacturer of the item.
    manufacturer_part_number: str
    #: Maximum number of items in inventory.
    max: float
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because `full_name` remains distinct.
    name: str
    #: A reference to the list object that is one level above this one. For example, an
    #: inventory item with the `full_name` of GermanCars:Mercedes-Benz:CL500I99AA might have a
    #: parent object with the `full_name` of GermanCars:Mercedes-Benz. In a request, if a
    #: `parent_ref` aggregate includes both `full_name` and `list_id`, `full_name` will be
    #: ignored.
    parent_ref: Ref
    #: The preferred vendor for this item. If a `pref_vendor_ref` aggregate includes both
    #: `full_name` and `list_id`, `full_name` will be ignored.
    pref_vendor_ref: Ref
    #: Amount that the QuickBooks user expects to pay when ordering or buying this item, or the
    #: amount that was actually paid for this item.
    purchase_cost: float
    #: Appears in the Description column of checks, bills, credit card charges, and item
    #: receipts when this item is reordered.
    purchase_desc: str
    #: Account used for taxes on purchases in CA or UK.
    purchase_tax_code_ref: Ref
    #: Quantity at which QuickBooks will remind the user to reorder this inventory item.
    reorder_point: float
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: Appears in the Description column of a sales form when the QuickBooks user sells this
    #: item. For a fixed asset, describes the sale of the asset (for accounting purposes).
    sales_desc: str
    #: Price charged for this item.
    sales_price: float
    #: `sales_tax_code_ref` points to the sales-tax code used for an item or customer context.
    #: QuickBooks includes default TAX and NON codes, and a code can be deleted only when
    #: nothing references it. If sales tax is disabled, QuickBooks assigns the default
    #: non-taxable code. If both `full_name` and `list_id` are provided in `sales_tax_code_ref`,
    #: `full_name` is ignored.
    sales_tax_code_ref: Ref
    #: The unit of measure set consists of a base unit and 0-n related units.
    unit_of_measure_set_ref: Ref


class ItemInventory:
    """QuickBooks item inventory operations: create, query, update.

    Get it from ``client.item_inventory``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[ItemInventoryCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create item inventory.

        Queues ``item_inventory.create``: POST /connections/{connection_id}/item-inventories, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``ItemInventoryCreateParams``)::

            asset_account_ref: Ref
                full_name: str
                list_id: str
            bar_code: ItemDiscountBarCode
                allow_override: bool
                assign_even_if_used: bool
                bar_code_value: str
            class_ref: Ref
            cogs_account_ref: Ref
            external_guid: str
            include_ret_element: List[Literal[...] (one of 35 values)]
            income_account_ref: Ref
            inventory_date: str
            is_active: bool
            is_tax_included: bool
            manufacturer_part_number: str
            max: float
            name: str (required)
            parent_ref: Ref
            pref_vendor_ref: Ref
            purchase_cost: float
            purchase_desc: str
            purchase_tax_code_ref: Ref
            quantity_on_hand: float
            reorder_point: float
            request_id: str
            sales_desc: str
            sales_price: float
            sales_tax_code_ref: Ref
            total_value: float
            unit_of_measure_set_ref: Ref

        Docs: https://docs.qubesync.com/api-reference/v2/item-inventories/create-item-inventory
        """
        return self._client._queue_operation("item_inventory.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[ItemInventoryQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List item inventories.

        Queues ``item_inventory.query``: GET /connections/{connection_id}/item-inventories, params in the query string.
        QuickBooks answers in pages: each page comes to ``webhook_url`` as its own webhook.
        Returns the queued request.

        Params (``ItemInventoryQueryParams``)::

            active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
            class_filter: EntityFilter
                full_name: List[str]
                full_name_with_children: str
                list_id: List[str]
                list_id_with_children: str
            from_modified_date: str
            full_name: List[str]
            include_ret_element: List[Literal[...] (one of 32 values)]
            iterator: bool
            list_id: List[str]
            max_returned: int
            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            name_filter: NameFilter
                match_criterion: Literal["Contains", "EndsWith", "StartsWith"] (required)
                name: str (required)
            name_range_filter: NameRangeFilter
                from_name: str
                to_name: str
            owner_id: List[str]
            request_id: str
            to_modified_date: str

        Docs: https://docs.qubesync.com/api-reference/v2/item-inventories/list-item-inventories
        """
        return self._client._queue_operation("item_inventory.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[ItemInventoryUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update item inventory.

        Queues ``item_inventory.update``: PUT /connections/{connection_id}/item-inventories, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``ItemInventoryUpdateParams``)::

            apply_cogs_account_ref_to_existing_txns: bool
            apply_income_account_ref_to_existing_txns: bool
            asset_account_ref: Ref
                full_name: str
                list_id: str
            bar_code: ItemDiscountBarCode
                allow_override: bool
                assign_even_if_used: bool
                bar_code_value: str
            class_ref: Ref
            cogs_account_ref: Ref
            edit_sequence: str (required)
            force_uom_change: bool
            include_ret_element: List[Literal[...] (one of 35 values)]
            income_account_ref: Ref
            is_active: bool
            is_tax_included: bool
            list_id: str (required)
            manufacturer_part_number: str
            max: float
            name: str
            parent_ref: Ref
            pref_vendor_ref: Ref
            purchase_cost: float
            purchase_desc: str
            purchase_tax_code_ref: Ref
            reorder_point: float
            request_id: str
            sales_desc: str
            sales_price: float
            sales_tax_code_ref: Ref
            unit_of_measure_set_ref: Ref

        Docs: https://docs.qubesync.com/api-reference/v2/item-inventories/update-item-inventory
        """
        return self._client._queue_operation("item_inventory.update", connection_id, params, webhook_url, idempotency_key)
