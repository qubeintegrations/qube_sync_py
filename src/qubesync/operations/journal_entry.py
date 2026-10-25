# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks journal entry operations (``client.journal_entry``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    CurrencyFilter,
    DateRangeFilter,
    EntityFilter,
    ModifiedDateRangeFilter,
    Ref,
    RefNumberFilter,
    RefNumberRangeFilter,
)

if TYPE_CHECKING:
    from ..v2 import Client


class JournalCreditLine(TypedDict, total=False):
    #: `account_ref` points to an account in the company file. If both `full_name` and `list_id`
    #: are provided, `full_name` is ignored. Meaning depends on context: for checks it is the
    #: funding account; for ExpenseLineAdd it may be required by accounting preferences; for
    #: credit-card transactions it identifies the bank or card account involved.
    account_ref: Ref
    #: A monetary amount.
    amount: float
    #: The billing status of this item line or expense line.
    billable_status: Literal["Billable", "HasBeenBilled", "NotBillable"]
    #: Use classes to categorize transactions (for example, by department, location, or work
    #: type). Class tracking is off by default in QuickBooks. A `class_ref` points to one class;
    #: if both `full_name` and `list_id` are provided, `full_name` is ignored. In InvoiceAdd, a
    #: header-level `class_ref` is applied to line items unless you override or clear it on
    #: individual lines.
    class_ref: Ref
    #: `def_macro` lets you assign a reusable name to a returned `txn_id` or `txn_line_id` so
    #: later requests can reference it with `useMacro`. This feature requires SDK 2.0+.
    def_macro: str
    #: A QuickBooks “entity” is a customer, vendor, employee, or person on the QuickBooks “other
    #: names” list. Special cases to note: In a BillToPayQuery message, `entity_ref` refers to
    #: the vendor name. In `journal_credit_line` and `journal_debit_line` messages for A/R
    #: accounts, `entity_ref` must refer to a customer, or else the transaction won’t be
    #: recorded.
    entity_ref: Ref
    #: An ItemSalesTax entry represents one tax rate paid to one tax agency. Use it when a
    #: transaction needs a single tax calculation. For multi-rate scenarios, use a sales-tax
    #: group instead. If both `full_name` and `list_id` are provided for `item_sales_tax_ref`,
    #: `list_id` is used.
    item_sales_tax_ref: Ref
    #: Additional information.
    memo: str
    tax_amount: float
    #: Identification number of the transaction line. (`txn_line_id` is supported as of v2.0 of
    #: the SDK. With qbXML v1.0 and v1.1, `txn_line_id` is always returned as zero.) If you need
    #: to add a new transaction line in a transaction Mod request, you can do so by setting the
    #: `txn_line_id` to -1.
    txn_line_id: str


class _JournalLineModRequired(TypedDict):
    #: Identification number of the transaction line. (`txn_line_id` is supported as of v2.0 of
    #: the SDK. With qbXML v1.0 and v1.1, `txn_line_id` is always returned as zero.) If you need
    #: to add a new transaction line in a transaction Mod request, you can do so by setting the
    #: `txn_line_id` to -1.
    txn_line_id: str


