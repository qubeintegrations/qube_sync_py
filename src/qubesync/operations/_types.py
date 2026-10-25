# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""Nested params types more than one entity uses."""

from typing import List, Literal, TypedDict


class Ref(TypedDict, total=False):
    #: `full_name` (along with `list_id`) is a way to identify a list object. The `full_name` is
    #: the name prefixed by the names of each ancestor, for example Jones:Kitchen:Cabinets.
    #: `full_name` values aren’t case-sensitive.
    full_name: str
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list type, not globally
    #: across all lists. If both `full_name` and `list_id` are supplied in a request, QuickBooks
    #: uses `list_id` and ignores `full_name`.
    list_id: str


class CurrencyFilter(TypedDict, total=False):
    #: `full_name` (along with `list_id`) is a way to identify a list object. The `full_name` is
    #: the name prefixed by the names of each ancestor, for example Jones:Kitchen:Cabinets.
    #: `full_name` values aren’t case-sensitive.
    full_name: List[str]
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list type, not globally
    #: across all lists. If both `full_name` and `list_id` are supplied in a request, QuickBooks
    #: uses `list_id` and ignores `full_name`.
    list_id: List[str]


class _NameFilterRequired(TypedDict):
    #: The criterion to match.
    match_criterion: Literal["Contains", "EndsWith", "StartsWith"]
    #: The string to match.
    name: str


class NameFilter(_NameFilterRequired, total=False):
    pass


class NameRangeFilter(TypedDict, total=False):
    #: The first name or item in the search range. If `from_name` is omitted, the range will
    #: begin with first name on the list.
    from_name: str
    #: The final name or item in the search range. If `to_name` is omitted, the range will end
    #: with last name on the list.
    to_name: str


class AccountFilter(TypedDict, total=False):
    #: Allows you to report on a specific account type.
    account_type_filter: Literal["APAndSalesTax", "APOrCreditCard", "ARAndAP", "AccountsPayable", "AccountsReceivable", "AllowedFor1099", "Asset", "BalanceSheet", "Bank", "BankAndARAndAPAndUF", "BankAndUF", "CostOfSales", "CreditCard", "CurrentAsset", "CurrentAssetAndExpense", "CurrentLiability", "Equity", "EquityAndIncomeAndExpense", "ExpenseAndOtherExpense", "FixedAsset", "IncomeAndExpense", "IncomeAndOtherIncome", "Liability", "LiabilityAndEquity", "LongTermLiability", "NonPosting", "OrdinaryExpense", "OrdinaryIncome", "OrdinaryIncomeAndCOGS", "OrdinaryIncomeAndExpense", "OtherAsset", "OtherCurrentAsset", "OtherCurrentLiability", "OtherExpense", "OtherIncome", "OtherIncomeOrExpense"]
    full_name: List[str]
    #: Allows you to filter for data that relates to the specified object and its descendants.
    #: For names that don’t have children, `full_name_with_children` is exactly the same as
    #: `full_name`.
    full_name_with_children: str
    list_id: List[str]
    #: Allows you to filter for data that relates to the specified object and its descendants.
    list_id_with_children: str


class EntityFilter(TypedDict, total=False):
    full_name: List[str]
    #: Allows you to filter for data that relates to the specified object and its descendants.
    #: For names that don’t have children, `full_name_with_children` is exactly the same as
    #: `full_name`.
    full_name_with_children: str
    list_id: List[str]
    #: Allows you to filter for data that relates to the specified object and its descendants.
    list_id_with_children: str


class ReportEntityFilter(TypedDict, total=False):
    #: Allows you to report on a specific name type.
    entity_type_filter: Literal["Customer", "Employee", "OtherName", "Vendor"]
    full_name: List[str]
    #: Allows you to filter for data that relates to the specified object and its descendants.
    #: For names that don’t have children, `full_name_with_children` is exactly the same as
    #: `full_name`.
    full_name_with_children: str
    list_id: List[str]
    #: Allows you to filter for data that relates to the specified object and its descendants.
    list_id_with_children: str


class ItemFilter(TypedDict, total=False):
    full_name: List[str]
    #: Allows you to filter for data that relates to the specified object and its descendants.
    #: For names that don’t have children, `full_name_with_children` is exactly the same as
    #: `full_name`.
    full_name_with_children: str
    #: Allows you to report on a specific item type.
    item_type_filter: Literal["AllExceptFixedAsset", "Assembly", "Discount", "FixedAsset", "Inventory", "InventoryAndAssembly", "NonInventory", "OtherCharge", "Payment", "Sales", "SalesTax", "Service"]
    list_id: List[str]
    #: Allows you to filter for data that relates to the specified object and its descendants.
    list_id_with_children: str


class ReportModifiedDateRangeFilter(TypedDict, total=False):
    #: Selects information from this date and later. The range of acceptable dates is 1970-01-01
    #: to 2038-01-19T03:14:07 (2038-01-18T19:14:07-08:00 PST).
    from_report_modified_date: str
    #: Selects information created on this date or earlier. The range of acceptable dates is
    #: 1970-01-01 to 2038-01-19T03:14:07 (2038-01-18T19:14:07-08:00 PST).
    to_report_modified_date: str


class ReportPeriod(TypedDict, total=False):
    #: Selects information from this date and later. The range of acceptable `from_report_date`
    #: and `to_report_date` values depends on how the report dates are determined. If the report
    #: dates are based on the dates of transactions, the range is 01/01/1901 to 12/31/9999.
    from_report_date: str
    #: Selects information created on this date or earlier. The range of acceptable
    #: `to_report_date` and `from_report_date` values depends on how the report dates are
    #: determined. If the report dates are based on the dates of transactions, the range is
    #: 01/01/1901 to 12/31/9999.
    to_report_date: str


class _TypeFilterRequired(TypedDict):
    txn_type_filter: List[Literal["ARRefundCreditCard", "All", "Bill", "BillPaymentCheck", "BillPaymentCreditCard", "BuildAssembly", "Charge", "Check", "CreditCardCharge", "CreditCardCredit", "CreditMemo", "Deposit", "Estimate", "InventoryAdjustment", "Invoice", "ItemReceipt", "JournalEntry", "LiabilityAdjustment", "Paycheck", "PayrollLiabilityCheck", "PurchaseOrder", "ReceivePayment", "SalesOrder", "SalesReceipt", "SalesTaxPaymentCheck", "Transfer", "VendorCredit", "YTDAdjustment"]]


