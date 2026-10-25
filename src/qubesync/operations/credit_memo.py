# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks credit memo operations (``client.credit_memo``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    Address,
    BillDataExt,
    CreditCardTxnInfo,
    CreditCardTxnInputInfo,
    CreditCardTxnResultInfo,
    CurrencyFilter,
    DateRangeFilter,
    DiscountLineAdd,
    EntityFilter,
    LineGroupAdd,
    ModifiedDateRangeFilter,
    Ref,
    RefNumberFilter,
    RefNumberRangeFilter,
    SalesTaxLineAdd,
    ShippingLineAdd,
)

if TYPE_CHECKING:
    from ..v2 import Client


class CreditMemoLineAdd(TypedDict, total=False):
    #: A monetary amount.
    amount: float
    #: Use classes to categorize transactions (for example, by department, location, or work
    #: type). Class tracking is off by default in QuickBooks. A `class_ref` points to one class;
    #: if both `full_name` and `list_id` are provided, `full_name` is ignored. In InvoiceAdd, a
    #: header-level `class_ref` is applied to line items unless you override or clear it on
    #: individual lines.
    class_ref: Ref
    #: Contains data from the credit card transaction used in the payment. This data originates
    #: from a previous qbmsXML credit card transaction. The data following the element
    #: `credit_card_txn_input_info`” data is the data from the original qbmsXML request. The
    #: “`credit_card_txn_result_info`” is the data from the original qbmsXML response.
    credit_card_txn_info: CreditCardTxnInfo
    data_ext: List[BillDataExt]
    #: `def_macro` lets you assign a reusable name to a returned `txn_id` or `txn_line_id` so
    #: later requests can reference it with `useMacro`. This feature requires SDK 2.0+.
    def_macro: str
    #: A descriptive text field.
    desc: str
    #: Location within the Inventory Site.
    inventory_site_location_ref: Ref
    #: Site where inventory is located.
    inventory_site_ref: Ref
    is_taxable: bool
    #: `item_ref` may accept all item types or a restricted subset, depending on the request.
    #: Examples: PurchaseOrder and Bill do not allow discount or sales-tax items;
    #: VehicleMileageAdd requires a service or other-charge item; BillingRateAdd requires a
    #: service item. If both `full_name` and `list_id` are provided, `full_name` is ignored.
    item_ref: Ref
    #: The lot number of the asset.
    #:
    #: Choose at most one of: `serial_number`, or `lot_number`.
    lot_number: str
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
    #: and you will receive a warning. If you specify both Quantity and Amount in an Add
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


class _CreditMemoLineModRequired(TypedDict):
    #: Identification number of the transaction line. (`txn_line_id` is supported as of v2.0 of
    #: the SDK. With qbXML v1.0 and v1.1, `txn_line_id` is always returned as zero.) If you need
    #: to add a new transaction line in a transaction Mod request, you can do so by setting the
    #: `txn_line_id` to -1.
    txn_line_id: str


class CreditMemoLineMod(_CreditMemoLineModRequired, total=False):
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
    #: and you will receive a warning. If you specify both Quantity and Amount in an Add
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


class _CreditMemoLineGroupModRequired(TypedDict):
    #: Identification number of the transaction line. (`txn_line_id` is supported as of v2.0 of
    #: the SDK. With qbXML v1.0 and v1.1, `txn_line_id` is always returned as zero.) If you need
    #: to add a new transaction line in a transaction Mod request, you can do so by setting the
    #: `txn_line_id` to -1.
    txn_line_id: str


class CreditMemoLineGroupMod(_CreditMemoLineGroupModRequired, total=False):
    #: Represents one line in the credit memo. Compare with CreditMemoGroupLine, which
    #: represents a previously defined group of lines in the credit memo.
    credit_memo_line_mod: List[CreditMemoLineMod]
    #: ItemGroup objects represent items that are grouped together for fast entry, and an
    #: `item_group_ref` aggregate refers to one of these item groups. In a request, if an
    #: `item_group_ref` aggregate includes both `full_name` and `list_id`, `full_name` will be
    #: ignored. You can use an ItemGroupQuery request to get information about all the item
    #: groups that are set up in the QuickBooks file.
    item_group_ref: Ref
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


