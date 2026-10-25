# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks ar refund credit card operations (``client.ar_refund_credit_card``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    Address,
    CreditCardTxnInfo,
    CreditCardTxnInputInfo,
    CreditCardTxnResultInfo,
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


class _RefundAppliedToTxnAddRequired(TypedDict):
    #: Specifies the amount to be taken from the credit transaction you are linking via this
    #: aggregate. The amount specified in this aggregate can’t exceed the amount of the credit
    #: transaction you are linking. If you supply an amount that exceeds, you’ll get a runtime
    #: error.
    refund_amount: float
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    txn_id: str


class RefundAppliedToTxnAdd(_RefundAppliedToTxnAddRequired, total=False):
    pass


class _ArRefundCreditCardCreateParamsRequired(TypedDict):
    #: `customer_ref` identifies a customer or customer job. If both `full_name` and `list_id`
    #: are provided, `full_name` is ignored. In SalesReceipt and ReceivePayment, it identifies
    #: who receives credit. In TimeTracking, it identifies who the time can be billed to and is
    #: required in TimeTrackingAdd when IsBillable is true.
    customer_ref: Ref
    refund_applied_to_txn_add: List[RefundAppliedToTxnAdd]


class ArRefundCreditCardCreateParams(_ArRefundCreditCardCreateParamsRequired, total=False):
    """Params for ``ar_refund_credit_card.create`` (Create ar refund credit card)."""
    #: If an address request fails, some combination of address fields might be too long. In a
    #: Check, BillPaymentCheck, or SalesTaxPaymentCheck message, Address is the address that
    #: will print on the check.
    address: Address
    #: `ar_account_ref` points to an Accounts Receivable account. If both `full_name` and
    #: `list_id` are provided, `full_name` is ignored.
    ar_account_ref: Ref
    #: Contains data from the credit card transaction used in the payment. This data originates
    #: from a previous qbmsXML credit card transaction. The data following the element
    #: `credit_card_txn_input_info`” data is the data from the original qbmsXML request. The
    #: “`credit_card_txn_result_info`” is the data from the original qbmsXML response.
    credit_card_txn_info: CreditCardTxnInfo
    #: `def_macro` lets you assign a reusable name to a returned `txn_id` or TxnLineID so later
    #: requests can reference it with `useMacro`. This feature requires SDK 2.0+.
    def_macro: str
    #: `exchange_rate` is the rate from this currency to the company’s home currency at
    #: AsOfDate. You can supply a rate when adding transactions, but QuickBooks does not provide
    #: rates through the SDK. If your home currency is USD and internet access is available,
    #: rates can be downloaded in the QuickBooks UI via Lists > Currency > Activities > Download
    #: Latest Exchange Rates.
    exchange_rate: float
    #: Allows for the attachment of a user defined GUID value.
    external_guid: str
    include_ret_element: List[Literal["ARAccountRef", "Address", "AddressBlock", "CreditCardTxnInfo", "CurrencyRef", "CustomerRef", "DataExtRet", "EditSequence", "ExchangeRate", "ExternalGUID", "ListID", "Memo", "OwnerID", "PaymentMethodRef", "RefNumber", "RefundAppliedToTxnRet", "RefundFromAccountRef", "TimeCreated", "TimeModified", "TotalAmount", "TotalAmountInHomeCurrency", "TxnDate", "TxnID", "TxnNumber"]]
    #: Additional information.
    memo: str
    #: `payment_method_ref` identifies how a payment is made (for example, cash, check, or card
    #: type). If both `full_name` and `list_id` are provided, `full_name` is ignored.
    payment_method_ref: Ref
    #: `ref_number` is a user-managed transaction reference (for example, a check number). It
    #: can be edited and is not guaranteed to be globally unique. Some transaction types
    #: auto-populate `ref_number` when omitted, based on QuickBooks preferences and numbering
    #: state.
    ref_number: str
    #: In an ARRefundCreditCardAdd, the account which is the source of funds for the credit card
    #: refund. Normally this is Undeposited Funds. However, you can specify another account if
    #: you wish. If you specify nothing here, Undeposited Funds is used by default.
    refund_from_account_ref: Ref
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: The date of the transaction. In some cases, if you leave `txn_date` out of an -Add
    #: message, QuickBooks will prefill `txn_date` with the date of the last-saved transaction
    #: of the same type.
    txn_date: str


