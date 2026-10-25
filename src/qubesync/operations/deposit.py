# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks deposit operations (``client.deposit``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    CurrencyFilter,
    DateRangeFilter,
    EntityFilter,
    ModifiedDateRangeFilter,
    Ref,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _CashBackInfoAddRequired(TypedDict):
    #: `account_ref` points to an account in the company file. If both `full_name` and `list_id`
    #: are provided, `full_name` is ignored. Meaning depends on context: for checks it is the
    #: funding account; for ExpenseLineAdd it may be required by accounting preferences; for
    #: credit-card transactions it identifies the bank or card account involved.
    account_ref: Ref


class CashBackInfoAdd(_CashBackInfoAddRequired, total=False):
    #: A monetary amount.
    amount: float
    #: `def_macro` lets you assign a reusable name to a returned `txn_id` or `txn_line_id` so
    #: later requests can reference it with `useMacro`. This feature requires SDK 2.0+.
    def_macro: str
    #: Additional information.
    memo: str


class DepositLineAdd(TypedDict, total=False):
    #: `account_ref` points to an account in the company file. If both `full_name` and `list_id`
    #: are provided, `full_name` is ignored. Meaning depends on context: for checks it is the
    #: funding account; for ExpenseLineAdd it may be required by accounting preferences; for
    #: credit-card transactions it identifies the bank or card account involved.
    #:
    #: Choose exactly one of: the set (`override_check_number`, `override_class_ref`,
    #: `override_memo`, `payment_txn_id`, `payment_txn_line_id`), or the set (`account_ref`,
    #: `amount`, `check_number`, `class_ref`, `entity_ref`, `memo`, `payment_method_ref`).
    #: Members of a set combine with each other, not with the other choices.
    account_ref: Ref
    #: A monetary amount.
    #:
    #: Choose exactly one of: the set (`override_check_number`, `override_class_ref`,
    #: `override_memo`, `payment_txn_id`, `payment_txn_line_id`), or the set (`account_ref`,
    #: `amount`, `check_number`, `class_ref`, `entity_ref`, `memo`, `payment_method_ref`).
    #: Members of a set combine with each other, not with the other choices.
    amount: float
    #: The check number of a check that a QuickBooks user writes or receives from someone else.
    #:
    #: Choose exactly one of: the set (`override_check_number`, `override_class_ref`,
    #: `override_memo`, `payment_txn_id`, `payment_txn_line_id`), or the set (`account_ref`,
    #: `amount`, `check_number`, `class_ref`, `entity_ref`, `memo`, `payment_method_ref`).
    #: Members of a set combine with each other, not with the other choices.
    check_number: str
    #: Use classes to categorize transactions (for example, by department, location, or work
    #: type). Class tracking is off by default in QuickBooks. A `class_ref` points to one class;
    #: if both `full_name` and `list_id` are provided, `full_name` is ignored. In InvoiceAdd, a
    #: header-level `class_ref` is applied to line items unless you override or clear it on
    #: individual lines.
    #:
    #: Choose exactly one of: the set (`override_check_number`, `override_class_ref`,
    #: `override_memo`, `payment_txn_id`, `payment_txn_line_id`), or the set (`account_ref`,
    #: `amount`, `check_number`, `class_ref`, `entity_ref`, `memo`, `payment_method_ref`).
    #: Members of a set combine with each other, not with the other choices.
    class_ref: Ref
    #: `def_macro` lets you assign a reusable name to a returned `txn_id` or `txn_line_id` so
    #: later requests can reference it with `useMacro`. This feature requires SDK 2.0+.
    def_macro: str
    #: A QuickBooks “entity” is a customer, vendor, employee, or person on the QuickBooks “other
    #: names” list. Special cases to note: In a BillToPayQuery message, `entity_ref` refers to
    #: the vendor name. In JournalCreditLine and JournalDebitLine messages for A/R accounts,
    #: `entity_ref` must refer to a customer, or else the transaction won’t be recorded.
    #:
    #: Choose exactly one of: the set (`override_check_number`, `override_class_ref`,
    #: `override_memo`, `payment_txn_id`, `payment_txn_line_id`), or the set (`account_ref`,
    #: `amount`, `check_number`, `class_ref`, `entity_ref`, `memo`, `payment_method_ref`).
    #: Members of a set combine with each other, not with the other choices.
    entity_ref: Ref
    #: Additional information.
    #:
    #: Choose exactly one of: the set (`override_check_number`, `override_class_ref`,
    #: `override_memo`, `payment_txn_id`, `payment_txn_line_id`), or the set (`account_ref`,
    #: `amount`, `check_number`, `class_ref`, `entity_ref`, `memo`, `payment_method_ref`).
    #: Members of a set combine with each other, not with the other choices.
    memo: str
    #: Deposit line check number.
    #:
    #: Choose exactly one of: the set (`override_check_number`, `override_class_ref`,
    #: `override_memo`, `payment_txn_id`, `payment_txn_line_id`), or the set (`account_ref`,
    #: `amount`, `check_number`, `class_ref`, `entity_ref`, `memo`, `payment_method_ref`).
    #: Members of a set combine with each other, not with the other choices.
    override_check_number: str
    #: Deposit line class reference.
    #:
    #: Choose exactly one of: the set (`override_check_number`, `override_class_ref`,
    #: `override_memo`, `payment_txn_id`, `payment_txn_line_id`), or the set (`account_ref`,
    #: `amount`, `check_number`, `class_ref`, `entity_ref`, `memo`, `payment_method_ref`).
    #: Members of a set combine with each other, not with the other choices.
    override_class_ref: Ref
    #: Depost line memo additional information.
    #:
    #: Choose exactly one of: the set (`override_check_number`, `override_class_ref`,
    #: `override_memo`, `payment_txn_id`, `payment_txn_line_id`), or the set (`account_ref`,
    #: `amount`, `check_number`, `class_ref`, `entity_ref`, `memo`, `payment_method_ref`).
    #: Members of a set combine with each other, not with the other choices.
    override_memo: str
    #: `payment_method_ref` identifies how a payment is made (for example, cash, check, or card
    #: type). If both `full_name` and `list_id` are provided, `full_name` is ignored.
    #:
    #: Choose exactly one of: the set (`override_check_number`, `override_class_ref`,
    #: `override_memo`, `payment_txn_id`, `payment_txn_line_id`), or the set (`account_ref`,
    #: `amount`, `check_number`, `class_ref`, `entity_ref`, `memo`, `payment_method_ref`).
    #: Members of a set combine with each other, not with the other choices.
    payment_method_ref: Ref
    #: For the `payment_txn_id`, use either of these two values:A `txn_id` value exactly as it
    #: is returned by the ReceivePaymentToDepositQuery request, or A `txn_id` value exactly as
    #: it is returned in a ReceivePaymentAdd response.
    #:
    #: Choose exactly one of: the set (`override_check_number`, `override_class_ref`,
    #: `override_memo`, `payment_txn_id`, `payment_txn_line_id`), or the set (`account_ref`,
    #: `amount`, `check_number`, `class_ref`, `entity_ref`, `memo`, `payment_method_ref`).
    #: Members of a set combine with each other, not with the other choices.
    payment_txn_id: str
    #: For the `payment_txn_line_id`, use a `txn_line_id` value exactly as it has been returned
    #: by the ReceivePaymentToDepositQuery request. If you don’t include a `payment_txn_line_id`
    #: and include a `payment_txn_id` for a transaction that includes payment lines, only the
    #: first payment line from that transaction will be deposited.
    #:
    #: Choose exactly one of: the set (`override_check_number`, `override_class_ref`,
    #: `override_memo`, `payment_txn_id`, `payment_txn_line_id`), or the set (`account_ref`,
    #: `amount`, `check_number`, `class_ref`, `entity_ref`, `memo`, `payment_method_ref`).
    #: Members of a set combine with each other, not with the other choices.
    payment_txn_line_id: str