class JournalLineMod(_JournalLineModRequired, total=False):
    #: `account_ref` points to an account in the company file. If both `full_name` and `list_id`
    #: are provided, `full_name` is ignored. Meaning depends on context: for checks it is the
    #: funding account; for ExpenseLineAdd it may be required by accounting preferences; for
    #: credit-card transactions it identifies the bank or card account involved.
    account_ref: Ref
    #: A monetary amount.
    amount: float
    #: The billing status of this item line or expense line.
    billable_status: Literal["Billable", "HasBeenBilled", "NotBillable"]
    #: Use classes to categorize transactions (for example, by department, location, or work
    #: type). Class tracking is off by default in QuickBooks. A `class_ref` points to one class;
    #: if both `full_name` and `list_id` are provided, `full_name` is ignored. In InvoiceAdd, a
    #: header-level `class_ref` is applied to line items unless you override or clear it on
    #: individual lines.
    class_ref: Ref
    #: A QuickBooks “entity” is a customer, vendor, employee, or person on the QuickBooks “other
    #: names” list. Special cases to note: In a BillToPayQuery message, `entity_ref` refers to
    #: the vendor name. In `journal_credit_line` and `journal_debit_line` messages for A/R
    #: accounts, `entity_ref` must refer to a customer, or else the transaction won’t be
    #: recorded.
    entity_ref: Ref
    #: An ItemSalesTax entry represents one tax rate paid to one tax agency. Use it when a
    #: transaction needs a single tax calculation. For multi-rate scenarios, use a sales-tax
    #: group instead. If both `full_name` and `list_id` are provided for `item_sales_tax_ref`,
    #: `list_id` is used.
    item_sales_tax_ref: Ref
    #: The type of journal line (debit or credit).
    journal_line_type: Literal["Credit", "Debit"]
    #: Additional information.
    memo: str
    tax_amount: float


class JournalEntryCreateParams(TypedDict, total=False):
    """Params for ``journal_entry.create`` (Create journal entry)."""
    #: A currency record defines how QuickBooks stores and displays a currency. Built-in
    #: currency name/code values are fixed; formatting and active status can vary by settings
    #: and workflow.
    #:
    #: Choose at most one of: `is_home_currency_adjustment`, or the set (`currency_ref`,
    #: `exchange_rate`, `is_amounts_entered_in_home_currency`). Members of a set combine with
    #: each other, not with the other choices.
    currency_ref: Ref
    #: `def_macro` lets you assign a reusable name to a returned `txn_id` or `txn_line_id` so
    #: later requests can reference it with `useMacro`. This feature requires SDK 2.0+.
    def_macro: str
    #: `exchange_rate` is the rate from this currency to the company’s home currency at
    #: AsOfDate. You can supply a rate when adding transactions, but QuickBooks does not provide
    #: rates through the SDK. If your home currency is USD and internet access is available,
    #: rates can be downloaded in the QuickBooks UI via Lists > Currency > Activities > Download
    #: Latest Exchange Rates.
    #:
    #: Choose at most one of: `is_home_currency_adjustment`, or the set (`currency_ref`,
    #: `exchange_rate`, `is_amounts_entered_in_home_currency`). Members of a set combine with
    #: each other, not with the other choices.
    exchange_rate: float
    #: Allows for the attachment of a user defined GUID value.
    external_guid: str
    include_ret_element: List[Literal["CurrencyRef", "DataExtRet", "EditSequence", "ExchangeRate", "ExternalGUID", "IsAdjustment", "IsAmountsEnteredInHomeCurrency", "IsHomeCurrencyAdjustment", "JournalCreditLine", "JournalDebitLine", "ListID", "Memo", "OwnerID", "RefNumber", "TimeCreated", "TimeModified", "TxnDate", "TxnID", "TxnNumber"]]
    #: When a change is an “adjustment,” the original information is retained, usually so an
    #: accountant can see the effects of the adjustment.
    is_adjustment: bool
    #: Flag that indicates the amount being entered is in the home currency.
    #:
    #: Choose at most one of: `is_home_currency_adjustment`, or the set (`currency_ref`,
    #: `exchange_rate`, `is_amounts_entered_in_home_currency`). Members of a set combine with
    #: each other, not with the other choices.
    is_amounts_entered_in_home_currency: bool
    #: Indicates whether the transaction is using a home currency or foreign currency.
    #:
    #: Choose at most one of: `is_home_currency_adjustment`, or the set (`currency_ref`,
    #: `exchange_rate`, `is_amounts_entered_in_home_currency`). Members of a set combine with
    #: each other, not with the other choices.
    is_home_currency_adjustment: bool
    #: If no amount is included in the first credit line (or debit line) of a journal entry in
    #: the QuickBooks user interface, then subsequent SDK queries on that JournalEntry object
    #: will fail XML validation.
    #:
    #: At least one entry is required across `journal_debit_line` and `journal_credit_line`;
    #: they combine, any number of each. QuickBooks receives them in that order: every
    #: `journal_debit_line`, then every `journal_credit_line`.
    journal_credit_line: List[JournalCreditLine]
    #: If no amount is included in the first debit line (or credit line) of a journal entry in
    #: the QuickBooks user interface, then subsequent SDK queries on that JournalEntry object
    #: will fail XML validation.
    #:
    #: At least one entry is required across `journal_debit_line` and `journal_credit_line`;
    #: they combine, any number of each. QuickBooks receives them in that order: every
    #: `journal_debit_line`, then every `journal_credit_line`.
    journal_debit_line: List[JournalCreditLine]
    #: Additional information.
    memo: str
    #: `ref_number` is a user-managed transaction reference (for example, a check number). It
    #: can be edited and is not guaranteed to be globally unique. Some transaction types
    #: auto-populate `ref_number` when omitted, based on QuickBooks preferences and numbering
    #: state.
    ref_number: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: The date of the transaction. In some cases, if you leave `txn_date` out of an -Add
    #: message, QuickBooks will prefill `txn_date` with the date of the last-saved transaction
    #: of the same type.
    txn_date: str


