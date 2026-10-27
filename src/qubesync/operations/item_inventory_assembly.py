# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks item inventory assembly operations (``client.item_inventory_assembly``)."""

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


class _ItemInventoryAssemblyLineRequired(TypedDict):
    #: An inventory item is any merchandise or part that a business purchases, tracks as
    #: inventory, and then resells. In QuickBooks, information about an inventory item is
    #: grouped into three categories:Puchase Information includes `purchase_desc`,
    #: `purchase_cost`, `cogs_account_ref`, and `pref_vendor_ref`. Sales Information includes
    #: `sales_desc`, `sales_price`, and `sales_tax_code_ref`.
    item_inventory_ref: Ref


class ItemInventoryAssemblyLine(_ItemInventoryAssemblyLineRequired, total=False):
    #: On transaction lines, QuickBooks can derive one value from the other two among Quantity,
    #: Rate, and Amount. If you supply Quantity and Amount, QuickBooks calculates Rate. If you
    #: supply Quantity and Rate, QuickBooks calculates Amount.
    quantity: float


class _ItemInventoryAssemblyCreateParamsRequired(TypedDict):
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because `full_name` remains distinct.
    name: str


class ItemInventoryAssemblyCreateParams(_ItemInventoryAssemblyCreateParamsRequired, total=False):
    """Params for ``item_inventory_assembly.create`` (Create item inventory assembly)."""
    #: Refers to the account QuickBooks uses to track the current value of the company’s
    #: inventory. (The AccountType of this account will be FixedAsset, OtherAsset, or
    #: OtherCurrentAsset.) In a request, if an `asset_account_ref` aggregate includes both
    #: `full_name` and `list_id`, `full_name` will be ignored.
    asset_account_ref: Ref
    #: Barcode reference information.
    bar_code: ItemDiscountBarCode
    #: The build notification point. The QuickBooks user will receive a notification when
    #: `quantity_on_hand` plus `quantity_on_order` falls below `build_point`.
    build_point: float
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
    include_ret_element: List[Literal["AssetAccountRef", "AverageCost", "BarCodeValue", "BuildPoint", "COGSAccountRef", "ClassRef", "DataExtRet", "EditSequence", "ExternalGUID", "FullName", "IncomeAccountRef", "IsActive", "IsTaxIncluded", "ItemInventoryAssemblyLine", "ListID", "ManufacturerPartNumber", "Max", "Name", "OwnerID", "ParentRef", "PrefVendorRef", "PurchaseCost", "PurchaseDesc", "PurchaseTaxCodeRef", "QuantityOnHand", "QuantityOnOrder", "QuantityOnSalesOrder", "SalesDesc", "SalesPrice", "SalesTaxCodeRef", "Sublevel", "TimeCreated", "TimeModified", "TxnID", "TxnNumber", "UnitOfMeasureSetRef"]]
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
    item_inventory_assembly_line: List[ItemInventoryAssemblyLine]
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
    #: Description that appears in the Description column of checks, bills, credit card charges,
    #: and item receipts (when an item is reordered). For a fixed asset, a description of the
    #: item as it was when it was purchased.
    purchase_desc: str
    #: Account used for taxes on purchases in CA or UK.
    purchase_tax_code_ref: Ref
    #: The number of these items in inventory. `quantity_on_hand` times `average_cost` is
    #: `total_value` in an inventory item list. To change the `quantity_on_hand` for an item,
    #: you would have to use InventoryAdjustmentAdd not an ItemInventoryMod.
    quantity_on_hand: float
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


