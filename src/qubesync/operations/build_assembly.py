# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks build assembly operations (``client.build_assembly``)."""

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


class _BuildAssemblyCreateParamsRequired(TypedDict):
    #: An inventory assembly item is one that is assembled or manufactured from inventory items.
    #: The items and/or assemblies that make up the assembly are called components. For Premier,
    #: an assembly can have a maximum of 100 components. For Enterprise, the maximum is 500
    #: components.
    item_inventory_assembly_ref: Ref
    #: Specifies the number of assemblies to be built. The transaction will fail if the number
    #: specified here exceeds the number of on-hand components.
    quantity_to_build: float


class BuildAssemblyCreateParams(_BuildAssemblyCreateParamsRequired, total=False):
    """Params for ``build_assembly.create`` (Create build assembly)."""
    #: `def_macro` lets you assign a reusable name to a returned `txn_id` or TxnLineID so later
    #: requests can reference it with `useMacro`. This feature requires SDK 2.0+.
    def_macro: str
    #: Allows for the attachment of a user defined GUID value.
    external_guid: str
    include_ret_element: List[Literal["ComponentItemLineRet", "DataExtRet", "EditSequence", "ExpirationDateForSerialLotNumber", "ExternalGUID", "InventorySiteLocationRef", "InventorySiteRef", "IsPending", "ItemInventoryAssemblyRef", "ListID", "LotNumber", "Memo", "OwnerID", "QuantityCanBuild", "QuantityOnHand", "QuantityOnSalesOrder", "QuantityToBuild", "RefNumber", "SerialNumber", "TimeCreated", "TimeModified", "TxnDate", "TxnID", "TxnNumber"]]
    #: Location within the Inventory Site
    inventory_site_location_ref: Ref
    #: Site where inventory is located.
    inventory_site_ref: Ref
    #: The lot number of the asset.
    #:
    #: Choose at most one of: `serial_number`, or `lot_number`.
    lot_number: str
    #: Allows the build assembly to be marked pending if there are insufficient quantities to
    #: complete the build assembly.
    mark_pending_if_required: bool
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
    #: The serial number of the asset.
    #:
    #: Choose at most one of: `serial_number`, or `lot_number`.
    serial_number: str
    #: The date of the transaction. In some cases, if you leave `txn_date` out of an -Add
    #: message, QuickBooks will prefill `txn_date` with the date of the last-saved transaction
    #: of the same type.
    txn_date: str


