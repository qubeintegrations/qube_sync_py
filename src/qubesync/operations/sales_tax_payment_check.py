# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks sales tax payment check operations (``client.sales_tax_payment_check``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    Address,
    DateRangeFilter,
    EntityFilter,
    ModifiedDateRangeFilter,
    Ref,
    RefNumberFilter,
    RefNumberRangeFilter,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _SalesTaxPaymentCheckLineAddRequired(TypedDict):
    #: A monetary amount.
    amount: float


class SalesTaxPaymentCheckLineAdd(_SalesTaxPaymentCheckLineAddRequired, total=False):
    #: An ItemSalesTax entry represents one tax rate paid to one tax agency. Use it when a
    #: transaction needs a single tax calculation. For multi-rate scenarios, use a sales-tax
    #: group instead. If both `full_name` and `list_id` are provided for `item_sales_tax_ref`,
    #: `list_id` is used.
    item_sales_tax_ref: Ref


class _SalesTaxPaymentCheckCreateParamsRequired(TypedDict):
    #: Refers to the account from which the funds are being drawn for this check, for example,
    #: Checking or Savings. If a `bank_account_ref` aggregate includes both `full_name` and
    #: `list_id`, `full_name` will be ignored.
    bank_account_ref: Ref
    #: `payee_entity_ref` identifies the payee (customer, vendor, employee, or Other Name). If
    #: both `full_name` and `list_id` are provided, `full_name` is ignored.
    payee_entity_ref: Ref
    sales_tax_payment_check_line_add: List[SalesTaxPaymentCheckLineAdd]
    #: The date of the transaction. In some cases, if you leave `txn_date` out of an -Add
    #: message, QuickBooks will prefill `txn_date` with the date of the last-saved transaction
    #: of the same type.
    txn_date: str


class SalesTaxPaymentCheckCreateParams(_SalesTaxPaymentCheckCreateParamsRequired, total=False):
    """Params for ``sales_tax_payment_check.create`` (Create sales tax payment check)."""
    #: If an address request fails, some combination of address fields might be too long. In a
    #: Check, BillPaymentCheck, or SalesTaxPaymentCheck message, Address is the address that
    #: will print on the check.
    address: Address
    #: `def_macro` lets you assign a reusable name to a returned `txn_id` or `txn_line_id` so
    #: later requests can reference it with `useMacro`. This feature requires SDK 2.0+.
    def_macro: str
    #: Allows for the attachment of a user defined GUID value.
    external_guid: str
    include_ret_element: List[Literal["Address", "AddressBlock", "Amount", "BankAccountRef", "DataExtRet", "EditSequence", "ExternalGUID", "IsToBePrinted", "ListID", "Memo", "OwnerID", "PayeeEntityRef", "RefNumber", "SalesTaxPaymentCheckLineRet", "TimeCreated", "TimeModified", "TxnDate", "TxnID", "TxnNumber"]]
    #: If `is_to_be_printed` is true, QuickBooks queues the form for later printing. It does not
    #: print immediately; printing is still a user action in QuickBooks.
    is_to_be_printed: bool
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


class SalesTaxPaymentCheckQueryParams(TypedDict, total=False):
    """Params for ``sales_tax_payment_check.query`` (List sales tax payment checks)."""
    #: Filters according to the account name or `list_id`. If the “Use account numbers”
    #: preference is enabled in the QuickBooks company file, you can specify an account number
    #: (instead of an account name) for `full_name` and get the account you’re looking for. But
    #: if numbers have been used as account names, confusion could arise.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `item_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    account_filter: EntityFilter
    #: An entity refers to a person on the QuickBooks Customer list, Vendor list, Employee list,
    #: or Other Names list. You can use an EntityQuery request to get information about all the
    #: entities that are set up in the QuickBooks file. In an ARRefundCreditCard query, this
    #: must be a customer/customer job.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `item_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    entity_filter: EntityFilter
    #: This filter allows you to omit line items from a query response to get a smaller result.
    #: The default value is false, so line items are omitted by default. Set
    #: `include_line_items` to true to include line items in the response if you don’t mind
    #: getting a larger result.
    include_line_items: bool
    include_ret_element: List[Literal["Address", "AddressBlock", "Amount", "BankAccountRef", "DataExtRet", "EditSequence", "ExternalGUID", "IsToBePrinted", "Memo", "PayeeEntityRef", "RefNumber", "SalesTaxPaymentCheckLineRet", "TimeCreated", "TimeModified", "TxnDate", "TxnID", "TxnNumber"]]
    #: Filters according to the item name or ID. You can use an ItemQuery request to get
    #: information about all the items that are set up in the QuickBooks file. “Items” are line
    #: items used for fast entry on sales and purchase forms. They include services and goods
    #: that a business buys and sells, as well as special items that perform calculations–for
    #: example, subtotal, discount, and sales-tax items.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `item_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    item_filter: EntityFilter
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
    #: set (`account_filter`, `entity_filter`, `item_filter`, `max_returned`,
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
    #: set (`account_filter`, `entity_filter`, `item_filter`, `max_returned`,
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
    #: set (`account_filter`, `entity_filter`, `item_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    ref_number: List[str]
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `item_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    ref_number_case_sensitive: List[str]
    #: Filters by `ref_number` range. Numeric-only bounds are compared numerically; otherwise
    #: comparison is lexicographic.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `item_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    ref_number_filter: RefNumberFilter
    #: Filters by `ref_number` range. Numeric-only bounds are compared numerically; otherwise
    #: comparison is lexicographic.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `item_filter`, `max_returned`,
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
    #: set (`account_filter`, `entity_filter`, `item_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    txn_date_range_filter: DateRangeFilter
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `item_filter`, `max_returned`,
    #: `modified_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    txn_id: List[str]


