# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks price level operations (``client.price_level``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    CurrencyFilter,
    NameFilter,
    NameRangeFilter,
    Ref,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _PriceLevelPerItemRequired(TypedDict):
    #: `item_ref` may accept all item types or a restricted subset, depending on the request.
    #: Examples: PurchaseOrder and Bill do not allow discount or sales-tax items;
    #: VehicleMileageAdd requires a service or other-charge item; BillingRateAdd requires a
    #: service item. If both `full_name` and `list_id` are provided, `full_name` is ignored.
    item_ref: Ref


class PriceLevelPerItem(_PriceLevelPerItemRequired, total=False):
    #: If you don’t want to apply a custom price (for price levels) or custom rate (for billing
    #: rates), you can apply an adjusted price discount using the pair of fields
    #: `adjust_percentage` and `adjust_relative_to` (AdjustBillingRateRelativeTo for billing
    #: rates).
    #:
    #: Choose exactly one of: the set (`custom_price`, `custom_price_percent`), or the set
    #: (`adjust_percentage`, `adjust_relative_to`). Members of a set combine with each other,
    #: not with the other choices.
    adjust_percentage: float
    #: When you create a price level, you have the option to create it with a flat custom price
    #: (flat amount or percentage) or you could use PriceLevelAdjustment to apply a price
    #: discount based on either the current custom price, the standard price of the item, or the
    #: cost of the item.
    #:
    #: Choose exactly one of: the set (`custom_price`, `custom_price_percent`), or the set
    #: (`adjust_percentage`, `adjust_relative_to`). Members of a set combine with each other,
    #: not with the other choices.
    adjust_relative_to: Literal["Cost", "CurrentCustomPrice", "StandardPrice"]
    #: When you create a price level, you have the option to create it with a custom price that
    #: is either a fixed amount (`custom_price`) or a fixed discount percentage
    #: (`custom_price_percent`). Alternatively, instead of a flat custom price or discount, you
    #: could apply a price discount based on either the current custom price, the standard price
    #: of the item, or the cost of the item.
    #:
    #: Choose exactly one of: the set (`custom_price`, `custom_price_percent`), or the set
    #: (`adjust_percentage`, `adjust_relative_to`). Members of a set combine with each other,
    #: not with the other choices.
    custom_price: float
    #: When you create a price level, you have the option to create it with a custom price that
    #: is either a fixed amount (`custom_price`) or a fixed discount percentage
    #: (`custom_price_percent`).
    #:
    #: Choose exactly one of: the set (`custom_price`, `custom_price_percent`), or the set
    #: (`adjust_percentage`, `adjust_relative_to`). Members of a set combine with each other,
    #: not with the other choices.
    custom_price_percent: float


class _PriceLevelCreateParamsRequired(TypedDict):
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because `full_name` remains distinct.
    name: str


