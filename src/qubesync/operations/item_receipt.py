# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks item receipt operations (``client.item_receipt``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    BillDataExt,
    CurrencyFilter,
    DateRangeFilter,
    EntityFilter,
    ExpenseLineAdd,
    ExpenseLineMod,
    ItemGroupLineAdd,
    ItemGroupLineMod,
    ItemLineAdd,
    ItemLineMod,
    LinkToTxn,
    ModifiedDateRangeFilter,
    Ref,
    RefNumberFilter,
    RefNumberRangeFilter,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _ItemReceiptCreateParamsRequired(TypedDict):
    #: A vendor is any person or company from whom a small business owner buys goods and
    #: services. (Banks and tax agencies usually are included on the vendor list.) A company’s
    #: vendor list contains information such as account balance and contact information about
    #: each vendor. A `vendor_ref` aggregate refers to one of the vendors on the list.
    vendor_ref: Ref


class ItemReceiptCreateParams(_ItemReceiptCreateParamsRequired, total=False):
    """Params for ``item_receipt.create`` (Create item receipt)."""
    #: Refers to an accounts payable account in the QuickBooks file. (The AccountType of this
    #: account will be AccountsPayable.) If `ap_account_ref` is missing, the SDK will use the
    #: QuickBooks default AP account. In a request, if an `ap_account_ref` aggregate includes
    #: both `full_name` and `list_id`, `full_name` will be ignored.
    ap_account_ref: Ref
    #: `def_macro` lets you assign a reusable name to a returned `txn_id` or `txn_line_id` so
    #: later requests can reference it with `useMacro`. This feature requires SDK 2.0+.
    def_macro: str
    #: `exchange_rate` is the rate from this currency to the company’s home currency at
    #: AsOfDate. You can supply a rate when adding transactions, but QuickBooks does not provide
    #: rates through the SDK. If your home currency is USD and internet access is available,
    #: rates can be downloaded in the QuickBooks UI via Lists > Currency > Activities > Download
    #: Latest Exchange Rates.
    exchange_rate: float
    expense_line_add: List[ExpenseLineAdd]
    #: Allows for the attachment of a user defined GUID value.
    external_guid: str
    include_ret_element: List[Literal["APAccountRef", "CurrencyRef", "DataExtRet", "EditSequence", "ExchangeRate", "ExpenseLineRet", "ExternalGUID", "IsTaxIncluded", "ItemGroupLineRet", "ItemLineRet", "LiabilityAccountRef", "LinkedTxn", "ListID", "Memo", "OwnerID", "RefNumber", "SalesTaxCodeRef", "TimeCreated", "TimeModified", "TotalAmount", "TotalAmountInHomeCurrency", "TxnDate", "TxnID", "TxnNumber", "VendorRef"]]
    #: For future use with international versions of QuickBooks.
    is_tax_included: bool
    #: Refers to items that are grouped together in QuickBooks for fast entry.
    #:
    #: `item_line_add` and `item_group_line_add` combine: any number of each. QuickBooks
    #: receives them in that order: every `item_line_add`, then every `item_group_line_add`.
    item_group_line_add: List[ItemGroupLineAdd]
    #: An ItemLine is used to track any portion of a transaction that represents the purchase of
    #: an “item.” If `item_line_add` doesn’t specify an Amount, Cost, or Quantity, then
    #: QuickBooks will calculate Amount based on a Quantity of 1 and the suggested Cost.
    #:
    #: `item_line_add` and `item_group_line_add` combine: any number of each. QuickBooks
    #: receives them in that order: every `item_line_add`, then every `item_group_line_add`.
    item_line_add: List[ItemLineAdd]
    link_to_txn_id: List[str]
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
    #: `sales_tax_code_ref` points to the sales-tax code used for an item or customer context.
    #: QuickBooks includes default TAX and NON codes, and a code can be deleted only when
    #: nothing references it. If sales tax is disabled, QuickBooks assigns the default
    #: non-taxable code. If both `full_name` and `list_id` are provided in `sales_tax_code_ref`,
    #: `full_name` is ignored.
    sales_tax_code_ref: Ref
    #: The date of the transaction. In some cases, if you leave `txn_date` out of an -Add
    #: message, QuickBooks will prefill `txn_date` with the date of the last-saved transaction
    #: of the same type.
    txn_date: str


