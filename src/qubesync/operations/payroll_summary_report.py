# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks payroll summary report operations (``client.payroll_summary_report``)."""

from typing import Any, Dict, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    AccountFilter,
    EntityFilter,
    ItemFilter,
    ReportEntityFilter,
    ReportModifiedDateRangeFilter,
    ReportPeriod,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _PayrollSummaryReportQueryParamsRequired(TypedDict):
    #: The type of payroll report: psrtEmployeeEarningsSummary This report shows information
    #: similar to the payroll summary report, but in a different layout.
    payroll_summary_report_type: Literal["EmployeeEarningsSummary", "PayrollLiabilityBalances", "PayrollSummary"]


class PayrollSummaryReportQueryParams(_PayrollSummaryReportQueryParamsRequired, total=False):
    """Params for ``payroll_summary_report.query`` (List payroll summary reports)."""
    #: Set `display_report` to true to display this report within the QuickBooks UI. (Default is
    #: false.) If you want the request to display the report without returning any data to your
    #: application, set the responseData attribute to includeNone.
    display_report: bool
    #: The default value is false, which means that the report won’t include any subcolumn
    #: information. To include all available types of subcolumns for this report, set
    #: `include_subcolumns` to true. The SDK won’t return subcolumn information for data that
    #: can be easily computed. (For example, the SDK doesn’t return the “percent of row”
    #: column.)
    include_subcolumns: bool
    #: Allows you to query for a specified account type or for specific list elements.
    report_account_filter: AccountFilter
    #: Specifies the type of year that will be used for this report.
    report_calendar: Literal["CalendarYear", "FiscalYear", "TaxYear"]
    #: Allows you to query for a specified class. Classes can be used to separate transactions
    #: into meaningful categories. (For example, transactions could be classified according to
    #: department, business location, or type of work.) In QuickBooks, class tracking is off by
    #: default.
    report_class_filter: EntityFilter
    #: The time period covered by this report.
    #:
    #: Choose at most one of: `report_period`, or `report_date_macro`.
    report_date_macro: Literal["All", "LastMonth", "LastMonthToDate", "LastQuarter", "LastQuarterToDate", "LastWeek", "LastWeekToDate", "LastYear", "LastYearToDate", "NextFourWeeks", "NextMonth", "NextQuarter", "NextWeek", "NextYear", "ThisMonth", "ThisMonthToDate", "ThisQuarter", "ThisQuarterToDate", "ThisWeek", "ThisWeekToDate", "ThisYear", "ThisYearToDate", "Today", "Yesterday"]
    #: The level of detail to include in the report.
    report_detail_level_filter: Literal["All", "AllExceptSummary", "SummaryOnly"]
    #: Allows you to query for a specified name type (customer, employee, vendor, or other) or
    #: query for specific list elements.
    report_entity_filter: ReportEntityFilter
    #: Allows you to query for a specified item type (for example, discount, inventory, or
    #: non-inventory) or query for specific list elements.
    report_item_filter: ItemFilter
    #: Returns reports that were modified between these two dates (inclusive). The range of
    #: acceptable dates for both `from_report_modified_date` and `to_report_modified_date` is
    #: 1970-01-01 to 2038-01-19T03:14:07 (2038-01-18T19:14:07-08:00 PST).
    #:
    #: Choose at most one of: `report_modified_date_range_filter`, or
    #: `report_modified_date_range_macro`.
    report_modified_date_range_filter: ReportModifiedDateRangeFilter
    #: The time period covered by this report.
    #:
    #: Choose at most one of: `report_modified_date_range_filter`, or
    #: `report_modified_date_range_macro`.
    report_modified_date_range_macro: Literal["All", "LastMonth", "LastMonthToDate", "LastQuarter", "LastQuarterToDate", "LastWeek", "LastWeekToDate", "LastYear", "LastYearToDate", "NextFourWeeks", "NextMonth", "NextQuarter", "NextWeek", "NextYear", "ThisMonth", "ThisMonthToDate", "ThisQuarter", "ThisQuarterToDate", "ThisWeek", "ThisWeekToDate", "ThisYear", "ThisYearToDate", "Today", "Yesterday"]
    #: If you omit both `to_report_date` and `from_report_date`, the report will cover the
    #: current fiscal year to date.
    #:
    #: Choose at most one of: `report_period`, or `report_date_macro`.
    report_period: ReportPeriod
    #: Allows you to query for posting reports, non-posting reports, or reports that are either
    #: one.
    report_posting_status_filter: Literal["Either", "NonPosting", "Posting"]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: Specifies whether you want the report to include only columns with active information,
    #: only columns with nonzero values, or all columns regardless of their content or active
    #: status.
    return_columns: Literal["ActiveOnly", "All", "NonZero"]
    #: Specifies whether you want the report to include only rows with active information, only
    #: rows with nonzero values, or all rows regardless of their content or active status.
    return_rows: Literal["ActiveOnly", "All", "NonZero"]
    #: `summarize_columns_by` determines which data the report calculates and how the columns
    #: will be labeled across the top of the report. For example, if you set the value to
    #: scbTwoWeek, the report’s column labels might be “Feb 10-23, 02,” “Feb 24-Mar9, 02,” and
    #: so on.
    summarize_columns_by: Literal["Account", "BalanceSheet", "Class", "Customer", "CustomerType", "Day", "Employee", "FourWeek", "HalfMonth", "IncomeStatement", "ItemDetail", "ItemType", "Month", "Payee", "PaymentMethod", "PayrollItemDetail", "PayrollYtdDetail", "Quarter", "SalesRep", "SalesTaxCode", "ShipMethod", "Terms", "TotalOnly", "TwoWeek", "Vendor", "VendorType", "Week", "Year"]