class PriceLevelCreateParams(_PriceLevelCreateParamsRequired, total=False):
    """Params for ``price_level.create`` (Create price level)."""
    #: A currency record defines how QuickBooks stores and displays a currency. Built-in
    #: currency name/code values are fixed; formatting and active status can vary by settings
    #: and workflow.
    currency_ref: Ref
    include_ret_element: List[Literal["CurrencyRef", "EditSequence", "ExternalGUID", "IsActive", "ListID", "Name", "OwnerID", "PriceLevelFixedPercentage", "PriceLevelPerItemRet", "PriceLevelType", "TimeCreated", "TimeModified", "TxnID", "TxnNumber"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: When you create a price level, you must specify whether it is a fixed percentage or a per
    #: item price level. Once you create the price level, you can’t change this. QuickBooks Pro
    #: and greater versions support fixed percentages, but only QuickBooks Premier and
    #: Enterprise support the per item price level. Where is this discount applied if Price
    #: Levels are enabled in QuickBooks preferences?
    price_level_fixed_percentage: float
    price_level_per_item: List[PriceLevelPerItem]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class PriceLevelQueryParams(TypedDict, total=False):
    """Params for ``price_level.query`` (List price levels)."""
    #: Used in filters to select list objects based on whether or not they are currently enabled
    #: for use by QuickBooks. The default value is asActiveOnly, which selects only list objects
    #: that are active.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `currency_filter`, `from_modified_date`, `item_ref`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
    #: Filters by the specified currency.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `currency_filter`, `from_modified_date`, `item_ref`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    currency_filter: CurrencyFilter
    #: Filters results to objects modified on or after this timestamp. QuickBooks Desktop
    #: accepts 1970-01-01 through 2038-01-19T03:14:07. If only a date is provided, time defaults
    #: to 00:00:00.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `currency_filter`, `from_modified_date`, `item_ref`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    from_modified_date: str
    #: `full_name` (along with `list_id`) is a way to identify a list object. The `full_name` is
    #: the name prefixed by the names of each ancestor, for example Jones:Kitchen:Cabinets.
    #: `full_name` values aren’t case-sensitive.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `currency_filter`, `from_modified_date`, `item_ref`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    full_name: List[str]
    include_ret_element: List[Literal["CurrencyRef", "EditSequence", "IsActive", "ListID", "Name", "PriceLevelFixedPercentage", "PriceLevelPerItemRet", "PriceLevelType", "TimeCreated", "TimeModified"]]
    #: `item_ref` may accept all item types or a restricted subset, depending on the request.
    #: Examples: PurchaseOrder and Bill do not allow discount or sales-tax items;
    #: VehicleMileageAdd requires a service or other-charge item; BillingRateAdd requires a
    #: service item. If both `full_name` and `list_id` are provided, `full_name` is ignored.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `currency_filter`, `from_modified_date`, `item_ref`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    item_ref: Ref
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list family, not across the
    #: company file: customers, vendors, employees and other names share one sequence, every
    #: item type shares another, and each other list has its own.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `currency_filter`, `from_modified_date`, `item_ref`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    list_id: List[str]
    #: Limits the number of objects that a query returns. (To get a count of how many objects
    #: could possibly be returned, use the `meta_data` query attribute.) If you include a
    #: `max_returned` value, it must be at least 1.
    #:
    #: QuickBooks doesn't page this query: at most this many records come back, in one answer,
    #: with no sign of whether more matched. Leave it out for every match, in one answer; one
    #: over 4 MB as the Web Connector sends it, about 3 MB of qbXML isn't kept (`error_type`
    #: `response_too_large`), so narrow a large one with its filters.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `currency_filter`, `from_modified_date`, `item_ref`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    max_returned: int
    #: Use the `meta_data` attribute to control whether query responses include counts. Options
    #: are NoMetaData (default), MetaDataOnly (count only), and MetaDataAndResponseData (count
    #: plus objects). Counts are approximate and may vary slightly if records are created or
    #: deleted during processing.
    meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
    #: Filters according to the object’s Name.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `currency_filter`, `from_modified_date`, `item_ref`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    name_filter: NameFilter
    #: Filters according to the object’s Name.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `currency_filter`, `from_modified_date`, `item_ref`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    name_range_filter: NameRangeFilter
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: Filters results to objects modified on or before this timestamp. QuickBooks Desktop
    #: accepts 1970-01-01 through 2038-01-19T03:14:07. If only a date is provided, time defaults
    #: to end-of-day (23:59:59).
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `currency_filter`, `from_modified_date`, `item_ref`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    to_modified_date: str


class _PriceLevelUpdateParamsRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list family, not across the
    #: company file: customers, vendors, employees and other names share one sequence, every
    #: item type shares another, and each other list has its own.
    list_id: str


class PriceLevelUpdateParams(_PriceLevelUpdateParamsRequired, total=False):
    """Params for ``price_level.update`` (Update price level)."""
    #: A currency record defines how QuickBooks stores and displays a currency. Built-in
    #: currency name/code values are fixed; formatting and active status can vary by settings
    #: and workflow.
    #:
    #: Choose at most one of: `price_level_fixed_percentage`, or the set (`currency_ref`,
    #: `price_level_per_item`). Members of a set combine with each other, not with the other
    #: choices.
    currency_ref: Ref
    include_ret_element: List[Literal["CurrencyRef", "EditSequence", "ExternalGUID", "IsActive", "ListID", "Name", "OwnerID", "PriceLevelFixedPercentage", "PriceLevelPerItemRet", "PriceLevelType", "TimeCreated", "TimeModified", "TxnID", "TxnNumber"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because `full_name` remains distinct.
    name: str
    #: When you create a price level, you must specify whether it is a fixed percentage or a per
    #: item price level. Once you create the price level, you can’t change this. QuickBooks Pro
    #: and greater versions support fixed percentages, but only QuickBooks Premier and
    #: Enterprise support the per item price level. Where is this discount applied if Price
    #: Levels are enabled in QuickBooks preferences?
    #:
    #: Choose at most one of: `price_level_fixed_percentage`, or the set (`currency_ref`,
    #: `price_level_per_item`). Members of a set combine with each other, not with the other
    #: choices.
    price_level_fixed_percentage: float
    #: Choose at most one of: `price_level_fixed_percentage`, or the set (`currency_ref`,
    #: `price_level_per_item`). Members of a set combine with each other, not with the other
    #: choices.
    price_level_per_item: List[PriceLevelPerItem]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class PriceLevel:
    """QuickBooks price level operations: create, query, update.

    Get it from ``client.price_level``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[PriceLevelCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create price level.

        Queues ``price_level.create``: POST /connections/{connection_id}/price-levels, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``PriceLevelCreateParams``)::

            currency_ref: Ref
                full_name: str
                list_id: str
            include_ret_element: List[Literal[...] (one of 14 values)]
            is_active: bool
            name: str (required)
            price_level_fixed_percentage: float
            price_level_per_item: List[PriceLevelPerItem]
                adjust_percentage: float
                adjust_relative_to: Literal["Cost", "CurrentCustomPrice", "StandardPrice"]
                custom_price: float
                custom_price_percent: float
                item_ref: Ref (required)
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/price-levels/create-price-level
        """
        return self._client._queue_operation("price_level.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[PriceLevelQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List price levels.

        Queues ``price_level.query``: GET /connections/{connection_id}/price-levels, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``PriceLevelQueryParams``)::

            active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
            currency_filter: CurrencyFilter
                full_name: List[str]
                list_id: List[str]
            from_modified_date: str
            full_name: List[str]
            include_ret_element: List[Literal[...] (one of 10 values)]
            item_ref: Ref
                full_name: str
                list_id: str
            list_id: List[str]
            max_returned: int
            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            name_filter: NameFilter
                match_criterion: Literal["Contains", "EndsWith", "StartsWith"] (required)
                name: str (required)
            name_range_filter: NameRangeFilter
                from_name: str
                to_name: str
            request_id: str
            to_modified_date: str

        Docs: https://docs.qubesync.com/api-reference/v2/price-levels/list-price-levels
        """
        return self._client._queue_operation("price_level.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[PriceLevelUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update price level.

        Queues ``price_level.update``: PUT /connections/{connection_id}/price-levels, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``PriceLevelUpdateParams``)::

            currency_ref: Ref
                full_name: str
                list_id: str
            edit_sequence: str (required)
            include_ret_element: List[Literal[...] (one of 14 values)]
            is_active: bool
            list_id: str (required)
            name: str
            price_level_fixed_percentage: float
            price_level_per_item: List[PriceLevelPerItem]
                adjust_percentage: float
                adjust_relative_to: Literal["Cost", "CurrentCustomPrice", "StandardPrice"]
                custom_price: float
                custom_price_percent: float
                item_ref: Ref (required)
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/price-levels/update-price-level
        """
        return self._client._queue_operation("price_level.update", connection_id, params, webhook_url, idempotency_key)
