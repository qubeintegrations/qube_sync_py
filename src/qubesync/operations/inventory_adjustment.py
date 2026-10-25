# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks inventory adjustment operations (``client.inventory_adjustment``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    DateRangeFilter,
    EntityFilter,
    ModifiedDateRangeFilter,
    Ref,
    RefNumberFilter,
    RefNumberRangeFilter,
)

if TYPE_CHECKING:
    from ..v2 import Client


class LotNumberAdjustment(TypedDict, total=False):
    #: Amount to adjust count.
    count_adjustment: int
    #: Location within the Inventory Site.
    inventory_site_location_ref: Ref
    #: The lot number of the asset.
    lot_number: str


class QuantityAdjustment(TypedDict, total=False):
    #: Location within the Inventory Site.
    inventory_site_location_ref: Ref
    #: The lot number of the asset.
    #:
    #: Choose at most one of: `serial_number`, or `lot_number`.
    lot_number: str
    #: The new quantity for this inventory item.
    new_quantity: float
    #: Either a positive or negative number that shows the change in quantity for this inventory
    #: item.
    quantity_difference: float
    #: The serial number of the asset.
    #:
    #: Choose at most one of: `serial_number`, or `lot_number`.
    serial_number: str


class SerialNumberAdjustment(TypedDict, total=False):
    #: Serial number that will be added to inventory.
    add_serial_number: str
    #: Location within the Inventory Site.
    inventory_site_location_ref: Ref
    #: Serial number that will be removed from inventory.
    remove_serial_number: str


class ValueAdjustment(TypedDict, total=False):
    #: The new quantity for this inventory item.
    new_quantity: float
    #: Either a positive or negative number that shows the change in quantity for this inventory
    #: item.
    quantity_difference: float


class _InventoryAdjustmentLineAddRequired(TypedDict):
    #: `item_ref` may accept all item types or a restricted subset, depending on the request.
    #: Examples: PurchaseOrder and Bill do not allow discount or sales-tax items;
    #: VehicleMileageAdd requires a service or other-charge item; BillingRateAdd requires a
    #: service item. If both `full_name` and `list_id` are provided, `full_name` is ignored.
    item_ref: Ref


class InventoryAdjustmentLineAdd(_InventoryAdjustmentLineAddRequired, total=False):
    #: Amount to adjust lot number.
    #:
    #: Choose exactly one of: `quantity_adjustment`, or `value_adjustment`, or
    #: `serial_number_adjustment`, or `lot_number_adjustment`.
    lot_number_adjustment: LotNumberAdjustment
    #: Adjusts the inventory quantity either by setting a new quantity or by adjusting the
    #: current quantity up or down.
    #:
    #: Choose exactly one of: `quantity_adjustment`, or `value_adjustment`, or
    #: `serial_number_adjustment`, or `lot_number_adjustment`.
    quantity_adjustment: QuantityAdjustment
    #: Serial number that will be adjusted in inventory.
    #:
    #: Choose exactly one of: `quantity_adjustment`, or `value_adjustment`, or
    #: `serial_number_adjustment`, or `lot_number_adjustment`.
    serial_number_adjustment: SerialNumberAdjustment
    #: Adjusts the total value of these inventory items by setting a new monetary value, and
    #: optionally by setting a new quantity.
    #:
    #: Choose exactly one of: `quantity_adjustment`, or `value_adjustment`, or
    #: `serial_number_adjustment`, or `lot_number_adjustment`.
    value_adjustment: ValueAdjustment


class _InventoryAdjustmentLineModRequired(TypedDict):
    #: Identification number of the transaction line. (`txn_line_id` is supported as of v2.0 of
    #: the SDK. With qbXML v1.0 and v1.1, `txn_line_id` is always returned as zero.) If you need
    #: to add a new transaction line in a transaction Mod request, you can do so by setting the
    #: `txn_line_id` to -1.
    txn_line_id: str


class InventoryAdjustmentLineMod(_InventoryAdjustmentLineModRequired, total=False):
    #: Amount to adjust count.
    #:
    #: Choose exactly one of: `serial_number`, or the set (`count_adjustment`, `lot_number`).
    #: Members of a set combine with each other, not with the other choices.
    count_adjustment: int
    #: Location within the Inventory Site.
    inventory_site_location_ref: Ref
    #: `item_ref` may accept all item types or a restricted subset, depending on the request.
    #: Examples: PurchaseOrder and Bill do not allow discount or sales-tax items;
    #: VehicleMileageAdd requires a service or other-charge item; BillingRateAdd requires a
    #: service item. If both `full_name` and `list_id` are provided, `full_name` is ignored.
    item_ref: Ref
    #: The lot number of the asset.
    #:
    #: Choose exactly one of: `serial_number`, or the set (`count_adjustment`, `lot_number`).
    #: Members of a set combine with each other, not with the other choices.
    lot_number: str
    #: Either a positive or negative number that shows the change in quantity for this inventory
    #: item.
    quantity_difference: float
    #: The serial number of the asset.
    #:
    #: Choose exactly one of: `serial_number`, or the set (`count_adjustment`, `lot_number`).
    #: Members of a set combine with each other, not with the other choices.
    serial_number: str
    #: Either a positive or negative number that shows a change in the total value of the entire
    #: stock of this inventory item.
    value_difference: float


