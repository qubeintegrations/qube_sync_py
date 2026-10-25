# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks item service operations (``client.item_service``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    EntityFilter,
    ItemDiscountBarCode,
    NameFilter,
    NameRangeFilter,
    Ref,
    SalesAndPurchase,
    SalesAndPurchaseMod,
    SalesOrPurchase,
    SalesOrPurchaseMod,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _ItemServiceCreateParamsRequired(TypedDict):
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because `full_name` remains distinct.
    name: str


class ItemServiceCreateParams(_ItemServiceCreateParamsRequired, total=False):
    """Params for ``item_service.create`` (Create item service)."""
    #: Barcode reference information.
    bar_code: ItemDiscountBarCode
    #: Use classes to categorize transactions (for example, by department, location, or work
    #: type). Class tracking is off by default in QuickBooks. A `class_ref` points to one class;
    #: if both `full_name` and `list_id` are provided, `full_name` is ignored. In InvoiceAdd, a
    #: header-level `class_ref` is applied to line items unless you override or clear it on
    #: individual lines.
    class_ref: Ref
    #: Allows for the attachment of a user defined GUID value.
    external_guid: str
    include_ret_element: List[Literal["BarCodeValue", "ClassRef", "DataExtRet", "EditSequence", "ExternalGUID", "FullName", "IsActive", "IsTaxIncluded", "ListID", "Name", "OwnerID", "ParentRef", "SalesAndPurchase", "SalesOrPurchase", "SalesTaxCodeRef", "Sublevel", "TimeCreated", "TimeModified", "TxnID", "TxnNumber", "UnitOfMeasureSetRef"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: For future use with international versions of QuickBooks.
    is_tax_included: bool
    #: A reference to the list object that is one level above this one. For example, an
    #: inventory item with the `full_name` of GermanCars:Mercedes-Benz:CL500I99AA might have a
    #: parent object with the `full_name` of GermanCars:Mercedes-Benz. In a request, if a
    #: `parent_ref` aggregate includes both `full_name` and `list_id`, `full_name` will be
    #: ignored.
    parent_ref: Ref
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: A `sales_and_purchase` aggregate is used for items that are meant to be both purchased
    #: and sold, such as an “other charge” item that is reimbursable.
    sales_and_purchase: SalesAndPurchase
    #: A `sales_or_purchase` aggregate is used for items that are meant to be either purchased
    #: or sold, but not both. For example, a `sales_or_purchase` aggregate would be used for a
    #: non-inventory item that is purchased but not sold, or for a service item that is sold but
    #: not purchased.
    sales_or_purchase: SalesOrPurchase
    #: `sales_tax_code_ref` points to the sales-tax code used for an item or customer context.
    #: QuickBooks includes default TAX and NON codes, and a code can be deleted only when
    #: nothing references it. If sales tax is disabled, QuickBooks assigns the default
    #: non-taxable code. If both `full_name` and `list_id` are provided in `sales_tax_code_ref`,
    #: `full_name` is ignored.
    sales_tax_code_ref: Ref
    #: The unit of measure set consists of a base unit and 0-n related units.
    unit_of_measure_set_ref: Ref


class ItemServiceQueryParams(TypedDict, total=False):
    """Params for ``item_service.query`` (List item services)."""
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
    include_ret_element: List[Literal["BarCodeValue", "ClassRef", "DataExtRet", "EditSequence", "ExternalGUID", "FullName", "IsActive", "IsTaxIncluded", "ListID", "Name", "ParentRef", "SalesAndPurchase", "SalesOrPurchase", "SalesTaxCodeRef", "Sublevel", "TimeCreated", "TimeModified", "UnitOfMeasureSetRef"]]
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


class _ItemServiceUpdateParamsRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list type, not globally
    #: across all lists. If both `full_name` and `list_id` are supplied in a request, QuickBooks
    #: uses `list_id` and ignores `full_name`.
    list_id: str


class ItemServiceUpdateParams(_ItemServiceUpdateParamsRequired, total=False):
    """Params for ``item_service.update`` (Update item service)."""
    #: Barcode reference information.
    bar_code: ItemDiscountBarCode
    #: Use classes to categorize transactions (for example, by department, location, or work
    #: type). Class tracking is off by default in QuickBooks. A `class_ref` points to one class;
    #: if both `full_name` and `list_id` are provided, `full_name` is ignored. In InvoiceAdd, a
    #: header-level `class_ref` is applied to line items unless you override or clear it on
    #: individual lines.
    class_ref: Ref
    #: By Default `force_uom_change` is false. However, in item Mod requests, you need to set
    #: the `force_uom_change` field to True if you are changing the UOM set and the base unit of
    #: the new set doesn’t match the base unit of the UOM set currently assigned to the item.
    #: This does the same thing as the user accepting the warning prompt in the UI.
    force_uom_change: bool
    include_ret_element: List[Literal["BarCodeValue", "ClassRef", "DataExtRet", "EditSequence", "ExternalGUID", "FullName", "IsActive", "IsTaxIncluded", "ListID", "Name", "OwnerID", "ParentRef", "SalesAndPurchase", "SalesOrPurchase", "SalesTaxCodeRef", "Sublevel", "TimeCreated", "TimeModified", "TxnID", "TxnNumber", "UnitOfMeasureSetRef"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: For future use with international versions of QuickBooks.
    is_tax_included: bool
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
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: A `sales_and_purchase` aggregate is used for items that are meant to be both purchased
    #: and sold, such as an “other charge” item that is reimbursable.
    #:
    #: Choose at most one of: `sales_or_purchase_mod`, or `sales_and_purchase_mod`.
    sales_and_purchase_mod: SalesAndPurchaseMod
    #: A `sales_or_purchase` aggregate is used for items that are meant to be either purchased
    #: or sold, but not both. For example, a `sales_or_purchase` aggregate would be used for a
    #: non-inventory item that is purchased but not sold, or for a service item that is sold but
    #: not purchased.
    #:
    #: Choose at most one of: `sales_or_purchase_mod`, or `sales_and_purchase_mod`.
    sales_or_purchase_mod: SalesOrPurchaseMod
    #: `sales_tax_code_ref` points to the sales-tax code used for an item or customer context.
    #: QuickBooks includes default TAX and NON codes, and a code can be deleted only when
    #: nothing references it. If sales tax is disabled, QuickBooks assigns the default
    #: non-taxable code. If both `full_name` and `list_id` are provided in `sales_tax_code_ref`,
    #: `full_name` is ignored.
    sales_tax_code_ref: Ref
    #: The unit of measure set consists of a base unit and 0-n related units.
    unit_of_measure_set_ref: Ref


class ItemService:
    """QuickBooks item service operations: create, query, update.

    Get it from ``client.item_service``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[ItemServiceCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create item service.

        Queues ``item_service.create``: POST /connections/{connection_id}/item-services, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``ItemServiceCreateParams``)::

            bar_code: ItemDiscountBarCode
                allow_override: bool
                assign_even_if_used: bool
                bar_code_value: str
            class_ref: Ref
                full_name: str
                list_id: str
            external_guid: str
            include_ret_element: List[Literal[...] (one of 21 values)]
            is_active: bool
            is_tax_included: bool
            name: str (required)
            parent_ref: Ref
            request_id: str
            sales_and_purchase: SalesAndPurchase
                expense_account_ref: Ref
                income_account_ref: Ref
                pref_vendor_ref: Ref
                purchase_cost: float
                purchase_desc: str
                purchase_tax_code_ref: Ref
                sales_desc: str
                sales_price: float
            sales_or_purchase: SalesOrPurchase
                account_ref: Ref
                desc: str
                price: float
                price_percent: float
            sales_tax_code_ref: Ref
            unit_of_measure_set_ref: Ref

        Docs: https://docs.qubesync.com/api-reference/v2/item-services/create-item-service
        """
        return self._client._queue_operation("item_service.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[ItemServiceQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List item services.

        Queues ``item_service.query``: GET /connections/{connection_id}/item-services, params in the query string.
        QuickBooks answers in pages: each page comes to ``webhook_url`` as its own webhook.
        Returns the queued request.

        Params (``ItemServiceQueryParams``)::

            active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
            class_filter: EntityFilter
                full_name: List[str]
                full_name_with_children: str
                list_id: List[str]
                list_id_with_children: str
            from_modified_date: str
            full_name: List[str]
            include_ret_element: List[Literal[...] (one of 18 values)]
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

        Docs: https://docs.qubesync.com/api-reference/v2/item-services/list-item-services
        """
        return self._client._queue_operation("item_service.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[ItemServiceUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update item service.

        Queues ``item_service.update``: PUT /connections/{connection_id}/item-services, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``ItemServiceUpdateParams``)::

            bar_code: ItemDiscountBarCode
                allow_override: bool
                assign_even_if_used: bool
                bar_code_value: str
            class_ref: Ref
                full_name: str
                list_id: str
            edit_sequence: str (required)
            force_uom_change: bool
            include_ret_element: List[Literal[...] (one of 21 values)]
            is_active: bool
            is_tax_included: bool
            list_id: str (required)
            name: str
            parent_ref: Ref
            request_id: str
            sales_and_purchase_mod: SalesAndPurchaseMod
                apply_expense_account_ref_to_existing_txns: bool
                apply_income_account_ref_to_existing_txns: bool
                expense_account_ref: Ref
                income_account_ref: Ref
                pref_vendor_ref: Ref
                purchase_cost: float
                purchase_desc: str
                purchase_tax_code_ref: Ref
                sales_desc: str
                sales_price: float
            sales_or_purchase_mod: SalesOrPurchaseMod
                account_ref: Ref
                apply_account_ref_to_existing_txns: bool
                desc: str
                price: float
                price_percent: float
            sales_tax_code_ref: Ref
            unit_of_measure_set_ref: Ref

        Docs: https://docs.qubesync.com/api-reference/v2/item-services/update-item-service
        """
        return self._client._queue_operation("item_service.update", connection_id, params, webhook_url, idempotency_key)