class _CreditMemoCreateParamsRequired(TypedDict):
    #: `customer_ref` identifies a customer or customer job. If both `full_name` and `list_id`
    #: are provided, `full_name` is ignored. In SalesReceipt and ReceivePayment, it identifies
    #: who receives credit. In TimeTracking, it identifies who the time can be billed to and is
    #: required in TimeTrackingAdd when IsBillable is true.
    customer_ref: Ref


class CreditMemoCreateParams(_CreditMemoCreateParamsRequired, total=False):
    """Params for ``credit_memo.create`` (Create credit memo)."""
    #: `ar_account_ref` points to an Accounts Receivable account. If both `full_name` and
    #: `list_id` are provided, `full_name` is ignored.
    ar_account_ref: Ref
    #: This aggregate supports at most five address lines. You can provide a structured address
    #: (Addr1-Addr3 plus City/State/`postal_code`/etc.) or use block mode (Addr1-Addr5 only). Do
    #: not mix block mode with other address fields. In block mode, each Addr line prints as its
    #: own line and is returned in `ship_address_block` or `bill_address_block`.
    bill_address: Address
    #: Use classes to categorize transactions (for example, by department, location, or work
    #: type). Class tracking is off by default in QuickBooks. A `class_ref` points to one class;
    #: if both `full_name` and `list_id` are provided, `full_name` is ignored. In InvoiceAdd, a
    #: header-level `class_ref` is applied to line items unless you override or clear it on
    #: individual lines.
    class_ref: Ref
    #: Represents one line in the credit memo. Compare with CreditMemoGroupLine, which
    #: represents a previously defined group of lines in the credit memo.
    #:
    #: At least one entry is required across `credit_memo_line_add` and
    #: `credit_memo_line_group_add`; they combine, any number of each. QuickBooks receives them
    #: in that order: every `credit_memo_line_add`, then every `credit_memo_line_group_add`.
    credit_memo_line_add: List[CreditMemoLineAdd]
    #: Represents a previously defined group of lines in the credit memo. Compare with
    #: CreditMemoLine, which represents just one line in the credit memo.
    #:
    #: At least one entry is required across `credit_memo_line_add` and
    #: `credit_memo_line_group_add`; they combine, any number of each. QuickBooks receives them
    #: in that order: every `credit_memo_line_add`, then every `credit_memo_line_group_add`.
    credit_memo_line_group_add: List[LineGroupAdd]
    #: A standard message such as “Thank you for your business,” or “Please sign and return this
    #: estimate to indicate your approval.” A customer message can be included at the bottom of
    #: a form. A `customer_msg_ref` aggregate refers to one of the messages on the CustomerMsg
    #: list. In a request, if a `customer_msg_ref` aggregate includes both `full_name` and
    #: `list_id`, `full_name` will be ignored.
    customer_msg_ref: Ref
    #: Refers to the sales-tax code for sales related to this customer. (That is, it refers to a
    #: member of the SalesTaxCode list.) The sales-tax code indicates whether an item is taxable
    #: or non-taxable, and why. In a request, if a `customer_sales_tax_code_ref` aggregate
    #: includes both `full_name` and `list_id`, `full_name` will be ignored.
    customer_sales_tax_code_ref: Ref
    #: `def_macro` lets you assign a reusable name to a returned `txn_id` or `txn_line_id` so
    #: later requests can reference it with `useMacro`. This feature requires SDK 2.0+.
    def_macro: str
    discount_line_add: DiscountLineAdd
    #: The date on which payment is due.
    due_date: str
    #: `exchange_rate` is the rate from this currency to the company’s home currency at
    #: AsOfDate. You can supply a rate when adding transactions, but QuickBooks does not provide
    #: rates through the SDK. If your home currency is USD and internet access is available,
    #: rates can be downloaded in the QuickBooks UI via Lists > Currency > Activities > Download
    #: Latest Exchange Rates.
    exchange_rate: float
    #: Allows for the attachment of a user defined GUID value.
    external_guid: str
    #: QuickBooks uses the term FOB, “freight on board,” to indicate the place from which the
    #: product is shipped. The FOB has no accounting implications.
    fob: str
    include_ret_element: List[Literal["ARAccountRef", "BillAddress", "BillAddressBlock", "ClassRef", "CreditMemoLineGroupRet", "CreditMemoLineRet", "CreditRemaining", "CreditRemainingInHomeCurrency", "CurrencyRef", "CustomerMsgRef", "CustomerRef", "CustomerSalesTaxCodeRef", "DataExtRet", "DiscountLineRet", "DueDate", "EditSequence", "ExchangeRate", "ExternalGUID", "FOB", "IsPending", "IsTaxIncluded", "IsToBeEmailed", "IsToBePrinted", "ItemSalesTaxRef", "LinkedTxn", "ListID", "Memo", "Other", "OwnerID", "PONumber", "RefNumber", "SalesRepRef", "SalesTaxLineRet", "SalesTaxPercentage", "SalesTaxTotal", "ShipAddress", "ShipAddressBlock", "ShipDate", "ShipMethodRef", "ShippingLineRet", "Subtotal", "TemplateRef", "TermsRef", "TimeCreated", "TimeModified", "TotalAmount", "TxnDate", "TxnID", "TxnNumber"]]
    #: If `is_pending` is set to true, the credit memo hasn’t been completed. Within QuickBooks,
    #: you can change the `is_pending` status for a credit memo by choosing “Mark Credit Memo As
    #: Pending” or “Mark Credit Memo As Final” from the Edit menu.
    is_pending: bool
    #: For future use with international versions of QuickBooks.
    is_tax_included: bool
    #: When enabled, QuickBooks validates the customer email at runtime before sending. If no
    #: valid email is available, the request fails.
    is_to_be_emailed: bool
    #: If `is_to_be_printed` is true, QuickBooks queues the form for later printing. It does not
    #: print immediately; printing is still a user action in QuickBooks.
    is_to_be_printed: bool
    #: An ItemSalesTax entry represents one tax rate paid to one tax agency. Use it when a
    #: transaction needs a single tax calculation. For multi-rate scenarios, use a sales-tax
    #: group instead. If both `full_name` and `list_id` are provided for `item_sales_tax_ref`,
    #: `list_id` is used.
    item_sales_tax_ref: Ref
    #: The memo doesn’t print on the credit memo, but does appear in the account register and
    #: the customer register.
    memo: str
    #: Other, Other1, and Other2 are built-in transaction custom fields. Other is
    #: transaction-level; Other1 and Other2 are line-level. These fields are always available
    #: through the SDK and do not require DataExtDef setup. Template labels in the UI can be
    #: renamed, but SDK names remain fixed as Other, Other1, and Other2.
    other: str
    #: Purchase order number.
    po_number: str
    #: `ref_number` is a user-managed transaction reference (for example, a check number). It
    #: can be edited and is not guaranteed to be globally unique. Some transaction types
    #: auto-populate `ref_number` when omitted, based on QuickBooks preferences and numbering
    #: state.
    ref_number: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: A sales representative must be on the Employee, Vendor, or Other Names list within
    #: QuickBooks. Sales representative’s names and initials appear on the Rep drop-down list on
    #: QuickBooks sales forms. A `sales_rep_ref` refers to a person on the SalesRep list. In a
    #: request, if a `sales_rep_ref` aggregate includes both `full_name` and `list_id`,
    #: `full_name` will be ignored.
    sales_rep_ref: Ref
    sales_tax_line_add: SalesTaxLineAdd
    #: This aggregate supports at most five address lines. You can provide a structured address
    #: (Addr1-Addr3 plus City/State/`postal_code`/etc.) or use block mode (Addr1-Addr5 only). Do
    #: not mix block mode with other address fields. In block mode, each Addr line prints as its
    #: own line and is returned in `ship_address_block` or `bill_address_block`.
    ship_address: Address
    #: The date when the product was, or will be, shipped.
    ship_date: str
    #: A shipping method, for example, standard mail or overnight delivery. A `ship_method_ref`
    #: aggregate refers to an item on the ShipMethod list. In a request, if a `ship_method_ref`
    #: aggregate includes both `full_name` and `list_id`, `full_name` will be ignored.
    ship_method_ref: Ref
    shipping_line_add: ShippingLineAdd
    #: QuickBooks templates specify how to print certain transactions. A template query returns
    #: the names of all templates that have been defined in QuickBooks. A `template_ref` element
    #: refers to one of these templates.
    template_ref: Ref
    #: Refers to the payment terms associated with this entity. (This will be an item on the
    #: DateDrivenTerms or StandardTerms list.) If a `terms_ref` aggregate includes both
    #: `full_name` and `list_id`, `full_name` will be ignored.
    terms_ref: Ref
    #: The date of the transaction. In some cases, if you leave `txn_date` out of an -Add
    #: message, QuickBooks will prefill `txn_date` with the date of the last-saved transaction
    #: of the same type.
    txn_date: str


