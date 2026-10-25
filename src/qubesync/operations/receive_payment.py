# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks receive payment operations (``client.receive_payment``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    AppliedToTxnAdd,
    AppliedToTxnMod,
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
    SetCredit,
    TxnLineDetail,
)

if TYPE_CHECKING:
    from ..v2 import Client


class CreditCardTxnInputInfoMod(TypedDict, total=False):
    #: This optional field is used only for Visa and Master Card commercial cards. There are
    #: three types of these cards: purchase, corporate, and business. Normally, special lower
    #: transaction fee rates apply when these cards are used and this field is filled out. If
    #: this field is left blank, then the usual (and higher) discount rate applies.
    commercial_card_code: str
    #: The address associated with this credit card.
    credit_card_address: str
    #: Credit-card number for this customer or this payment. Beginning with qbXML spec 6.0 and
    #: QuickBooks 2007, you must mask the credit card number with lower case “x” and no dashes.
    #: For example, xxxxxxxxxxxx1234.
    credit_card_number: str
    #: The postal code associated with the address for this credit card.
    credit_card_postal_code: str
    #: Indicates the QBMS transaction from which the current transaction data originated, for
    #: example, Charge, Authorization, Capture, Refund, VoiceAuthorization, or Void.
    credit_card_txn_type: Literal["Authorization", "Capture", "Charge", "Refund", "VoiceAuthorization"]
    #: The month when the credit card expires.
    expiration_month: int
    #: The year when the credit card expires.
    expiration_year: int
    #: The name on the customer’s credit card.
    name_on_card: str
    #: Indicates whether this transaction came from a card swipe (tmCardPresent) or not
    #: (tmCardNotPresent).
    transaction_mode: Literal["CardNotPresent", "CardPresent"]


class CreditCardTxnResultInfoMod(TypedDict, total=False):
    #: The authorization code is returned from the credit card processor to indicate that the
    #: charge will be paid by the card issuer. In a voice authorization request
    #: (CustomerCreditCardVoiceAuthRq), the authorization code is supplied by the card issuer
    #: over the telephone.
    authorization_code: str
    #: This field contains the value avssPass if the street address supplied in the transaction
    #: request matches the customer’s address on file at the card issuer. It contains the value
    #: avssFail if there isn’t a match, or avssNotAvailable if the card issuer doesn’t support
    #: AVS. Note: This field was required in qbXML 4.1, but is optional in qbXML 5.0 and later.
    avs_street: Literal["Fail", "NotAvailable", "Pass"]
    #: This field contains the value avszPass if the customer postal ZIP code supplied in the
    #: transaction request matches the customer’s postal code recognized at the card issuer. It
    #: contains the value avszFail if there isn’t a match, or avszNotAvailable if the card
    #: issuer doesn’t support AVS. Note: This field was required in qbXML 4.1, but is optional
    #: in qbXML 5.0 and later.
    avs_zip: Literal["Fail", "NotAvailable", "Pass"]
    #: This field contains the value Pass if the card security code supplied in the transaction
    #: request matches the card security code recognized for that credit card number at the card
    #: issuer. It contains the value Fail if there isn’t a match.
    card_security_code_match: Literal["Fail", "NotAvailable", "Pass"]
    #: This value is returned from QBMS transactions for future use by the QuickBooks
    #: Reconciliation feature.
    client_trans_id: str
    #: This transaction ID is returned from the credit card processor. You should save this
    #: value for any possible QBMS SDK transaction requests that need it, for example,
    #: CustomerCreditCardTxnVoidRq, or CustomerCreditCardCaptureRq.
    credit_card_trans_id: str
    #: This is the QBMS account number of the merchant who is running the transaction using the
    #: customer’s credit card. It is returned from the transaction request and should be stored
    #: for subsequent transactions, such as using it in the QB SDK SalesReceiptAdd,
    #: ReceivePaymentAdd, ARRefundCreditCard requests to save the transaction data in
    #: QuickBooks.
    merchant_account_number: str
    #: Internal code needed for the QuickBooks reconciliation feature, if integrating with
    #: QuickBooks. This value is returned in the QBMS response to a QBMS transaction request,
    #: and must be subsequently supplied by your application in the QB SDK ReceivePaymentAdd or
    #: SalesReceiptAdd request.
    payment_grouping_code: int
    #: Indicates payment processing status as known by QuickBooks/QBMS integration state.
    #: `psCompleted` indicates confirmed success; `psUnknown` indicates status could not be
    #: definitively confirmed.
    payment_status: Literal["Completed", "Unknown"]
    #: This value is returned by QBMS from the transaction request, and is used internally by
    #: the QuickBooks/QBMS Recon (reconcile) feature. You should save this value without
    #: modification and include it in the QB SDK SalesReceiptAdd or ReceivePaymentAdd requests
    #: if you want to save the transaction data in QuickBooks.
    recon_batch_id: str
    #: This contains the status code returned in the original QBMS transaction response.
    result_code: int
    #: This contains the status message returned in the original QBMS transaction response.
    result_message: str
    #: This value is used to support the credit card transaction Reconcile feature within
    #: QuickBooks.
    txn_authorization_stamp: int
    #: Timestamp indicating the time in which the card processor authorized the transaction.
    txn_authorization_time: str