class TypeFilter(_TypeFilterRequired, total=False):
    pass


class Address(TypedDict, total=False):
    #: The first line of an address.
    addr1: str
    #: The second line of an address (if a second line is needed).
    addr2: str
    #: The third line of an address (if a third line is needed).
    addr3: str
    #: The fourth line of an address (if a fourth line is needed).
    addr4: str
    #: The fifth line of an address (if a fifth line is needed).
    addr5: str
    #: The city name in an address.
    city: str
    #: The country name in an address, or, in returned Host information (HostRet or HostInfo),
    #: the country for which this edition of QuickBooks was designed. (Possible values are US,
    #: CA, UK, and AU.)
    country: str
    #: In a BillAddress or ShipAddress aggregate, the Note field value is written at the bottom
    #: of the address in the form in which it appears, such as the invoice form.
    note: str
    #: The postal code in an address.
    postal_code: str
    #: The state name in an address.
    state: str


class _CreditCardTxnInputInfoRequired(TypedDict):
    #: Credit-card number for this customer or this payment. Beginning with qbXML spec 6.0 and
    #: QuickBooks 2007, you must mask the credit card number with lower case “x” and no dashes.
    #: For example, xxxxxxxxxxxx1234.
    credit_card_number: str
    #: The month when the credit card expires.
    expiration_month: int
    #: The year when the credit card expires.
    expiration_year: int
    #: The name on the customer’s credit card.
    name_on_card: str


class CreditCardTxnInputInfo(_CreditCardTxnInputInfoRequired, total=False):
    #: This optional field is used only for Visa and Master Card commercial cards. There are
    #: three types of these cards: purchase, corporate, and business. Normally, special lower
    #: transaction fee rates apply when these cards are used and this field is filled out. If
    #: this field is left blank, then the usual (and higher) discount rate applies.
    commercial_card_code: str
    #: The address associated with this credit card.
    credit_card_address: str
    #: The postal code associated with the address for this credit card.
    credit_card_postal_code: str
    #: Indicates the QBMS transaction from which the current transaction data originated, for
    #: example, Charge, Authorization, Capture, Refund, VoiceAuthorization, or Void.
    credit_card_txn_type: Literal["Authorization", "Capture", "Charge", "Refund", "VoiceAuthorization"]
    #: Indicates whether this transaction came from a card swipe (tmCardPresent) or not
    #: (tmCardNotPresent).
    transaction_mode: Literal["CardNotPresent", "CardPresent"]


class _CreditCardTxnResultInfoRequired(TypedDict):
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
    #: Indicates payment processing status as known by QuickBooks/QBMS integration state.
    #: `psCompleted` indicates confirmed success; `psUnknown` indicates status could not be
    #: definitively confirmed.
    payment_status: Literal["Completed", "Unknown"]
    #: This contains the status code returned in the original QBMS transaction response.
    result_code: int
    #: This contains the status message returned in the original QBMS transaction response.
    result_message: str
    #: Timestamp indicating the time in which the card processor authorized the transaction.
    txn_authorization_time: str


class CreditCardTxnResultInfo(_CreditCardTxnResultInfoRequired, total=False):
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
    #: Internal code needed for the QuickBooks reconciliation feature, if integrating with
    #: QuickBooks. This value is returned in the QBMS response to a QBMS transaction request,
    #: and must be subsequently supplied by your application in the QB SDK ReceivePaymentAdd or
    #: SalesReceiptAdd request.
    payment_grouping_code: int
    #: This value is returned by QBMS from the transaction request, and is used internally by
    #: the QuickBooks/QBMS Recon (reconcile) feature. You should save this value without
    #: modification and include it in the QB SDK SalesReceiptAdd or ReceivePaymentAdd requests
    #: if you want to save the transaction data in QuickBooks.
    recon_batch_id: str
    #: This value is used to support the credit card transaction Reconcile feature within
    #: QuickBooks.
    txn_authorization_stamp: int


class _CreditCardTxnInfoRequired(TypedDict):
    #: This contains data originally supplied in the QBMS transaction request. This information
    #: block shouldn’t be used in CreditMemo requests for QuickBooks 2007 and new versions.
    #: Instead, use the ARRefundCreditCard request.
    credit_card_txn_input_info: CreditCardTxnInputInfo
    #: This contains data returned in the QBMS transaction response. This information block
    #: shouldn’t be used in CreditMemo requests for QuickBooks 2007 and new versions. Instead,
    #: use the ARRefundCreditCard request.
    credit_card_txn_result_info: CreditCardTxnResultInfo


class CreditCardTxnInfo(_CreditCardTxnInfoRequired, total=False):
    pass


class ModifiedDateRangeFilter(TypedDict, total=False):
    #: Filters results to objects modified on or after this timestamp. QuickBooks Desktop
    #: accepts 1970-01-01 through 2038-01-19T03:14:07. If only a date is provided, time defaults
    #: to 00:00:00.
    from_modified_date: str
    #: Filters results to objects modified on or before this timestamp. QuickBooks Desktop
    #: accepts 1970-01-01 through 2038-01-19T03:14:07. If only a date is provided, time defaults
    #: to end-of-day (23:59:59).
    to_modified_date: str


class _RefNumberFilterRequired(TypedDict):
    #: The criterion to match.
    match_criterion: Literal["Contains", "EndsWith", "StartsWith"]
    #: `ref_number` is a user-managed transaction reference (for example, a check number). It
    #: can be edited and is not guaranteed to be globally unique. Some transaction types
    #: auto-populate `ref_number` when omitted, based on QuickBooks preferences and numbering
    #: state.
    ref_number: str


class RefNumberFilter(_RefNumberFilterRequired, total=False):
    pass


class RefNumberRangeFilter(TypedDict, total=False):
    #: The first `ref_number` in the search range. If `from_ref_number` is omitted, the range
    #: will begin with first number on the list.
    from_ref_number: str
    #: The final `ref_number` in the search range. If `to_ref_number` is omitted, the range will
    #: end with last number on the list.
    to_ref_number: str


