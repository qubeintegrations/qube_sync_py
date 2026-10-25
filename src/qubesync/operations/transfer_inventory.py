# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks transfer inventory operations (``client.transfer_inventory``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    CurrencyFilter,
    DateRangeFilter,
    EntityFilter,
    ModifiedDateRangeFilter,
    Ref,
    RefNumberFilter,
    RefNumberRangeFilter,
)

if TYPE_CHECKING:
    from ..v2 import Client


class TransferInventoryLineAdd(TypedDict, total=False):
    #: `def_macro` lets you assign a reusable name to a returned `txn_id` or `txn_line_id` so
    #: later requests can reference it with `useMacro`. This feature requires SDK 2.0+.
    def_macro: str
    #: Location within the inventory site that transfer will be taken from.
    from_inventory_site_location_ref: Ref
    #: `item_ref` may accept all item types or a restricted subset, depending on the request.
    #: Examples: PurchaseOrder and Bill do not allow discount or sales-tax items;
    #: VehicleMileageAdd requires a service or other-charge item; BillingRateAdd requires a
    #: service item. If both `full_name` and `list_id` are provided, `full_name` is ignored.
    item_ref: Ref
    #: The lot number of the asset.
    #:
    #: Choose at most one of: `serial_number`, or `lot_number`.
    lot_number: str
    #: Quantity of items transferred.
    quantity_to_transfer: float
    #: The serial number of the asset.
    #:
    #: Choose at most one of: `serial_number`, or `lot_number`.
    serial_number: str
    #: Location within the inventory site that transfer will be sent to.
    to_inventory_site_location_ref: Ref


class _TransferInventoryLineModRequired(TypedDict):
    #: Identification number of the transaction line. (`txn_line_id` is supported as of v2.0 of
    #: the SDK. With qbXML v1.0 and v1.1, `txn_line_id` is always returned as zero.) If you need
    #: to add a new transaction line in a transaction Mod request, you can do so by setting the
    #: `txn_line_id` to -1.
    txn_line_id: str


class TransferInventoryLineMod(_TransferInventoryLineModRequired, total=False):
    #: Location within the inventory site that transfer will be taken from.
    from_inventory_site_location_ref: Ref
    #: `item_ref` may accept all item types or a restricted subset, depending on the request.
    #: Examples: PurchaseOrder and Bill do not allow discount or sales-tax items;
    #: VehicleMileageAdd requires a service or other-charge item; BillingRateAdd requires a
    #: service item. If both `full_name` and `list_id` are provided, `full_name` is ignored.
    item_ref: Ref
    #: The lot number of the asset.
    #:
    #: Choose at most one of: `serial_number`, or `lot_number`.
    lot_number: str
    #: Quantity of items transferred.
    quantity_to_transfer: float
    #: The serial number of the asset.
    #:
    #: Choose at most one of: `serial_number`, or `lot_number`.
    serial_number: str
    #: Location within the inventory site that transfer will be sent to.
    to_inventory_site_location_ref: Ref


class _TransferInventoryCreateParamsRequired(TypedDict):
    #: Inventory site that transfer will be taken from.
    from_inventory_site_ref: Ref
    #: Inventory site that transfer will be sent to.
    to_inventory_site_ref: Ref


class TransferInventoryCreateParams(_TransferInventoryCreateParamsRequired, total=False):
    """Params for ``transfer_inventory.create`` (Create transfer inventory)."""
    #: `def_macro` lets you assign a reusable name to a returned `txn_id` or `txn_line_id` so
    #: later requests can reference it with `useMacro`. This feature requires SDK 2.0+.
    def_macro: str
    #: Allows for the attachment of a user defined GUID value.
    external_guid: str
    include_ret_element: List[Literal["EditSequence", "ExternalGUID", "FromInventorySiteRef", "ListID", "Memo", "OwnerID", "RefNumber", "TimeCreated", "TimeModified", "ToInventorySiteRef", "TransferInventoryLineRet", "TxnDate", "TxnID", "TxnNumber"]]
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
    transfer_inventory_line_add: List[TransferInventoryLineAdd]
    #: The date of the transaction. In some cases, if you leave `txn_date` out of an -Add
    #: message, QuickBooks will prefill `txn_date` with the date of the last-saved transaction
    #: of the same type.
    txn_date: str