class CreditCardTxnInfoMod(TypedDict, total=False):
    #: This contains data originally supplied in the QBMS transaction request. This information
    #: block shouldn’t be used in CreditMemo requests for QuickBooks 2007 and new versions.
    #: Instead, use the ARRefundCreditCard request.
    credit_card_txn_input_info_mod: CreditCardTxnInputInfoMod
    #: This contains data returned in the QBMS transaction response. This information block
    #: shouldn’t be used in CreditMemo requests for QuickBooks 2007 and new versions. Instead,
    #: use the ARRefundCreditCard request.
    credit_card_txn_result_info_mod: CreditCardTxnResultInfoMod


class _ReceivePaymentCreateParamsRequired(TypedDict):
    #: `customer_ref` identifies a customer or customer job. If both `full_name` and `list_id`
    #: are provided, `full_name` is ignored. In SalesReceipt and ReceivePayment, it identifies
    #: who receives credit. In TimeTracking, it identifies who the time can be billed to and is
    #: required in TimeTrackingAdd when IsBillable is true.
    customer_ref: Ref


class ReceivePaymentCreateParams(_ReceivePaymentCreateParamsRequired, total=False):
    """Params for ``receive_payment.create`` (Record payment)."""
    applied_to_txn_add: List[AppliedToTxnAdd]
    #: `ar_account_ref` points to an Accounts Receivable account. If both `full_name` and
    #: `list_id` are provided, `full_name` is ignored.
    ar_account_ref: Ref
    #: Contains data from the credit card transaction used in the payment. This data originates
    #: from a previous qbmsXML credit card transaction. The data following the element
    #: `credit_card_txn_input_info`” data is the data from the original qbmsXML request. The
    #: “`credit_card_txn_result_info`” is the data from the original qbmsXML response.
    credit_card_txn_info: CreditCardTxnInfo
    #: `def_macro` lets you assign a reusable name to a returned `txn_id` or `txn_line_id` so
    #: later requests can reference it with `useMacro`. This feature requires SDK 2.0+.
    def_macro: str
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
    #: Allows for the attachment of a user defined GUID value.
    external_guid: str
    include_ret_element: List[Literal["ARAccountRef", "AppliedToTxnRet", "CreditCardTxnInfo", "CurrencyRef", "CustomerRef", "DataExtRet", "DepositToAccountRef", "EditSequence", "ExchangeRate", "ExternalGUID", "ListID", "Memo", "OwnerID", "PaymentMethodRef", "RefNumber", "TimeCreated", "TimeModified", "TotalAmount", "TotalAmountInHomeCurrency", "TxnDate", "TxnID", "TxnNumber", "UnusedCredits", "UnusedPayment"]]
    #: If `is_auto_apply` is true, QuickBooks applies `total_amount` to any outstanding
    #: transaction that exactly matches `total_amount`. If no exact match is found, the payment
    #: is applied to the customer job’s outstanding transactions, beginning with the oldest one.
    #: If `is_auto_apply` is false, QuickBooks receives the payment but doesn’t apply it to any
    #: outstanding transaction.
    is_auto_apply: bool
    #: The beginning of this memo will appear in reports that show details of this receive
    #: payment.
    memo: str
    #: `payment_method_ref` identifies how a payment is made (for example, cash, check, or card
    #: type). If both `full_name` and `list_id` are provided, `full_name` is ignored.
    payment_method_ref: Ref
    #: `ref_number` is a user-managed transaction reference (for example, a check number). It
    #: can be edited and is not guaranteed to be globally unique. Some transaction types
    #: auto-populate `ref_number` when omitted, based on QuickBooks preferences and numbering
    #: state.
    ref_number: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: Total amount of money received. For ReceivePaymentAdd, the sum of the `payment_amount`
    #: amounts (in the `applied_to_txn_add` aggregates that are included) can’t be greater than
    #: the `total_amount`, or you will receive an error.
    total_amount: float
    #: The date of the transaction. In some cases, if you leave `txn_date` out of an -Add
    #: message, QuickBooks will prefill `txn_date` with the date of the last-saved transaction
    #: of the same type.
    txn_date: str