class DateRangeFilter(TypedDict, total=False):
    #: `date_macro` filters by transaction date (not last-modified date). Do not combine
    #: `date_macro` with `from_modified_date`/`to_modified_date` in the same query filter set.
    date_macro: Literal["All", "LastCalendarQuarter", "LastCalendarQuarterToDate", "LastCalendarYear", "LastCalendarYearToDate", "LastFiscalQuarter", "LastFiscalQuarterToDate", "LastFiscalYear", "LastFiscalYearToDate", "LastMonth", "LastMonthToDate", "LastWeek", "LastWeekToDate", "NextCalendarQuarter", "NextCalendarYear", "NextFiscalQuarter", "NextFiscalYear", "NextFourWeeks", "NextMonth", "NextWeek", "ThisCalendarQuarter", "ThisCalendarQuarterToDate", "ThisCalendarYear", "ThisCalendarYearToDate", "ThisFiscalQuarter", "ThisFiscalQuarterToDate", "ThisFiscalYear", "ThisFiscalYearToDate", "ThisMonth", "ThisMonthToDate", "ThisWeek", "ThisWeekToDate", "Today", "Yesterday"]
    #: Selects transactions created on or after this date. Both `from_txn_date` and
    #: `to_txn_date` must be between 01/01/1901 and 12/31/9999.If you omit `from_txn_date`, it
    #: will be set to 1970-01-01 (1969-12-31 PST).
    from_txn_date: str
    #: Selects transactions created on or before this date. Both `to_txn_date` and
    #: `from_txn_date` must be between 01/01/1901 and 12/31/9999. If you omit `to_txn_date`, it
    #: will be set to 2038-01-19 (2038-01-18 PST).
    to_txn_date: str


class _BillDataExtRequired(TypedDict):
    #: The name of the data extension. If this is a custom field, `data_ext_name` will be
    #: visible as a label in the QuickBooks user interface. Also because `owner_id` and
    #: `data_ext_name` together make the data extension unique, and because custom fields all
    #: have the same `owner_id` of zero, the `data_ext_name` must be a unique value among
    #: existing custom fields.
    data_ext_name: str
    #: The data in this field. The maximum length of `data_ext_value` will depend on the
    #: `data_ext_type` of this data extension. For example, if `data_ext_type` is STR255TYPE,
    #: the maximum length of `data_ext_value` is 255 characters. If `data_ext_type` is
    #: STR1024TYPE, the maximum size of `data_ext_value` is 1KB.
    data_ext_value: str
    #: `owner_id` identifies who owns the data extension. Use 0 for QuickBooks custom fields
    #: that appear in the UI, or use a GUID for private extensions owned by an app. Keep private
    #: GUIDs confidential unless you intentionally share extensions across apps. If you do share
    #: them, both apps must use the same `owner_id` and `data_ext_name`, because that pair
    #: uniquely identifies the extension.
    owner_id: str


class BillDataExt(_BillDataExtRequired, total=False):
    pass


class ExpenseLineAdd(TypedDict, total=False):
    #: `account_ref` points to an account in the company file. If both `full_name` and `list_id`
    #: are provided, `full_name` is ignored. Meaning depends on context: for checks it is the
    #: funding account; for `expense_line_add` it may be required by accounting preferences; for
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
    #: `customer_ref` identifies a customer or customer job. If both `full_name` and `list_id`
    #: are provided, `full_name` is ignored. In SalesReceipt and ReceivePayment, it identifies
    #: who receives credit. In TimeTracking, it identifies who the time can be billed to and is
    #: required in TimeTrackingAdd when IsBillable is true.
    customer_ref: Ref
    data_ext: List[BillDataExt]
    #: `def_macro` lets you assign a reusable name to a returned `txn_id` or `txn_line_id` so
    #: later requests can reference it with `useMacro`. This feature requires SDK 2.0+.
    def_macro: str
    #: Appears in the A/P register and in reports that include this bill.
    memo: str
    #: A sales representative must be on the Employee, Vendor, or Other Names list within
    #: QuickBooks. Sales representative’s names and initials appear on the Rep drop-down list on
    #: QuickBooks sales forms. A `sales_rep_ref` refers to a person on the SalesRep list. In a
    #: request, if a `sales_rep_ref` aggregate includes both `full_name` and `list_id`,
    #: `full_name` will be ignored.
    sales_rep_ref: Ref
    #: `sales_tax_code_ref` points to the sales-tax code used for an item or customer context.
    #: QuickBooks includes default TAX and NON codes, and a code can be deleted only when
    #: nothing references it. If sales tax is disabled, QuickBooks assigns the default
    #: non-taxable code. If both `full_name` and `list_id` are provided in `sales_tax_code_ref`,
    #: `full_name` is ignored.
    sales_tax_code_ref: Ref
    tax_amount: float


class _ItemGroupLineAddRequired(TypedDict):
    #: ItemGroup objects represent items that are grouped together for fast entry, and an
    #: `item_group_ref` aggregate refers to one of these item groups. In a request, if an
    #: `item_group_ref` aggregate includes both `full_name` and `list_id`, `full_name` will be
    #: ignored. You can use an ItemGroupQuery request to get information about all the item
    #: groups that are set up in the QuickBooks file.
    item_group_ref: Ref


class ItemGroupLineAdd(_ItemGroupLineAddRequired, total=False):
    data_ext: List[BillDataExt]
    #: A descriptive text field.
    desc: str
    #: Location within the Inventory Site
    inventory_site_location_ref: Ref
    #: Site where inventory is located.
    inventory_site_ref: Ref
    #: On transaction lines, QuickBooks can derive one value from the other two among Quantity,
    #: Rate, and Amount. If you supply Quantity and Amount, QuickBooks calculates Rate. If you
    #: supply Quantity and Rate, QuickBooks calculates Amount.
    quantity: float
    #: In a transaction line item, the name of the unit of measure selected from within the
    #: item’s available units. If the company file is enabled only for single unit of measure
    #: per item, this must be the base unit!
    unit_of_measure: str


class _LinkToTxnRequired(TypedDict):
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    txn_id: str
    #: Identification number of the transaction line. (`txn_line_id` is supported as of v2.0 of
    #: the SDK. With qbXML v1.0 and v1.1, `txn_line_id` is always returned as zero.) If you need
    #: to add a new transaction line in a transaction Mod request, you can do so by setting the
    #: `txn_line_id` to -1.
    txn_line_id: str