class CreditMemoQueryParams(TypedDict, total=False):
    """Params for ``credit_memo.query`` (List credit memos)."""
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
    include_ret_element: List[Literal["ARAccountRef", "BillAddress", "BillAddressBlock", "ClassRef", "CreditMemoLineGroupRet", "CreditMemoLineRet", "CreditRemaining", "CreditRemainingInHomeCurrency", "CurrencyRef", "CustomerMsgRef", "CustomerRef", "CustomerSalesTaxCodeRef", "DataExtRet", "DiscountLineRet", "DueDate", "EditSequence", "ExchangeRate", "ExternalGUID", "FOB", "IsPending", "IsTaxIncluded", "IsToBeEmailed", "IsToBePrinted", "ItemSalesTaxRef", "LinkedTxn", "Memo", "Other", "PONumber", "RefNumber", "SalesRepRef", "SalesTaxLineRet", "SalesTaxPercentage", "SalesTaxTotal", "ShipAddress", "ShipAddressBlock", "ShipDate", "ShipMethodRef", "ShippingLineRet", "Subtotal", "TemplateRef", "TermsRef", "TimeCreated", "TimeModified", "TotalAmount", "TxnDate", "TxnID", "TxnNumber"]]
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


class _CreditMemoUpdateParamsRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    txn_id: str


