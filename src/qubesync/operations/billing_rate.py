# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks billing rate operations (``client.billing_rate``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    NameFilter,
    NameRangeFilter,
    Ref,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _BillingRatePerItemRequired(TypedDict):
    #: `item_ref` may accept all item types or a restricted subset, depending on the request.
    #: Examples: PurchaseOrder and Bill do not allow discount or sales-tax items;
    #: VehicleMileageAdd requires a service or other-charge item; BillingRateAdd requires a
    #: service item. If both `full_name` and `list_id` are provided, `full_name` is ignored.
    item_ref: Ref


class BillingRatePerItem(_BillingRatePerItemRequired, total=False):
    #: Specifies the service item rate that `adjust_percentage` is applied to. Normally, this is
    #: set to StandardRate.
    #:
    #: Choose exactly one of: the set (`custom_rate`, `custom_rate_percent`), or the set
    #: (`adjust_billing_rate_relative_to`, `adjust_percentage`). Members of a set combine with
    #: each other, not with the other choices.
    adjust_billing_rate_relative_to: Literal["CurrentCustomRate", "StandardRate"]
    #: If you don’t want to apply a custom price (for price levels) or custom rate (for billing
    #: rates), you can apply an adjusted price discount using the pair of fields
    #: `adjust_percentage` and AdjustRelativeTo (`adjust_billing_rate_relative_to` for billing
    #: rates).
    #:
    #: Choose exactly one of: the set (`custom_rate`, `custom_rate_percent`), or the set
    #: (`adjust_billing_rate_relative_to`, `adjust_percentage`). Members of a set combine with
    #: each other, not with the other choices.
    adjust_percentage: float
    #: The value specified here overrides the rate of the service item referenced in this
    #: aggregate (in the `item_ref`) with the rate you specify here. If instead you wanted a
    #: rate that is a percentage higher or lower than the service item rate, you wouldn’t use
    #: `custom_rate`, but you would use `adjust_percentage` and
    #: `adjust_billing_rate_relative_to`.
    #:
    #: Choose exactly one of: the set (`custom_rate`, `custom_rate_percent`), or the set
    #: (`adjust_billing_rate_relative_to`, `adjust_percentage`). Members of a set combine with
    #: each other, not with the other choices.
    custom_rate: float
    #: Using this field with BillingRateAdd will work only if the service item itself is set to
    #: a percentage, not to an amount. If you attempt to set the Billing Rate to a percentage
    #: for a service item that has an amount for the Rate, you will get an error. The kind of
    #: rate you have on the service item determines the kind of billing rate you may have on
    #: that item.
    #:
    #: Choose exactly one of: the set (`custom_rate`, `custom_rate_percent`), or the set
    #: (`adjust_billing_rate_relative_to`, `adjust_percentage`). Members of a set combine with
    #: each other, not with the other choices.
    custom_rate_percent: float


class _BillingRateCreateParamsRequired(TypedDict):
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because `full_name` remains distinct.
    name: str