class LinkToTxn(_LinkToTxnRequired, total=False):
    pass


class ItemLineAdd(TypedDict, total=False):
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
    #: If both Quantity and Amount are specified, QuickBooks will use them to calculate Cost.
    #: Likewise, if both Quantity and Cost are specified, QuickBooks will use them to calculate
    #: the total Amount.
    cost: float
    #: `customer_ref` identifies a customer or customer job. If both `full_name` and `list_id`
    #: are provided, `full_name` is ignored. In SalesReceipt and ReceivePayment, it identifies
    #: who receives credit. In TimeTracking, it identifies who the time can be billed to and is
    #: required in TimeTrackingAdd when IsBillable is true.
    customer_ref: Ref
    data_ext: List[BillDataExt]
    #: A descriptive text field.
    desc: str
    #: Location within the Inventory Site
    inventory_site_location_ref: Ref
    #: Site where inventory is located.
    inventory_site_ref: Ref
    #: `item_ref` may accept all item types or a restricted subset, depending on the request.
    #: Examples: PurchaseOrder and Bill do not allow discount or sales-tax items;
    #: VehicleMileageAdd requires a service or other-charge item; BillingRateAdd requires a
    #: service item. If both `full_name` and `list_id` are provided, `full_name` is ignored.
    item_ref: Ref
    #: When used with InvoiceAdd, the transaction you are linking to via this field must be a
    #: SalesOrder; links to other transactions, such as to estimates, aren’t currently
    #: supported. When used with BillAdd or ItemReceiptAdd, the transaction you are linking to
    #: via this field must be a PurchaseOrder: links to other transactions aren’t currently
    #: supported.
    link_to_txn: LinkToTxn
    #: The lot number of the asset.
    #:
    #: Choose at most one of: `serial_number`, or `lot_number`.
    lot_number: str
    #: Refers to a QuickBooks account. If an `override_item_account_ref` aggregate includes both
    #: `full_name` and `list_id`, `full_name` will be ignored.
    override_item_account_ref: Ref
    #: On transaction lines, QuickBooks can derive one value from the other two among Quantity,
    #: Rate, and Amount. If you supply Quantity and Amount, QuickBooks calculates Rate. If you
    #: supply Quantity and Rate, QuickBooks calculates Amount.
    quantity: float
    #: A sales representative must be on the Employee, Vendor, or Other Names list within
    #: QuickBooks. Sales representative’s names and initials appear on the Rep drop-down list on
    #: QuickBooks sales forms. A `sales_rep_ref` refers to a person on the SalesRep list. In a
    #: request, if a `sales_rep_ref` aggregate includes both `full_name` and `list_id`,
    #: `full_name` will be ignored.
    sales_rep_ref: Ref
    #: `sales_tax_code_ref` points to the sales-tax code used for an item or customer context.
    #: QuickBooks includes default TAX and NON codes, and a code can be deleted only when
    #: nothing references it. If sales tax is disabled, QuickBooks assigns the default
    #: non-taxable code. If both `full_name` and `list_id` are provided in `sales_tax_code_ref`,
    #: `full_name` is ignored.
    sales_tax_code_ref: Ref
    #: The serial number of the asset.
    #:
    #: Choose at most one of: `serial_number`, or `lot_number`.
    serial_number: str
    tax_amount: float
    #: In a transaction line item, the name of the unit of measure selected from within the
    #: item’s available units. If the company file is enabled only for single unit of measure
    #: per item, this must be the base unit!
    unit_of_measure: str


class _ExpenseLineModRequired(TypedDict):
    #: Identification number of the transaction line. (`txn_line_id` is supported as of v2.0 of
    #: the SDK. With qbXML v1.0 and v1.1, `txn_line_id` is always returned as zero.) If you need
    #: to add a new transaction line in a transaction Mod request, you can do so by setting the
    #: `txn_line_id` to -1.
    txn_line_id: str


class ExpenseLineMod(_ExpenseLineModRequired, total=False):
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
    #: `customer_ref` identifies a customer or customer job. If both `full_name` and `list_id`
    #: are provided, `full_name` is ignored. In SalesReceipt and ReceivePayment, it identifies
    #: who receives credit. In TimeTracking, it identifies who the time can be billed to and is
    #: required in TimeTrackingAdd when IsBillable is true.
    customer_ref: Ref
    #: Appears in the A/P register and in reports that include this bill.
    memo: str
    #: A sales representative must be on the Employee, Vendor, or Other Names list within
    #: QuickBooks. Sales representative’s names and initials appear on the Rep drop-down list on
    #: QuickBooks sales forms. A `sales_rep_ref` refers to a person on the SalesRep list. In a
    #: request, if a `sales_rep_ref` aggregate includes both `full_name` and `list_id`,
    #: `full_name` will be ignored.
    sales_rep_ref: Ref
    #: `sales_tax_code_ref` points to the sales-tax code used for an item or customer context.
    #: QuickBooks includes default TAX and NON codes, and a code can be deleted only when
    #: nothing references it. If sales tax is disabled, QuickBooks assigns the default
    #: non-taxable code. If both `full_name` and `list_id` are provided in `sales_tax_code_ref`,
    #: `full_name` is ignored.
    sales_tax_code_ref: Ref
    tax_amount: float


class _ItemLineModRequired(TypedDict):
    #: Identification number of the transaction line. (`txn_line_id` is supported as of v2.0 of
    #: the SDK. With qbXML v1.0 and v1.1, `txn_line_id` is always returned as zero.) If you need
    #: to add a new transaction line in a transaction Mod request, you can do so by setting the
    #: `txn_line_id` to -1.
    txn_line_id: str