class CreditMemoUpdateParams(_CreditMemoUpdateParamsRequired, total=False):
    """Params for ``credit_memo.update`` (Update credit memo)."""
    #: `ar_account_ref` points to an Accounts Receivable account. If both `full_name` and
    #: `list_id` are provided, `full_name` is ignored.
    ar_account_ref: Ref
    #: This aggregate supports at most five address lines. You can provide a structured address
    #: (Addr1-Addr3 plus City/State/`postal_code`/etc.) or use block mode (Addr1-Addr5 only). Do
    #: not mix block mode with other address fields. In block mode, each Addr line prints as its
    #: own line and is returned in `ship_address_block` or `bill_address_block`.
    bill_address: Address
    #: Use classes to categorize transactions (for example, by department, location, or work
    #: type). Class tracking is off by default in QuickBooks. A `class_ref` points to one class;
    #: if both `full_name` and `list_id` are provided, `full_name` is ignored. In InvoiceAdd, a
    #: header-level `class_ref` is applied to line items unless you override or clear it on
    #: individual lines.
    class_ref: Ref
    #: Represents a previously defined group of lines in the credit memo. Compare with
    #: CreditMemoLine, which represents just one line in the credit memo.
    #:
    #: `credit_memo_line_mod` and `credit_memo_line_group_mod` combine: any number of each.
    #: QuickBooks receives them in that order: every `credit_memo_line_mod`, then every
    #: `credit_memo_line_group_mod`.
    credit_memo_line_group_mod: List[CreditMemoLineGroupMod]
    #: Represents one line in the credit memo. Compare with CreditMemoGroupLine, which
    #: represents a previously defined group of lines in the credit memo.
    #:
    #: `credit_memo_line_mod` and `credit_memo_line_group_mod` combine: any number of each.
    #: QuickBooks receives them in that order: every `credit_memo_line_mod`, then every
    #: `credit_memo_line_group_mod`.
    credit_memo_line_mod: List[CreditMemoLineMod]
    #: A standard message such as “Thank you for your business,” or “Please sign and return this
    #: estimate to indicate your approval.” A customer message can be included at the bottom of
    #: a form. A `customer_msg_ref` aggregate refers to one of the messages on the CustomerMsg
    #: list. In a request, if a `customer_msg_ref` aggregate includes both `full_name` and
    #: `list_id`, `full_name` will be ignored.
    customer_msg_ref: Ref
    #: `customer_ref` identifies a customer or customer job. If both `full_name` and `list_id`
    #: are provided, `full_name` is ignored. In SalesReceipt and ReceivePayment, it identifies
    #: who receives credit. In TimeTracking, it identifies who the time can be billed to and is
    #: required in TimeTrackingAdd when IsBillable is true.
    customer_ref: Ref
    #: Refers to the sales-tax code for sales related to this customer. (That is, it refers to a
    #: member of the SalesTaxCode list.) The sales-tax code indicates whether an item is taxable
    #: or non-taxable, and why. In a request, if a `customer_sales_tax_code_ref` aggregate
    #: includes both `full_name` and `list_id`, `full_name` will be ignored.
    customer_sales_tax_code_ref: Ref
    #: The date on which payment is due.
    due_date: str
    #: `exchange_rate` is the rate from this currency to the company’s home currency at
    #: AsOfDate. You can supply a rate when adding transactions, but QuickBooks does not provide
    #: rates through the SDK. If your home currency is USD and internet access is available,
    #: rates can be downloaded in the QuickBooks UI via Lists > Currency > Activities > Download
    #: Latest Exchange Rates.
    exchange_rate: float
    #: QuickBooks uses the term FOB, “freight on board,” to indicate the place from which the
    #: product is shipped. The FOB has no accounting implications.
    fob: str
    include_ret_element: List[Literal["ARAccountRef", "BillAddress", "BillAddressBlock", "ClassRef", "CreditMemoLineGroupRet", "CreditMemoLineRet", "CreditRemaining", "CreditRemainingInHomeCurrency", "CurrencyRef", "CustomerMsgRef", "CustomerRef", "CustomerSalesTaxCodeRef", "DataExtRet", "DiscountLineRet", "DueDate", "EditSequence", "ExchangeRate", "ExternalGUID", "FOB", "IsPending", "IsTaxIncluded", "IsToBeEmailed", "IsToBePrinted", "ItemSalesTaxRef", "LinkedTxn", "ListID", "Memo", "Other", "OwnerID", "PONumber", "RefNumber", "SalesRepRef", "SalesTaxLineRet", "SalesTaxPercentage", "SalesTaxTotal", "ShipAddress", "ShipAddressBlock", "ShipDate", "ShipMethodRef", "ShippingLineRet", "Subtotal", "TemplateRef", "TermsRef", "TimeCreated", "TimeModified", "TotalAmount", "TxnDate", "TxnID", "TxnNumber"]]
    #: If `is_pending` is set to true, the credit memo hasn’t been completed. Within QuickBooks,
    #: you can change the `is_pending` status for a credit memo by choosing “Mark Credit Memo As
    #: Pending” or “Mark Credit Memo As Final” from the Edit menu.
    is_pending: bool
    #: For future use with international versions of QuickBooks.
    is_tax_included: bool
    #: When enabled, QuickBooks validates the customer email at runtime before sending. If no
    #: valid email is available, the request fails.
    is_to_be_emailed: bool
    #: If `is_to_be_printed` is true, QuickBooks queues the form for later printing. It does not
    #: print immediately; printing is still a user action in QuickBooks.
    is_to_be_printed: bool
    #: An ItemSalesTax entry represents one tax rate paid to one tax agency. Use it when a
    #: transaction needs a single tax calculation. For multi-rate scenarios, use a sales-tax
    #: group instead. If both `full_name` and `list_id` are provided for `item_sales_tax_ref`,
    #: `list_id` is used.
    item_sales_tax_ref: Ref
    #: The memo doesn’t print on the credit memo, but does appear in the account register and
    #: the customer register.
    memo: str
    #: Other, Other1, and Other2 are built-in transaction custom fields. Other is
    #: transaction-level; Other1 and Other2 are line-level. These fields are always available
    #: through the SDK and do not require DataExtDef setup. Template labels in the UI can be
    #: renamed, but SDK names remain fixed as Other, Other1, and Other2.
    other: str
    #: Purchase order number.
    po_number: str
    #: `ref_number` is a user-managed transaction reference (for example, a check number). It
    #: can be edited and is not guaranteed to be globally unique. Some transaction types
    #: auto-populate `ref_number` when omitted, based on QuickBooks preferences and numbering
    #: state.
    ref_number: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: A sales representative must be on the Employee, Vendor, or Other Names list within
    #: QuickBooks. Sales representative’s names and initials appear on the Rep drop-down list on
    #: QuickBooks sales forms. A `sales_rep_ref` refers to a person on the SalesRep list. In a
    #: request, if a `sales_rep_ref` aggregate includes both `full_name` and `list_id`,
    #: `full_name` will be ignored.
    sales_rep_ref: Ref
    #: This aggregate supports at most five address lines. You can provide a structured address
    #: (Addr1-Addr3 plus City/State/`postal_code`/etc.) or use block mode (Addr1-Addr5 only). Do
    #: not mix block mode with other address fields. In block mode, each Addr line prints as its
    #: own line and is returned in `ship_address_block` or `bill_address_block`.
    ship_address: Address
    #: The date when the product was, or will be, shipped.
    ship_date: str
    #: A shipping method, for example, standard mail or overnight delivery. A `ship_method_ref`
    #: aggregate refers to an item on the ShipMethod list. In a request, if a `ship_method_ref`
    #: aggregate includes both `full_name` and `list_id`, `full_name` will be ignored.
    ship_method_ref: Ref
    #: QuickBooks templates specify how to print certain transactions. A template query returns
    #: the names of all templates that have been defined in QuickBooks. A `template_ref` element
    #: refers to one of these templates.
    template_ref: Ref
    #: Refers to the payment terms associated with this entity. (This will be an item on the
    #: DateDrivenTerms or StandardTerms list.) If a `terms_ref` aggregate includes both
    #: `full_name` and `list_id`, `full_name` will be ignored.
    terms_ref: Ref
    #: The date of the transaction. In some cases, if you leave `txn_date` out of an -Add
    #: message, QuickBooks will prefill `txn_date` with the date of the last-saved transaction
    #: of the same type.
    txn_date: str