class CashBackInfoMod(TypedDict, total=False):
    #: `account_ref` points to an account in the company file. If both `full_name` and `list_id`
    #: are provided, `full_name` is ignored. Meaning depends on context: for checks it is the
    #: funding account; for ExpenseLineAdd it may be required by accounting preferences; for
    #: credit-card transactions it identifies the bank or card account involved.
    account_ref: Ref
    #: A monetary amount.
    amount: float
    #: Additional information.
    memo: str


class _DepositLineModRequired(TypedDict):
    #: Identification number of the transaction line. (`txn_line_id` is supported as of v2.0 of
    #: the SDK. With qbXML v1.0 and v1.1, `txn_line_id` is always returned as zero.) If you need
    #: to add a new transaction line in a transaction Mod request, you can do so by setting the
    #: `txn_line_id` to -1.
    txn_line_id: str


class DepositLineMod(_DepositLineModRequired, total=False):
    #: `account_ref` points to an account in the company file. If both `full_name` and `list_id`
    #: are provided, `full_name` is ignored. Meaning depends on context: for checks it is the
    #: funding account; for ExpenseLineAdd it may be required by accounting preferences; for
    #: credit-card transactions it identifies the bank or card account involved.
    #:
    #: Choose exactly one of: the set (`override_check_number`, `override_class_ref`,
    #: `override_memo`, `payment_txn_id`, `payment_txn_line_id`), or the set (`account_ref`,
    #: `amount`, `check_number`, `class_ref`, `entity_ref`, `memo`, `payment_method_ref`).
    #: Members of a set combine with each other, not with the other choices.
    account_ref: Ref
    #: A monetary amount.
    #:
    #: Choose exactly one of: the set (`override_check_number`, `override_class_ref`,
    #: `override_memo`, `payment_txn_id`, `payment_txn_line_id`), or the set (`account_ref`,
    #: `amount`, `check_number`, `class_ref`, `entity_ref`, `memo`, `payment_method_ref`).
    #: Members of a set combine with each other, not with the other choices.
    amount: float
    #: The check number of a check that a QuickBooks user writes or receives from someone else.
    #:
    #: Choose exactly one of: the set (`override_check_number`, `override_class_ref`,
    #: `override_memo`, `payment_txn_id`, `payment_txn_line_id`), or the set (`account_ref`,
    #: `amount`, `check_number`, `class_ref`, `entity_ref`, `memo`, `payment_method_ref`).
    #: Members of a set combine with each other, not with the other choices.
    check_number: str
    #: Use classes to categorize transactions (for example, by department, location, or work
    #: type). Class tracking is off by default in QuickBooks. A `class_ref` points to one class;
    #: if both `full_name` and `list_id` are provided, `full_name` is ignored. In InvoiceAdd, a
    #: header-level `class_ref` is applied to line items unless you override or clear it on
    #: individual lines.
    #:
    #: Choose exactly one of: the set (`override_check_number`, `override_class_ref`,
    #: `override_memo`, `payment_txn_id`, `payment_txn_line_id`), or the set (`account_ref`,
    #: `amount`, `check_number`, `class_ref`, `entity_ref`, `memo`, `payment_method_ref`).
    #: Members of a set combine with each other, not with the other choices.
    class_ref: Ref
    #: A QuickBooks “entity” is a customer, vendor, employee, or person on the QuickBooks “other
    #: names” list. Special cases to note: In a BillToPayQuery message, `entity_ref` refers to
    #: the vendor name. In JournalCreditLine and JournalDebitLine messages for A/R accounts,
    #: `entity_ref` must refer to a customer, or else the transaction won’t be recorded.
    #:
    #: Choose exactly one of: the set (`override_check_number`, `override_class_ref`,
    #: `override_memo`, `payment_txn_id`, `payment_txn_line_id`), or the set (`account_ref`,
    #: `amount`, `check_number`, `class_ref`, `entity_ref`, `memo`, `payment_method_ref`).
    #: Members of a set combine with each other, not with the other choices.
    entity_ref: Ref
    #: Additional information.
    #:
    #: Choose exactly one of: the set (`override_check_number`, `override_class_ref`,
    #: `override_memo`, `payment_txn_id`, `payment_txn_line_id`), or the set (`account_ref`,
    #: `amount`, `check_number`, `class_ref`, `entity_ref`, `memo`, `payment_method_ref`).
    #: Members of a set combine with each other, not with the other choices.
    memo: str
    #: Deposit line check number.
    #:
    #: Choose exactly one of: the set (`override_check_number`, `override_class_ref`,
    #: `override_memo`, `payment_txn_id`, `payment_txn_line_id`), or the set (`account_ref`,
    #: `amount`, `check_number`, `class_ref`, `entity_ref`, `memo`, `payment_method_ref`).
    #: Members of a set combine with each other, not with the other choices.
    override_check_number: str
    #: Deposit line class reference.
    #:
    #: Choose exactly one of: the set (`override_check_number`, `override_class_ref`,
    #: `override_memo`, `payment_txn_id`, `payment_txn_line_id`), or the set (`account_ref`,
    #: `amount`, `check_number`, `class_ref`, `entity_ref`, `memo`, `payment_method_ref`).
    #: Members of a set combine with each other, not with the other choices.
    override_class_ref: Ref
    #: Depost line memo additional information.
    #:
    #: Choose exactly one of: the set (`override_check_number`, `override_class_ref`,
    #: `override_memo`, `payment_txn_id`, `payment_txn_line_id`), or the set (`account_ref`,
    #: `amount`, `check_number`, `class_ref`, `entity_ref`, `memo`, `payment_method_ref`).
    #: Members of a set combine with each other, not with the other choices.
    override_memo: str
    #: `payment_method_ref` identifies how a payment is made (for example, cash, check, or card
    #: type). If both `full_name` and `list_id` are provided, `full_name` is ignored.
    #:
    #: Choose exactly one of: the set (`override_check_number`, `override_class_ref`,
    #: `override_memo`, `payment_txn_id`, `payment_txn_line_id`), or the set (`account_ref`,
    #: `amount`, `check_number`, `class_ref`, `entity_ref`, `memo`, `payment_method_ref`).
    #: Members of a set combine with each other, not with the other choices.
    payment_method_ref: Ref
    #: For the `payment_txn_id`, use either of these two values:A `txn_id` value exactly as it
    #: is returned by the ReceivePaymentToDepositQuery request, or A `txn_id` value exactly as
    #: it is returned in a ReceivePaymentAdd response.
    #:
    #: Choose exactly one of: the set (`override_check_number`, `override_class_ref`,
    #: `override_memo`, `payment_txn_id`, `payment_txn_line_id`), or the set (`account_ref`,
    #: `amount`, `check_number`, `class_ref`, `entity_ref`, `memo`, `payment_method_ref`).
    #: Members of a set combine with each other, not with the other choices.
    payment_txn_id: str
    #: For the `payment_txn_line_id`, use a `txn_line_id` value exactly as it has been returned
    #: by the ReceivePaymentToDepositQuery request. If you don’t include a `payment_txn_line_id`
    #: and include a `payment_txn_id` for a transaction that includes payment lines, only the
    #: first payment line from that transaction will be deposited.
    #:
    #: Choose exactly one of: the set (`override_check_number`, `override_class_ref`,
    #: `override_memo`, `payment_txn_id`, `payment_txn_line_id`), or the set (`account_ref`,
    #: `amount`, `check_number`, `class_ref`, `entity_ref`, `memo`, `payment_method_ref`).
    #: Members of a set combine with each other, not with the other choices.
    payment_txn_line_id: str