class BuildAssemblyQueryParams(TypedDict, total=False):
    """Params for ``build_assembly.query`` (List build assemblies)."""
    #: Specify “true” if component line items for each returned transaction are to be included
    #: in the returned data. Specify “false” if the line items aren’t be returned.
    include_component_line_items: bool
    include_ret_element: List[Literal["ComponentItemLineRet", "DataExtRet", "EditSequence", "ExpirationDateForSerialLotNumber", "ExternalGUID", "InventorySiteLocationRef", "InventorySiteRef", "IsPending", "ItemInventoryAssemblyRef", "LotNumber", "Memo", "QuantityCanBuild", "QuantityOnHand", "QuantityOnSalesOrder", "QuantityToBuild", "RefNumber", "SerialNumber", "TimeCreated", "TimeModified", "TxnDate", "TxnID", "TxnNumber"]]
    #: Filters according to the item name or ID. You can use an ItemQuery request to get
    #: information about all the items that are set up in the QuickBooks file. “Items” are line
    #: items used for fast entry on sales and purchase forms. They include services and goods
    #: that a business buys and sells, as well as special items that perform calculations–for
    #: example, subtotal, discount, and sales-tax items.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`item_filter`, `max_returned`, `modified_date_range_filter`, `pending_status`,
    #: `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`). Members of a
    #: set combine with each other, not with the other choices.
    item_filter: EntityFilter
    #: Page through every match: QuBe Sync asks QuickBooks for each page in turn and sends each
    #: to your `webhook_url` as it arrives, all with the same `id`. On by default, with pages of
    #: 100 records; send `iterator=true` with `max_returned` for another size. Off when you send
    #: `iterator=false` (every match in one answer) or `max_returned` alone (at most that many,
    #: in one answer). It pages a filtered query only: with `ref_number`,
    #: `ref_number_case_sensitive` or `txn_id` every match comes back in one answer, so leave
    #: `iterator` out.
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
    #: set (`item_filter`, `max_returned`, `modified_date_range_filter`, `pending_status`,
    #: `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`). Members of a
    #: set combine with each other, not with the other choices.
    max_returned: int
    #: Use the `meta_data` attribute to control whether query responses include counts. Options
    #: are NoMetaData (default), MetaDataOnly (count only), and MetaDataAndResponseData (count
    #: plus objects). Counts are approximate and may vary slightly if records are created or
    #: deleted during processing.
    meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
    #: Filters according to the dates when transactions were last modified. The
    #: `modified_date_range_filter` aggregate isn’t required to contain any elements, but if it
    #: is empty, we recommend that you leave it out altogether.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`item_filter`, `max_returned`, `modified_date_range_filter`, `pending_status`,
    #: `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`). Members of a
    #: set combine with each other, not with the other choices.
    modified_date_range_filter: ModifiedDateRangeFilter
    #: `owner_id` identifies who owns the data extension. Use 0 for QuickBooks custom fields
    #: that appear in the UI, or use a GUID for private extensions owned by an app. Keep private
    #: GUIDs confidential unless you intentionally share extensions across apps. If you do share
    #: them, both apps must use the same `owner_id` and `data_ext_name`, because that pair
    #: uniquely identifies the extension.
    owner_id: List[str]
    #: Specifies whether the transaction is pending (posted) or not.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`item_filter`, `max_returned`, `modified_date_range_filter`, `pending_status`,
    #: `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`). Members of a
    #: set combine with each other, not with the other choices.
    pending_status: Literal["All", "NotPendingOnly", "PendingOnly"]
    #: `ref_number` is a user-managed transaction reference (for example, a check number). It
    #: can be edited and is not guaranteed to be globally unique. Some transaction types
    #: auto-populate `ref_number` when omitted, based on QuickBooks preferences and numbering
    #: state.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`item_filter`, `max_returned`, `modified_date_range_filter`, `pending_status`,
    #: `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`). Members of a
    #: set combine with each other, not with the other choices.
    ref_number: List[str]
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`item_filter`, `max_returned`, `modified_date_range_filter`, `pending_status`,
    #: `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`). Members of a
    #: set combine with each other, not with the other choices.
    ref_number_case_sensitive: List[str]
    #: Filters by `ref_number` range. Numeric-only bounds are compared numerically; otherwise
    #: comparison is lexicographic.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`item_filter`, `max_returned`, `modified_date_range_filter`, `pending_status`,
    #: `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`). Members of a
    #: set combine with each other, not with the other choices.
    ref_number_filter: RefNumberFilter
    #: Filters by `ref_number` range. Numeric-only bounds are compared numerically; otherwise
    #: comparison is lexicographic.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`item_filter`, `max_returned`, `modified_date_range_filter`, `pending_status`,
    #: `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`). Members of a
    #: set combine with each other, not with the other choices.
    ref_number_range_filter: RefNumberRangeFilter
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: Filters according to the original transaction dates.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`item_filter`, `max_returned`, `modified_date_range_filter`, `pending_status`,
    #: `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`). Members of a
    #: set combine with each other, not with the other choices.
    txn_date_range_filter: DateRangeFilter
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`item_filter`, `max_returned`, `modified_date_range_filter`, `pending_status`,
    #: `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`). Members of a
    #: set combine with each other, not with the other choices.
    txn_id: List[str]


class _BuildAssemblyUpdateParamsRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    txn_id: str


