# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks date driven terms operations (``client.date_driven_terms``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    NameFilter,
    NameRangeFilter,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _DateDrivenTermsCreateParamsRequired(TypedDict):
    #: The day of the month when full payment is due with no discount.
    day_of_month_due: int
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because FullName remains distinct.
    name: str


class DateDrivenTermsCreateParams(_DateDrivenTermsCreateParamsRequired, total=False):
    """Params for ``date_driven_terms.create`` (Create date driven terms)."""
    #: If the payment is made by this day of the month, then `discount_pct` applies.
    discount_day_of_month: int
    #: If payment is received by `discount_day_of_month`, then this discount will apply to the
    #: payment. `discount_pct` must be between 0 and 100.
    discount_pct: float
    #: Handles cases when an invoice or bill is issued close to its due date. If the invoice or
    #: bill is issued within this many days of the due date, payment isn’t due until the
    #: following month. For example, with a `day_of_month_due` of 15 and a `due_next_month_days`
    #: of 2, an invoice issued on May 13th wouldn’t be due until June 15th.
    due_next_month_days: int
    include_ret_element: List[Literal["DayOfMonthDue", "DiscountDayOfMonth", "DiscountPct", "DueNextMonthDays", "EditSequence", "ExternalGUID", "IsActive", "ListID", "Name", "OwnerID", "TimeCreated", "TimeModified", "TxnID", "TxnNumber"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class DateDrivenTermsQueryParams(TypedDict, total=False):
    """Params for ``date_driven_terms.query`` (List date driven terms)."""
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
    include_ret_element: List[Literal["DayOfMonthDue", "DiscountDayOfMonth", "DiscountPct", "DueNextMonthDays", "EditSequence", "IsActive", "ListID", "Name", "TimeCreated", "TimeModified"]]
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
    #: QuickBooks doesn't page this query: at most this many records come back, in one answer,
    #: with no sign of whether more matched. Leave it out for every match, in one answer; one
    #: over 4 MB as the Web Connector sends it, about 3 MB of qbXML isn't kept (`error_type`
    #: `response_too_large`), so narrow a large one with its filters.
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


class DateDrivenTerms:
    """QuickBooks date driven terms operations: create, query.

    Get it from ``client.date_driven_terms``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[DateDrivenTermsCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create date driven terms.

        Queues ``date_driven_terms.create``: POST /connections/{connection_id}/date-driven-terms, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``DateDrivenTermsCreateParams``)::

            day_of_month_due: int (required)
            discount_day_of_month: int
            discount_pct: float
            due_next_month_days: int
            include_ret_element: List[Literal[...] (one of 14 values)]
            is_active: bool
            name: str (required)
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/date-driven-terms/create-date-driven-terms
        """
        return self._client._queue_operation("date_driven_terms.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[DateDrivenTermsQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List date driven terms.

        Queues ``date_driven_terms.query``: GET /connections/{connection_id}/date-driven-terms, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``DateDrivenTermsQueryParams``)::

            active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
            from_modified_date: str
            full_name: List[str]
            include_ret_element: List[Literal[...] (one of 10 values)]
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

        Docs: https://docs.qubesync.com/api-reference/v2/date-driven-terms/list-date-driven-terms
        """
        return self._client._queue_operation("date_driven_terms.query", connection_id, params, webhook_url, idempotency_key)