class _DepositCreateParamsRequired(TypedDict):
    #: Refers to the account where these funds will be (or have been) deposited. In a
    #: ReceivePaymentAdd request, the default is Undeposited Funds if this isn’t included in the
    #: request. In a request, if a `deposit_to_account_ref` aggregate includes both `full_name`
    #: and `list_id`, `full_name` will be ignored.
    deposit_to_account_ref: Ref


class DepositCreateParams(_DepositCreateParamsRequired, total=False):
    """Params for ``deposit.create`` (Create deposit)."""
    #: This aggregate is included if there is cash back from this deposit. `account_ref`
    #: indicates where the cash back Amount is going (for example, into a petty cash account).
    cash_back_info_add: CashBackInfoAdd
    #: A currency record defines how QuickBooks stores and displays a currency. Built-in
    #: currency name/code values are fixed; formatting and active status can vary by settings
    #: and workflow.
    currency_ref: Ref
    #: `def_macro` lets you assign a reusable name to a returned `txn_id` or `txn_line_id` so
    #: later requests can reference it with `useMacro`. This feature requires SDK 2.0+.
    def_macro: str
    deposit_line_add: List[DepositLineAdd]
    #: `exchange_rate` is the rate from this currency to the company’s home currency at
    #: AsOfDate. You can supply a rate when adding transactions, but QuickBooks does not provide
    #: rates through the SDK. If your home currency is USD and internet access is available,
    #: rates can be downloaded in the QuickBooks UI via Lists > Currency > Activities > Download
    #: Latest Exchange Rates.
    exchange_rate: float
    #: Allows for the attachment of a user defined GUID value.
    external_guid: str
    include_ret_element: List[Literal["CashBackInfoRet", "CurrencyRef", "DataExtRet", "DepositLineRet", "DepositToAccountRef", "DepositTotal", "DepositTotalInHomeCurrency", "EditSequence", "ExchangeRate", "ExternalGUID", "ListID", "Memo", "OwnerID", "TimeCreated", "TimeModified", "TxnDate", "TxnID", "TxnNumber"]]
    #: Additional information.
    memo: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: The date of the transaction. In some cases, if you leave `txn_date` out of an -Add
    #: message, QuickBooks will prefill `txn_date` with the date of the last-saved transaction
    #: of the same type.
    txn_date: str


