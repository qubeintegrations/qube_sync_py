# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks transaction operations (``client.transaction``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    AccountFilter,
    CurrencyFilter,
    DateRangeFilter,
    EntityFilter,
    ItemFilter,
    RefNumberFilter,
    RefNumberRangeFilter,
    ReportEntityFilter,
    TypeFilter,
)

if TYPE_CHECKING:
    from ..v2 import Client


class TransactionModifiedDateRangeFilter(TypedDict, total=False):
    #: `date_macro` filters by transaction date (not last-modified date). Do not combine
    #: `date_macro` with `from_modified_date`/`to_modified_date` in the same query filter set.
    date_macro: Literal["All", "LastCalendarQuarter", "LastCalendarQuarterToDate", "LastCalendarYear", "LastCalendarYearToDate", "LastFiscalQuarter", "LastFiscalQuarterToDate", "LastFiscalYear", "LastFiscalYearToDate", "LastMonth", "LastMonthToDate", "LastWeek", "LastWeekToDate", "NextCalendarQuarter", "NextCalendarYear", "NextFiscalQuarter", "NextFiscalYear", "NextFourWeeks", "NextMonth", "NextWeek", "ThisCalendarQuarter", "ThisCalendarQuarterToDate", "ThisCalendarYear", "ThisCalendarYearToDate", "ThisFiscalQuarter", "ThisFiscalQuarterToDate", "ThisFiscalYear", "ThisFiscalYearToDate", "ThisMonth", "ThisMonthToDate", "ThisWeek", "ThisWeekToDate", "Today", "Yesterday"]
    #: Filters results to objects modified on or after this timestamp. QuickBooks Desktop
    #: accepts 1970-01-01 through 2038-01-19T03:14:07. If only a date is provided, time defaults
    #: to 00:00:00.
    from_modified_date: str
    #: Filters results to objects modified on or before this timestamp. QuickBooks Desktop
    #: accepts 1970-01-01 through 2038-01-19T03:14:07. If only a date is provided, time defaults
    #: to end-of-day (23:59:59).
    to_modified_date: str