class ItemLineMod(_ItemLineModRequired, total=False):
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
    #: If both Quantity and Amount are specified, QuickBooks will use them to calculate Cost.
    #: Likewise, if both Quantity and Cost are specified, QuickBooks will use them to calculate
    #: the total Amount.
    cost: float
    #: `customer_ref` identifies a customer or customer job. If both `full_name` and `list_id`
    #: are provided, `full_name` is ignored. In SalesReceipt and ReceivePayment, it identifies
    #: who receives credit. In TimeTracking, it identifies who the time can be billed to and is
    #: required in TimeTrackingAdd when IsBillable is true.
    customer_ref: Ref
    #: A descriptive text field.
    desc: str
    #: Location within the Inventory Site
    inventory_site_location_ref: Ref
    #: Site where inventory is located.
    inventory_site_ref: Ref
    #: `item_ref` may accept all item types or a restricted subset, depending on the request.
    #: Examples: PurchaseOrder and Bill do not allow discount or sales-tax items;
    #: VehicleMileageAdd requires a service or other-charge item; BillingRateAdd requires a
    #: service item. If both `full_name` and `list_id` are provided, `full_name` is ignored.
    item_ref: Ref
    #: The lot number of the asset.
    #:
    #: Choose at most one of: `serial_number`, or `lot_number`.
    lot_number: str
    #: Refers to a QuickBooks account. If an `override_item_account_ref` aggregate includes both
    #: `full_name` and `list_id`, `full_name` will be ignored.
    override_item_account_ref: Ref
    #: When you modify a transaction line to change the unit of measure used in that line, you
    #: use this aggregate to specify the UOM set within which you are choosing an available unit
    #: of measure. The “override” here refers to the unit within the set, not the UOM Set
    #: itself, which you can’t change or override–the UOM set that can be set or changed only in
    #: the item itself via an Item Mod request.
    override_uom_set_ref: Ref
    #: On transaction lines, QuickBooks can derive one value from the other two among Quantity,
    #: Rate, and Amount. If you supply Quantity and Amount, QuickBooks calculates Rate. If you
    #: supply Quantity and Rate, QuickBooks calculates Amount.
    quantity: float
    #: A sales representative must be on the Employee, Vendor, or Other Names list within
    #: QuickBooks. Sales representative’s names and initials appear on the Rep drop-down list on
    #: QuickBooks sales forms. A `sales_rep_ref` refers to a person on the SalesRep list. In a
    #: request, if a `sales_rep_ref` aggregate includes both `full_name` and `list_id`,
    #: `full_name` will be ignored.
    sales_rep_ref: Ref
    #: `sales_tax_code_ref` points to the sales-tax code used for an item or customer context.
    #: QuickBooks includes default TAX and NON codes, and a code can be deleted only when
    #: nothing references it. If sales tax is disabled, QuickBooks assigns the default
    #: non-taxable code. If both `full_name` and `list_id` are provided in `sales_tax_code_ref`,
    #: `full_name` is ignored.
    sales_tax_code_ref: Ref
    #: The serial number of the asset.
    #:
    #: Choose at most one of: `serial_number`, or `lot_number`.
    serial_number: str
    tax_amount: float
    #: In a transaction line item, the name of the unit of measure selected from within the
    #: item’s available units. If the company file is enabled only for single unit of measure
    #: per item, this must be the base unit!
    unit_of_measure: str


class _ItemGroupLineModRequired(TypedDict):
    #: Identification number of the transaction line. (`txn_line_id` is supported as of v2.0 of
    #: the SDK. With qbXML v1.0 and v1.1, `txn_line_id` is always returned as zero.) If you need
    #: to add a new transaction line in a transaction Mod request, you can do so by setting the
    #: `txn_line_id` to -1.
    txn_line_id: str


class ItemGroupLineMod(_ItemGroupLineModRequired, total=False):
    #: ItemGroup objects represent items that are grouped together for fast entry, and an
    #: `item_group_ref` aggregate refers to one of these item groups. In a request, if an
    #: `item_group_ref` aggregate includes both `full_name` and `list_id`, `full_name` will be
    #: ignored. You can use an ItemGroupQuery request to get information about all the item
    #: groups that are set up in the QuickBooks file.
    item_group_ref: Ref
    #: An ItemLine is used to track any portion of a transaction that represents the purchase of
    #: an “item.” If ItemLineAdd doesn’t specify an Amount, Cost, or Quantity, then QuickBooks
    #: will calculate Amount based on a Quantity of 1 and the suggested Cost.
    item_line_mod: List[ItemLineMod]
    #: When you modify a transaction line to change the unit of measure used in that line, you
    #: use this aggregate to specify the UOM set within which you are choosing an available unit
    #: of measure. The “override” here refers to the unit within the set, not the UOM Set
    #: itself, which you can’t change or override–the UOM set that can be set or changed only in
    #: the item itself via an Item Mod request.
    override_uom_set_ref: Ref
    #: On transaction lines, QuickBooks can derive one value from the other two among Quantity,
    #: Rate, and Amount. If you supply Quantity and Amount, QuickBooks calculates Rate. If you
    #: supply Quantity and Rate, QuickBooks calculates Amount.
    quantity: float
    #: In a transaction line item, the name of the unit of measure selected from within the
    #: item’s available units. If the company file is enabled only for single unit of measure
    #: per item, this must be the base unit!
    unit_of_measure: str


class _SetCreditRequired(TypedDict):
    #: Amount of a credit that is applied to a customer’s invoice, or amount of a payment that
    #: is applied to a particular bill or vendor credit.
    applied_amount: float
    #: The ID of the credit memo that you are applying to this invoice or bill.
    credit_txn_id: str


class SetCredit(_SetCreditRequired, total=False):
    #: Option to override credit
    override: bool
    txn_line_id: str


class _TxnLineDetailRequired(TypedDict):
    #: A monetary amount.
    amount: float
    txn_line_id: str


class TxnLineDetail(_TxnLineDetailRequired, total=False):
    pass


class _AppliedToTxnAddRequired(TypedDict):
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    txn_id: str


class AppliedToTxnAdd(_AppliedToTxnAddRequired, total=False):
    #: Refers to the account where this discount is tracked. In a request, if a
    #: `discount_account_ref` aggregate includes both `full_name` and `list_id`, `full_name`
    #: will be ignored.
    discount_account_ref: Ref
    #: Reduces the receivable amount.
    discount_amount: float
    #: Class reference used in the Discount object
    discount_class_ref: Ref
    #: Represents the amount assigned to a particular receivable. The sum of all
    #: `payment_amount` elements in any given receive payment transaction must not be greater
    #: than TotalAmount.
    payment_amount: float
    set_credit: List[SetCredit]
    txn_line_detail: List[TxnLineDetail]


class _AppliedToTxnModRequired(TypedDict):
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    txn_id: str