class _InventoryAdjustmentCreateParamsRequired(TypedDict):
    #: `account_ref` points to an account in the company file. If both `full_name` and `list_id`
    #: are provided, `full_name` is ignored. Meaning depends on context: for checks it is the
    #: funding account; for ExpenseLineAdd it may be required by accounting preferences; for
    #: credit-card transactions it identifies the bank or card account involved.
    account_ref: Ref
    inventory_adjustment_line_add: List[InventoryAdjustmentLineAdd]


class InventoryAdjustmentCreateParams(_InventoryAdjustmentCreateParamsRequired, total=False):
    """Params for ``inventory_adjustment.create`` (Create inventory adjustment)."""
    #: Use classes to categorize transactions (for example, by department, location, or work
    #: type). Class tracking is off by default in QuickBooks. A `class_ref` points to one class;
    #: if both `full_name` and `list_id` are provided, `full_name` is ignored. In InvoiceAdd, a
    #: header-level `class_ref` is applied to line items unless you override or clear it on
    #: individual lines.
    class_ref: Ref
    #: `customer_ref` identifies a customer or customer job. If both `full_name` and `list_id`
    #: are provided, `full_name` is ignored. In SalesReceipt and ReceivePayment, it identifies
    #: who receives credit. In TimeTracking, it identifies who the time can be billed to and is
    #: required in TimeTrackingAdd when IsBillable is true.
    customer_ref: Ref
    #: `def_macro` lets you assign a reusable name to a returned `txn_id` or `txn_line_id` so
    #: later requests can reference it with `useMacro`. This feature requires SDK 2.0+.
    def_macro: str
    #: Allows for the attachment of a user defined GUID value.
    external_guid: str
    include_ret_element: List[Literal["AccountRef", "ClassRef", "CustomerRef", "DataExtRet", "EditSequence", "ExternalGUID", "InventoryAdjustmentLineRet", "InventorySiteRef", "ListID", "Memo", "OwnerID", "RefNumber", "TimeCreated", "TimeModified", "TxnDate", "TxnID", "TxnNumber"]]
    #: Site where inventory is located.
    inventory_site_ref: Ref
    #: Additional information.
    memo: str
    #: `ref_number` is a user-managed transaction reference (for example, a check number). It
    #: can be edited and is not guaranteed to be globally unique. Some transaction types
    #: auto-populate `ref_number` when omitted, based on QuickBooks preferences and numbering
    #: state.
    ref_number: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: The date of the transaction. In some cases, if you leave `txn_date` out of an -Add
    #: message, QuickBooks will prefill `txn_date` with the date of the last-saved transaction
    #: of the same type.
    txn_date: str