class PayrollSummaryReport:
    """QuickBooks payroll summary report operations: query.

    Get it from ``client.payroll_summary_report``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def query(
        self,
        connection_id: str,
        params: Optional[PayrollSummaryReportQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List payroll summary reports.

        Queues ``payroll_summary_report.query``: GET /connections/{connection_id}/payroll-summary-reports, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``PayrollSummaryReportQueryParams``)::

            display_report: bool
            include_subcolumns: bool
            payroll_summary_report_type: Literal["EmployeeEarningsSummary", "PayrollLiabilityBalances", "PayrollSummary"] (required)
            report_account_filter: AccountFilter
                account_type_filter: Literal[...] (one of 36 values)
                full_name: List[str]
                full_name_with_children: str
                list_id: List[str]
                list_id_with_children: str
            report_calendar: Literal["CalendarYear", "FiscalYear", "TaxYear"]
            report_class_filter: EntityFilter
                full_name: List[str]
                full_name_with_children: str
                list_id: List[str]
                list_id_with_children: str
            report_date_macro: Literal[...] (one of 24 values)
            report_detail_level_filter: Literal["All", "AllExceptSummary", "SummaryOnly"]
            report_entity_filter: ReportEntityFilter
                entity_type_filter: Literal["Customer", "Employee", "OtherName", "Vendor"]
                full_name: List[str]
                full_name_with_children: str
                list_id: List[str]
                list_id_with_children: str
            report_item_filter: ItemFilter
                full_name: List[str]
                full_name_with_children: str
                item_type_filter: Literal[...] (one of 12 values)
                list_id: List[str]
                list_id_with_children: str
            report_modified_date_range_filter: ReportModifiedDateRangeFilter
                from_report_modified_date: str
                to_report_modified_date: str
            report_modified_date_range_macro: Literal[...] (one of 24 values)
            report_period: ReportPeriod
                from_report_date: str
                to_report_date: str
            report_posting_status_filter: Literal["Either", "NonPosting", "Posting"]
            request_id: str
            return_columns: Literal["ActiveOnly", "All", "NonZero"]
            return_rows: Literal["ActiveOnly", "All", "NonZero"]
            summarize_columns_by: Literal[...] (one of 28 values)

        Docs: https://docs.qubesync.com/api-reference/v2/payroll-summary-reports/list-payroll-summary-reports
        """
        return self._client._queue_operation("payroll_summary_report.query", connection_id, params, webhook_url, idempotency_key)