class ItemReceiptQueryParams(TypedDict, total=False):
    """Params for ``item_receipt.query`` (List item receipts)."""
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
    #: If you set `include_linked_txns` to true, then the returned object will include a list of
    #: all the transactions linked to the queried object. (This list is similar to the History
    #: view of a transaction in the user interface, but not identical, as the SDK list contains
    #: only linked transactions, not items.) Each linked transaction will be represented by a
    #: `linked_txn` aggregate.
    include_linked_txns: bool
    include_ret_element: List[Literal["APAccountRef", "CurrencyRef", "DataExtRet", "EditSequence", "ExchangeRate", "ExpenseLineRet", "ExternalGUID", "IsTaxIncluded", "ItemGroupLineRet", "ItemLineRet", "LiabilityAccountRef", "LinkedTxn", "Memo", "RefNumber", "SalesTaxCodeRef", "TimeCreated", "TimeModified", "TotalAmount", "TotalAmountInHomeCurrency", "TxnDate", "TxnID", "TxnNumber", "VendorRef"]]
    #: Page through every match: QuBe Sync asks QuickBooks for each page in turn and sends each
    #: to your `webhook_url` as it arrives, all with the same `id`. On by default, with pages of
    #: 100 records (25 with `include_line_items` or `include_linked_txns`); send `iterator=true`
    #: with `max_returned` for another size. Off when you send `iterator=false` (every match in
    #: one answer) or `max_returned` alone (at most that many, in one answer). It pages a
    #: filtered query only: with `ref_number`, `ref_number_case_sensitive` or `txn_id` every
    #: match comes back in one answer, so leave `iterator` out.
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


class _ItemReceiptUpdateParamsRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    txn_id: str


class ItemReceiptUpdateParams(_ItemReceiptUpdateParamsRequired, total=False):
    """Params for ``item_receipt.update`` (Update item receipt)."""
    #: Refers to an accounts payable account in the QuickBooks file. (The AccountType of this
    #: account will be AccountsPayable.) If `ap_account_ref` is missing, the SDK will use the
    #: QuickBooks default AP account. In a request, if an `ap_account_ref` aggregate includes
    #: both `full_name` and `list_id`, `full_name` will be ignored.
    ap_account_ref: Ref
    #: Set `clear_expense_lines` to true to clear all the expense lines. To modify individual
    #: lines, use `expense_line_mod`.
    clear_expense_lines: bool
    #: Set `clear_item_lines` to true to clear all the item lines. To modify individual lines,
    #: use `item_line_mod`.
    clear_item_lines: bool
    #: `exchange_rate` is the rate from this currency to the company’s home currency at
    #: AsOfDate. You can supply a rate when adding transactions, but QuickBooks does not provide
    #: rates through the SDK. If your home currency is USD and internet access is available,
    #: rates can be downloaded in the QuickBooks UI via Lists > Currency > Activities > Download
    #: Latest Exchange Rates.
    exchange_rate: float
    expense_line_mod: List[ExpenseLineMod]
    include_ret_element: List[Literal["APAccountRef", "CurrencyRef", "DataExtRet", "EditSequence", "ExchangeRate", "ExpenseLineRet", "ExternalGUID", "IsTaxIncluded", "ItemGroupLineRet", "ItemLineRet", "LiabilityAccountRef", "LinkedTxn", "ListID", "Memo", "OwnerID", "RefNumber", "SalesTaxCodeRef", "TimeCreated", "TimeModified", "TotalAmount", "TotalAmountInHomeCurrency", "TxnDate", "TxnID", "TxnNumber", "VendorRef"]]
    #: For future use with international versions of QuickBooks.
    is_tax_included: bool
    #: Refers to items that are grouped together in QuickBooks for fast entry.
    #:
    #: `item_line_mod` and `item_group_line_mod` combine: any number of each. QuickBooks
    #: receives them in that order: every `item_line_mod`, then every `item_group_line_mod`.
    item_group_line_mod: List[ItemGroupLineMod]
    #: An ItemLine is used to track any portion of a transaction that represents the purchase of
    #: an “item.” If ItemLineAdd doesn’t specify an Amount, Cost, or Quantity, then QuickBooks
    #: will calculate Amount based on a Quantity of 1 and the suggested Cost.
    #:
    #: `item_line_mod` and `item_group_line_mod` combine: any number of each. QuickBooks
    #: receives them in that order: every `item_line_mod`, then every `item_group_line_mod`.
    item_line_mod: List[ItemLineMod]
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
    #: `sales_tax_code_ref` points to the sales-tax code used for an item or customer context.
    #: QuickBooks includes default TAX and NON codes, and a code can be deleted only when
    #: nothing references it. If sales tax is disabled, QuickBooks assigns the default
    #: non-taxable code. If both `full_name` and `list_id` are provided in `sales_tax_code_ref`,
    #: `full_name` is ignored.
    sales_tax_code_ref: Ref
    #: The date of the transaction. In some cases, if you leave `txn_date` out of an -Add
    #: message, QuickBooks will prefill `txn_date` with the date of the last-saved transaction
    #: of the same type.
    txn_date: str
    #: A vendor is any person or company from whom a small business owner buys goods and
    #: services. (Banks and tax agencies usually are included on the vendor list.) A company’s
    #: vendor list contains information such as account balance and contact information about
    #: each vendor. A `vendor_ref` aggregate refers to one of the vendors on the list.
    vendor_ref: Ref