class InventoryAdjustmentQueryParams(TypedDict, total=False):
    """Params for ``inventory_adjustment.query`` (List inventory adjustments)."""
    #: Filters according to the account name or `list_id`. If the “Use account numbers”
    #: preference is enabled in the QuickBooks company file, you can specify an account number
    #: (instead of an account name) for `full_name` and get the account you’re looking for. But
    #: if numbers have been used as account names, confusion could arise.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `item_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    account_filter: EntityFilter
    #: An entity refers to a person on the QuickBooks Customer list, Vendor list, Employee list,
    #: or Other Names list. You can use an EntityQuery request to get information about all the
    #: entities that are set up in the QuickBooks file. In an ARRefundCreditCard query, this
    #: must be a customer/customer job.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `item_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    entity_filter: EntityFilter
    #: This filter allows you to omit line items from a query response to get a smaller result.
    #: The default value is false, so line items are omitted by default. Set
    #: `include_line_items` to true to include line items in the response if you don’t mind
    #: getting a larger result.
    include_line_items: bool
    include_ret_element: List[Literal["AccountRef", "ClassRef", "CustomerRef", "DataExtRet", "EditSequence", "ExternalGUID", "InventoryAdjustmentLineRet", "InventorySiteRef", "Memo", "RefNumber", "TimeCreated", "TimeModified", "TxnDate", "TxnID", "TxnNumber"]]
    #: Filters according to the item name or ID. You can use an ItemQuery request to get
    #: information about all the items that are set up in the QuickBooks file. “Items” are line
    #: items used for fast entry on sales and purchase forms. They include services and goods
    #: that a business buys and sells, as well as special items that perform calculations–for
    #: example, subtotal, discount, and sales-tax items.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `item_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    item_filter: EntityFilter
    #: Page through every match: QuBe Sync asks QuickBooks for each page in turn and sends each
    #: to your `webhook_url` as it arrives, all with the same `id`. On by default, with pages of
    #: 100 records (25 with `include_line_items`); send `iterator=true` with `max_returned` for
    #: another size. Off when you send `iterator=false` (every match in one answer) or
    #: `max_returned` alone (at most that many, in one answer). It pages a filtered query only:
    #: with `ref_number`, `ref_number_case_sensitive` or `txn_id` every match comes back in one
    #: answer, so leave `iterator` out.
    iterator: bool
    #: Limits the number of objects that a query returns. (To get a count of how many objects
    #: could possibly be returned, use the `meta_data` query attribute.) If you include a
    #: `max_returned` value, it must be at least 1.
    #:
    #: The page size, with `iterator=true`. Sent without `iterator`, or with `iterator=false`,
    #: it's a cap instead: at most this many records come back, in one answer, and QuickBooks
    #: doesn't say whether more matched.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `item_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    max_returned: int
    #: Use the `meta_data` attribute to control whether query responses include counts. Options
    #: are NoMetaData (default), MetaDataOnly (count only), and MetaDataAndResponseData (count
    #: plus objects). Counts are approximate and may vary slightly if records are created or
    #: deleted during processing.
    meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
    #: Filters according to the dates when transactions were last modified. The
    #: `modified_date_range_filter` aggregate isn’t required to contain any elements, but if it
    #: is empty, we recommend that you leave it out altogether. Note that the time portion of
    #: the `from_modified_date` and `to_modified_date` fields wasn’t supported in qbXML version
    #: 1.0 or 1.1.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `item_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    modified_date_range_filter: ModifiedDateRangeFilter
    #: `owner_id` identifies who owns the data extension. Use 0 for QuickBooks custom fields
    #: that appear in the UI, or use a GUID for private extensions owned by an app. Keep private
    #: GUIDs confidential unless you intentionally share extensions across apps. If you do share
    #: them, both apps must use the same `owner_id` and `data_ext_name`, because that pair
    #: uniquely identifies the extension.
    owner_id: List[str]
    #: `ref_number` is a user-managed transaction reference (for example, a check number). It
    #: can be edited and is not guaranteed to be globally unique. Some transaction types
    #: auto-populate `ref_number` when omitted, based on QuickBooks preferences and numbering
    #: state.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `item_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    ref_number: List[str]
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `item_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    ref_number_case_sensitive: List[str]
    #: Filters by `ref_number` range. Numeric-only bounds are compared numerically; otherwise
    #: comparison is lexicographic.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `item_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    ref_number_filter: RefNumberFilter
    #: Filters by `ref_number` range. Numeric-only bounds are compared numerically; otherwise
    #: comparison is lexicographic.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `item_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    ref_number_range_filter: RefNumberRangeFilter
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: Filters according to the original transaction dates.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `item_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    txn_date_range_filter: DateRangeFilter
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `item_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    txn_id: List[str]


class _InventoryAdjustmentUpdateParamsRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    txn_id: str


class InventoryAdjustmentUpdateParams(_InventoryAdjustmentUpdateParamsRequired, total=False):
    """Params for ``inventory_adjustment.update`` (Update inventory adjustment)."""
    #: `account_ref` points to an account in the company file. If both `full_name` and `list_id`
    #: are provided, `full_name` is ignored. Meaning depends on context: for checks it is the
    #: funding account; for ExpenseLineAdd it may be required by accounting preferences; for
    #: credit-card transactions it identifies the bank or card account involved.
    account_ref: Ref
    #: Use classes to categorize transactions (for example, by department, location, or work
    #: type). Class tracking is off by default in QuickBooks. A `class_ref` points to one class;
    #: if both `full_name` and `list_id` are provided, `full_name` is ignored. In InvoiceAdd, a
    #: header-level `class_ref` is applied to line items unless you override or clear it on
    #: individual lines.
    class_ref: Ref
    #: `customer_ref` identifies a customer or customer job. If both `full_name` and `list_id`
    #: are provided, `full_name` is ignored. In SalesReceipt and ReceivePayment, it identifies
    #: who receives credit. In TimeTracking, it identifies who the time can be billed to and is
    #: required in TimeTrackingAdd when IsBillable is true.
    customer_ref: Ref
    include_ret_element: List[Literal["AccountRef", "ClassRef", "CustomerRef", "DataExtRet", "EditSequence", "ExternalGUID", "InventoryAdjustmentLineRet", "InventorySiteRef", "ListID", "Memo", "OwnerID", "RefNumber", "TimeCreated", "TimeModified", "TxnDate", "TxnID", "TxnNumber"]]
    inventory_adjustment_line_mod: List[InventoryAdjustmentLineMod]
    #: Site where inventory is located.
    inventory_site_ref: Ref
    #: Additional information.
    memo: str
    #: `ref_number` is a user-managed transaction reference (for example, a check number). It
    #: can be edited and is not guaranteed to be globally unique. Some transaction types
    #: auto-populate `ref_number` when omitted, based on QuickBooks preferences and numbering
    #: state.
    ref_number: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: The date of the transaction. In some cases, if you leave `txn_date` out of an -Add
    #: message, QuickBooks will prefill `txn_date` with the date of the last-saved transaction
    #: of the same type.
    txn_date: str