class AppliedToTxnMod(_AppliedToTxnModRequired, total=False):
    #: Refers to the account where this discount is tracked. In a request, if a
    #: `discount_account_ref` aggregate includes both `full_name` and `list_id`, `full_name`
    #: will be ignored.
    discount_account_ref: Ref
    #: Reduces the receivable amount.
    discount_amount: float
    #: Class reference used in the Discount object
    discount_class_ref: Ref
    #: Represents the amount assigned to a particular receivable. The sum of all
    #: `payment_amount` elements in any given receive payment transaction must not be greater
    #: than TotalAmount.
    payment_amount: float
    set_credit: List[SetCredit]


class _LineGroupAddRequired(TypedDict):
    #: ItemGroup objects represent items that are grouped together for fast entry, and an
    #: `item_group_ref` aggregate refers to one of these item groups. In a request, if an
    #: `item_group_ref` aggregate includes both `full_name` and `list_id`, `full_name` will be
    #: ignored. You can use an ItemGroupQuery request to get information about all the item
    #: groups that are set up in the QuickBooks file.
    item_group_ref: Ref


class LineGroupAdd(_LineGroupAddRequired, total=False):
    data_ext: List[BillDataExt]
    #: A descriptive text field.
    desc: str
    #: Location within the Inventory Site.
    inventory_site_location_ref: Ref
    #: Site where inventory is located.
    inventory_site_ref: Ref
    #: On transaction lines, QuickBooks can derive one value from the other two among Quantity,
    #: Rate, and Amount. If you supply Quantity and Amount, QuickBooks calculates Rate. If you
    #: supply Quantity and Rate, QuickBooks calculates Amount.
    quantity: float
    #: Indicates the date on which the QuickBooks user performs the service for the customer.
    service_date: str
    #: In a transaction line item, the name of the unit of measure selected from within the
    #: item’s available units. If the company file is enabled only for single unit of measure
    #: per item, this must be the base unit!
    unit_of_measure: str


class DiscountLineAdd(TypedDict, total=False):
    account_ref: Ref
    #: A monetary amount.
    #:
    #: Choose at most one of: `amount`, or `rate_percent`.
    amount: float
    is_taxable: bool
    #: Indicates the price of something as a percent.
    #:
    #: Choose at most one of: `amount`, or `rate_percent`.
    rate_percent: float


class SalesTaxLineAdd(TypedDict, total=False):
    account_ref: Ref
    #: A monetary amount.
    #:
    #: Choose at most one of: `amount`, or `rate_percent`.
    amount: float
    #: Indicates the price of something as a percent.
    #:
    #: Choose at most one of: `amount`, or `rate_percent`.
    rate_percent: float


class _ShippingLineAddRequired(TypedDict):
    #: A monetary amount.
    amount: float


class ShippingLineAdd(_ShippingLineAddRequired, total=False):
    account_ref: Ref


class _AdditionalContactRefRequired(TypedDict):
    #: The name of the contact.
    contact_name: str
    #: The value of the contact field.
    contact_value: str


class AdditionalContactRef(_AdditionalContactRefRequired, total=False):
    pass


class _AdditionalNotesRequired(TypedDict):
    #: In a `bill_address` or `ship_address` aggregate, the Note field value is written at the
    #: bottom of the address in the form in which it appears, such as the invoice form.
    note: str


class AdditionalNotes(_AdditionalNotesRequired, total=False):
    pass


class _ContactsRequired(TypedDict):
    #: The first name of a customer, vendor, employee, or person on the “other names” list.
    first_name: str


class Contacts(_ContactsRequired, total=False):
    additional_contact_ref: List[AdditionalContactRef]
    #: The job title of a customer, vendor, employee, or person on the “other names” list.
    job_title: str
    #: The last name of a customer, vendor, employee, or person on the “other names” list.
    last_name: str
    #: The middle name of a customer, vendor, employee, or person on the “other names” list.
    middle_name: str
    #: A formal reference, such as Mr. or Dr., that precedes a name.
    salutation: str


class _AdditionalNotesModRequired(TypedDict):
    #: In a `bill_address` or `ship_address` aggregate, the Note field value is written at the
    #: bottom of the address in the form in which it appears, such as the invoice form.
    note: str
    #: The ID of the note.
    note_id: int


class AdditionalNotesMod(_AdditionalNotesModRequired, total=False):
    pass


class _ContactsModRequired(TypedDict):
    #: The first name of a customer, vendor, employee, or person on the “other names” list.
    first_name: str


class ContactsMod(_ContactsModRequired, total=False):
    additional_contact_ref: List[AdditionalContactRef]
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: The job title of a customer, vendor, employee, or person on the “other names” list.
    job_title: str
    #: The last name of a customer, vendor, employee, or person on the “other names” list.
    last_name: str
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list type, not globally
    #: across all lists. If both `full_name` and `list_id` are supplied in a request, QuickBooks
    #: uses `list_id` and ignores `full_name`.
    list_id: str
    #: The middle name of a customer, vendor, employee, or person on the “other names” list.
    middle_name: str
    #: A formal reference, such as Mr. or Dr., that precedes a name.
    salutation: str


class _EarningsRequired(TypedDict):
    #: Each payroll wage item describes and names a payment scheme, for example, Regular Pay or
    #: Overtime Pay. A `payroll_item_wage_ref` aggregate refers to one of these wage items. In a
    #: request, if a `payroll_item_wage_ref` aggregate includes both `full_name` and `list_id`,
    #: `full_name` will be ignored.
    payroll_item_wage_ref: Ref


class Earnings(_EarningsRequired, total=False):
    #: Indicates the price of something.
    #:
    #: Choose at most one of: `rate`, or `rate_percent`.
    rate: float
    #: Indicates the price of something as a percent.
    #:
    #: Choose at most one of: `rate`, or `rate_percent`.
    rate_percent: float


class _LineModRequired(TypedDict):
    #: Identification number of the transaction line. (`txn_line_id` is supported as of v2.0 of
    #: the SDK. With qbXML v1.0 and v1.1, `txn_line_id` is always returned as zero.) If you need
    #: to add a new transaction line in a transaction Mod request, you can do so by setting the
    #: `txn_line_id` to -1.
    txn_line_id: str