class ItemReceipt:
    """QuickBooks item receipt operations: create, query, update.

    Get it from ``client.item_receipt``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[ItemReceiptCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create item receipt.

        Queues ``item_receipt.create``: POST /connections/{connection_id}/item-receipts, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``ItemReceiptCreateParams``)::

            ap_account_ref: Ref
                full_name: str
                list_id: str
            def_macro: str
            exchange_rate: float
            expense_line_add: List[ExpenseLineAdd]
                account_ref: Ref
                amount: float
                billable_status: Literal["Billable", "HasBeenBilled", "NotBillable"]
                class_ref: Ref
                customer_ref: Ref
                data_ext: List[BillDataExt]
                    data_ext_name: str (required)
                    data_ext_value: str (required)
                    owner_id: str (required)
                def_macro: str
                memo: str
                sales_rep_ref: Ref
                sales_tax_code_ref: Ref
                tax_amount: float
            external_guid: str
            include_ret_element: List[Literal[...] (one of 25 values)]
            is_tax_included: bool
            item_group_line_add: List[ItemGroupLineAdd]
                data_ext: List[BillDataExt]
                desc: str
                inventory_site_location_ref: Ref
                inventory_site_ref: Ref
                item_group_ref: Ref (required)
                quantity: float
                unit_of_measure: str
            item_line_add: List[ItemLineAdd]
                amount: float
                billable_status: Literal["Billable", "HasBeenBilled", "NotBillable"]
                class_ref: Ref
                cost: float
                customer_ref: Ref
                data_ext: List[BillDataExt]
                desc: str
                inventory_site_location_ref: Ref
                inventory_site_ref: Ref
                item_ref: Ref
                link_to_txn: LinkToTxn
                    txn_id: str (required)
                    txn_line_id: str (required)
                lot_number: str
                override_item_account_ref: Ref
                quantity: float
                sales_rep_ref: Ref
                sales_tax_code_ref: Ref
                serial_number: str
                tax_amount: float
                unit_of_measure: str
            link_to_txn_id: List[str]
            memo: str
            ref_number: str
            request_id: str
            sales_tax_code_ref: Ref
            txn_date: str
            vendor_ref: Ref (required)

        Docs: https://docs.qubesync.com/api-reference/v2/item-receipts/create-item-receipt
        """
        return self._client._queue_operation("item_receipt.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[ItemReceiptQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List item receipts.

        Queues ``item_receipt.query``: GET /connections/{connection_id}/item-receipts, params in the query string.
        QuickBooks answers in pages: each page comes to ``webhook_url`` as its own webhook.
        Returns the queued request.

        Params (``ItemReceiptQueryParams``)::

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
            include_linked_txns: bool
            include_ret_element: List[Literal[...] (one of 23 values)]
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

        Docs: https://docs.qubesync.com/api-reference/v2/item-receipts/list-item-receipts
        """
        return self._client._queue_operation("item_receipt.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[ItemReceiptUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update item receipt.

        Queues ``item_receipt.update``: PUT /connections/{connection_id}/item-receipts, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``ItemReceiptUpdateParams``)::

            ap_account_ref: Ref
                full_name: str
                list_id: str
            clear_expense_lines: bool
            clear_item_lines: bool
            edit_sequence: str (required)
            exchange_rate: float
            expense_line_mod: List[ExpenseLineMod]
                account_ref: Ref
                amount: float
                billable_status: Literal["Billable", "HasBeenBilled", "NotBillable"]
                class_ref: Ref
                customer_ref: Ref
                memo: str
                sales_rep_ref: Ref
                sales_tax_code_ref: Ref
                tax_amount: float
                txn_line_id: str (required)
            include_ret_element: List[Literal[...] (one of 25 values)]
            is_tax_included: bool
            item_group_line_mod: List[ItemGroupLineMod]
                item_group_ref: Ref
                item_line_mod: List[ItemLineMod]
                    amount: float
                    billable_status: Literal["Billable", "HasBeenBilled", "NotBillable"]
                    class_ref: Ref
                    cost: float
                    customer_ref: Ref
                    desc: str
                    inventory_site_location_ref: Ref
                    inventory_site_ref: Ref
                    item_ref: Ref
                    lot_number: str
                    override_item_account_ref: Ref
                    override_uom_set_ref: Ref
                    quantity: float
                    sales_rep_ref: Ref
                    sales_tax_code_ref: Ref
                    serial_number: str
                    tax_amount: float
                    txn_line_id: str (required)
                    unit_of_measure: str
                override_uom_set_ref: Ref
                quantity: float
                txn_line_id: str (required)
                unit_of_measure: str
            item_line_mod: List[ItemLineMod]
            memo: str
            ref_number: str
            request_id: str
            sales_tax_code_ref: Ref
            txn_date: str
            txn_id: str (required)
            vendor_ref: Ref

        Docs: https://docs.qubesync.com/api-reference/v2/item-receipts/update-item-receipt
        """
        return self._client._queue_operation("item_receipt.update", connection_id, params, webhook_url, idempotency_key)