class JournalEntryQueryParams(TypedDict, total=False):
    """Params for ``journal_entry.query`` (List journal entries)."""
    #: Filters according to the account name or `list_id`. If the “Use account numbers”
    #: preference is enabled in the QuickBooks company file, you can specify an account number
    #: (instead of an account name) for `full_name` and get the account you’re looking for. But
    #: if numbers have been used as account names, confusion could arise.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `currency_filter`, `entity_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    account_filter: EntityFilter
    #: Filters by the specified currency.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `currency_filter`, `entity_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    currency_filter: CurrencyFilter
    #: An entity refers to a person on the QuickBooks Customer list, Vendor list, Employee list,
    #: or Other Names list. You can use an EntityQuery request to get information about all the
    #: entities that are set up in the QuickBooks file. In an ARRefundCreditCard query, this
    #: must be a customer/customer job.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `currency_filter`, `entity_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    entity_filter: EntityFilter
    #: This filter allows you to omit line items from a query response to get a smaller result.
    #: The default value is false, so line items are omitted by default. Set
    #: `include_line_items` to true to include line items in the response if you don’t mind
    #: getting a larger result.
    include_line_items: bool
    include_ret_element: List[Literal["CurrencyRef", "DataExtRet", "EditSequence", "ExchangeRate", "ExternalGUID", "IsAdjustment", "IsAmountsEnteredInHomeCurrency", "IsHomeCurrencyAdjustment", "JournalCreditLine", "JournalDebitLine", "Memo", "RefNumber", "TimeCreated", "TimeModified", "TxnDate", "TxnID", "TxnNumber"]]
    #: Page through every match: QuBe Sync asks QuickBooks for each page in turn and sends each
    #: to your `webhook_url` as it arrives, all with the same `id`. On by default, with pages of
    #: 100 records (25 with `include_line_items`); send `iterator=true` with `max_returned` for
    #: another size. Off when you send `iterator=false` (every match in one answer) or
    #: `max_returned` alone (at most that many, in one answer). It pages a filtered query only:
    #: with `ref_number`, `ref_number_case_sensitive` or `txn_id` every match comes back in one
    #: answer, so leave `iterator` out.
    iterator: bool
    #: Limits the number of objects that a query returns. (To get a count of how many objects
    #: could possibly be returned, use the `meta_data` query attribute.) If you include a
    #: `max_returned` value, it must be at least 1.
    #:
    #: The page size, with `iterator=true`. Sent without `iterator`, or with `iterator=false`,
    #: it's a cap instead: at most this many records come back, in one answer, and QuickBooks
    #: doesn't say whether more matched.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `currency_filter`, `entity_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    max_returned: int
    #: Use the `meta_data` attribute to control whether query responses include counts. Options
    #: are NoMetaData (default), MetaDataOnly (count only), and MetaDataAndResponseData (count
    #: plus objects). Counts are approximate and may vary slightly if records are created or
    #: deleted during processing.
    meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
    #: Filters according to the dates when transactions were last modified. The
    #: `modified_date_range_filter` aggregate isn’t required to contain any elements, but if it
    #: is empty, we recommend that you leave it out altogether. Note that the time portion of
    #: the `from_modified_date` and `to_modified_date` fields wasn’t supported in qbXML version
    #: 1.0 or 1.1.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `currency_filter`, `entity_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    modified_date_range_filter: ModifiedDateRangeFilter
    #: `owner_id` identifies who owns the data extension. Use 0 for QuickBooks custom fields
    #: that appear in the UI, or use a GUID for private extensions owned by an app. Keep private
    #: GUIDs confidential unless you intentionally share extensions across apps. If you do share
    #: them, both apps must use the same `owner_id` and `data_ext_name`, because that pair
    #: uniquely identifies the extension.
    owner_id: List[str]
    #: `ref_number` is a user-managed transaction reference (for example, a check number). It
    #: can be edited and is not guaranteed to be globally unique. Some transaction types
    #: auto-populate `ref_number` when omitted, based on QuickBooks preferences and numbering
    #: state.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `currency_filter`, `entity_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    ref_number: List[str]
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `currency_filter`, `entity_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    ref_number_case_sensitive: List[str]
    #: Filters by `ref_number` range. Numeric-only bounds are compared numerically; otherwise
    #: comparison is lexicographic.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `currency_filter`, `entity_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    ref_number_filter: RefNumberFilter
    #: Filters by `ref_number` range. Numeric-only bounds are compared numerically; otherwise
    #: comparison is lexicographic.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `currency_filter`, `entity_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    ref_number_range_filter: RefNumberRangeFilter
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: Filters according to the original transaction dates.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `currency_filter`, `entity_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    txn_date_range_filter: DateRangeFilter
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `currency_filter`, `entity_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    txn_id: List[str]


class _JournalEntryUpdateParamsRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    txn_id: str


class JournalEntryUpdateParams(_JournalEntryUpdateParamsRequired, total=False):
    """Params for ``journal_entry.update`` (Update journal entry)."""
    #: A currency record defines how QuickBooks stores and displays a currency. Built-in
    #: currency name/code values are fixed; formatting and active status can vary by settings
    #: and workflow.
    currency_ref: Ref
    #: `exchange_rate` is the rate from this currency to the company’s home currency at
    #: AsOfDate. You can supply a rate when adding transactions, but QuickBooks does not provide
    #: rates through the SDK. If your home currency is USD and internet access is available,
    #: rates can be downloaded in the QuickBooks UI via Lists > Currency > Activities > Download
    #: Latest Exchange Rates.
    exchange_rate: float
    include_ret_element: List[Literal["CurrencyRef", "DataExtRet", "EditSequence", "ExchangeRate", "ExternalGUID", "IsAdjustment", "IsAmountsEnteredInHomeCurrency", "IsHomeCurrencyAdjustment", "JournalCreditLine", "JournalDebitLine", "ListID", "Memo", "OwnerID", "RefNumber", "TimeCreated", "TimeModified", "TxnDate", "TxnID", "TxnNumber"]]
    #: When a change is an “adjustment,” the original information is retained, usually so an
    #: accountant can see the effects of the adjustment.
    is_adjustment: bool
    #: Flag that indicates the amount being entered is in the home currency.
    is_amounts_entered_in_home_currency: bool
    journal_line_mod: List[JournalLineMod]
    #: `ref_number` is a user-managed transaction reference (for example, a check number). It
    #: can be edited and is not guaranteed to be globally unique. Some transaction types
    #: auto-populate `ref_number` when omitted, based on QuickBooks preferences and numbering
    #: state.
    ref_number: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: The date of the transaction. In some cases, if you leave `txn_date` out of an -Add
    #: message, QuickBooks will prefill `txn_date` with the date of the last-saved transaction
    #: of the same type.
    txn_date: str