class InventoryAdjustment:
    """QuickBooks inventory adjustment operations: create, query, update.

    Get it from ``client.inventory_adjustment``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[InventoryAdjustmentCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create inventory adjustment.

        Queues ``inventory_adjustment.create``: POST /connections/{connection_id}/inventory-adjustments, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``InventoryAdjustmentCreateParams``)::

            account_ref: Ref (required)
                full_name: str
                list_id: str
            class_ref: Ref
            customer_ref: Ref
            def_macro: str
            external_guid: str
            include_ret_element: List[Literal[...] (one of 17 values)]
            inventory_adjustment_line_add: List[InventoryAdjustmentLineAdd] (required)
                item_ref: Ref (required)
                lot_number_adjustment: LotNumberAdjustment
                    count_adjustment: int
                    inventory_site_location_ref: Ref
                    lot_number: str
                quantity_adjustment: QuantityAdjustment
                    inventory_site_location_ref: Ref
                    lot_number: str
                    new_quantity: float
                    quantity_difference: float
                    serial_number: str
                serial_number_adjustment: SerialNumberAdjustment
                    add_serial_number: str
                    inventory_site_location_ref: Ref
                    remove_serial_number: str
                value_adjustment: ValueAdjustment
                    new_quantity: float
                    quantity_difference: float
            inventory_site_ref: Ref
            memo: str
            ref_number: str
            request_id: str
            txn_date: str

        Docs: https://docs.qubesync.com/api-reference/v2/inventory-adjustments/create-inventory-adjustment
        """
        return self._client._queue_operation("inventory_adjustment.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[InventoryAdjustmentQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List inventory adjustments.

        Queues ``inventory_adjustment.query``: GET /connections/{connection_id}/inventory-adjustments, params in the query string.
        QuickBooks answers in pages: each page comes to ``webhook_url`` as its own webhook.
        Returns the queued request.

        Params (``InventoryAdjustmentQueryParams``)::

            account_filter: EntityFilter
                full_name: List[str]
                full_name_with_children: str
                list_id: List[str]
                list_id_with_children: str
            entity_filter: EntityFilter
            include_line_items: bool
            include_ret_element: List[Literal[...] (one of 15 values)]
            item_filter: EntityFilter
            iterator: bool
            max_returned: int
            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            modified_date_range_filter: ModifiedDateRangeFilter
                from_modified_date: str
                to_modified_date: str
            owner_id: List[str]
            ref_number: List[str]
            ref_number_case_sensitive: List[str]
            ref_number_filter: RefNumberFilter
                match_criterion: Literal["Contains", "EndsWith", "StartsWith"] (required)
                ref_number: str (required)
            ref_number_range_filter: RefNumberRangeFilter
                from_ref_number: str
                to_ref_number: str
            request_id: str
            txn_date_range_filter: DateRangeFilter
                date_macro: Literal[...] (one of 34 values)
                from_txn_date: str
                to_txn_date: str
            txn_id: List[str]

        Docs: https://docs.qubesync.com/api-reference/v2/inventory-adjustments/list-inventory-adjustments
        """
        return self._client._queue_operation("inventory_adjustment.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[InventoryAdjustmentUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update inventory adjustment.

        Queues ``inventory_adjustment.update``: PUT /connections/{connection_id}/inventory-adjustments, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``InventoryAdjustmentUpdateParams``)::

            account_ref: Ref
                full_name: str
                list_id: str
            class_ref: Ref
            customer_ref: Ref
            edit_sequence: str (required)
            include_ret_element: List[Literal[...] (one of 17 values)]
            inventory_adjustment_line_mod: List[InventoryAdjustmentLineMod]
                count_adjustment: int
                inventory_site_location_ref: Ref
                item_ref: Ref
                lot_number: str
                quantity_difference: float
                serial_number: str
                txn_line_id: str (required)
                value_difference: float
            inventory_site_ref: Ref
            memo: str
            ref_number: str
            request_id: str
            txn_date: str
            txn_id: str (required)

        Docs: https://docs.qubesync.com/api-reference/v2/inventory-adjustments/update-inventory-adjustment
        """
        return self._client._queue_operation("inventory_adjustment.update", connection_id, params, webhook_url, idempotency_key)