class BuildAssemblyUpdateParams(_BuildAssemblyUpdateParamsRequired, total=False):
    """Params for ``build_assembly.update`` (Update build assembly)."""
    include_ret_element: List[Literal["ComponentItemLineRet", "DataExtRet", "EditSequence", "ExpirationDateForSerialLotNumber", "ExternalGUID", "InventorySiteLocationRef", "InventorySiteRef", "IsPending", "ItemInventoryAssemblyRef", "ListID", "LotNumber", "Memo", "OwnerID", "QuantityCanBuild", "QuantityOnHand", "QuantityOnSalesOrder", "QuantityToBuild", "RefNumber", "SerialNumber", "TimeCreated", "TimeModified", "TxnDate", "TxnID", "TxnNumber"]]
    #: Location within the Inventory Site
    inventory_site_location_ref: Ref
    #: Site where inventory is located.
    inventory_site_ref: Ref
    #: The lot number of the asset.
    #:
    #: Choose at most one of: `serial_number`, or `lot_number`.
    lot_number: str
    #: Allows the build assembly to be marked pending if there are insufficient quantities to
    #: complete the build assembly.
    mark_pending_if_required: bool
    #: Additional information.
    memo: str
    #: Specifies the number of assemblies to be built. The transaction will fail if the number
    #: specified here exceeds the number of on-hand components.
    quantity_to_build: float
    #: `ref_number` is a user-managed transaction reference (for example, a check number). It
    #: can be edited and is not guaranteed to be globally unique. Some transaction types
    #: auto-populate `ref_number` when omitted, based on QuickBooks preferences and numbering
    #: state.
    ref_number: str
    #: Changes the transaction’s pending status from Pending to non pending. In BuildAssembly
    #: transactions, this effectively does the build transaction. Hence, removing the Pending
    #: status will fail if there aren’t enough components on hand for the build.
    remove_pending: bool
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: The serial number of the asset.
    #:
    #: Choose at most one of: `serial_number`, or `lot_number`.
    serial_number: str
    #: The date of the transaction. In some cases, if you leave `txn_date` out of an -Add
    #: message, QuickBooks will prefill `txn_date` with the date of the last-saved transaction
    #: of the same type.
    txn_date: str


class BuildAssembly:
    """QuickBooks build assembly operations: create, query, update.

    Get it from ``client.build_assembly``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[BuildAssemblyCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create build assembly.

        Queues ``build_assembly.create``: POST /connections/{connection_id}/build-assemblies, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``BuildAssemblyCreateParams``)::

            def_macro: str
            external_guid: str
            include_ret_element: List[Literal[...] (one of 24 values)]
            inventory_site_location_ref: Ref
                full_name: str
                list_id: str
            inventory_site_ref: Ref
            item_inventory_assembly_ref: Ref (required)
            lot_number: str
            mark_pending_if_required: bool
            memo: str
            quantity_to_build: float (required)
            ref_number: str
            request_id: str
            serial_number: str
            txn_date: str

        Docs: https://docs.qubesync.com/api-reference/v2/build-assemblies/create-build-assembly
        """
        return self._client._queue_operation("build_assembly.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[BuildAssemblyQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List build assemblies.

        Queues ``build_assembly.query``: GET /connections/{connection_id}/build-assemblies, params in the query string.
        QuickBooks answers in pages: each page comes to ``webhook_url`` as its own webhook.
        Returns the queued request.

        Params (``BuildAssemblyQueryParams``)::

            include_component_line_items: bool
            include_ret_element: List[Literal[...] (one of 22 values)]
            item_filter: EntityFilter
                full_name: List[str]
                full_name_with_children: str
                list_id: List[str]
                list_id_with_children: str
            iterator: bool
            max_returned: int
            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            modified_date_range_filter: ModifiedDateRangeFilter
                from_modified_date: str
                to_modified_date: str
            owner_id: List[str]
            pending_status: Literal["All", "NotPendingOnly", "PendingOnly"]
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

        Docs: https://docs.qubesync.com/api-reference/v2/build-assemblies/list-build-assemblies
        """
        return self._client._queue_operation("build_assembly.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[BuildAssemblyUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update build assembly.

        Queues ``build_assembly.update``: PUT /connections/{connection_id}/build-assemblies, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``BuildAssemblyUpdateParams``)::

            edit_sequence: str (required)
            include_ret_element: List[Literal[...] (one of 24 values)]
            inventory_site_location_ref: Ref
                full_name: str
                list_id: str
            inventory_site_ref: Ref
            lot_number: str
            mark_pending_if_required: bool
            memo: str
            quantity_to_build: float
            ref_number: str
            remove_pending: bool
            request_id: str
            serial_number: str
            txn_date: str
            txn_id: str (required)

        Docs: https://docs.qubesync.com/api-reference/v2/build-assemblies/update-build-assembly
        """
        return self._client._queue_operation("build_assembly.update", connection_id, params, webhook_url, idempotency_key)
