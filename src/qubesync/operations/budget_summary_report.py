# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks budget summary report operations (``client.budget_summary_report``)."""

from typing import Any, Dict, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    EntityFilter,
    ReportPeriod,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _BudgetSummaryReportQueryParamsRequired(TypedDict):
    #: The type of budget report being queried.
    budget_summary_report_type: Literal["BalanceSheetBudgetOverview", "BalanceSheetBudgetVsActual", "ProfitAndLossBudgetOverview", "ProfitAndLossBudgetPerformance", "ProfitAndLossBudgetVsActual"]
    #: Specify the fiscal year of the budget to be queried. There can only be one balance sheet
    #: budget for each fiscal year, one profit and loss (P&L) by account budget per fiscal year,
    #: and one profit and loss (P&L) by account and customer budget per fiscal year. When Fiscal
    #: year isn’t the current year, the report returns the data for the full fiscal year.
    fiscal_year: int


class BudgetSummaryReportQueryParams(_BudgetSummaryReportQueryParamsRequired, total=False):
    """Params for ``budget_summary_report.query`` (List budget summary reports)."""
    #: What this budget covers.
    budget_criterion: Literal["Accounts", "AccountsAndClasses", "AccountsAndCustomers"]
    #: Set `display_report` to true to display this report within the QuickBooks UI. (Default is
    #: false.) If you want the request to display the report without returning any data to your
    #: application, set the responseData attribute to includeNone.
    display_report: bool
    #: Allows you to query for a specified class. Classes can be used to separate transactions
    #: into meaningful categories. (For example, transactions could be classified according to
    #: department, business location, or type of work.) In QuickBooks, class tracking is off by
    #: default.
    report_class_filter: EntityFilter
    #: The time period covered by this report.
    #:
    #: Choose at most one of: `report_period`, or `report_date_macro`.
    report_date_macro: Literal["All", "LastMonth", "LastMonthToDate", "LastQuarter", "LastQuarterToDate", "LastWeek", "LastWeekToDate", "LastYear", "LastYearToDate", "NextFourWeeks", "NextMonth", "NextQuarter", "NextWeek", "NextYear", "ThisMonth", "ThisMonthToDate", "ThisQuarter", "ThisQuarterToDate", "ThisWeek", "ThisWeekToDate", "ThisYear", "ThisYearToDate", "Today", "Yesterday"]
    #: If you omit both `to_report_date` and `from_report_date`, the report will cover the
    #: current fiscal year to date.
    #:
    #: Choose at most one of: `report_period`, or `report_date_macro`.
    report_period: ReportPeriod
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: `summarize_budget_columns_by` determines which data the report calculates and how the
    #: columns will be labeled across the top of the report.
    summarize_budget_columns_by: Literal["Class", "Customer", "Date"]
    #: How you want rows to be labeled in the report. For example, if you set the value to
    #: sbrbAccount, the report’s row labels might be “Checking,” “Savings,” and so on.
    summarize_budget_rows_by: Literal["Account", "Class", "Customer"]


class BudgetSummaryReport:
    """QuickBooks budget summary report operations: query.

    Get it from ``client.budget_summary_report``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def query(
        self,
        connection_id: str,
        params: Optional[BudgetSummaryReportQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List budget summary reports.

        Queues ``budget_summary_report.query``: GET /connections/{connection_id}/budget-summary-reports, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``BudgetSummaryReportQueryParams``)::

            budget_criterion: Literal["Accounts", "AccountsAndClasses", "AccountsAndCustomers"]
            budget_summary_report_type: Literal["BalanceSheetBudgetOverview", "BalanceSheetBudgetVsActual", "ProfitAndLossBudgetOverview", "ProfitAndLossBudgetPerformance", "ProfitAndLossBudgetVsActual"] (required)
            display_report: bool
            fiscal_year: int (required)
            report_class_filter: EntityFilter
                full_name: List[str]
                full_name_with_children: str
                list_id: List[str]
                list_id_with_children: str
            report_date_macro: Literal[...] (one of 24 values)
            report_period: ReportPeriod
                from_report_date: str
                to_report_date: str
            request_id: str
            summarize_budget_columns_by: Literal["Class", "Customer", "Date"]
            summarize_budget_rows_by: Literal["Account", "Class", "Customer"]

        Docs: https://docs.qubesync.com/api-reference/v2/budget-summary-reports/list-budget-summary-reports
        """
        return self._client._queue_operation("budget_summary_report.query", connection_id, params, webhook_url, idempotency_key)