class TransactionQueryParams(TypedDict, total=False):
    """Params for ``transaction.query`` (List transactions)."""
    #: Filters by the specified currency.
    #:
    #: Choose at most one of: `txn_id`, or the set (`currency_filter`, `max_returned`,
    #: `ref_number`, `ref_number_case_sensitive`, `ref_number_filter`,
    #: `ref_number_range_filter`, `transaction_account_filter`, `transaction_class_filter`,
    #: `transaction_date_range_filter`, `transaction_detail_level_filter`,
    #: `transaction_entity_filter`, `transaction_item_filter`,
    #: `transaction_modified_date_range_filter`, `transaction_paid_status_filter`,
    #: `transaction_posting_status_filter`, `transaction_type_filter`). Members of a set combine
    #: with each other, not with the other choices.
    currency_filter: CurrencyFilter
    include_ret_element: List[Literal["AccountRef", "Amount", "AmountInHomeCurrency", "CurrencyRef", "EntityRef", "ExchangeRate", "Memo", "RefNumber", "TimeCreated", "TimeModified", "TxnDate", "TxnID", "TxnLineID", "TxnType"]]
    #: Page through every match: QuBe Sync asks QuickBooks for each page in turn and sends each
    #: to your `webhook_url` as it arrives, all with the same `id`. On by default, with pages of
    #: 100 records; send `iterator=true` with `max_returned` for another size. Off when you send
    #: `iterator=false` (every match in one answer) or `max_returned` alone (at most that many,
    #: in one answer). It pages a filtered query only: with `txn_id` every match comes back in
    #: one answer, so leave `iterator` out.
    iterator: bool
    #: Limits the number of objects that a query returns. (To get a count of how many objects
    #: could possibly be returned, use the `meta_data` query attribute.) If you include a
    #: `max_returned` value, it must be at least 1.
    #:
    #: The page size, with `iterator=true`. Sent without `iterator`, or with `iterator=false`,
    #: it's a cap instead: at most this many records come back, in one answer, and QuickBooks
    #: doesn't say whether more matched.
    #:
    #: Choose at most one of: `txn_id`, or the set (`currency_filter`, `max_returned`,
    #: `ref_number`, `ref_number_case_sensitive`, `ref_number_filter`,
    #: `ref_number_range_filter`, `transaction_account_filter`, `transaction_class_filter`,
    #: `transaction_date_range_filter`, `transaction_detail_level_filter`,
    #: `transaction_entity_filter`, `transaction_item_filter`,
    #: `transaction_modified_date_range_filter`, `transaction_paid_status_filter`,
    #: `transaction_posting_status_filter`, `transaction_type_filter`). Members of a set combine
    #: with each other, not with the other choices.
    max_returned: int
    #: Use the `meta_data` attribute to control whether query responses include counts. Options
    #: are NoMetaData (default), MetaDataOnly (count only), and MetaDataAndResponseData (count
    #: plus objects). Counts are approximate and may vary slightly if records are created or
    #: deleted during processing.
    meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
    #: `ref_number` is a user-managed transaction reference (for example, a check number). It
    #: can be edited and is not guaranteed to be globally unique. Some transaction types
    #: auto-populate `ref_number` when omitted, based on QuickBooks preferences and numbering
    #: state.
    #:
    #: Choose at most one of: `txn_id`, or the set (`currency_filter`, `max_returned`,
    #: `ref_number`, `ref_number_case_sensitive`, `ref_number_filter`,
    #: `ref_number_range_filter`, `transaction_account_filter`, `transaction_class_filter`,
    #: `transaction_date_range_filter`, `transaction_detail_level_filter`,
    #: `transaction_entity_filter`, `transaction_item_filter`,
    #: `transaction_modified_date_range_filter`, `transaction_paid_status_filter`,
    #: `transaction_posting_status_filter`, `transaction_type_filter`). Members of a set combine
    #: with each other, not with the other choices.
    ref_number: List[str]
    #: Choose at most one of: `txn_id`, or the set (`currency_filter`, `max_returned`,
    #: `ref_number`, `ref_number_case_sensitive`, `ref_number_filter`,
    #: `ref_number_range_filter`, `transaction_account_filter`, `transaction_class_filter`,
    #: `transaction_date_range_filter`, `transaction_detail_level_filter`,
    #: `transaction_entity_filter`, `transaction_item_filter`,
    #: `transaction_modified_date_range_filter`, `transaction_paid_status_filter`,
    #: `transaction_posting_status_filter`, `transaction_type_filter`). Members of a set combine
    #: with each other, not with the other choices.
    ref_number_case_sensitive: List[str]
    #: Filters by `ref_number` range. Numeric-only bounds are compared numerically; otherwise
    #: comparison is lexicographic.
    #:
    #: Choose at most one of: `txn_id`, or the set (`currency_filter`, `max_returned`,
    #: `ref_number`, `ref_number_case_sensitive`, `ref_number_filter`,
    #: `ref_number_range_filter`, `transaction_account_filter`, `transaction_class_filter`,
    #: `transaction_date_range_filter`, `transaction_detail_level_filter`,
    #: `transaction_entity_filter`, `transaction_item_filter`,
    #: `transaction_modified_date_range_filter`, `transaction_paid_status_filter`,
    #: `transaction_posting_status_filter`, `transaction_type_filter`). Members of a set combine
    #: with each other, not with the other choices.
    ref_number_filter: RefNumberFilter
    #: Filters by `ref_number` range. Numeric-only bounds are compared numerically; otherwise
    #: comparison is lexicographic.
    #:
    #: Choose at most one of: `txn_id`, or the set (`currency_filter`, `max_returned`,
    #: `ref_number`, `ref_number_case_sensitive`, `ref_number_filter`,
    #: `ref_number_range_filter`, `transaction_account_filter`, `transaction_class_filter`,
    #: `transaction_date_range_filter`, `transaction_detail_level_filter`,
    #: `transaction_entity_filter`, `transaction_item_filter`,
    #: `transaction_modified_date_range_filter`, `transaction_paid_status_filter`,
    #: `transaction_posting_status_filter`, `transaction_type_filter`). Members of a set combine
    #: with each other, not with the other choices.
    ref_number_range_filter: RefNumberRangeFilter
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: Filters the transactions based on the `account_ref` in the transaction or transaction
    #: line using an account type filter or a specific `list_id`, or a `full_name`, or a
    #: `list_id_with_children`, or a `full_name_with_children`. To filter on transaction lines,
    #: you must specify the `transaction_detail_level_filter` with a value of either “All” or
    #: “AllExceptSummary”.
    #:
    #: Choose at most one of: `txn_id`, or the set (`currency_filter`, `max_returned`,
    #: `ref_number`, `ref_number_case_sensitive`, `ref_number_filter`,
    #: `ref_number_range_filter`, `transaction_account_filter`, `transaction_class_filter`,
    #: `transaction_date_range_filter`, `transaction_detail_level_filter`,
    #: `transaction_entity_filter`, `transaction_item_filter`,
    #: `transaction_modified_date_range_filter`, `transaction_paid_status_filter`,
    #: `transaction_posting_status_filter`, `transaction_type_filter`). Members of a set combine
    #: with each other, not with the other choices.
    transaction_account_filter: AccountFilter
    #: Filters the transactions based on the ClassRef in the transaction or transaction line by
    #: using a specific `list_id`, or a `full_name`, or a `list_id_with_children`, or a
    #: `full_name_with_children`. To filter on transaction lines, you must specify the
    #: `transaction_detail_level_filter` with a value of either “All” or “AllExceptSummary”.
    #:
    #: Choose at most one of: `txn_id`, or the set (`currency_filter`, `max_returned`,
    #: `ref_number`, `ref_number_case_sensitive`, `ref_number_filter`,
    #: `ref_number_range_filter`, `transaction_account_filter`, `transaction_class_filter`,
    #: `transaction_date_range_filter`, `transaction_detail_level_filter`,
    #: `transaction_entity_filter`, `transaction_item_filter`,
    #: `transaction_modified_date_range_filter`, `transaction_paid_status_filter`,
    #: `transaction_posting_status_filter`, `transaction_type_filter`). Members of a set combine
    #: with each other, not with the other choices.
    transaction_class_filter: EntityFilter
    #: Filters the transactions based on the transaction’s date either by specifying a “from”
    #: and/or “to” date, or by using a `date_macro`.
    #:
    #: Choose at most one of: `txn_id`, or the set (`currency_filter`, `max_returned`,
    #: `ref_number`, `ref_number_case_sensitive`, `ref_number_filter`,
    #: `ref_number_range_filter`, `transaction_account_filter`, `transaction_class_filter`,
    #: `transaction_date_range_filter`, `transaction_detail_level_filter`,
    #: `transaction_entity_filter`, `transaction_item_filter`,
    #: `transaction_modified_date_range_filter`, `transaction_paid_status_filter`,
    #: `transaction_posting_status_filter`, `transaction_type_filter`). Members of a set combine
    #: with each other, not with the other choices.
    transaction_date_range_filter: DateRangeFilter
    #: Allows you to specify the detail level of the query results. You can specify all, summary
    #: only (the default), or all except summary. Summary only refers to the transaction as a
    #: whole, whereas all except summary refers to the transaction lines.
    #:
    #: Choose at most one of: `txn_id`, or the set (`currency_filter`, `max_returned`,
    #: `ref_number`, `ref_number_case_sensitive`, `ref_number_filter`,
    #: `ref_number_range_filter`, `transaction_account_filter`, `transaction_class_filter`,
    #: `transaction_date_range_filter`, `transaction_detail_level_filter`,
    #: `transaction_entity_filter`, `transaction_item_filter`,
    #: `transaction_modified_date_range_filter`, `transaction_paid_status_filter`,
    #: `transaction_posting_status_filter`, `transaction_type_filter`). Members of a set combine
    #: with each other, not with the other choices.
    transaction_detail_level_filter: Literal["All", "AllExceptSummary", "SummaryOnly"]
    #: Filters the transactions based on the `entity_ref` used in the transaction or transaction
    #: line by specifying an entity type filter, a `list_id`, a `full_name`, a
    #: `list_id_with_children`, or a `full_name_with_children`. If you want to filter on
    #: transaction lines you must specify the `transaction_detail_level_filter` with a value of
    #: either “All” or “AllExceptSummary”.
    #:
    #: Choose at most one of: `txn_id`, or the set (`currency_filter`, `max_returned`,
    #: `ref_number`, `ref_number_case_sensitive`, `ref_number_filter`,
    #: `ref_number_range_filter`, `transaction_account_filter`, `transaction_class_filter`,
    #: `transaction_date_range_filter`, `transaction_detail_level_filter`,
    #: `transaction_entity_filter`, `transaction_item_filter`,
    #: `transaction_modified_date_range_filter`, `transaction_paid_status_filter`,
    #: `transaction_posting_status_filter`, `transaction_type_filter`). Members of a set combine
    #: with each other, not with the other choices.
    transaction_entity_filter: ReportEntityFilter
    #: Filters the transactions based on the ItemRef used in the transaction line using an item
    #: type filter, or a specific `list_id`, or a `full_name`, or a `list_id_with_children`, or
    #: a `full_name_with_children`. To filter on transaction lines, you must specify the
    #: `transaction_detail_level_filter` with a value of either “All” or “AllExceptSummary”.
    #:
    #: Choose at most one of: `txn_id`, or the set (`currency_filter`, `max_returned`,
    #: `ref_number`, `ref_number_case_sensitive`, `ref_number_filter`,
    #: `ref_number_range_filter`, `transaction_account_filter`, `transaction_class_filter`,
    #: `transaction_date_range_filter`, `transaction_detail_level_filter`,
    #: `transaction_entity_filter`, `transaction_item_filter`,
    #: `transaction_modified_date_range_filter`, `transaction_paid_status_filter`,
    #: `transaction_posting_status_filter`, `transaction_type_filter`). Members of a set combine
    #: with each other, not with the other choices.
    transaction_item_filter: ItemFilter
    #: Filters the transactions based on the transaction’s modified datetime, either by
    #: specifying a “from” and/or “to” date or by using a `date_macro`.
    #:
    #: Choose at most one of: `txn_id`, or the set (`currency_filter`, `max_returned`,
    #: `ref_number`, `ref_number_case_sensitive`, `ref_number_filter`,
    #: `ref_number_range_filter`, `transaction_account_filter`, `transaction_class_filter`,
    #: `transaction_date_range_filter`, `transaction_detail_level_filter`,
    #: `transaction_entity_filter`, `transaction_item_filter`,
    #: `transaction_modified_date_range_filter`, `transaction_paid_status_filter`,
    #: `transaction_posting_status_filter`, `transaction_type_filter`). Members of a set combine
    #: with each other, not with the other choices.
    transaction_modified_date_range_filter: TransactionModifiedDateRangeFilter
    #: This filter allows you to search for “open” transactions, i.e. transactions with a
    #: remaining balance (for example, credits not fully applied or invoices not fully paid).
    #: Valid values are closed, open, or either, which is the default.
    #:
    #: Choose at most one of: `txn_id`, or the set (`currency_filter`, `max_returned`,
    #: `ref_number`, `ref_number_case_sensitive`, `ref_number_filter`,
    #: `ref_number_range_filter`, `transaction_account_filter`, `transaction_class_filter`,
    #: `transaction_date_range_filter`, `transaction_detail_level_filter`,
    #: `transaction_entity_filter`, `transaction_item_filter`,
    #: `transaction_modified_date_range_filter`, `transaction_paid_status_filter`,
    #: `transaction_posting_status_filter`, `transaction_type_filter`). Members of a set combine
    #: with each other, not with the other choices.
    transaction_paid_status_filter: Literal["Closed", "Either", "Open"]
    #: Allows you to filter transactions based on posting status. Valid values are posting,
    #: non-posting, or either. The default is “either.” (Posting status refers to whether
    #: QuickBooks records a transaction in one of your account registers.)
    #:
    #: Choose at most one of: `txn_id`, or the set (`currency_filter`, `max_returned`,
    #: `ref_number`, `ref_number_case_sensitive`, `ref_number_filter`,
    #: `ref_number_range_filter`, `transaction_account_filter`, `transaction_class_filter`,
    #: `transaction_date_range_filter`, `transaction_detail_level_filter`,
    #: `transaction_entity_filter`, `transaction_item_filter`,
    #: `transaction_modified_date_range_filter`, `transaction_paid_status_filter`,
    #: `transaction_posting_status_filter`, `transaction_type_filter`). Members of a set combine
    #: with each other, not with the other choices.
    transaction_posting_status_filter: Literal["Either", "NonPosting", "Posting"]
    #: Filters the transactions based on the transaction’s type. You can specify one or more
    #: transaction types in the filter. Notice that TimeTracking transactions aren’t supported.
    #: If you set the transaction type filter to “All” (or if you don’t set it at all), the
    #: query will be searching only those transaction types that are permissible types for the
    #: user currently logged in.
    #:
    #: Choose at most one of: `txn_id`, or the set (`currency_filter`, `max_returned`,
    #: `ref_number`, `ref_number_case_sensitive`, `ref_number_filter`,
    #: `ref_number_range_filter`, `transaction_account_filter`, `transaction_class_filter`,
    #: `transaction_date_range_filter`, `transaction_detail_level_filter`,
    #: `transaction_entity_filter`, `transaction_item_filter`,
    #: `transaction_modified_date_range_filter`, `transaction_paid_status_filter`,
    #: `transaction_posting_status_filter`, `transaction_type_filter`). Members of a set combine
    #: with each other, not with the other choices.
    transaction_type_filter: TypeFilter
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    #:
    #: Choose at most one of: `txn_id`, or the set (`currency_filter`, `max_returned`,
    #: `ref_number`, `ref_number_case_sensitive`, `ref_number_filter`,
    #: `ref_number_range_filter`, `transaction_account_filter`, `transaction_class_filter`,
    #: `transaction_date_range_filter`, `transaction_detail_level_filter`,
    #: `transaction_entity_filter`, `transaction_item_filter`,
    #: `transaction_modified_date_range_filter`, `transaction_paid_status_filter`,
    #: `transaction_posting_status_filter`, `transaction_type_filter`). Members of a set combine
    #: with each other, not with the other choices.
    txn_id: List[str]


