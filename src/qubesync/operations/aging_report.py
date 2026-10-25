# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks aging report operations (``client.aging_report``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    AccountFilter,
    EntityFilter,
    ItemFilter,
    ReportEntityFilter,
    ReportModifiedDateRangeFilter,
    ReportPeriod,
    TypeFilter,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _AgingReportQueryParamsRequired(TypedDict):
    #: The type of aging report being queried.
    aging_report_type: Literal["APAgingDetail", "APAgingSummary", "ARAgingDetail", "ARAgingSummary", "CollectionsReport"]


class AgingReportQueryParams(_AgingReportQueryParamsRequired, total=False):
    """Params for ``aging_report.query`` (List aging reports)."""
    #: Set `display_report` to true to display this report within the QuickBooks UI. (Default is
    #: false.) If you want the request to display the report without returning any data to your
    #: application, set the responseData attribute to includeNone.
    display_report: bool
    #: Indicates whether this report should include all accounts or just those that are
    #: currently in use.
    include_accounts: Literal["All", "InUse"]
    include_column: List[Literal["Account", "Aging", "Amount", "AmountDifference", "AverageCost", "BilledDate", "BillingStatus", "CalculatedAmount", "Class", "ClearedStatus", "CostPrice", "Credit", "Currency", "Date", "Debit", "DeliveryDate", "DueDate", "EstimateActive", "ExchangeRate", "FOB", "IncomeSubjectToTax", "Invoiced", "Item", "ItemDesc", "LastModifiedBy", "LatestOrPriorState", "Memo", "ModifiedTime", "Name", "NameAccountNumber", "NameAddress", "NameCity", "NameContact", "NameEmail", "NameFax", "NamePhone", "NameState", "NameZip", "OpenBalance", "OriginalAmount", "PONumber", "PaidAmount", "PaidStatus", "PaidThroughDate", "PaymentMethod", "PayrollItem", "PrintStatus", "ProgressAmount", "ProgressPercent", "Quantity", "QuantityAvailable", "QuantityOnHand", "QuantityOnSalesOrder", "ReceivedQuantity", "RefNumber", "RunningBalance", "SSNOrTaxID", "SalesRep", "SalesTaxCode", "SerialOrLotNumber", "ShipDate", "ShipMethod", "SourceName", "SplitAccount", "TaxLine", "TaxTableVersion", "Terms", "TxnID", "TxnNumber", "TxnType", "UnitPrice", "UserEdit", "ValueOnHand", "WageBase", "WageBaseTips"]]
    #: Allows you to query for a specified account type or for specific list elements.
    report_account_filter: AccountFilter
    #: The report will return aging information up to the `report_aging_as_of` date.
    report_aging_as_of: Literal["ReportEndDate", "Today"]
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
    #: Allows you to report on specific transaction types (for example, charge, check, deposit,
    #: or estimate).
    report_txn_type_filter: TypeFilter
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class AgingReport:
    """QuickBooks aging report operations: query.

    Get it from ``client.aging_report``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def query(
        self,
        connection_id: str,
        params: Optional[AgingReportQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List aging reports.

        Queues ``aging_report.query``: GET /connections/{connection_id}/aging-reports, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``AgingReportQueryParams``)::

            aging_report_type: Literal["APAgingDetail", "APAgingSummary", "ARAgingDetail", "ARAgingSummary", "CollectionsReport"] (required)
            display_report: bool
            include_accounts: Literal["All", "InUse"]
            include_column: List[Literal[...] (one of 75 values)]
            report_account_filter: AccountFilter
                account_type_filter: Literal[...] (one of 36 values)
                full_name: List[str]
                full_name_with_children: str
                list_id: List[str]
                list_id_with_children: str
            report_aging_as_of: Literal["ReportEndDate", "Today"]
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
            report_txn_type_filter: TypeFilter
                txn_type_filter: List[Literal[...] (one of 28 values)] (required)
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/aging-reports/list-aging-reports
        """
        return self._client._queue_operation("aging_report.query", connection_id, params, webhook_url, idempotency_key)
