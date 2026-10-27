# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks vendor operations (``client.vendor``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    AdditionalContactRef,
    AdditionalNotes,
    AdditionalNotesMod,
    Address,
    Contacts,
    ContactsMod,
    CurrencyFilter,
    EntityFilter,
    NameFilter,
    NameRangeFilter,
    Ref,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _TotalBalanceFilterRequired(TypedDict):
    #: The monetary amount to which Operator refers.
    amount: float
    #: Indicates whether to filter for amounts that are less than, equal to or less than,
    #: exactly equal to, greater than, or equal to or greater than the given Amount.
    operator: Literal["Equal", "GreaterThan", "GreaterThanEqual", "LessThan", "LessThanEqual"]


class TotalBalanceFilter(_TotalBalanceFilterRequired, total=False):
    pass


class _VendorCreateParamsRequired(TypedDict):
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because `full_name` remains distinct.
    name: str


class VendorCreateParams(_VendorCreateParamsRequired, total=False):
    """Params for ``vendor.create`` (Create vendor)."""
    #: Account numbers appear in the QuickBooks chart of accounts, Account fields, and reports
    #: and graphs. If the IsUsingAccountNumber preference is false (that is, if the QuickBooks
    #: user has the account numbers Preference turned off), you can still set account numbers
    #: through the SDK, but the numbers won’t be visible in the user interface.
    account_number: str
    additional_contact_ref: List[AdditionalContactRef]
    additional_notes: List[AdditionalNotes]
    #: The name of an alternate contact person for a vendor, customer, or “other name” entry.
    alt_contact: str
    #: A telephone number given as an alternative to Phone.
    alt_phone: str
    #: Billing rates are used to override the service item rate in a time transaction
    #: (TimeTrackingAdd) based on the employee or vendor performing the work. Billing rates are
    #: assigned to an employee or a vendor to specify overrides to service items.
    billing_rate_ref: Ref
    #: Email address that would be carbon copied or CC.
    cc: str
    #: Use classes to categorize transactions (for example, by department, location, or work
    #: type). Class tracking is off by default in QuickBooks. A `class_ref` points to one class;
    #: if both `full_name` and `list_id` are provided, `full_name` is ignored. In InvoiceAdd, a
    #: header-level `class_ref` is applied to line items unless you override or clear it on
    #: individual lines.
    class_ref: Ref
    #: The name of the QuickBooks user’s business, as specified in QuickBooks. `company_name`
    #: and Address are used on invoices, checks, and other forms. (LegalCompanyName and
    #: LegalAddress, on the other hand, are used on a company’s tax forms and pay stubs.)
    company_name: str
    #: The name of a contact person for a customer or vendor.
    contact: str
    contacts: List[Contacts]
    #: Set and returned as a positive number that indicates a customer’s or vendor’s credit
    #: limit. If no value has been defined, there is no credit limit.
    credit_limit: float
    #: A currency record defines how QuickBooks stores and displays a currency. Built-in
    #: currency name/code values are fixed; formatting and active status can vary by settings
    #: and workflow.
    currency_ref: Ref
    #: E-mail address.
    email: str
    #: Allows for the attachment of a user defined GUID value.
    external_guid: str
    #: Fax number.
    fax: str
    #: The first name of a customer, vendor, employee, or person on the “other names” list.
    first_name: str
    include_ret_element: List[Literal["AccountNumber", "AdditionalContactRef", "AdditionalNotesRet", "AltContact", "AltPhone", "Balance", "BillingRateRef", "Cc", "ClassRef", "CompanyName", "Contact", "ContactsRet", "CreditLimit", "CurrencyRef", "DataExtRet", "EditSequence", "Email", "ExternalGUID", "Fax", "FirstName", "IsActive", "IsSalesTaxAgency", "IsTaxAgency", "IsTaxOnTax", "IsTaxTrackedOnPurchases", "IsTaxTrackedOnSales", "IsVendorEligibleFor1099", "JobTitle", "LastName", "ListID", "MiddleName", "Mobile", "Name", "NameOnCheck", "Notes", "OwnerID", "Pager", "Phone", "PrefillAccountRef", "ReportingPeriod", "SalesTaxCodeRef", "SalesTaxCountry", "SalesTaxReturnRef", "Salutation", "ShipAddress", "Suffix", "TaxOnPurchasesAccountRef", "TaxOnSalesAccountRef", "TaxRegistrationNumber", "TermsRef", "TimeCreated", "TimeModified", "TxnID", "TxnNumber", "VendorAddress", "VendorAddressBlock", "VendorTaxIdent", "VendorTypeRef"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: Indicates whether the entity is a sales tax agency.
    is_sales_tax_agency: bool
    #: For vendor in CA or UK, is there tax charged on top of tax.
    is_tax_on_tax: bool
    #: This flag is used for CA or UK and whether tax is tracked on purchases.
    is_tax_tracked_on_purchases: bool
    #: This flag is used for CA or UK and whether tax is tracked on sales.
    is_tax_tracked_on_sales: bool
    #: If `is_vendor_eligible_for1099` is set to true, `vendor_tax_ident` and `vendor_address`
    #: are required in a vendor add request message. Otherwise, `vendor_tax_ident` and
    #: `vendor_address` are optional.
    is_vendor_eligible_for1099: bool
    #: The job title of a customer, vendor, employee, or person on the “other names” list.
    job_title: str
    #: The last name of a customer, vendor, employee, or person on the “other names” list.
    last_name: str
    #: The middle name of a customer, vendor, employee, or person on the “other names” list.
    middle_name: str
    mobile: str
    #: The vendor’s name as it will appear on checks sent to the vendor. (Corresponds in the
    #: QuickBooks user interface to the “Print on Check as” field of the Edit Vendor and New
    #: Vendor windows.)
    name_on_check: str
    #: Additional information about this vendor.
    notes: str
    #: The opening balance of this vendor’s account. A positive number indicates money owed to
    #: this vendor.
    open_balance: float
    #: The date of the opening balance for this vendor.
    open_balance_date: str
    pager: str
    #: The telephone number.
    phone: str
    prefill_account_ref: List[Ref]
    #: Vendor reporting period for CA or UK. This can be monthly or quarterly.
    reporting_period: Literal["Monthly", "Quarterly"]
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
    #: The country that sales tax is collected for.
    sales_tax_country: Literal["Australia", "Canada", "UK", "US"]
    #: Sales tax return information.
    sales_tax_return_ref: Ref
    #: A formal reference, such as Mr. or Dr., that precedes a name.
    salutation: str
    #: This aggregate supports at most five address lines. You can provide a structured address
    #: (Addr1-Addr3 plus City/State/`postal_code`/etc.) or use block mode (Addr1-Addr5 only). Do
    #: not mix block mode with other address fields. In block mode, each Addr line prints as its
    #: own line and is returned in ShipAddressBlock or BillAddressBlock.
    ship_address: Address
    suffix: str
    #: Account used for taxes on purchases in CA or UK.
    tax_on_purchases_account_ref: Ref
    #: Account used for taxes on sales in CA or UK.
    tax_on_sales_account_ref: Ref
    #: The tax registration number used in CA and UK.
    tax_registration_number: str
    #: Refers to the payment terms associated with this entity. (This will be an item on the
    #: DateDrivenTerms or StandardTerms list.) If a `terms_ref` aggregate includes both
    #: `full_name` and `list_id`, `full_name` will be ignored.
    terms_ref: Ref
    #: If an address request fails, some combination of address fields might be too long.
    vendor_address: Address
    #: A character string that identifies a vendor.
    vendor_tax_ident: str
    #: Vendor types allow business owners to categorize vendors in ways that are meaningful for
    #: their businesses. For example, a vendor type might indicate which industry a vendor
    #: represents, or which part of the country a vendor is in. A `vendor_type_ref` aggregate
    #: refers to one of the types on the VendorType list.
    vendor_type_ref: Ref


class VendorQueryParams(TypedDict, total=False):
    """Params for ``vendor.query`` (List vendors)."""
    #: Used in filters to select list objects based on whether or not they are currently enabled
    #: for use by QuickBooks. The default value is asActiveOnly, which selects only list objects
    #: that are active.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `currency_filter`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`, `total_balance_filter`). Members of a set
    #: combine with each other, not with the other choices.
    active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
    #: Filter according to class.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `currency_filter`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`, `total_balance_filter`). Members of a set
    #: combine with each other, not with the other choices.
    class_filter: EntityFilter
    #: Filters by the specified currency.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `currency_filter`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`, `total_balance_filter`). Members of a set
    #: combine with each other, not with the other choices.
    currency_filter: CurrencyFilter
    #: Filters results to objects modified on or after this timestamp. QuickBooks Desktop
    #: accepts 1970-01-01 through 2038-01-19T03:14:07. If only a date is provided, time defaults
    #: to 00:00:00.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `currency_filter`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`, `total_balance_filter`). Members of a set
    #: combine with each other, not with the other choices.
    from_modified_date: str
    #: `full_name` (along with `list_id`) is a way to identify a list object. The `full_name` is
    #: the name prefixed by the names of each ancestor, for example Jones:Kitchen:Cabinets.
    #: `full_name` values aren’t case-sensitive.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `currency_filter`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`, `total_balance_filter`). Members of a set
    #: combine with each other, not with the other choices.
    full_name: List[str]
    include_ret_element: List[Literal["AccountNumber", "AdditionalContactRef", "AdditionalNotesRet", "AltContact", "AltPhone", "Balance", "BillingRateRef", "Cc", "ClassRef", "CompanyName", "Contact", "ContactsRet", "CreditLimit", "CurrencyRef", "DataExtRet", "EditSequence", "Email", "ExternalGUID", "Fax", "FirstName", "IsActive", "IsSalesTaxAgency", "IsTaxAgency", "IsTaxOnTax", "IsTaxTrackedOnPurchases", "IsTaxTrackedOnSales", "IsVendorEligibleFor1099", "JobTitle", "LastName", "ListID", "MiddleName", "Mobile", "Name", "NameOnCheck", "Notes", "Pager", "Phone", "PrefillAccountRef", "ReportingPeriod", "SalesTaxCodeRef", "SalesTaxCountry", "SalesTaxReturnRef", "Salutation", "ShipAddress", "Suffix", "TaxOnPurchasesAccountRef", "TaxOnSalesAccountRef", "TaxRegistrationNumber", "TermsRef", "TimeCreated", "TimeModified", "VendorAddress", "VendorAddressBlock", "VendorTaxIdent", "VendorTypeRef"]]
    #: Page through every match: QuBe Sync asks QuickBooks for each page in turn and sends each
    #: to your `webhook_url` as it arrives, all with the same `id`. On by default, with pages of
    #: 100 records; send `iterator=true` with `max_returned` for another size. Off when you send
    #: `iterator=false` (every match in one answer) or `max_returned` alone (at most that many,
    #: in one answer). It pages a filtered query only: with `full_name` or `list_id` every match
    #: comes back in one answer, so leave `iterator` out.
    iterator: bool
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list family, not across the
    #: company file: customers, vendors, employees and other names share one sequence, every
    #: item type shares another, and each other list has its own.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `currency_filter`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`, `total_balance_filter`). Members of a set
    #: combine with each other, not with the other choices.
    list_id: List[str]
    #: Limits the number of objects that a query returns. (To get a count of how many objects
    #: could possibly be returned, use the `meta_data` query attribute.) If you include a
    #: `max_returned` value, it must be at least 1.
    #:
    #: The page size, with `iterator=true`. Sent without `iterator`, or with `iterator=false`,
    #: it's a cap instead: at most this many records come back, in one answer, and QuickBooks
    #: doesn't say whether more matched.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `currency_filter`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`, `total_balance_filter`). Members of a set
    #: combine with each other, not with the other choices.
    max_returned: int
    #: Use the `meta_data` attribute to control whether query responses include counts. Options
    #: are NoMetaData (default), MetaDataOnly (count only), and MetaDataAndResponseData (count
    #: plus objects). Counts are approximate and may vary slightly if records are created or
    #: deleted during processing.
    meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
    #: Filters according to the object’s Name.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `currency_filter`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`, `total_balance_filter`). Members of a set
    #: combine with each other, not with the other choices.
    name_filter: NameFilter
    #: Filters according to the object’s Name.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `currency_filter`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`, `total_balance_filter`). Members of a set
    #: combine with each other, not with the other choices.
    name_range_filter: NameRangeFilter
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
    #: Filters results to objects modified on or before this timestamp. QuickBooks Desktop
    #: accepts 1970-01-01 through 2038-01-19T03:14:07. If only a date is provided, time defaults
    #: to end-of-day (23:59:59).
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `currency_filter`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`, `total_balance_filter`). Members of a set
    #: combine with each other, not with the other choices.
    to_modified_date: str
    #: Filters according to total balance. Total balance includes the balance for all
    #: subaccounts; for example, a customer’s TotalBalance would include all the jobs for that
    #: customer.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `currency_filter`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`, `total_balance_filter`). Members of a set
    #: combine with each other, not with the other choices.
    total_balance_filter: TotalBalanceFilter


class _VendorUpdateParamsRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list family, not across the
    #: company file: customers, vendors, employees and other names share one sequence, every
    #: item type shares another, and each other list has its own.
    list_id: str


class VendorUpdateParams(_VendorUpdateParamsRequired, total=False):
    """Params for ``vendor.update`` (Update vendor)."""
    #: Account numbers appear in the QuickBooks chart of accounts, Account fields, and reports
    #: and graphs. If the IsUsingAccountNumber preference is false (that is, if the QuickBooks
    #: user has the account numbers Preference turned off), you can still set account numbers
    #: through the SDK, but the numbers won’t be visible in the user interface.
    account_number: str
    additional_contact_ref: List[AdditionalContactRef]
    additional_notes_mod: List[AdditionalNotesMod]
    #: The name of an alternate contact person for a vendor, customer, or “other name” entry.
    alt_contact: str
    #: A telephone number given as an alternative to Phone.
    alt_phone: str
    #: Billing rates are used to override the service item rate in a time transaction
    #: (TimeTrackingAdd) based on the employee or vendor performing the work. Billing rates are
    #: assigned to an employee or a vendor to specify overrides to service items.
    billing_rate_ref: Ref
    #: Email address that would be carbon copied or CC.
    cc: str
    #: Use classes to categorize transactions (for example, by department, location, or work
    #: type). Class tracking is off by default in QuickBooks. A `class_ref` points to one class;
    #: if both `full_name` and `list_id` are provided, `full_name` is ignored. In InvoiceAdd, a
    #: header-level `class_ref` is applied to line items unless you override or clear it on
    #: individual lines.
    class_ref: Ref
    #: The name of the QuickBooks user’s business, as specified in QuickBooks. `company_name`
    #: and Address are used on invoices, checks, and other forms. (LegalCompanyName and
    #: LegalAddress, on the other hand, are used on a company’s tax forms and pay stubs.)
    company_name: str
    #: The name of a contact person for a customer or vendor.
    contact: str
    contacts_mod: List[ContactsMod]
    #: Set and returned as a positive number that indicates a customer’s or vendor’s credit
    #: limit. If no value has been defined, there is no credit limit.
    credit_limit: float
    #: A currency record defines how QuickBooks stores and displays a currency. Built-in
    #: currency name/code values are fixed; formatting and active status can vary by settings
    #: and workflow.
    currency_ref: Ref
    #: E-mail address.
    email: str
    #: Fax number.
    fax: str
    #: The first name of a customer, vendor, employee, or person on the “other names” list.
    first_name: str
    include_ret_element: List[Literal["AccountNumber", "AdditionalContactRef", "AdditionalNotesRet", "AltContact", "AltPhone", "Balance", "BillingRateRef", "Cc", "ClassRef", "CompanyName", "Contact", "ContactsRet", "CreditLimit", "CurrencyRef", "DataExtRet", "EditSequence", "Email", "ExternalGUID", "Fax", "FirstName", "IsActive", "IsSalesTaxAgency", "IsTaxAgency", "IsTaxOnTax", "IsTaxTrackedOnPurchases", "IsTaxTrackedOnSales", "IsVendorEligibleFor1099", "JobTitle", "LastName", "ListID", "MiddleName", "Mobile", "Name", "NameOnCheck", "Notes", "OwnerID", "Pager", "Phone", "PrefillAccountRef", "ReportingPeriod", "SalesTaxCodeRef", "SalesTaxCountry", "SalesTaxReturnRef", "Salutation", "ShipAddress", "Suffix", "TaxOnPurchasesAccountRef", "TaxOnSalesAccountRef", "TaxRegistrationNumber", "TermsRef", "TimeCreated", "TimeModified", "TxnID", "TxnNumber", "VendorAddress", "VendorAddressBlock", "VendorTaxIdent", "VendorTypeRef"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: Indicates whether the entity is a sales tax agency.
    is_sales_tax_agency: bool
    #: For vendor in CA or UK, is there tax charged on top of tax.
    is_tax_on_tax: bool
    #: This flag is used for CA or UK and whether tax is tracked on purchases.
    is_tax_tracked_on_purchases: bool
    #: This flag is used for CA or UK and whether tax is tracked on sales.
    is_tax_tracked_on_sales: bool
    #: If `is_vendor_eligible_for1099` is set to true, `vendor_tax_ident` and `vendor_address`
    #: are required in a vendor add request message. Otherwise, `vendor_tax_ident` and
    #: `vendor_address` are optional.
    is_vendor_eligible_for1099: bool
    #: The job title of a customer, vendor, employee, or person on the “other names” list.
    job_title: str
    #: The last name of a customer, vendor, employee, or person on the “other names” list.
    last_name: str
    #: The middle name of a customer, vendor, employee, or person on the “other names” list.
    middle_name: str
    mobile: str
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because `full_name` remains distinct.
    name: str
    #: The vendor’s name as it will appear on checks sent to the vendor. (Corresponds in the
    #: QuickBooks user interface to the “Print on Check as” field of the Edit Vendor and New
    #: Vendor windows.)
    name_on_check: str
    #: Additional information about this vendor.
    notes: str
    pager: str
    #: The telephone number.
    phone: str
    prefill_account_ref: List[Ref]
    #: Vendor reporting period for CA or UK. This can be monthly or quarterly.
    reporting_period: Literal["Monthly", "Quarterly"]
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
    #: The country that sales tax is collected for.
    sales_tax_country: Literal["Australia", "Canada", "UK", "US"]
    #: Sales tax return information.
    sales_tax_return_ref: Ref
    #: A formal reference, such as Mr. or Dr., that precedes a name.
    salutation: str
    #: This aggregate supports at most five address lines. You can provide a structured address
    #: (Addr1-Addr3 plus City/State/`postal_code`/etc.) or use block mode (Addr1-Addr5 only). Do
    #: not mix block mode with other address fields. In block mode, each Addr line prints as its
    #: own line and is returned in ShipAddressBlock or BillAddressBlock.
    ship_address: Address
    suffix: str
    #: Account used for taxes on purchases in CA or UK.
    tax_on_purchases_account_ref: Ref
    #: Account used for taxes on sales in CA or UK.
    tax_on_sales_account_ref: Ref
    #: The tax registration number used in CA and UK.
    tax_registration_number: str
    #: Refers to the payment terms associated with this entity. (This will be an item on the
    #: DateDrivenTerms or StandardTerms list.) If a `terms_ref` aggregate includes both
    #: `full_name` and `list_id`, `full_name` will be ignored.
    terms_ref: Ref
    #: If an address request fails, some combination of address fields might be too long.
    vendor_address: Address
    #: A character string that identifies a vendor.
    vendor_tax_ident: str
    #: Vendor types allow business owners to categorize vendors in ways that are meaningful for
    #: their businesses. For example, a vendor type might indicate which industry a vendor
    #: represents, or which part of the country a vendor is in. A `vendor_type_ref` aggregate
    #: refers to one of the types on the VendorType list.
    vendor_type_ref: Ref


class Vendor:
    """QuickBooks vendor operations: create, query, update.

    Get it from ``client.vendor``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[VendorCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create vendor.

        Queues ``vendor.create``: POST /connections/{connection_id}/vendors, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``VendorCreateParams``)::

            account_number: str
            additional_contact_ref: List[AdditionalContactRef]
                contact_name: str (required)
                contact_value: str (required)
            additional_notes: List[AdditionalNotes]
                note: str (required)
            alt_contact: str
            alt_phone: str
            billing_rate_ref: Ref
                full_name: str
                list_id: str
            cc: str
            class_ref: Ref
            company_name: str
            contact: str
            contacts: List[Contacts]
                additional_contact_ref: List[AdditionalContactRef]
                first_name: str (required)
                job_title: str
                last_name: str
                middle_name: str
                salutation: str
            credit_limit: float
            currency_ref: Ref
            email: str
            external_guid: str
            fax: str
            first_name: str
            include_ret_element: List[Literal[...] (one of 58 values)]
            is_active: bool
            is_sales_tax_agency: bool
            is_tax_on_tax: bool
            is_tax_tracked_on_purchases: bool
            is_tax_tracked_on_sales: bool
            is_vendor_eligible_for1099: bool
            job_title: str
            last_name: str
            middle_name: str
            mobile: str
            name: str (required)
            name_on_check: str
            notes: str
            open_balance: float
            open_balance_date: str
            pager: str
            phone: str
            prefill_account_ref: List[Ref]
            reporting_period: Literal["Monthly", "Quarterly"]
            request_id: str
            sales_tax_code_ref: Ref
            sales_tax_country: Literal["Australia", "Canada", "UK", "US"]
            sales_tax_return_ref: Ref
            salutation: str
            ship_address: Address
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
            suffix: str
            tax_on_purchases_account_ref: Ref
            tax_on_sales_account_ref: Ref
            tax_registration_number: str
            terms_ref: Ref
            vendor_address: Address
            vendor_tax_ident: str
            vendor_type_ref: Ref

        Docs: https://docs.qubesync.com/api-reference/v2/vendors/create-vendor
        """
        return self._client._queue_operation("vendor.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[VendorQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List vendors.

        Queues ``vendor.query``: GET /connections/{connection_id}/vendors, params in the query string.
        QuickBooks answers in pages: each page comes to ``webhook_url`` as its own webhook.
        Returns the queued request.

        Params (``VendorQueryParams``)::

            active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
            class_filter: EntityFilter
                full_name: List[str]
                full_name_with_children: str
                list_id: List[str]
                list_id_with_children: str
            currency_filter: CurrencyFilter
                full_name: List[str]
                list_id: List[str]
            from_modified_date: str
            full_name: List[str]
            include_ret_element: List[Literal[...] (one of 55 values)]
            iterator: bool
            list_id: List[str]
            max_returned: int
            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            name_filter: NameFilter
                match_criterion: Literal["Contains", "EndsWith", "StartsWith"] (required)
                name: str (required)
            name_range_filter: NameRangeFilter
                from_name: str
                to_name: str
            owner_id: List[str]
            request_id: str
            to_modified_date: str
            total_balance_filter: TotalBalanceFilter
                amount: float (required)
                operator: Literal["Equal", "GreaterThan", "GreaterThanEqual", "LessThan", "LessThanEqual"] (required)

        Docs: https://docs.qubesync.com/api-reference/v2/vendors/list-vendors
        """
        return self._client._queue_operation("vendor.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[VendorUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update vendor.

        Queues ``vendor.update``: PUT /connections/{connection_id}/vendors, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``VendorUpdateParams``)::

            account_number: str
            additional_contact_ref: List[AdditionalContactRef]
                contact_name: str (required)
                contact_value: str (required)
            additional_notes_mod: List[AdditionalNotesMod]
                note: str (required)
                note_id: int (required)
            alt_contact: str
            alt_phone: str
            billing_rate_ref: Ref
                full_name: str
                list_id: str
            cc: str
            class_ref: Ref
            company_name: str
            contact: str
            contacts_mod: List[ContactsMod]
                additional_contact_ref: List[AdditionalContactRef]
                edit_sequence: str
                first_name: str (required)
                job_title: str
                last_name: str
                list_id: str
                middle_name: str
                salutation: str
            credit_limit: float
            currency_ref: Ref
            edit_sequence: str (required)
            email: str
            fax: str
            first_name: str
            include_ret_element: List[Literal[...] (one of 58 values)]
            is_active: bool
            is_sales_tax_agency: bool
            is_tax_on_tax: bool
            is_tax_tracked_on_purchases: bool
            is_tax_tracked_on_sales: bool
            is_vendor_eligible_for1099: bool
            job_title: str
            last_name: str
            list_id: str (required)
            middle_name: str
            mobile: str
            name: str
            name_on_check: str
            notes: str
            pager: str
            phone: str
            prefill_account_ref: List[Ref]
            reporting_period: Literal["Monthly", "Quarterly"]
            request_id: str
            sales_tax_code_ref: Ref
            sales_tax_country: Literal["Australia", "Canada", "UK", "US"]
            sales_tax_return_ref: Ref
            salutation: str
            ship_address: Address
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
            suffix: str
            tax_on_purchases_account_ref: Ref
            tax_on_sales_account_ref: Ref
            tax_registration_number: str
            terms_ref: Ref
            vendor_address: Address
            vendor_tax_ident: str
            vendor_type_ref: Ref

        Docs: https://docs.qubesync.com/api-reference/v2/vendors/update-vendor
        """
        return self._client._queue_operation("vendor.update", connection_id, params, webhook_url, idempotency_key)