class LineMod(_LineModRequired, total=False):
    #: A monetary amount.
    amount: float
    #: Use classes to categorize transactions (for example, by department, location, or work
    #: type). Class tracking is off by default in QuickBooks. A `class_ref` points to one class;
    #: if both `full_name` and `list_id` are provided, `full_name` is ignored. In InvoiceAdd, a
    #: header-level `class_ref` is applied to line items unless you override or clear it on
    #: individual lines.
    class_ref: Ref
    #: A descriptive text field.
    desc: str
    #: Location within the Inventory Site.
    inventory_site_location_ref: Ref
    #: Site where inventory is located.
    inventory_site_ref: Ref
    #: `item_ref` may accept all item types or a restricted subset, depending on the request.
    #: Examples: PurchaseOrder and Bill do not allow discount or sales-tax items;
    #: VehicleMileageAdd requires a service or other-charge item; BillingRateAdd requires a
    #: service item. If both `full_name` and `list_id` are provided, `full_name` is ignored.
    item_ref: Ref
    #: The lot number of the asset.
    #:
    #: Choose at most one of: `serial_number`, or `lot_number`.
    lot_number: str
    #: Flag to override price rule conflict.
    option_for_price_rule_conflict: Literal["BasePrice", "Zero"]
    #: Other, Other1, and Other2 are built-in transaction custom fields. Other is
    #: transaction-level; Other1 and Other2 are line-level. These fields are always available
    #: through the SDK and do not require DataExtDef setup. Template labels in the UI can be
    #: renamed, but SDK names remain fixed as Other, Other1, and Other2.
    other1: str
    #: Other, Other1, and Other2 are built-in transaction custom fields. Other is
    #: transaction-level; Other1 and Other2 are line-level. These fields are always available
    #: through the SDK and do not require DataExtDef setup. Template labels in the UI can be
    #: renamed, but SDK names remain fixed as Other, Other1, and Other2.
    other2: str
    #: Refers to a QuickBooks account. If an `override_item_account_ref` aggregate includes both
    #: `full_name` and `list_id`, `full_name` will be ignored.
    override_item_account_ref: Ref
    #: When you modify a transaction line to change the unit of measure used in that line, you
    #: use this aggregate to specify the UOM set within which you are choosing an available unit
    #: of measure. The “override” here refers to the unit within the set, not the UOM Set
    #: itself, which you can’t change or override–the UOM set that can be set or changed only in
    #: the item itself via an Item Mod request.
    override_uom_set_ref: Ref
    #: Price levels let you apply custom pricing rules for selected customers. Once assigned,
    #: QuickBooks uses those prices automatically on supported sales forms unless explicitly
    #: overridden.
    #:
    #: Choose at most one of: `rate`, or `rate_percent`, or `price_level_ref`.
    price_level_ref: Ref
    #: On transaction lines, QuickBooks can derive one value from the other two among Quantity,
    #: Rate, and Amount. If you supply Quantity and Amount, QuickBooks calculates Rate. If you
    #: supply Quantity and Rate, QuickBooks calculates Amount.
    quantity: float
    #: If you specify both Rate and Amount in a request, the Rate you provide will be ignored,
    #: and you will receive a warning. If you specify both Quantity and Amount in an Add or Mod
    #: request, QuickBooks will use them to calculate Rate. (Rate, Amount, and Quantity can’t be
    #: cleared.)
    #:
    #: Choose at most one of: `rate`, or `rate_percent`, or `price_level_ref`.
    rate: float
    #: Indicates the price of something as a percent.
    #:
    #: Choose at most one of: `rate`, or `rate_percent`, or `price_level_ref`.
    rate_percent: float
    #: `sales_tax_code_ref` points to the sales-tax code used for an item or customer context.
    #: QuickBooks includes default TAX and NON codes, and a code can be deleted only when
    #: nothing references it. If sales tax is disabled, QuickBooks assigns the default
    #: non-taxable code. If both `full_name` and `list_id` are provided in `sales_tax_code_ref`,
    #: `full_name` is ignored.
    sales_tax_code_ref: Ref
    #: The serial number of the asset.
    #:
    #: Choose at most one of: `serial_number`, or `lot_number`.
    serial_number: str
    #: Indicates the date on which the QuickBooks user performs the service for the customer.
    service_date: str
    tax_amount: float
    #: In a transaction line item, the name of the unit of measure selected from within the
    #: item’s available units. If the company file is enabled only for single unit of measure
    #: per item, this must be the base unit!
    unit_of_measure: str


class ItemDiscountBarCode(TypedDict, total=False):
    #: Allows for barcode to be overridden for an item.
    allow_override: bool
    #: Allow barcode to be assigned to item, even if already in use.
    assign_even_if_used: bool
    #: Value of the barcode in the item.
    bar_code_value: str


class SalesAndPurchase(TypedDict, total=False):
    #: Refers to an expense account. If an `expense_account_ref` aggregate includes both
    #: `full_name` and `list_id`, `full_name` will be ignored.
    expense_account_ref: Ref
    #: Refers to an income account. If an `income_account_ref` aggregate includes both
    #: `full_name` and `list_id`, `full_name` will be ignored.
    income_account_ref: Ref
    #: The preferred vendor for this item. If a `pref_vendor_ref` aggregate includes both
    #: `full_name` and `list_id`, `full_name` will be ignored.
    pref_vendor_ref: Ref
    #: Amount that the QuickBooks user expects to pay when ordering or buying this item, or the
    #: amount that was actually paid for this item.
    purchase_cost: float
    #: Description that appears in the Description column of checks, bills, credit card charges,
    #: and item receipts (when an item is reordered). For a fixed asset, a description of the
    #: item as it was when it was purchased.
    purchase_desc: str
    #: Account used for taxes on purchases in CA or UK.
    purchase_tax_code_ref: Ref
    #: Appears in the Description column of a sales form when the QuickBooks user sells this
    #: item. For a fixed asset, describes the sale of the asset (for accounting purposes).
    sales_desc: str
    #: Price charged for this item.
    sales_price: float


class SalesOrPurchase(TypedDict, total=False):
    #: `account_ref` points to an account in the company file. If both `full_name` and `list_id`
    #: are provided, `full_name` is ignored. Meaning depends on context: for checks it is the
    #: funding account; for ExpenseLineAdd it may be required by accounting preferences; for
    #: credit-card transactions it identifies the bank or card account involved.
    account_ref: Ref
    #: A descriptive text field.
    desc: str
    #: The purchase price or sales price of this item.
    #:
    #: Choose at most one of: `price`, or `price_percent`.
    price: float
    #: The price expressed as a percent. (For example, an auto shop that calculates the cost of
    #: labor as a percentage of the cost of parts might have a service item called “Labor” that
    #: uses `price_percent` instead of Price.)
    #:
    #: Choose at most one of: `price`, or `price_percent`.
    price_percent: float


