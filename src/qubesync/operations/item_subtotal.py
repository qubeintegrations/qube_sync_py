# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks item subtotal operations (``client.item_subtotal``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    ItemDiscountBarCode,
    NameFilter,
    NameRangeFilter,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _ItemSubtotalCreateParamsRequired(TypedDict):
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because FullName remains distinct.
    name: str


class ItemSubtotalCreateParams(_ItemSubtotalCreateParamsRequired, total=False):
    """Params for ``item_subtotal.create`` (Create item subtotal)."""
    #: Barcode reference information.
    bar_code: ItemDiscountBarCode
    #: Allows for the attachment of a user defined GUID value.
    external_guid: str
    include_ret_element: List[Literal["BarCodeValue", "DataExtRet", "EditSequence", "ExternalGUID", "IsActive", "ItemDesc", "ListID", "Name", "OwnerID", "SpecialItemType", "TimeCreated", "TimeModified", "TxnID", "TxnNumber"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: The description that will appear on a sales form when the item is used.
    item_desc: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class ItemSubtotalQueryParams(TypedDict, total=False):
    """Params for ``item_subtotal.query`` (List item subtotals)."""
    #: Used in filters to select list objects based on whether or not they are currently enabled
    #: for use by QuickBooks. The default value is asActiveOnly, which selects only list objects
    #: that are active.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
    #: Filters results to objects modified on or after this timestamp. QuickBooks Desktop
    #: accepts 1970-01-01 through 2038-01-19T03:14:07. If only a date is provided, time defaults
    #: to 00:00:00.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    from_modified_date: str
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    full_name: List[str]
    include_ret_element: List[Literal["BarCodeValue", "DataExtRet", "EditSequence", "ExternalGUID", "IsActive", "ItemDesc", "ListID", "Name", "SpecialItemType", "TimeCreated", "TimeModified"]]
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
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
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
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
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
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    name_filter: NameFilter
    #: Filters according to the object’s Name.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
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
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    to_modified_date: str


class _ItemSubtotalUpdateParamsRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `list_id` and FullName both identify a list object. QuickBooks assigns `list_id` when the
    #: object is created. `list_id` values are unique within a list family, not across the
    #: company file: customers, vendors, employees and other names share one sequence, every
    #: item type shares another, and each other list has its own.
    list_id: str


class ItemSubtotalUpdateParams(_ItemSubtotalUpdateParamsRequired, total=False):
    """Params for ``item_subtotal.update`` (Update item subtotal)."""
    #: Barcode reference information.
    bar_code: ItemDiscountBarCode
    include_ret_element: List[Literal["BarCodeValue", "DataExtRet", "EditSequence", "ExternalGUID", "IsActive", "ItemDesc", "ListID", "Name", "OwnerID", "SpecialItemType", "TimeCreated", "TimeModified", "TxnID", "TxnNumber"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: The description that will appear on a sales form when the item is used.
    item_desc: str
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because FullName remains distinct.
    name: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class ItemSubtotal:
    """QuickBooks item subtotal operations: create, query, update.

    Get it from ``client.item_subtotal``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[ItemSubtotalCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create item subtotal.

        Queues ``item_subtotal.create``: POST /connections/{connection_id}/item-subtotals, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``ItemSubtotalCreateParams``)::

            bar_code: ItemDiscountBarCode
                allow_override: bool
                assign_even_if_used: bool
                bar_code_value: str
            external_guid: str
            include_ret_element: List[Literal[...] (one of 14 values)]
            is_active: bool
            item_desc: str
            name: str (required)
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/item-subtotals/create-item-subtotal
        """
        return self._client._queue_operation("item_subtotal.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[ItemSubtotalQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List item subtotals.

        Queues ``item_subtotal.query``: GET /connections/{connection_id}/item-subtotals, params in the query string.
        QuickBooks answers in pages: each page comes to ``webhook_url`` as its own webhook.
        Returns the queued request.

        Params (``ItemSubtotalQueryParams``)::

            active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
            from_modified_date: str
            full_name: List[str]
            include_ret_element: List[Literal[...] (one of 11 values)]
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

        Docs: https://docs.qubesync.com/api-reference/v2/item-subtotals/list-item-subtotals
        """
        return self._client._queue_operation("item_subtotal.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[ItemSubtotalUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update item subtotal.

        Queues ``item_subtotal.update``: PUT /connections/{connection_id}/item-subtotals, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``ItemSubtotalUpdateParams``)::

            bar_code: ItemDiscountBarCode
                allow_override: bool
                assign_even_if_used: bool
                bar_code_value: str
            edit_sequence: str (required)
            include_ret_element: List[Literal[...] (one of 14 values)]
            is_active: bool
            item_desc: str
            list_id: str (required)
            name: str
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/item-subtotals/update-item-subtotal
        """
        return self._client._queue_operation("item_subtotal.update", connection_id, params, webhook_url, idempotency_key)