class JournalEntry:
    """QuickBooks journal entry operations: create, query, update.

    Get it from ``client.journal_entry``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[JournalEntryCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create journal entry.

        Queues ``journal_entry.create``: POST /connections/{connection_id}/journal-entries, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``JournalEntryCreateParams``)::

            currency_ref: Ref
                full_name: str
                list_id: str
            def_macro: str
            exchange_rate: float
            external_guid: str
            include_ret_element: List[Literal[...] (one of 19 values)]
            is_adjustment: bool
            is_amounts_entered_in_home_currency: bool
            is_home_currency_adjustment: bool
            journal_credit_line: List[JournalCreditLine]
                account_ref: Ref
                amount: float
                billable_status: Literal["Billable", "HasBeenBilled", "NotBillable"]
                class_ref: Ref
                def_macro: str
                entity_ref: Ref
                item_sales_tax_ref: Ref
                memo: str
                tax_amount: float
                txn_line_id: str
            journal_debit_line: List[JournalCreditLine]
            memo: str
            ref_number: str
            request_id: str
            txn_date: str

        Docs: https://docs.qubesync.com/api-reference/v2/journal-entries/create-journal-entry
        """
        return self._client._queue_operation("journal_entry.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[JournalEntryQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List journal entries.

        Queues ``journal_entry.query``: GET /connections/{connection_id}/journal-entries, params in the query string.
        QuickBooks answers in pages: each page comes to ``webhook_url`` as its own webhook.
        Returns the queued request.

        Params (``JournalEntryQueryParams``)::

            account_filter: EntityFilter
                full_name: List[str]
                full_name_with_children: str
                list_id: List[str]
                list_id_with_children: str
            currency_filter: CurrencyFilter
                full_name: List[str]
                list_id: List[str]
            entity_filter: EntityFilter
            include_line_items: bool
            include_ret_element: List[Literal[...] (one of 17 values)]
            iterator: bool
            max_returned: int
            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            modified_date_range_filter: ModifiedDateRangeFilter
                from_modified_date: str
                to_modified_date: str
            owner_id: List[str]
            ref_number: List[str]
            ref_number_case_sensitive: List[str]
            ref_number_filter: RefNumberFilter
                match_criterion: Literal["Contains", "EndsWith", "StartsWith"] (required)
                ref_number: str (required)
            ref_number_range_filter: RefNumberRangeFilter
                from_ref_number: str
                to_ref_number: str
            request_id: str
            txn_date_range_filter: DateRangeFilter
                date_macro: Literal[...] (one of 34 values)
                from_txn_date: str
                to_txn_date: str
            txn_id: List[str]

        Docs: https://docs.qubesync.com/api-reference/v2/journal-entries/list-journal-entries
        """
        return self._client._queue_operation("journal_entry.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[JournalEntryUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update journal entry.

        Queues ``journal_entry.update``: PUT /connections/{connection_id}/journal-entries, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``JournalEntryUpdateParams``)::

            currency_ref: Ref
                full_name: str
                list_id: str
            edit_sequence: str (required)
            exchange_rate: float
            include_ret_element: List[Literal[...] (one of 19 values)]
            is_adjustment: bool
            is_amounts_entered_in_home_currency: bool
            journal_line_mod: List[JournalLineMod]
                account_ref: Ref
                amount: float
                billable_status: Literal["Billable", "HasBeenBilled", "NotBillable"]
                class_ref: Ref
                entity_ref: Ref
                item_sales_tax_ref: Ref
                journal_line_type: Literal["Credit", "Debit"]
                memo: str
                tax_amount: float
                txn_line_id: str (required)
            ref_number: str
            request_id: str
            txn_date: str
            txn_id: str (required)

        Docs: https://docs.qubesync.com/api-reference/v2/journal-entries/update-journal-entry
        """
        return self._client._queue_operation("journal_entry.update", connection_id, params, webhook_url, idempotency_key)