class _SalesTaxPaymentCheckUpdateParamsRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    txn_id: str


class SalesTaxPaymentCheckUpdateParams(_SalesTaxPaymentCheckUpdateParamsRequired, total=False):
    """Params for ``sales_tax_payment_check.update`` (Update sales tax payment check)."""
    #: If an address request fails, some combination of address fields might be too long. In a
    #: Check, BillPaymentCheck, or SalesTaxPaymentCheck message, Address is the address that
    #: will print on the check.
    address: Address
    #: Refers to the account from which the funds are being drawn for this check, for example,
    #: Checking or Savings. If a `bank_account_ref` aggregate includes both `full_name` and
    #: `list_id`, `full_name` will be ignored.
    bank_account_ref: Ref
    include_ret_element: List[Literal["Address", "AddressBlock", "Amount", "BankAccountRef", "DataExtRet", "EditSequence", "ExternalGUID", "IsToBePrinted", "ListID", "Memo", "OwnerID", "PayeeEntityRef", "RefNumber", "SalesTaxPaymentCheckLineRet", "TimeCreated", "TimeModified", "TxnDate", "TxnID", "TxnNumber"]]
    #: If `is_to_be_printed` is true, QuickBooks queues the form for later printing. It does not
    #: print immediately; printing is still a user action in QuickBooks.
    #:
    #: Choose at most one of: `is_to_be_printed`, or `ref_number`.
    is_to_be_printed: bool
    #: Additional information.
    memo: str
    #: `ref_number` is a user-managed transaction reference (for example, a check number). It
    #: can be edited and is not guaranteed to be globally unique. Some transaction types
    #: auto-populate `ref_number` when omitted, based on QuickBooks preferences and numbering
    #: state.
    #:
    #: Choose at most one of: `is_to_be_printed`, or `ref_number`.
    ref_number: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: The date of the transaction. In some cases, if you leave `txn_date` out of an -Add
    #: message, QuickBooks will prefill `txn_date` with the date of the last-saved transaction
    #: of the same type.
    txn_date: str


class SalesTaxPaymentCheck:
    """QuickBooks sales tax payment check operations: create, query, update.

    Get it from ``client.sales_tax_payment_check``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[SalesTaxPaymentCheckCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create sales tax payment check.

        Queues ``sales_tax_payment_check.create``: POST /connections/{connection_id}/sales-tax-payment-checks, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``SalesTaxPaymentCheckCreateParams``)::

            address: Address
                addr1: str
                addr2: str
                addr3: str
                addr4: str
                addr5: str
                city: str
                country: str
                note: str
                postal_code: str
                state: str
            bank_account_ref: Ref (required)
                full_name: str
                list_id: str
            def_macro: str
            external_guid: str
            include_ret_element: List[Literal[...] (one of 19 values)]
            is_to_be_printed: bool
            memo: str
            payee_entity_ref: Ref (required)
            ref_number: str
            request_id: str
            sales_tax_payment_check_line_add: List[SalesTaxPaymentCheckLineAdd] (required)
                amount: float (required)
                item_sales_tax_ref: Ref
            txn_date: str (required)

        Docs: https://docs.qubesync.com/api-reference/v2/sales-tax-payment-checks/create-sales-tax-payment-check
        """
        return self._client._queue_operation("sales_tax_payment_check.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[SalesTaxPaymentCheckQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List sales tax payment checks.

        Queues ``sales_tax_payment_check.query``: GET /connections/{connection_id}/sales-tax-payment-checks, params in the query string.
        QuickBooks answers in pages: each page comes to ``webhook_url`` as its own webhook.
        Returns the queued request.

        Params (``SalesTaxPaymentCheckQueryParams``)::

            account_filter: EntityFilter
                full_name: List[str]
                full_name_with_children: str
                list_id: List[str]
                list_id_with_children: str
            entity_filter: EntityFilter
            include_line_items: bool
            include_ret_element: List[Literal[...] (one of 17 values)]
            item_filter: EntityFilter
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

        Docs: https://docs.qubesync.com/api-reference/v2/sales-tax-payment-checks/list-sales-tax-payment-checks
        """
        return self._client._queue_operation("sales_tax_payment_check.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[SalesTaxPaymentCheckUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update sales tax payment check.

        Queues ``sales_tax_payment_check.update``: PUT /connections/{connection_id}/sales-tax-payment-checks, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``SalesTaxPaymentCheckUpdateParams``)::

            address: Address
                addr1: str
                addr2: str
                addr3: str
                addr4: str
                addr5: str
                city: str
                country: str
                note: str
                postal_code: str
                state: str
            bank_account_ref: Ref
                full_name: str
                list_id: str
            edit_sequence: str (required)
            include_ret_element: List[Literal[...] (one of 19 values)]
            is_to_be_printed: bool
            memo: str
            ref_number: str
            request_id: str
            txn_date: str
            txn_id: str (required)

        Docs: https://docs.qubesync.com/api-reference/v2/sales-tax-payment-checks/update-sales-tax-payment-check
        """
        return self._client._queue_operation("sales_tax_payment_check.update", connection_id, params, webhook_url, idempotency_key)