class CreditMemo:
    """QuickBooks credit memo operations: create, query, update.

    Get it from ``client.credit_memo``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[CreditMemoCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create credit memo.

        Queues ``credit_memo.create``: POST /connections/{connection_id}/credit-memos, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``CreditMemoCreateParams``)::

            ar_account_ref: Ref
                full_name: str
                list_id: str
            bill_address: Address
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
            class_ref: Ref
            credit_memo_line_add: List[CreditMemoLineAdd]
                amount: float
                class_ref: Ref
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
                data_ext: List[BillDataExt]
                    data_ext_name: str (required)
                    data_ext_value: str (required)
                    owner_id: str (required)
                def_macro: str
                desc: str
                inventory_site_location_ref: Ref
                inventory_site_ref: Ref
                is_taxable: bool
                item_ref: Ref
                lot_number: str
                other1: str
                other2: str
                override_item_account_ref: Ref
                price_level_ref: Ref
                quantity: float
                rate: float
                rate_percent: float
                sales_tax_code_ref: Ref
                serial_number: str
                service_date: str
                tax_amount: float
                unit_of_measure: str
            credit_memo_line_group_add: List[LineGroupAdd]
                data_ext: List[BillDataExt]
                desc: str
                inventory_site_location_ref: Ref
                inventory_site_ref: Ref
                item_group_ref: Ref (required)
                quantity: float
                service_date: str
                unit_of_measure: str
            customer_msg_ref: Ref
            customer_ref: Ref (required)
            customer_sales_tax_code_ref: Ref
            def_macro: str
            discount_line_add: DiscountLineAdd
                account_ref: Ref
                amount: float
                is_taxable: bool
                rate_percent: float
            due_date: str
            exchange_rate: float
            external_guid: str
            fob: str
            include_ret_element: List[Literal[...] (one of 49 values)]
            is_pending: bool
            is_tax_included: bool
            is_to_be_emailed: bool
            is_to_be_printed: bool
            item_sales_tax_ref: Ref
            memo: str
            other: str
            po_number: str
            ref_number: str
            request_id: str
            sales_rep_ref: Ref
            sales_tax_line_add: SalesTaxLineAdd
                account_ref: Ref
                amount: float
                rate_percent: float
            ship_address: Address
            ship_date: str
            ship_method_ref: Ref
            shipping_line_add: ShippingLineAdd
                account_ref: Ref
                amount: float (required)
            template_ref: Ref
            terms_ref: Ref
            txn_date: str

        Docs: https://docs.qubesync.com/api-reference/v2/credit-memos/create-credit-memo
        """
        return self._client._queue_operation("credit_memo.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[CreditMemoQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List credit memos.

        Queues ``credit_memo.query``: GET /connections/{connection_id}/credit-memos, params in the query string.
        QuickBooks answers in pages: each page comes to ``webhook_url`` as its own webhook.
        Returns the queued request.

        Params (``CreditMemoQueryParams``)::

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
            include_ret_element: List[Literal[...] (one of 47 values)]
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

        Docs: https://docs.qubesync.com/api-reference/v2/credit-memos/list-credit-memos
        """
        return self._client._queue_operation("credit_memo.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[CreditMemoUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update credit memo.

        Queues ``credit_memo.update``: PUT /connections/{connection_id}/credit-memos, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``CreditMemoUpdateParams``)::

            ar_account_ref: Ref
                full_name: str
                list_id: str
            bill_address: Address
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
            class_ref: Ref
            credit_memo_line_group_mod: List[CreditMemoLineGroupMod]
                credit_memo_line_mod: List[CreditMemoLineMod]
                    amount: float
                    class_ref: Ref
                    desc: str
                    inventory_site_location_ref: Ref
                    inventory_site_ref: Ref
                    item_ref: Ref
                    lot_number: str
                    other1: str
                    other2: str
                    override_item_account_ref: Ref
                    override_uom_set_ref: Ref
                    price_level_ref: Ref
                    quantity: float
                    rate: float
                    rate_percent: float
                    sales_tax_code_ref: Ref
                    serial_number: str
                    service_date: str
                    tax_amount: float
                    txn_line_id: str (required)
                    unit_of_measure: str
                item_group_ref: Ref
                override_uom_set_ref: Ref
                quantity: float
                txn_line_id: str (required)
                unit_of_measure: str
            credit_memo_line_mod: List[CreditMemoLineMod]
            customer_msg_ref: Ref
            customer_ref: Ref
            customer_sales_tax_code_ref: Ref
            due_date: str
            edit_sequence: str (required)
            exchange_rate: float
            fob: str
            include_ret_element: List[Literal[...] (one of 49 values)]
            is_pending: bool
            is_tax_included: bool
            is_to_be_emailed: bool
            is_to_be_printed: bool
            item_sales_tax_ref: Ref
            memo: str
            other: str
            po_number: str
            ref_number: str
            request_id: str
            sales_rep_ref: Ref
            ship_address: Address
            ship_date: str
            ship_method_ref: Ref
            template_ref: Ref
            terms_ref: Ref
            txn_date: str
            txn_id: str (required)

        Docs: https://docs.qubesync.com/api-reference/v2/credit-memos/update-credit-memo
        """
        return self._client._queue_operation("credit_memo.update", connection_id, params, webhook_url, idempotency_key)