class SalesAndPurchaseMod(TypedDict, total=False):
    #: Used to support changing the `account_ref` in the Mod request. When you do this, the
    #: QuickBooks UI normally displays a prompt asking whether the change should apply to
    #: existing transactions or not. Specifying False basically dismisses this with a “No”
    #: answer; specifying True dismisses it with a “Yes” answer and then changes the existing
    #: transactions that use the item with that `account_ref`.
    apply_expense_account_ref_to_existing_txns: bool
    #: Used to support changing the `account_ref` in the Mod request. When you do this, the
    #: QuickBooks UI normally displays a prompt asking whether the change should apply to
    #: existing transactions or not. Specifying False basically dismisses this with a “No”
    #: answer; specifying True dismisses it with a “Yes” answer and then changes the existing
    #: transactions that use the item with that `account_ref`.
    apply_income_account_ref_to_existing_txns: bool
    #: Refers to an expense account. If an `expense_account_ref` aggregate includes both
    #: `full_name` and `list_id`, `full_name` will be ignored.
    expense_account_ref: Ref
    #: Refers to an income account. If an `income_account_ref` aggregate includes both
    #: `full_name` and `list_id`, `full_name` will be ignored.
    income_account_ref: Ref
    #: The preferred vendor for this item. If a `pref_vendor_ref` aggregate includes both
    #: `full_name` and `list_id`, `full_name` will be ignored.
    pref_vendor_ref: Ref
    #: Amount that the QuickBooks user expects to pay when ordering or buying this item, or the
    #: amount that was actually paid for this item.
    purchase_cost: float
    #: Description that appears in the Description column of checks, bills, credit card charges,
    #: and item receipts (when an item is reordered). For a fixed asset, a description of the
    #: item as it was when it was purchased.
    purchase_desc: str
    #: Account used for taxes on purchases in CA or UK.
    purchase_tax_code_ref: Ref
    #: Appears in the Description column of a sales form when the QuickBooks user sells this
    #: item. For a fixed asset, describes the sale of the asset (for accounting purposes).
    sales_desc: str
    #: Price charged for this item.
    sales_price: float


class SalesOrPurchaseMod(TypedDict, total=False):
    #: `account_ref` points to an account in the company file. If both `full_name` and `list_id`
    #: are provided, `full_name` is ignored. Meaning depends on context: for checks it is the
    #: funding account; for ExpenseLineAdd it may be required by accounting preferences; for
    #: credit-card transactions it identifies the bank or card account involved.
    account_ref: Ref
    #: Used to support changing the `account_ref` in the Mod request. When you do this, the
    #: QuickBooks UI normally displays a prompt asking whether the change should apply to
    #: existing transactions or not. Specifying False basically dismisses this with a “No”
    #: answer; specifying True dismisses it with a “Yes” answer and then changes the existing
    #: transactions that use the item with that `account_ref`.
    apply_account_ref_to_existing_txns: bool
    #: A descriptive text field.
    desc: str
    #: The purchase price or sales price of this item.
    #:
    #: Choose at most one of: `price`, or `price_percent`.
    price: float
    #: The price expressed as a percent. (For example, an auto shop that calculates the cost of
    #: labor as a percentage of the cost of parts might have a service item called “Labor” that
    #: uses `price_percent` instead of Price.)
    #:
    #: Choose at most one of: `price`, or `price_percent`.
    price_percent: float


class DeletedDateRangeFilter(TypedDict, total=False):
    #: Selects objects deleted on or after this date. Both `from_deleted_date` and
    #: `to_deleted_date` must be between 1970-01-01 and 2038-01-19T03:14:07
    #: (2038-01-18T19:14:07-08:00 PST). (But note that ListDeletedQuery requests will only
    #: return records deleted within the last 90 days, even if the specified `from_deleted_date`
    #: is earlier.)
    from_deleted_date: str
    #: Selects objects deleted on or before this date. Both `to_deleted_date` and
    #: `from_deleted_date` must be between 1970-01-01 and 2038-01-19T03:14:07
    #: (2038-01-18T19:14:07-08:00 PST). If `to_deleted_date` includes a date but not a time (for
    #: example, if you set it to 2002-02-14), the time is assumed to be the end of the day
    #: (2003-02-14T23:59:59).
    to_deleted_date: str


class PayrollDateRangeFilter(TypedDict, total=False):
    date_macro: Literal["All", "LastCalendarQuarter", "LastCalendarQuarterToDate", "LastCalendarYear", "LastCalendarYearToDate", "LastFiscalQuarter", "LastFiscalQuarterToDate", "LastFiscalYear", "LastFiscalYearToDate", "LastMonth", "LastMonthToDate", "LastWeek", "LastWeekToDate", "NextCalendarQuarter", "NextCalendarYear", "NextFiscalQuarter", "NextFiscalYear", "NextFourWeeks", "NextMonth", "NextWeek", "ThisCalendarQuarter", "ThisCalendarQuarterToDate", "ThisCalendarYear", "ThisCalendarYearToDate", "ThisFiscalQuarter", "ThisFiscalQuarterToDate", "ThisFiscalYear", "ThisFiscalYearToDate", "ThisMonth", "ThisMonthToDate", "ThisWeek", "ThisWeekToDate", "Today", "Yesterday"]
    from_payroll_date: str
    to_payroll_date: str


class _TaxabilityRequired(TypedDict):
    is_tax_applied: bool
    payroll_item_tax_ref: Ref


class Taxability(_TaxabilityRequired, total=False):
    pass


class _LiabilityPaymentScheduleRequired(TypedDict):
    payment_schedule_type: Literal["Empty", "FederalMonthly", "FederalNextDay", "FederalQuarterly", "FederalSemiweekly", "Monthly", "Quarterly", "Semiweekly", "Weekly", "Yearly"]


class LiabilityPaymentSchedule(_LiabilityPaymentScheduleRequired, total=False):
    payment_due_date: str
    payment_due_num_days_after: int