class ItemInventoryAssemblyQueryParams(TypedDict, total=False):
    """Params for ``item_inventory_assembly.query`` (List item inventory assemblies)."""
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
    include_ret_element: List[Literal["AssetAccountRef", "AverageCost", "BarCodeValue", "BuildPoint", "COGSAccountRef", "ClassRef", "DataExtRet", "EditSequence", "ExternalGUID", "FullName", "IncomeAccountRef", "IsActive", "IsTaxIncluded", "ItemInventoryAssemblyLine", "ListID", "ManufacturerPartNumber", "Max", "Name", "ParentRef", "PrefVendorRef", "PurchaseCost", "PurchaseDesc", "PurchaseTaxCodeRef", "QuantityOnHand", "QuantityOnOrder", "QuantityOnSalesOrder", "SalesDesc", "SalesPrice", "SalesTaxCodeRef", "Sublevel", "TimeCreated", "TimeModified", "UnitOfMeasureSetRef"]]
    #: Page through every match: QuBe Sync asks QuickBooks for each page in turn and sends each
    #: to your `webhook_url` as it arrives, all with the same `id`. On by default, with pages of
    #: 100 records; send `iterator=true` with `max_returned` for another size. Off when you send
    #: `iterator=false` (every match in one answer) or `max_returned` alone (at most that many,
    #: in one answer). It pages a filtered query only: with `full_name` or `list_id` every match
    #: comes back in one answer, so leave `iterator` out.
    iterator: bool
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list family, not across the
    #: company file: customers, vendors, employees and other names share one sequence, every
    #: item type shares another, and each other list has its own.
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


class _ItemInventoryAssemblyUpdateParamsRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list family, not across the
    #: company file: customers, vendors, employees and other names share one sequence, every
    #: item type shares another, and each other list has its own.
    list_id: str


class ItemInventoryAssemblyUpdateParams(_ItemInventoryAssemblyUpdateParamsRequired, total=False):
    """Params for ``item_inventory_assembly.update`` (Update item inventory assembly)."""
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
    #: The build notification point. The QuickBooks user will receive a notification when
    #: `quantity_on_hand` plus `quantity_on_order` falls below `build_point`.
    build_point: float
    #: Use classes to categorize transactions (for example, by department, location, or work
    #: type). Class tracking is off by default in QuickBooks. A `class_ref` points to one class;
    #: if both `full_name` and `list_id` are provided, `full_name` is ignored. In InvoiceAdd, a
    #: header-level `class_ref` is applied to line items unless you override or clear it on
    #: individual lines.
    class_ref: Ref
    #: Set to true to clear all the items in this group.
    #:
    #: Choose at most one of: `clear_items_in_group`, or `item_inventory_assembly_line`.
    clear_items_in_group: bool
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
    include_ret_element: List[Literal["AssetAccountRef", "AverageCost", "BarCodeValue", "BuildPoint", "COGSAccountRef", "ClassRef", "DataExtRet", "EditSequence", "ExternalGUID", "FullName", "IncomeAccountRef", "IsActive", "IsTaxIncluded", "ItemInventoryAssemblyLine", "ListID", "ManufacturerPartNumber", "Max", "Name", "OwnerID", "ParentRef", "PrefVendorRef", "PurchaseCost", "PurchaseDesc", "PurchaseTaxCodeRef", "QuantityOnHand", "QuantityOnOrder", "QuantityOnSalesOrder", "SalesDesc", "SalesPrice", "SalesTaxCodeRef", "Sublevel", "TimeCreated", "TimeModified", "TxnID", "TxnNumber", "UnitOfMeasureSetRef"]]
    #: Refers to an income account. If an `income_account_ref` aggregate includes both
    #: `full_name` and `list_id`, `full_name` will be ignored.
    income_account_ref: Ref
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: For future use with international versions of QuickBooks.
    is_tax_included: bool
    #: Choose at most one of: `clear_items_in_group`, or `item_inventory_assembly_line`.
    item_inventory_assembly_line: List[ItemInventoryAssemblyLine]
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
    #: Description that appears in the Description column of checks, bills, credit card charges,
    #: and item receipts (when an item is reordered). For a fixed asset, a description of the
    #: item as it was when it was purchased.
    purchase_desc: str
    #: Account used for taxes on purchases in CA or UK.
    purchase_tax_code_ref: Ref
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