class DepositQueryParams(TypedDict, total=False):
    """Params for ``deposit.query`` (List deposits)."""
    #: Filters according to the account name or `list_id`. If the “Use account numbers”
    #: preference is enabled in the QuickBooks company file, you can specify an account number
    #: (instead of an account name) for `full_name` and get the account you’re looking for. But
    #: if numbers have been used as account names, confusion could arise.
    #:
    #: Choose at most one of: `txn_id`, or the set (`account_filter`, `currency_filter`,
    #: `entity_filter`, `max_returned`, `modified_date_range_filter`, `txn_date_range_filter`).
    #: Members of a set combine with each other, not with the other choices.
    account_filter: EntityFilter
    #: Filters by the specified currency.
    #:
    #: Choose at most one of: `txn_id`, or the set (`account_filter`, `currency_filter`,
    #: `entity_filter`, `max_returned`, `modified_date_range_filter`, `txn_date_range_filter`).
    #: Members of a set combine with each other, not with the other choices.
    currency_filter: CurrencyFilter
    #: An entity refers to a person on the QuickBooks Customer list, Vendor list, Employee list,
    #: or Other Names list. You can use an EntityQuery request to get information about all the
    #: entities that are set up in the QuickBooks file. In an ARRefundCreditCard query, this
    #: must be a customer/customer job.
    #:
    #: Choose at most one of: `txn_id`, or the set (`account_filter`, `currency_filter`,
    #: `entity_filter`, `max_returned`, `modified_date_range_filter`, `txn_date_range_filter`).
    #: Members of a set combine with each other, not with the other choices.
    entity_filter: EntityFilter
    #: This filter allows you to omit line items from a query response to get a smaller result.
    #: The default value is false, so line items are omitted by default. Set
    #: `include_line_items` to true to include line items in the response if you don’t mind
    #: getting a larger result.
    include_line_items: bool
    include_ret_element: List[Literal["CashBackInfoRet", "CurrencyRef", "DataExtRet", "DepositLineRet", "DepositToAccountRef", "DepositTotal", "DepositTotalInHomeCurrency", "EditSequence", "ExchangeRate", "ExternalGUID", "Memo", "TimeCreated", "TimeModified", "TxnDate", "TxnID", "TxnNumber"]]
    #: Page through every match: QuBe Sync asks QuickBooks for each page in turn and sends each
    #: to your `webhook_url` as it arrives, all with the same `id`. On by default, with pages of
    #: 100 records (25 with `include_line_items`); send `iterator=true` with `max_returned` for
    #: another size. Off when you send `iterator=false` (every match in one answer) or
    #: `max_returned` alone (at most that many, in one answer). It pages a filtered query only:
    #: with `txn_id` every match comes back in one answer, so leave `iterator` out.
    iterator: bool
    #: Limits the number of objects that a query returns. (To get a count of how many objects
    #: could possibly be returned, use the `meta_data` query attribute.) If you include a
    #: `max_returned` value, it must be at least 1.
    #:
    #: The page size, with `iterator=true`. Sent without `iterator`, or with `iterator=false`,
    #: it's a cap instead: at most this many records come back, in one answer, and QuickBooks
    #: doesn't say whether more matched.
    #:
    #: Choose at most one of: `txn_id`, or the set (`account_filter`, `currency_filter`,
    #: `entity_filter`, `max_returned`, `modified_date_range_filter`, `txn_date_range_filter`).
    #: Members of a set combine with each other, not with the other choices.
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
    #: Choose at most one of: `txn_id`, or the set (`account_filter`, `currency_filter`,
    #: `entity_filter`, `max_returned`, `modified_date_range_filter`, `txn_date_range_filter`).
    #: Members of a set combine with each other, not with the other choices.
    modified_date_range_filter: ModifiedDateRangeFilter
    #: `owner_id` identifies who owns the data extension. Use 0 for QuickBooks custom fields
    #: that appear in the UI, or use a GUID for private extensions owned by an app. Keep private
    #: GUIDs confidential unless you intentionally share extensions across apps. If you do share
    #: them, both apps must use the same `owner_id` and `data_ext_name`, because that pair
    #: uniquely identifies the extension.
    owner_id: List[str]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: Filters according to the original transaction dates.
    #:
    #: Choose at most one of: `txn_id`, or the set (`account_filter`, `currency_filter`,
    #: `entity_filter`, `max_returned`, `modified_date_range_filter`, `txn_date_range_filter`).
    #: Members of a set combine with each other, not with the other choices.
    txn_date_range_filter: DateRangeFilter
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    #:
    #: Choose at most one of: `txn_id`, or the set (`account_filter`, `currency_filter`,
    #: `entity_filter`, `max_returned`, `modified_date_range_filter`, `txn_date_range_filter`).
    #: Members of a set combine with each other, not with the other choices.
    txn_id: List[str]