class ReceivePaymentQueryParams(TypedDict, total=False):
    """Params for ``receive_payment.query`` (List receive payments)."""
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
    include_ret_element: List[Literal["ARAccountRef", "AppliedToTxnRet", "CreditCardTxnInfo", "CurrencyRef", "CustomerRef", "DataExtRet", "DepositToAccountRef", "EditSequence", "ExchangeRate", "ExternalGUID", "Memo", "PaymentMethodRef", "RefNumber", "TimeCreated", "TimeModified", "TotalAmount", "TotalAmountInHomeCurrency", "TxnDate", "TxnID", "TxnNumber", "UnusedCredits", "UnusedPayment"]]
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


class _ReceivePaymentUpdateParamsRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    txn_id: str


class ReceivePaymentUpdateParams(_ReceivePaymentUpdateParamsRequired, total=False):
    """Params for ``receive_payment.update`` (Update receive payment)."""
    applied_to_txn_mod: List[AppliedToTxnMod]
    #: `ar_account_ref` points to an Accounts Receivable account. If both `full_name` and
    #: `list_id` are provided, `full_name` is ignored.
    ar_account_ref: Ref
    #: Contains data from the credit card transaction used in the payment. This data originates
    #: from a previous qbmsXML credit card transaction. The data following the element
    #: `credit_card_txn_input_info`” data is the data from the original qbmsXML request. The
    #: “`credit_card_txn_result_info`” is the data from the original qbmsXML response.
    credit_card_txn_info_mod: CreditCardTxnInfoMod
    #: `customer_ref` identifies a customer or customer job. If both `full_name` and `list_id`
    #: are provided, `full_name` is ignored. In SalesReceipt and ReceivePayment, it identifies
    #: who receives credit. In TimeTracking, it identifies who the time can be billed to and is
    #: required in TimeTrackingAdd when IsBillable is true.
    customer_ref: Ref
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
    include_ret_element: List[Literal["ARAccountRef", "AppliedToTxnRet", "CreditCardTxnInfo", "CurrencyRef", "CustomerRef", "DataExtRet", "DepositToAccountRef", "EditSequence", "ExchangeRate", "ExternalGUID", "ListID", "Memo", "OwnerID", "PaymentMethodRef", "RefNumber", "TimeCreated", "TimeModified", "TotalAmount", "TotalAmountInHomeCurrency", "TxnDate", "TxnID", "TxnNumber", "UnusedCredits", "UnusedPayment"]]
    #: The beginning of this memo will appear in reports that show details of this receive
    #: payment.
    memo: str
    #: `payment_method_ref` identifies how a payment is made (for example, cash, check, or card
    #: type). If both `full_name` and `list_id` are provided, `full_name` is ignored.
    payment_method_ref: Ref
    #: `ref_number` is a user-managed transaction reference (for example, a check number). It
    #: can be edited and is not guaranteed to be globally unique. Some transaction types
    #: auto-populate `ref_number` when omitted, based on QuickBooks preferences and numbering
    #: state.
    ref_number: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: Total amount of money received. For ReceivePaymentAdd, the sum of the `payment_amount`
    #: amounts (in the AppliedToTxnAdd aggregates that are included) can’t be greater than the
    #: `total_amount`, or you will receive an error.
    total_amount: float
    #: The date of the transaction. In some cases, if you leave `txn_date` out of an -Add
    #: message, QuickBooks will prefill `txn_date` with the date of the last-saved transaction
    #: of the same type.
    txn_date: str