class ItemInventoryAssembly:
    """QuickBooks item inventory assembly operations: create, query, update.

    Get it from ``client.item_inventory_assembly``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[ItemInventoryAssemblyCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create item inventory assembly.

        Queues ``item_inventory_assembly.create``: POST /connections/{connection_id}/item-inventory-assemblies, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``ItemInventoryAssemblyCreateParams``)::

            asset_account_ref: Ref
                full_name: str
                list_id: str
            bar_code: ItemDiscountBarCode
                allow_override: bool
                assign_even_if_used: bool
                bar_code_value: str
            build_point: float
            class_ref: Ref
            cogs_account_ref: Ref
            external_guid: str
            include_ret_element: List[Literal[...] (one of 36 values)]
            income_account_ref: Ref
            inventory_date: str
            is_active: bool
            is_tax_included: bool
            item_inventory_assembly_line: List[ItemInventoryAssemblyLine]
                item_inventory_ref: Ref (required)
                quantity: float
            manufacturer_part_number: str
            max: float
            name: str (required)
            parent_ref: Ref
            pref_vendor_ref: Ref
            purchase_cost: float
            purchase_desc: str
            purchase_tax_code_ref: Ref
            quantity_on_hand: float
            request_id: str
            sales_desc: str
            sales_price: float
            sales_tax_code_ref: Ref
            total_value: float
            unit_of_measure_set_ref: Ref

        Docs: https://docs.qubesync.com/api-reference/v2/item-inventory-assemblies/create-item-inventory-assembly
        """
        return self._client._queue_operation("item_inventory_assembly.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[ItemInventoryAssemblyQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List item inventory assemblies.

        Queues ``item_inventory_assembly.query``: GET /connections/{connection_id}/item-inventory-assemblies, params in the query string.
        QuickBooks answers in pages: each page comes to ``webhook_url`` as its own webhook.
        Returns the queued request.

        Params (``ItemInventoryAssemblyQueryParams``)::

            active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
            class_filter: EntityFilter
                full_name: List[str]
                full_name_with_children: str
                list_id: List[str]
                list_id_with_children: str
            from_modified_date: str
            full_name: List[str]
            include_ret_element: List[Literal[...] (one of 33 values)]
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

        Docs: https://docs.qubesync.com/api-reference/v2/item-inventory-assemblies/list-item-inventory-assemblies
        """
        return self._client._queue_operation("item_inventory_assembly.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[ItemInventoryAssemblyUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update item inventory assembly.

        Queues ``item_inventory_assembly.update``: PUT /connections/{connection_id}/item-inventory-assemblies, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``ItemInventoryAssemblyUpdateParams``)::

            apply_income_account_ref_to_existing_txns: bool
            asset_account_ref: Ref
                full_name: str
                list_id: str
            bar_code: ItemDiscountBarCode
                allow_override: bool
                assign_even_if_used: bool
                bar_code_value: str
            build_point: float
            class_ref: Ref
            clear_items_in_group: bool
            cogs_account_ref: Ref
            edit_sequence: str (required)
            force_uom_change: bool
            include_ret_element: List[Literal[...] (one of 36 values)]
            income_account_ref: Ref
            is_active: bool
            is_tax_included: bool
            item_inventory_assembly_line: List[ItemInventoryAssemblyLine]
                item_inventory_ref: Ref (required)
                quantity: float
            list_id: str (required)
            manufacturer_part_number: str
            max: float
            name: str
            parent_ref: Ref
            pref_vendor_ref: Ref
            purchase_cost: float
            purchase_desc: str
            purchase_tax_code_ref: Ref
            request_id: str
            sales_desc: str
            sales_price: float
            sales_tax_code_ref: Ref
            unit_of_measure_set_ref: Ref

        Docs: https://docs.qubesync.com/api-reference/v2/item-inventory-assemblies/update-item-inventory-assembly
        """
        return self._client._queue_operation("item_inventory_assembly.update", connection_id, params, webhook_url, idempotency_key)