class Transaction:
    """QuickBooks transaction operations: query.

    Get it from ``client.transaction``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def query(
        self,
        connection_id: str,
        params: Optional[TransactionQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List transactions.

        Queues ``transaction.query``: GET /connections/{connection_id}/transactions, params in the query string.
        QuickBooks answers in pages: each page comes to ``webhook_url`` as its own webhook.
        Returns the queued request.

        Params (``TransactionQueryParams``)::

            currency_filter: CurrencyFilter
                full_name: List[str]
                list_id: List[str]
            include_ret_element: List[Literal[...] (one of 14 values)]
            iterator: bool
            max_returned: int
            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            ref_number: List[str]
            ref_number_case_sensitive: List[str]
            ref_number_filter: RefNumberFilter
                match_criterion: Literal["Contains", "EndsWith", "StartsWith"] (required)
                ref_number: str (required)
            ref_number_range_filter: RefNumberRangeFilter
                from_ref_number: str
                to_ref_number: str
            request_id: str
            transaction_account_filter: AccountFilter
                account_type_filter: Literal[...] (one of 36 values)
                full_name: List[str]
                full_name_with_children: str
                list_id: List[str]
                list_id_with_children: str
            transaction_class_filter: EntityFilter
                full_name: List[str]
                full_name_with_children: str
                list_id: List[str]
                list_id_with_children: str
            transaction_date_range_filter: DateRangeFilter
                date_macro: Literal[...] (one of 34 values)
                from_txn_date: str
                to_txn_date: str
            transaction_detail_level_filter: Literal["All", "AllExceptSummary", "SummaryOnly"]
            transaction_entity_filter: ReportEntityFilter
                entity_type_filter: Literal["Customer", "Employee", "OtherName", "Vendor"]
                full_name: List[str]
                full_name_with_children: str
                list_id: List[str]
                list_id_with_children: str
            transaction_item_filter: ItemFilter
                full_name: List[str]
                full_name_with_children: str
                item_type_filter: Literal[...] (one of 12 values)
                list_id: List[str]
                list_id_with_children: str
            transaction_modified_date_range_filter: TransactionModifiedDateRangeFilter
                date_macro: Literal[...] (one of 34 values)
                from_modified_date: str
                to_modified_date: str
            transaction_paid_status_filter: Literal["Closed", "Either", "Open"]
            transaction_posting_status_filter: Literal["Either", "NonPosting", "Posting"]
            transaction_type_filter: TypeFilter
                txn_type_filter: List[Literal[...] (one of 28 values)] (required)
            txn_id: List[str]

        Docs: https://docs.qubesync.com/api-reference/v2/transactions/list-transactions
        """
        return self._client._queue_operation("transaction.query", connection_id, params, webhook_url, idempotency_key)