class TransferInventoryQueryParams(TypedDict, total=False):
    """Params for ``transfer_inventory.query`` (List transfer inventories)."""
    #: Filters according to the account name or `list_id`. If the “Use account numbers”
    #: preference is enabled in the QuickBooks company file, you can specify an account number
    #: (instead of an account name) for `full_name` and get the account you’re looking for. But
    #: if numbers have been used as account names, confusion could arise.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`), or
    #: `site_filter`. Members of a set combine with each other, not with the other choices.
    account_filter: EntityFilter
    #: An entity refers to a person on the QuickBooks Customer list, Vendor list, Employee list,
    #: or Other Names list. You can use an EntityQuery request to get information about all the
    #: entities that are set up in the QuickBooks file. In an ARRefundCreditCard query, this
    #: must be a customer/customer job.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`), or
    #: `site_filter`. Members of a set combine with each other, not with the other choices.
    entity_filter: EntityFilter
    #: This filter allows you to omit line items from a query response to get a smaller result.
    #: The default value is false, so line items are omitted by default. Set
    #: `include_line_items` to true to include line items in the response if you don’t mind
    #: getting a larger result.
    include_line_items: bool
    include_ret_element: List[Literal["EditSequence", "ExternalGUID", "FromInventorySiteRef", "Memo", "RefNumber", "TimeCreated", "TimeModified", "ToInventorySiteRef", "TransferInventoryLineRet", "TxnDate", "TxnID", "TxnNumber"]]
    #: Page through every match: QuBe Sync asks QuickBooks for each page in turn and sends each
    #: to your `webhook_url` as it arrives, all with the same `id`. On by default, with pages of
    #: 100 records (25 with `include_line_items`); send `iterator=true` with `max_returned` for
    #: another size. Off when you send `iterator=false` (every match in one answer) or
    #: `max_returned` alone (at most that many, in one answer). It pages a filtered query only:
    #: with `ref_number`, `ref_number_case_sensitive`, `site_filter` or `txn_id` every match
    #: comes back in one answer, so leave `iterator` out.
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
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`), or
    #: `site_filter`. Members of a set combine with each other, not with the other choices.
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
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`), or
    #: `site_filter`. Members of a set combine with each other, not with the other choices.
    modified_date_range_filter: ModifiedDateRangeFilter
    #: `ref_number` is a user-managed transaction reference (for example, a check number). It
    #: can be edited and is not guaranteed to be globally unique. Some transaction types
    #: auto-populate `ref_number` when omitted, based on QuickBooks preferences and numbering
    #: state.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`), or
    #: `site_filter`. Members of a set combine with each other, not with the other choices.
    ref_number: List[str]
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`), or
    #: `site_filter`. Members of a set combine with each other, not with the other choices.
    ref_number_case_sensitive: List[str]
    #: Filters by `ref_number` range. Numeric-only bounds are compared numerically; otherwise
    #: comparison is lexicographic.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`), or
    #: `site_filter`. Members of a set combine with each other, not with the other choices.
    ref_number_filter: RefNumberFilter
    #: Filters by `ref_number` range. Numeric-only bounds are compared numerically; otherwise
    #: comparison is lexicographic.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`), or
    #: `site_filter`. Members of a set combine with each other, not with the other choices.
    ref_number_range_filter: RefNumberRangeFilter
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: Allows you to report on Sites.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`), or
    #: `site_filter`. Members of a set combine with each other, not with the other choices.
    site_filter: CurrencyFilter
    #: Filters according to the original transaction dates.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`), or
    #: `site_filter`. Members of a set combine with each other, not with the other choices.
    txn_date_range_filter: DateRangeFilter
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`), or
    #: `site_filter`. Members of a set combine with each other, not with the other choices.
    txn_id: List[str]


class _TransferInventoryUpdateParamsRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    txn_id: str


class TransferInventoryUpdateParams(_TransferInventoryUpdateParamsRequired, total=False):
    """Params for ``transfer_inventory.update`` (Update transfer inventory)."""
    #: Inventory site that transfer will be taken from.
    from_inventory_site_ref: Ref
    include_ret_element: List[Literal["EditSequence", "ExternalGUID", "FromInventorySiteRef", "ListID", "Memo", "OwnerID", "RefNumber", "TimeCreated", "TimeModified", "ToInventorySiteRef", "TransferInventoryLineRet", "TxnDate", "TxnID", "TxnNumber"]]
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
    #: Inventory site that transfer will be sent to.
    to_inventory_site_ref: Ref
    transfer_inventory_line_mod: List[TransferInventoryLineMod]
    #: The date of the transaction. In some cases, if you leave `txn_date` out of an -Add
    #: message, QuickBooks will prefill `txn_date` with the date of the last-saved transaction
    #: of the same type.
    txn_date: str


class TransferInventory:
    """QuickBooks transfer inventory operations: create, query, update.

    Get it from ``client.transfer_inventory``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[TransferInventoryCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create transfer inventory.

        Queues ``transfer_inventory.create``: POST /connections/{connection_id}/transfer-inventories, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``TransferInventoryCreateParams``)::

            def_macro: str
            external_guid: str
            from_inventory_site_ref: Ref (required)
                full_name: str
                list_id: str
            include_ret_element: List[Literal[...] (one of 14 values)]
            memo: str
            ref_number: str
            request_id: str
            to_inventory_site_ref: Ref (required)
            transfer_inventory_line_add: List[TransferInventoryLineAdd]
                def_macro: str
                from_inventory_site_location_ref: Ref
                item_ref: Ref
                lot_number: str
                quantity_to_transfer: float
                serial_number: str
                to_inventory_site_location_ref: Ref
            txn_date: str

        Docs: https://docs.qubesync.com/api-reference/v2/transfer-inventories/create-transfer-inventory
        """
        return self._client._queue_operation("transfer_inventory.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[TransferInventoryQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List transfer inventories.

        Queues ``transfer_inventory.query``: GET /connections/{connection_id}/transfer-inventories, params in the query string.
        QuickBooks answers in pages: each page comes to ``webhook_url`` as its own webhook.
        Returns the queued request.

        Params (``TransferInventoryQueryParams``)::

            account_filter: EntityFilter
                full_name: List[str]
                full_name_with_children: str
                list_id: List[str]
                list_id_with_children: str
            entity_filter: EntityFilter
            include_line_items: bool
            include_ret_element: List[Literal[...] (one of 12 values)]
            iterator: bool
            max_returned: int
            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            modified_date_range_filter: ModifiedDateRangeFilter
                from_modified_date: str
                to_modified_date: str
            ref_number: List[str]
            ref_number_case_sensitive: List[str]
            ref_number_filter: RefNumberFilter
                match_criterion: Literal["Contains", "EndsWith", "StartsWith"] (required)
                ref_number: str (required)
            ref_number_range_filter: RefNumberRangeFilter
                from_ref_number: str
                to_ref_number: str
            request_id: str
            site_filter: CurrencyFilter
                full_name: List[str]
                list_id: List[str]
            txn_date_range_filter: DateRangeFilter
                date_macro: Literal[...] (one of 34 values)
                from_txn_date: str
                to_txn_date: str
            txn_id: List[str]

        Docs: https://docs.qubesync.com/api-reference/v2/transfer-inventories/list-transfer-inventories
        """
        return self._client._queue_operation("transfer_inventory.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[TransferInventoryUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update transfer inventory.

        Queues ``transfer_inventory.update``: PUT /connections/{connection_id}/transfer-inventories, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``TransferInventoryUpdateParams``)::

            edit_sequence: str (required)
            from_inventory_site_ref: Ref
                full_name: str
                list_id: str
            include_ret_element: List[Literal[...] (one of 14 values)]
            memo: str
            ref_number: str
            request_id: str
            to_inventory_site_ref: Ref
            transfer_inventory_line_mod: List[TransferInventoryLineMod]
                from_inventory_site_location_ref: Ref
                item_ref: Ref
                lot_number: str
                quantity_to_transfer: float
                serial_number: str
                to_inventory_site_location_ref: Ref
                txn_line_id: str (required)
            txn_date: str
            txn_id: str (required)

        Docs: https://docs.qubesync.com/api-reference/v2/transfer-inventories/update-transfer-inventory
        """
        return self._client._queue_operation("transfer_inventory.update", connection_id, params, webhook_url, idempotency_key)