class ReceivePayment:
    """QuickBooks receive payment operations: create, query, update.

    Get it from ``client.receive_payment``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[ReceivePaymentCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record payment.

        Queues ``receive_payment.create``: POST /connections/{connection_id}/payments, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``ReceivePaymentCreateParams``)::

            applied_to_txn_add: List[AppliedToTxnAdd]
                discount_account_ref: Ref
                    full_name: str
                    list_id: str
                discount_amount: float
                discount_class_ref: Ref
                payment_amount: float
                set_credit: List[SetCredit]
                    applied_amount: float (required)
                    credit_txn_id: str (required)
                    override: bool
                    txn_line_id: str
                txn_id: str (required)
                txn_line_detail: List[TxnLineDetail]
                    amount: float (required)
                    txn_line_id: str (required)
            ar_account_ref: Ref
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
            deposit_to_account_ref: Ref
            exchange_rate: float
            external_guid: str
            include_ret_element: List[Literal[...] (one of 24 values)]
            is_auto_apply: bool
            memo: str
            payment_method_ref: Ref
            ref_number: str
            request_id: str
            total_amount: float
            txn_date: str

        Docs: https://docs.qubesync.com/api-reference/v2/payments/record-payment
        """
        return self._client._queue_operation("receive_payment.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[ReceivePaymentQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List receive payments.

        Queues ``receive_payment.query``: GET /connections/{connection_id}/receive-payments, params in the query string.
        QuickBooks answers in pages: each page comes to ``webhook_url`` as its own webhook.
        Returns the queued request.

        Params (``ReceivePaymentQueryParams``)::

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

        Docs: https://docs.qubesync.com/api-reference/v2/receive-payments/list-receive-payments
        """
        return self._client._queue_operation("receive_payment.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[ReceivePaymentUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update receive payment.

        Queues ``receive_payment.update``: PUT /connections/{connection_id}/receive-payments, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``ReceivePaymentUpdateParams``)::

            applied_to_txn_mod: List[AppliedToTxnMod]
                discount_account_ref: Ref
                    full_name: str
                    list_id: str
                discount_amount: float
                discount_class_ref: Ref
                payment_amount: float
                set_credit: List[SetCredit]
                    applied_amount: float (required)
                    credit_txn_id: str (required)
                    override: bool
                    txn_line_id: str
                txn_id: str (required)
            ar_account_ref: Ref
            credit_card_txn_info_mod: CreditCardTxnInfoMod
                credit_card_txn_input_info_mod: CreditCardTxnInputInfoMod
                    commercial_card_code: str
                    credit_card_address: str
                    credit_card_number: str
                    credit_card_postal_code: str
                    credit_card_txn_type: Literal["Authorization", "Capture", "Charge", "Refund", "VoiceAuthorization"]
                    expiration_month: int
                    expiration_year: int
                    name_on_card: str
                    transaction_mode: Literal["CardNotPresent", "CardPresent"]
                credit_card_txn_result_info_mod: CreditCardTxnResultInfoMod
                    authorization_code: str
                    avs_street: Literal["Fail", "NotAvailable", "Pass"]
                    avs_zip: Literal["Fail", "NotAvailable", "Pass"]
                    card_security_code_match: Literal["Fail", "NotAvailable", "Pass"]
                    client_trans_id: str
                    credit_card_trans_id: str
                    merchant_account_number: str
                    payment_grouping_code: int
                    payment_status: Literal["Completed", "Unknown"]
                    recon_batch_id: str
                    result_code: int
                    result_message: str
                    txn_authorization_stamp: int
                    txn_authorization_time: str
            customer_ref: Ref
            deposit_to_account_ref: Ref
            edit_sequence: str (required)
            exchange_rate: float
            include_ret_element: List[Literal[...] (one of 24 values)]
            memo: str
            payment_method_ref: Ref
            ref_number: str
            request_id: str
            total_amount: float
            txn_date: str
            txn_id: str (required)

        Docs: https://docs.qubesync.com/api-reference/v2/receive-payments/update-receive-payment
        """
        return self._client._queue_operation("receive_payment.update", connection_id, params, webhook_url, idempotency_key)
