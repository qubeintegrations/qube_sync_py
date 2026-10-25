# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks time report operations (``client.time_report``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    EntityFilter,
    ItemFilter,
    ReportEntityFilter,
    ReportPeriod,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _TimeReportQueryParamsRequired(TypedDict):
    #: Allows you to report on time that has been recorded in a particular category.
    time_report_type: Literal["TimeByItem", "TimeByJobDetail", "TimeByJobSummary", "TimeByName"]


class TimeReportQueryParams(_TimeReportQueryParamsRequired, total=False):
    """Params for ``time_report.query`` (List time reports)."""
    #: Set `display_report` to true to display this report within the QuickBooks UI. (Default is
    #: false.) If you want the request to display the report without returning any data to your
    #: application, set the responseData attribute to includeNone.
    display_report: bool
    include_column: List[Literal["Account", "Aging", "Amount", "AmountDifference", "AverageCost", "BilledDate", "BillingStatus", "CalculatedAmount", "Class", "ClearedStatus", "CostPrice", "Credit", "Currency", "Date", "Debit", "DeliveryDate", "DueDate", "EstimateActive", "ExchangeRate", "FOB", "IncomeSubjectToTax", "Invoiced", "Item", "ItemDesc", "LastModifiedBy", "LatestOrPriorState", "Memo", "ModifiedTime", "Name", "NameAccountNumber", "NameAddress", "NameCity", "NameContact", "NameEmail", "NameFax", "NamePhone", "NameState", "NameZip", "OpenBalance", "OriginalAmount", "PONumber", "PaidAmount", "PaidStatus", "PaidThroughDate", "PaymentMethod", "PayrollItem", "PrintStatus", "ProgressAmount", "ProgressPercent", "Quantity", "QuantityAvailable", "QuantityOnHand", "QuantityOnSalesOrder", "ReceivedQuantity", "RefNumber", "RunningBalance", "SSNOrTaxID", "SalesRep", "SalesTaxCode", "SerialOrLotNumber", "ShipDate", "ShipMethod", "SourceName", "SplitAccount", "TaxLine", "TaxTableVersion", "Terms", "TxnID", "TxnNumber", "TxnType", "UnitPrice", "UserEdit", "ValueOnHand", "WageBase", "WageBaseTips"]]
    #: The default value is false, which means that the report won’t include any subcolumn
    #: information. To include all available types of subcolumns for this report, set
    #: `include_subcolumns` to true. The SDK won’t return subcolumn information for data that
    #: can be easily computed. (For example, the SDK doesn’t return the “percent of row”
    #: column.)
    include_subcolumns: bool
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
    #: Allows you to query for a specified name type (customer, employee, vendor, or other) or
    #: query for specific list elements.
    report_entity_filter: ReportEntityFilter
    #: Allows you to query for a specified item type (for example, discount, inventory, or
    #: non-inventory) or query for specific list elements.
    report_item_filter: ItemFilter
    #: If you omit both `to_report_date` and `from_report_date`, the report will cover the
    #: current fiscal year to date.
    #:
    #: Choose at most one of: `report_period`, or `report_date_macro`.
    report_period: ReportPeriod
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


class TimeReport:
    """QuickBooks time report operations: query.

    Get it from ``client.time_report``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def query(
        self,
        connection_id: str,
        params: Optional[TimeReportQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List time reports.

        Queues ``time_report.query``: GET /connections/{connection_id}/time-reports, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``TimeReportQueryParams``)::

            display_report: bool
            include_column: List[Literal[...] (one of 75 values)]
            include_subcolumns: bool
            report_calendar: Literal["CalendarYear", "FiscalYear", "TaxYear"]
            report_class_filter: EntityFilter
                full_name: List[str]
                full_name_with_children: str
                list_id: List[str]
                list_id_with_children: str
            report_date_macro: Literal[...] (one of 24 values)
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
            report_period: ReportPeriod
                from_report_date: str
                to_report_date: str
            request_id: str
            return_columns: Literal["ActiveOnly", "All", "NonZero"]
            return_rows: Literal["ActiveOnly", "All", "NonZero"]
            summarize_columns_by: Literal[...] (one of 28 values)
            time_report_type: Literal["TimeByItem", "TimeByJobDetail", "TimeByJobSummary", "TimeByName"] (required)

        Docs: https://docs.qubesync.com/api-reference/v2/time-reports/list-time-reports
        """
        return self._client._queue_operation("time_report.query", connection_id, params, webhook_url, idempotency_key)