class ArRefundCreditCardQueryParams(TypedDict, total=False):
    """Params for ``ar_refund_credit_card.query`` (List ar refund credit cards)."""
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
    include_ret_element: List[Literal["ARAccountRef", "Address", "AddressBlock", "CreditCardTxnInfo", "CurrencyRef", "CustomerRef", "DataExtRet", "EditSequence", "ExchangeRate", "ExternalGUID", "Memo", "PaymentMethodRef", "RefNumber", "RefundAppliedToTxnRet", "RefundFromAccountRef", "TimeCreated", "TimeModified", "TotalAmount", "TotalAmountInHomeCurrency", "TxnDate", "TxnID", "TxnNumber"]]
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


class ArRefundCreditCard:
    """QuickBooks ar refund credit card operations: create, query.

    Get it from ``client.ar_refund_credit_card``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[ArRefundCreditCardCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create ar refund credit card.

        Queues ``ar_refund_credit_card.create``: POST /connections/{connection_id}/ar-refund-credit-cards, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``ArRefundCreditCardCreateParams``)::

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
            ar_account_ref: Ref
                full_name: str
                list_id: str
            credit_card_txn_info: CreditCardTxnInfo
                credit_card_txn_input_info: CreditCardTxnInputInfo (required)
                    commercial_card_code: str
                    credit_card_address: str
                    credit_card_number: str (required)
                    credit_card_postal_code: str
                    credit_card_txn_type: Literal["Authorization", "Capture", "Charge", "Refund", "VoiceAuthorization"]
                    expiration_month: int (required)
                    expiration_year: int (required)
                    name_on_card: str (required)
                    transaction_mode: Literal["CardNotPresent", "CardPresent"]
                credit_card_txn_result_info: CreditCardTxnResultInfo (required)
                    authorization_code: str
                    avs_street: Literal["Fail", "NotAvailable", "Pass"]
                    avs_zip: Literal["Fail", "NotAvailable", "Pass"]
                    card_security_code_match: Literal["Fail", "NotAvailable", "Pass"]
                    client_trans_id: str
                    credit_card_trans_id: str (required)
                    merchant_account_number: str (required)
                    payment_grouping_code: int
                    payment_status: Literal["Completed", "Unknown"] (required)
                    recon_batch_id: str
                    result_code: int (required)
                    result_message: str (required)
                    txn_authorization_stamp: int
                    txn_authorization_time: str (required)
            customer_ref: Ref (required)
            def_macro: str
            exchange_rate: float
            external_guid: str
            include_ret_element: List[Literal[...] (one of 24 values)]
            memo: str
            payment_method_ref: Ref
            ref_number: str
            refund_applied_to_txn_add: List[RefundAppliedToTxnAdd] (required)
                refund_amount: float (required)
                txn_id: str (required)
            refund_from_account_ref: Ref
            request_id: str
            txn_date: str

        Docs: https://docs.qubesync.com/api-reference/v2/ar-refund-credit-cards/create-ar-refund-credit-card
        """
        return self._client._queue_operation("ar_refund_credit_card.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[ArRefundCreditCardQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List ar refund credit cards.

        Queues ``ar_refund_credit_card.query``: GET /connections/{connection_id}/ar-refund-credit-cards, params in the query string.
        QuickBooks answers in pages: each page comes to ``webhook_url`` as its own webhook.
        Returns the queued request.

        Params (``ArRefundCreditCardQueryParams``)::

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
            include_ret_element: List[Literal[...] (one of 22 values)]
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

        Docs: https://docs.qubesync.com/api-reference/v2/ar-refund-credit-cards/list-ar-refund-credit-cards
        """
        return self._client._queue_operation("ar_refund_credit_card.query", connection_id, params, webhook_url, idempotency_key)