class BillingRateCreateParams(_BillingRateCreateParamsRequired, total=False):
    """Params for ``billing_rate.create`` (Create billing rate)."""
    billing_rate_per_item: List[BillingRatePerItem]
    #: You use `fixed_billing_rate` if you want the rate to override all service items rates.
    #: Consequently, there is no need to specify any service items (and in fact you can’t
    #: specify them) if you use this element.
    fixed_billing_rate: float
    include_ret_element: List[Literal["BillingRatePerItemRet", "BillingRateType", "EditSequence", "ExternalGUID", "FixedBillingRate", "ListID", "Name", "OwnerID", "TimeCreated", "TimeModified", "TxnID", "TxnNumber"]]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class BillingRateQueryParams(TypedDict, total=False):
    """Params for ``billing_rate.query`` (List billing rates)."""
    #: Filters results to objects modified on or after this timestamp. QuickBooks Desktop
    #: accepts 1970-01-01 through 2038-01-19T03:14:07. If only a date is provided, time defaults
    #: to 00:00:00.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`from_modified_date`,
    #: `item_ref`, `max_returned`, `name_filter`, `name_range_filter`, `to_modified_date`).
    #: Members of a set combine with each other, not with the other choices.
    from_modified_date: str
    #: `full_name` (along with `list_id`) is a way to identify a list object. The `full_name` is
    #: the name prefixed by the names of each ancestor, for example Jones:Kitchen:Cabinets.
    #: `full_name` values aren’t case-sensitive.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`from_modified_date`,
    #: `item_ref`, `max_returned`, `name_filter`, `name_range_filter`, `to_modified_date`).
    #: Members of a set combine with each other, not with the other choices.
    full_name: List[str]
    include_ret_element: List[Literal["BillingRatePerItemRet", "BillingRateType", "EditSequence", "FixedBillingRate", "ListID", "Name", "TimeCreated", "TimeModified"]]
    #: `item_ref` may accept all item types or a restricted subset, depending on the request.
    #: Examples: PurchaseOrder and Bill do not allow discount or sales-tax items;
    #: VehicleMileageAdd requires a service or other-charge item; BillingRateAdd requires a
    #: service item. If both `full_name` and `list_id` are provided, `full_name` is ignored.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`from_modified_date`,
    #: `item_ref`, `max_returned`, `name_filter`, `name_range_filter`, `to_modified_date`).
    #: Members of a set combine with each other, not with the other choices.
    item_ref: Ref
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list family, not across the
    #: company file: customers, vendors, employees and other names share one sequence, every
    #: item type shares another, and each other list has its own.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`from_modified_date`,
    #: `item_ref`, `max_returned`, `name_filter`, `name_range_filter`, `to_modified_date`).
    #: Members of a set combine with each other, not with the other choices.
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
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`from_modified_date`,
    #: `item_ref`, `max_returned`, `name_filter`, `name_range_filter`, `to_modified_date`).
    #: Members of a set combine with each other, not with the other choices.
    max_returned: int
    #: Use the `meta_data` attribute to control whether query responses include counts. Options
    #: are NoMetaData (default), MetaDataOnly (count only), and MetaDataAndResponseData (count
    #: plus objects). Counts are approximate and may vary slightly if records are created or
    #: deleted during processing.
    meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
    #: Filters according to the object’s Name.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`from_modified_date`,
    #: `item_ref`, `max_returned`, `name_filter`, `name_range_filter`, `to_modified_date`).
    #: Members of a set combine with each other, not with the other choices.
    name_filter: NameFilter
    #: Filters according to the object’s Name.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`from_modified_date`,
    #: `item_ref`, `max_returned`, `name_filter`, `name_range_filter`, `to_modified_date`).
    #: Members of a set combine with each other, not with the other choices.
    name_range_filter: NameRangeFilter
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: Filters results to objects modified on or before this timestamp. QuickBooks Desktop
    #: accepts 1970-01-01 through 2038-01-19T03:14:07. If only a date is provided, time defaults
    #: to end-of-day (23:59:59).
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`from_modified_date`,
    #: `item_ref`, `max_returned`, `name_filter`, `name_range_filter`, `to_modified_date`).
    #: Members of a set combine with each other, not with the other choices.
    to_modified_date: str


class BillingRate:
    """QuickBooks billing rate operations: create, query.

    Get it from ``client.billing_rate``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[BillingRateCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create billing rate.

        Queues ``billing_rate.create``: POST /connections/{connection_id}/billing-rates, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``BillingRateCreateParams``)::

            billing_rate_per_item: List[BillingRatePerItem]
                adjust_billing_rate_relative_to: Literal["CurrentCustomRate", "StandardRate"]
                adjust_percentage: float
                custom_rate: float
                custom_rate_percent: float
                item_ref: Ref (required)
                    full_name: str
                    list_id: str
            fixed_billing_rate: float
            include_ret_element: List[Literal[...] (one of 12 values)]
            name: str (required)
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/billing-rates/create-billing-rate
        """
        return self._client._queue_operation("billing_rate.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[BillingRateQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List billing rates.

        Queues ``billing_rate.query``: GET /connections/{connection_id}/billing-rates, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``BillingRateQueryParams``)::

            from_modified_date: str
            full_name: List[str]
            include_ret_element: List[Literal[...] (one of 8 values)]
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

        Docs: https://docs.qubesync.com/api-reference/v2/billing-rates/list-billing-rates
        """
        return self._client._queue_operation("billing_rate.query", connection_id, params, webhook_url, idempotency_key)