class _DepositUpdateParamsRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    txn_id: str


class DepositUpdateParams(_DepositUpdateParamsRequired, total=False):
    """Params for ``deposit.update`` (Update deposit)."""
    #: This aggregate is included if there is cash back from this deposit. `account_ref`
    #: indicates where the cash back Amount is going (for example, into a petty cash account).
    cash_back_info_mod: CashBackInfoMod
    #: A currency record defines how QuickBooks stores and displays a currency. Built-in
    #: currency name/code values are fixed; formatting and active status can vary by settings
    #: and workflow.
    currency_ref: Ref
    deposit_line_mod: List[DepositLineMod]
    #: Refers to the account where these funds will be (or have been) deposited. In a
    #: ReceivePaymentAdd request, the default is Undeposited Funds if this isn’t included in the
    #: request. In a request, if a `deposit_to_account_ref` aggregate includes both `full_name`
    #: and `list_id`, `full_name` will be ignored.
    deposit_to_account_ref: Ref
    #: `exchange_rate` is the rate from this currency to the company’s home currency at
    #: AsOfDate. You can supply a rate when adding transactions, but QuickBooks does not provide
    #: rates through the SDK. If your home currency is USD and internet access is available,
    #: rates can be downloaded in the QuickBooks UI via Lists > Currency > Activities > Download
    #: Latest Exchange Rates.
    exchange_rate: float
    include_ret_element: List[Literal["CashBackInfoRet", "CurrencyRef", "DataExtRet", "DepositLineRet", "DepositToAccountRef", "DepositTotal", "DepositTotalInHomeCurrency", "EditSequence", "ExchangeRate", "ExternalGUID", "ListID", "Memo", "OwnerID", "TimeCreated", "TimeModified", "TxnDate", "TxnID", "TxnNumber"]]
    #: Additional information.
    memo: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: The date of the transaction. In some cases, if you leave `txn_date` out of an -Add
    #: message, QuickBooks will prefill `txn_date` with the date of the last-saved transaction
    #: of the same type.
    txn_date: str


