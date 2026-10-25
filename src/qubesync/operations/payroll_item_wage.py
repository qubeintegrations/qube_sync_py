# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks payroll item wage operations (``client.payroll_item_wage``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    NameFilter,
    NameRangeFilter,
    Ref,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _PayrollItemWageCreateParamsRequired(TypedDict):
    #: Refers to an expense account. If an `expense_account_ref` aggregate includes both
    #: `full_name` and `list_id`, `full_name` will be ignored.
    expense_account_ref: Ref
    #: Description of the wage: for example, Regular Pay or Overtime Pay.
    name: str
    #: The type of pay.
    wage_type: Literal["Bonus", "Commission", "HourlyOvertime", "HourlyRegular", "HourlySick", "HourlyVacation", "SalaryRegular", "SalarySick", "SalaryVacation"]


class PayrollItemWageCreateParams(_PayrollItemWageCreateParamsRequired, total=False):
    """Params for ``payroll_item_wage.create`` (Create payroll item wage)."""
    include_ret_element: List[Literal["EditSequence", "ExpenseAccountRef", "IsActive", "ListID", "Name", "OvertimeMultiplier", "PayrollItemDetailTypeValue", "Rate", "RatePercent", "TimeCreated", "TimeModified", "WageType"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class PayrollItemWageQueryParams(TypedDict, total=False):
    """Params for ``payroll_item_wage.query`` (List payroll item wages)."""
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
    #: `full_name` (along with `list_id`) is a way to identify a list object. The `full_name` is
    #: the name prefixed by the names of each ancestor, for example Jones:Kitchen:Cabinets.
    #: `full_name` values aren’t case-sensitive.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    full_name: List[str]
    include_ret_element: List[Literal["EditSequence", "ExpenseAccountRef", "IsActive", "ListID", "Name", "OvertimeMultiplier", "PayrollItemDetailTypeValue", "Rate", "RatePercent", "TimeCreated", "TimeModified", "WageType"]]
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list type, not globally
    #: across all lists. If both `full_name` and `list_id` are supplied in a request, QuickBooks
    #: uses `list_id` and ignores `full_name`.
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


class _PayrollItemWageUpdateParamsRequired(TypedDict):
    edit_sequence: str
    list_id: str


class PayrollItemWageUpdateParams(_PayrollItemWageUpdateParamsRequired, total=False):
    """Params for ``payroll_item_wage.update`` (Update payroll item wage)."""
    expense_account_ref: Ref
    include_ret_element: List[Literal["EditSequence", "ExpenseAccountRef", "IsActive", "ListID", "Name", "OvertimeMultiplier", "PayrollItemDetailTypeValue", "Rate", "RatePercent", "TimeCreated", "TimeModified", "WageType"]]
    is_active: bool
    name: str
    overtime_multiplier: float
    payroll_item_detail_type_value: int
    #: Choose at most one of: `rate`, or `rate_percent`.
    rate: float
    #: Choose at most one of: `rate`, or `rate_percent`.
    rate_percent: float
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class PayrollItemWage:
    """QuickBooks payroll item wage operations: create, query, update.

    Get it from ``client.payroll_item_wage``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[PayrollItemWageCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create payroll item wage.

        Queues ``payroll_item_wage.create``: POST /connections/{connection_id}/payroll-item-wages, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``PayrollItemWageCreateParams``)::

            expense_account_ref: Ref (required)
                full_name: str
                list_id: str
            include_ret_element: List[Literal[...] (one of 12 values)]
            is_active: bool
            name: str (required)
            request_id: str
            wage_type: Literal[...] (one of 9 values) (required)

        Docs: https://docs.qubesync.com/api-reference/v2/payroll-item-wages/create-payroll-item-wage
        """
        return self._client._queue_operation("payroll_item_wage.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[PayrollItemWageQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List payroll item wages.

        Queues ``payroll_item_wage.query``: GET /connections/{connection_id}/payroll-item-wages, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``PayrollItemWageQueryParams``)::

            active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
            from_modified_date: str
            full_name: List[str]
            include_ret_element: List[Literal[...] (one of 12 values)]
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

        Docs: https://docs.qubesync.com/api-reference/v2/payroll-item-wages/list-payroll-item-wages
        """
        return self._client._queue_operation("payroll_item_wage.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[PayrollItemWageUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update payroll item wage.

        Queues ``payroll_item_wage.update``: PUT /connections/{connection_id}/payroll-item-wages, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``PayrollItemWageUpdateParams``)::

            edit_sequence: str (required)
            expense_account_ref: Ref
                full_name: str
                list_id: str
            include_ret_element: List[Literal[...] (one of 12 values)]
            is_active: bool
            list_id: str (required)
            name: str
            overtime_multiplier: float
            payroll_item_detail_type_value: int
            rate: float
            rate_percent: float
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/payroll-item-wages/update-payroll-item-wage
        """
        return self._client._queue_operation("payroll_item_wage.update", connection_id, params, webhook_url, idempotency_key)