class Deposit:
    """QuickBooks deposit operations: create, query, update.

    Get it from ``client.deposit``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[DepositCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create deposit.

        Queues ``deposit.create``: POST /connections/{connection_id}/deposits, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``DepositCreateParams``)::

            cash_back_info_add: CashBackInfoAdd
                account_ref: Ref (required)
                    full_name: str
                    list_id: str
                amount: float
                def_macro: str
                memo: str
            currency_ref: Ref
            def_macro: str
            deposit_line_add: List[DepositLineAdd]
                account_ref: Ref
                amount: float
                check_number: str
                class_ref: Ref
                def_macro: str
                entity_ref: Ref
                memo: str
                override_check_number: str
                override_class_ref: Ref
                override_memo: str
                payment_method_ref: Ref
                payment_txn_id: str
                payment_txn_line_id: str
            deposit_to_account_ref: Ref (required)
            exchange_rate: float
            external_guid: str
            include_ret_element: List[Literal[...] (one of 18 values)]
            memo: str
            request_id: str
            txn_date: str

        Docs: https://docs.qubesync.com/api-reference/v2/deposits/create-deposit
        """
        return self._client._queue_operation("deposit.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[DepositQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List deposits.

        Queues ``deposit.query``: GET /connections/{connection_id}/deposits, params in the query string.
        QuickBooks answers in pages: each page comes to ``webhook_url`` as its own webhook.
        Returns the queued request.

        Params (``DepositQueryParams``)::

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
            include_ret_element: List[Literal[...] (one of 16 values)]
            iterator: bool
            max_returned: int
            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            modified_date_range_filter: ModifiedDateRangeFilter
                from_modified_date: str
                to_modified_date: str
            owner_id: List[str]
            request_id: str
            txn_date_range_filter: DateRangeFilter
                date_macro: Literal[...] (one of 34 values)
                from_txn_date: str
                to_txn_date: str
            txn_id: List[str]

        Docs: https://docs.qubesync.com/api-reference/v2/deposits/list-deposits
        """
        return self._client._queue_operation("deposit.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[DepositUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update deposit.

        Queues ``deposit.update``: PUT /connections/{connection_id}/deposits, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``DepositUpdateParams``)::

            cash_back_info_mod: CashBackInfoMod
                account_ref: Ref
                    full_name: str
                    list_id: str
                amount: float
                memo: str
            currency_ref: Ref
            deposit_line_mod: List[DepositLineMod]
                account_ref: Ref
                amount: float
                check_number: str
                class_ref: Ref
                entity_ref: Ref
                memo: str
                override_check_number: str
                override_class_ref: Ref
                override_memo: str
                payment_method_ref: Ref
                payment_txn_id: str
                payment_txn_line_id: str
                txn_line_id: str (required)
            deposit_to_account_ref: Ref
            edit_sequence: str (required)
            exchange_rate: float
            include_ret_element: List[Literal[...] (one of 18 values)]
            memo: str
            request_id: str
            txn_date: str
            txn_id: str (required)

        Docs: https://docs.qubesync.com/api-reference/v2/deposits/update-deposit
        """
        return self._client._queue_operation("deposit.update", connection_id, params, webhook_url, idempotency_key)
