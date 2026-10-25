# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks customer operations (``client.customer``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    AdditionalContactRef,
    AdditionalNotes,
    AdditionalNotesMod,
    Address,
    Contacts,
    ContactsMod,
    Ref,
)

if TYPE_CHECKING:
    from ..v2 import Client


class CreditCardInfo(TypedDict, total=False):
    #: The address associated with this credit card.
    credit_card_address: str
    #: Credit-card number for this customer or this payment. Beginning with qbXML spec 6.0 and
    #: QuickBooks 2007, you must mask the credit card number with lower case “x” and no dashes.
    #: For example, xxxxxxxxxxxx1234.
    credit_card_number: str
    #: The postal code associated with the address for this credit card.
    credit_card_postal_code: str
    #: The month when the credit card expires.
    expiration_month: int
    #: The year when the credit card expires.
    expiration_year: int
    #: The name on the customer’s credit card.
    name_on_card: str


class _ShipToAddressRequired(TypedDict):
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because `full_name` remains distinct.
    name: str


class ShipToAddress(_ShipToAddressRequired, total=False):
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
    #: Flag that address is the default ship to address.
    default_ship_to: bool
    #: In a `bill_address` or `ship_address` aggregate, the Note field value is written at the
    #: bottom of the address in the form in which it appears, such as the invoice form.
    note: str
    #: The postal code in an address.
    postal_code: str
    #: The state name in an address.
    state: str


_NameRangeOptionalKeys = TypedDict(
    "_NameRangeOptionalKeys",
    {
        "from": str,
    },
    total=False,
)


class NameRange(_NameRangeOptionalKeys, total=False):
    to: str


class _CustomerCreateParamsRequired(TypedDict):
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because `full_name` remains distinct.
    name: str


class CustomerCreateParams(_CustomerCreateParamsRequired, total=False):
    """Params for ``customer.create`` (Create customer)."""
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
    #: This aggregate supports at most five address lines. You can provide a structured address
    #: (Addr1-Addr3 plus City/State/`postal_code`/etc.) or use block mode (Addr1-Addr5 only). Do
    #: not mix block mode with other address fields. In block mode, each Addr line prints as its
    #: own line and is returned in `ship_address_block` or `bill_address_block`.
    bill_address: Address
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
    #: Customer’s credit-card information.
    credit_card_info: CreditCardInfo
    #: Set and returned as a positive number that indicates a customer’s or vendor’s credit
    #: limit. If no value has been defined, there is no credit limit.
    credit_limit: float
    #: A currency record defines how QuickBooks stores and displays a currency. Built-in
    #: currency name/code values are fixed; formatting and active status can vary by settings
    #: and workflow.
    currency_ref: Ref
    #: Customer types allow business owners to categorize customers in ways that are meaningful
    #: for their businesses. For example, a customer type might indicate which industry a
    #: customer represents, or which part of the country a customer is in. A `customer_type_ref`
    #: aggregate refers to one of the types on the CustomerType list.
    customer_type_ref: Ref
    delivery_method: Literal["Email", "Fax", "Print"]
    #: E-mail address.
    email: str
    #: Allows for the attachment of a user defined GUID value.
    external_guid: str
    #: Fax number.
    fax: str
    #: The first name of a customer, vendor, employee, or person on the “other names” list.
    first_name: str
    include_ret_element: List[Literal["AccountNumber", "AdditionalContactRef", "AdditionalNotesRet", "AltContact", "AltPhone", "Balance", "BillAddress", "BillAddressBlock", "Cc", "ClassRef", "CompanyName", "Contact", "ContactsRet", "CreditCardInfo", "CreditLimit", "CurrencyRef", "CustomerTypeRef", "DataExtRet", "DeliveryMethod", "EditSequence", "Email", "ExternalGUID", "Fax", "FirstName", "FullName", "IsActive", "IsStatementWithParent", "ItemSalesTaxRef", "JobDesc", "JobEndDate", "JobProjectedEndDate", "JobStartDate", "JobStatus", "JobTitle", "JobTypeRef", "LastName", "ListID", "MiddleName", "Mobile", "Name", "Notes", "OwnerID", "Pager", "ParentRef", "Phone", "PreferredDeliveryMethod", "PreferredPaymentMethodRef", "PriceLevelRef", "PrintAs", "ResaleNumber", "SalesRepRef", "SalesTaxCodeRef", "SalesTaxCountry", "Salutation", "ShipAddress", "ShipAddressBlock", "ShipToAddress", "Sublevel", "Suffix", "TaxRegistrationNumber", "TermsRef", "TimeCreated", "TimeModified", "TotalBalance", "TxnID", "TxnNumber"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    is_statement_with_parent: bool
    #: An ItemSalesTax entry represents one tax rate paid to one tax agency. Use it when a
    #: transaction needs a single tax calculation. For multi-rate scenarios, use a sales-tax
    #: group instead. If both `full_name` and `list_id` are provided for `item_sales_tax_ref`,
    #: `list_id` is used.
    item_sales_tax_ref: Ref
    #: A short job description for a sub-customer; used in reports. The Job- elements
    #: (`job_desc`, `job_end_date`, `job_projected_end_date`, `job_start_date`, and
    #: `job_status`) correspond to the fields in the Job Info tab of the Edit Job window in
    #: QuickBooks.
    job_desc: str
    #: The date on which work for a sub-customer was completed; used in reports. The Job-
    #: elements (`job_desc`, `job_end_date`, `job_projected_end_date`, `job_start_date`, and
    #: `job_status`) correspond to the fields in the Job Info tab of the Edit Job window in
    #: QuickBooks.
    job_end_date: str
    #: The date on which work for a sub-customer is expected to be complete; used in reports.
    #: The Job- elements (`job_desc`, `job_end_date`, `job_projected_end_date`,
    #: `job_start_date`, and `job_status`) correspond to the fields in the Job Info tab of the
    #: Edit Job window in QuickBooks.
    job_projected_end_date: str
    #: The date on which work for a sub-customer was started; used in reports. The Job- elements
    #: (`job_desc`, `job_end_date`, `job_projected_end_date`, `job_start_date`, and
    #: `job_status`) correspond to the fields in the Job Info tab of the Edit Job window in
    #: QuickBooks.
    job_start_date: str
    #: `job_status` Status information about a sub-customer; used in reports. The Job- elements
    #: (`job_desc`, `job_end_date`, `job_projected_end_date`, `job_start_date`, and
    #: `job_status`) correspond to the fields in the Job Info tab of the Edit Job window in
    #: QuickBooks.
    job_status: Literal["Awarded", "Closed", "InProgress", "None", "NotAwarded", "Pending"]
    #: The job title of a customer, vendor, employee, or person on the “other names” list.
    job_title: str
    #: Job type can be used to separate jobs into any categories that are meaningful to the
    #: business. A `job_type_ref` aggregate refers to a job type on the JobType list. In a
    #: request, if a `job_type_ref` aggregate includes both `full_name` and `list_id`,
    #: `full_name` will be ignored.
    job_type_ref: Ref
    #: The last name of a customer, vendor, employee, or person on the “other names” list.
    last_name: str
    #: The middle name of a customer, vendor, employee, or person on the “other names” list.
    middle_name: str
    mobile: str
    #: Not supported.
    notes: str
    #: The opening balance of this customer’s account. A positive number indicates money owed by
    #: the customer.
    open_balance: float
    #: The date of the opening balance for this customer.
    open_balance_date: str
    pager: str
    #: A reference to the list object that is one level above this one. For example, an
    #: inventory item with the `full_name` of GermanCars:Mercedes-Benz:CL500I99AA might have a
    #: parent object with the `full_name` of GermanCars:Mercedes-Benz. In a request, if a
    #: `parent_ref` aggregate includes both `full_name` and `list_id`, `full_name` will be
    #: ignored.
    parent_ref: Ref
    #: The telephone number.
    phone: str
    #: Preference for how invoices are delivered.
    preferred_delivery_method: Literal["Email", "Fax", "None"]
    #: Refers to a PaymentMethod object. In a request, if a `preferred_payment_method_ref`
    #: aggregate includes both `full_name` and `list_id`, `full_name` will be ignored.
    preferred_payment_method_ref: Ref
    #: Price levels let you apply custom pricing rules for selected customers. Once assigned,
    #: QuickBooks uses those prices automatically on supported sales forms unless explicitly
    #: overridden.
    price_level_ref: Ref
    print_as: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: The customer’s resale number, if they have one. This number won’t affect reports or sales
    #: tax calculations.
    resale_number: str
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
    #: Country that sales tax is collected for.
    sales_tax_country: Literal["Australia", "Canada", "UK", "US"]
    #: A formal reference, such as Mr. or Dr., that precedes a name.
    salutation: str
    #: This aggregate supports at most five address lines. You can provide a structured address
    #: (Addr1-Addr3 plus City/State/`postal_code`/etc.) or use block mode (Addr1-Addr5 only). Do
    #: not mix block mode with other address fields. In block mode, each Addr line prints as its
    #: own line and is returned in `ship_address_block` or `bill_address_block`.
    ship_address: Address
    ship_to_address: List[ShipToAddress]
    suffix: str
    #: Tax registration number used in CA and UK.
    tax_registration_number: str
    #: Refers to the payment terms associated with this entity. (This will be an item on the
    #: DateDrivenTerms or StandardTerms list.) If a `terms_ref` aggregate includes both
    #: `full_name` and `list_id`, `full_name` will be ignored.
    terms_ref: Ref


class CustomerQueryParams(TypedDict, total=False):
    """Params for ``customer.query`` (List customers)."""
    #: Used in filters to select list objects based on whether or not they are currently enabled
    #: for use by QuickBooks. The default value is asActiveOnly, which selects only list objects
    #: that are active.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `max_returned`, `name_contains`, `name_ends_with`, `name_range`,
    #: `name_starts_with`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
    #: Filters results to objects modified on or after this timestamp. QuickBooks Desktop
    #: accepts 1970-01-01 through 2038-01-19T03:14:07. If only a date is provided, time defaults
    #: to 00:00:00.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `max_returned`, `name_contains`, `name_ends_with`, `name_range`,
    #: `name_starts_with`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    from_modified_date: str
    #: `full_name` (along with `list_id`) is a way to identify a list object. The `full_name` is
    #: the name prefixed by the names of each ancestor, for example Jones:Kitchen:Cabinets.
    #: `full_name` values aren’t case-sensitive.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `max_returned`, `name_contains`, `name_ends_with`, `name_range`,
    #: `name_starts_with`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    full_name: List[str]
    include: List[Literal["AccountNumber", "AdditionalContactRef", "AdditionalNotesRet", "AltContact", "AltPhone", "Balance", "BillAddress", "BillAddressBlock", "Cc", "ClassRef", "CompanyName", "Contact", "ContactsRet", "CreditCardInfo", "CreditLimit", "CurrencyRef", "CustomerTypeRef", "DataExtRet", "DeliveryMethod", "EditSequence", "Email", "ExternalGUID", "Fax", "FirstName", "FullName", "IsActive", "IsStatementWithParent", "ItemSalesTaxRef", "JobDesc", "JobEndDate", "JobProjectedEndDate", "JobStartDate", "JobStatus", "JobTitle", "JobTypeRef", "LastName", "ListID", "MiddleName", "Mobile", "Name", "Notes", "Pager", "ParentRef", "Phone", "PreferredDeliveryMethod", "PreferredPaymentMethodRef", "PriceLevelRef", "PrintAs", "ResaleNumber", "SalesRepRef", "SalesTaxCodeRef", "SalesTaxCountry", "Salutation", "ShipAddress", "ShipAddressBlock", "ShipToAddress", "Sublevel", "Suffix", "TaxRegistrationNumber", "TermsRef", "TimeCreated", "TimeModified", "TotalBalance"]]
    #: Page through every match: QuBe Sync asks QuickBooks for each page in turn and sends each
    #: to your `webhook_url` as it arrives, all with the same `id`. On by default, with pages of
    #: 100 records; send `iterator=true` with `max_returned` for another size. Off when you send
    #: `iterator=false` (every match in one answer) or `max_returned` alone (at most that many,
    #: in one answer). It pages a filtered query only: with `full_name` or `list_id` every match
    #: comes back in one answer, so leave `iterator` out.
    iterator: bool
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list type, not globally
    #: across all lists. If both `full_name` and `list_id` are supplied in a request, QuickBooks
    #: uses `list_id` and ignores `full_name`.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `max_returned`, `name_contains`, `name_ends_with`, `name_range`,
    #: `name_starts_with`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    list_id: List[str]
    #: Limits the number of objects that a query returns. (To get a count of how many objects
    #: could possibly be returned, use the metaData query attribute.) If you include a
    #: `max_returned` value, it must be at least 1.
    #:
    #: The page size, with `iterator=true`. Sent without `iterator`, or with `iterator=false`,
    #: it's a cap instead: at most this many records come back, in one answer, and QuickBooks
    #: doesn't say whether more matched.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `max_returned`, `name_contains`, `name_ends_with`, `name_range`,
    #: `name_starts_with`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    max_returned: int
    #: Filters according to the object’s Name.
    #:
    #: Choose at most one of: the set (`name_contains`, `name_ends_with`, `name_starts_with`),
    #: or `name_range`. Members of a set combine with each other, not with the other choices.
    name_contains: str
    #: Filters according to the object’s Name.
    #:
    #: Choose at most one of: the set (`name_contains`, `name_ends_with`, `name_starts_with`),
    #: or `name_range`. Members of a set combine with each other, not with the other choices.
    name_ends_with: str
    #: Filters according to the object’s Name.
    #:
    #: Choose at most one of: the set (`name_contains`, `name_ends_with`, `name_starts_with`),
    #: or `name_range`. Members of a set combine with each other, not with the other choices.
    name_range: NameRange
    #: Filters according to the object’s Name.
    #:
    #: Choose at most one of: the set (`name_contains`, `name_ends_with`, `name_starts_with`),
    #: or `name_range`. Members of a set combine with each other, not with the other choices.
    name_starts_with: str
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
    #: `from_modified_date`, `max_returned`, `name_contains`, `name_ends_with`, `name_range`,
    #: `name_starts_with`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    to_modified_date: str


class _CustomerUpdateParamsRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list type, not globally
    #: across all lists. If both `full_name` and `list_id` are supplied in a request, QuickBooks
    #: uses `list_id` and ignores `full_name`.
    list_id: str


class CustomerUpdateParams(_CustomerUpdateParamsRequired, total=False):
    """Params for ``customer.update`` (Update customer)."""
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
    #: This aggregate supports at most five address lines. You can provide a structured address
    #: (Addr1-Addr3 plus City/State/`postal_code`/etc.) or use block mode (Addr1-Addr5 only). Do
    #: not mix block mode with other address fields. In block mode, each Addr line prints as its
    #: own line and is returned in `ship_address_block` or `bill_address_block`.
    bill_address: Address
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
    #: Customer’s credit-card information.
    credit_card_info: CreditCardInfo
    #: Set and returned as a positive number that indicates a customer’s or vendor’s credit
    #: limit. If no value has been defined, there is no credit limit.
    credit_limit: float
    #: A currency record defines how QuickBooks stores and displays a currency. Built-in
    #: currency name/code values are fixed; formatting and active status can vary by settings
    #: and workflow.
    currency_ref: Ref
    #: Customer types allow business owners to categorize customers in ways that are meaningful
    #: for their businesses. For example, a customer type might indicate which industry a
    #: customer represents, or which part of the country a customer is in. A `customer_type_ref`
    #: aggregate refers to one of the types on the CustomerType list.
    customer_type_ref: Ref
    delivery_method: Literal["Email", "Fax", "Print"]
    #: E-mail address.
    email: str
    #: Fax number.
    fax: str
    #: The first name of a customer, vendor, employee, or person on the “other names” list.
    first_name: str
    include_ret_element: List[Literal["AccountNumber", "AdditionalContactRef", "AdditionalNotesRet", "AltContact", "AltPhone", "Balance", "BillAddress", "BillAddressBlock", "Cc", "ClassRef", "CompanyName", "Contact", "ContactsRet", "CreditCardInfo", "CreditLimit", "CurrencyRef", "CustomerTypeRef", "DataExtRet", "DeliveryMethod", "EditSequence", "Email", "ExternalGUID", "Fax", "FirstName", "FullName", "IsActive", "IsStatementWithParent", "ItemSalesTaxRef", "JobDesc", "JobEndDate", "JobProjectedEndDate", "JobStartDate", "JobStatus", "JobTitle", "JobTypeRef", "LastName", "ListID", "MiddleName", "Mobile", "Name", "Notes", "OwnerID", "Pager", "ParentRef", "Phone", "PreferredDeliveryMethod", "PreferredPaymentMethodRef", "PriceLevelRef", "PrintAs", "ResaleNumber", "SalesRepRef", "SalesTaxCodeRef", "SalesTaxCountry", "Salutation", "ShipAddress", "ShipAddressBlock", "ShipToAddress", "Sublevel", "Suffix", "TaxRegistrationNumber", "TermsRef", "TimeCreated", "TimeModified", "TotalBalance", "TxnID", "TxnNumber"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    is_statement_with_parent: bool
    #: An ItemSalesTax entry represents one tax rate paid to one tax agency. Use it when a
    #: transaction needs a single tax calculation. For multi-rate scenarios, use a sales-tax
    #: group instead. If both `full_name` and `list_id` are provided for `item_sales_tax_ref`,
    #: `list_id` is used.
    item_sales_tax_ref: Ref
    #: A short job description for a sub-customer; used in reports. The Job- elements
    #: (`job_desc`, `job_end_date`, `job_projected_end_date`, `job_start_date`, and
    #: `job_status`) correspond to the fields in the Job Info tab of the Edit Job window in
    #: QuickBooks.
    job_desc: str
    #: The date on which work for a sub-customer was completed; used in reports. The Job-
    #: elements (`job_desc`, `job_end_date`, `job_projected_end_date`, `job_start_date`, and
    #: `job_status`) correspond to the fields in the Job Info tab of the Edit Job window in
    #: QuickBooks.
    job_end_date: str
    #: The date on which work for a sub-customer is expected to be complete; used in reports.
    #: The Job- elements (`job_desc`, `job_end_date`, `job_projected_end_date`,
    #: `job_start_date`, and `job_status`) correspond to the fields in the Job Info tab of the
    #: Edit Job window in QuickBooks.
    job_projected_end_date: str
    #: The date on which work for a sub-customer was started; used in reports. The Job- elements
    #: (`job_desc`, `job_end_date`, `job_projected_end_date`, `job_start_date`, and
    #: `job_status`) correspond to the fields in the Job Info tab of the Edit Job window in
    #: QuickBooks.
    job_start_date: str
    #: `job_status` Status information about a sub-customer; used in reports. The Job- elements
    #: (`job_desc`, `job_end_date`, `job_projected_end_date`, `job_start_date`, and
    #: `job_status`) correspond to the fields in the Job Info tab of the Edit Job window in
    #: QuickBooks.
    job_status: Literal["Awarded", "Closed", "InProgress", "None", "NotAwarded", "Pending"]
    #: The job title of a customer, vendor, employee, or person on the “other names” list.
    job_title: str
    #: Job type can be used to separate jobs into any categories that are meaningful to the
    #: business. A `job_type_ref` aggregate refers to a job type on the JobType list. In a
    #: request, if a `job_type_ref` aggregate includes both `full_name` and `list_id`,
    #: `full_name` will be ignored.
    job_type_ref: Ref
    #: The last name of a customer, vendor, employee, or person on the “other names” list.
    last_name: str
    #: The middle name of a customer, vendor, employee, or person on the “other names” list.
    middle_name: str
    mobile: str
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because `full_name` remains distinct.
    name: str
    #: Not supported.
    notes: str
    pager: str
    #: A reference to the list object that is one level above this one. For example, an
    #: inventory item with the `full_name` of GermanCars:Mercedes-Benz:CL500I99AA might have a
    #: parent object with the `full_name` of GermanCars:Mercedes-Benz. In a request, if a
    #: `parent_ref` aggregate includes both `full_name` and `list_id`, `full_name` will be
    #: ignored.
    parent_ref: Ref
    #: The telephone number.
    phone: str
    #: Preference for how invoices are delivered.
    preferred_delivery_method: Literal["Email", "Fax", "None"]
    #: Refers to a PaymentMethod object. In a request, if a `preferred_payment_method_ref`
    #: aggregate includes both `full_name` and `list_id`, `full_name` will be ignored.
    preferred_payment_method_ref: Ref
    #: Price levels let you apply custom pricing rules for selected customers. Once assigned,
    #: QuickBooks uses those prices automatically on supported sales forms unless explicitly
    #: overridden.
    price_level_ref: Ref
    print_as: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: The customer’s resale number, if they have one. This number won’t affect reports or sales
    #: tax calculations.
    resale_number: str
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
    #: The country that sales tax is collected for.
    sales_tax_country: Literal["Australia", "Canada", "UK", "US"]
    #: A formal reference, such as Mr. or Dr., that precedes a name.
    salutation: str
    #: This aggregate supports at most five address lines. You can provide a structured address
    #: (Addr1-Addr3 plus City/State/`postal_code`/etc.) or use block mode (Addr1-Addr5 only). Do
    #: not mix block mode with other address fields. In block mode, each Addr line prints as its
    #: own line and is returned in `ship_address_block` or `bill_address_block`.
    ship_address: Address
    ship_to_address: List[ShipToAddress]
    suffix: str
    #: The tax registration number used in CA and UK.
    tax_registration_number: str
    #: Refers to the payment terms associated with this entity. (This will be an item on the
    #: DateDrivenTerms or StandardTerms list.) If a `terms_ref` aggregate includes both
    #: `full_name` and `list_id`, `full_name` will be ignored.
    terms_ref: Ref


class Customer:
    """QuickBooks customer operations: create, query, update.

    Get it from ``client.customer``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[CustomerCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create customer.

        Queues ``customer.create``: POST /connections/{connection_id}/customers, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``CustomerCreateParams``)::

            account_number: str
            additional_contact_ref: List[AdditionalContactRef]
                contact_name: str (required)
                contact_value: str (required)
            additional_notes: List[AdditionalNotes]
                note: str (required)
            alt_contact: str
            alt_phone: str
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
            cc: str
            class_ref: Ref
                full_name: str
                list_id: str
            company_name: str
            contact: str
            contacts: List[Contacts]
                additional_contact_ref: List[AdditionalContactRef]
                first_name: str (required)
                job_title: str
                last_name: str
                middle_name: str
                salutation: str
            credit_card_info: CreditCardInfo
                credit_card_address: str
                credit_card_number: str
                credit_card_postal_code: str
                expiration_month: int
                expiration_year: int
                name_on_card: str
            credit_limit: float
            currency_ref: Ref
            customer_type_ref: Ref
            delivery_method: Literal["Email", "Fax", "Print"]
            email: str
            external_guid: str
            fax: str
            first_name: str
            include_ret_element: List[Literal[...] (one of 66 values)]
            is_active: bool
            is_statement_with_parent: bool
            item_sales_tax_ref: Ref
            job_desc: str
            job_end_date: str
            job_projected_end_date: str
            job_start_date: str
            job_status: Literal["Awarded", "Closed", "InProgress", "None", "NotAwarded", "Pending"]
            job_title: str
            job_type_ref: Ref
            last_name: str
            middle_name: str
            mobile: str
            name: str (required)
            notes: str
            open_balance: float
            open_balance_date: str
            pager: str
            parent_ref: Ref
            phone: str
            preferred_delivery_method: Literal["Email", "Fax", "None"]
            preferred_payment_method_ref: Ref
            price_level_ref: Ref
            print_as: str
            request_id: str
            resale_number: str
            sales_rep_ref: Ref
            sales_tax_code_ref: Ref
            sales_tax_country: Literal["Australia", "Canada", "UK", "US"]
            salutation: str
            ship_address: Address
            ship_to_address: List[ShipToAddress]
                addr1: str
                addr2: str
                addr3: str
                addr4: str
                addr5: str
                city: str
                country: str
                default_ship_to: bool
                name: str (required)
                note: str
                postal_code: str
                state: str
            suffix: str
            tax_registration_number: str
            terms_ref: Ref

        Docs: https://docs.qubesync.com/api-reference/v2/customers/create-customer
        """
        return self._client._queue_operation("customer.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[CustomerQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List customers.

        Queues ``customer.query``: GET /connections/{connection_id}/customers, params in the query string.
        QuickBooks answers in pages: each page comes to ``webhook_url`` as its own webhook.
        Returns the queued request.

        Params (``CustomerQueryParams``)::

            active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
            from_modified_date: str
            full_name: List[str]
            include: List[Literal[...] (one of 63 values)]
            iterator: bool
            list_id: List[str]
            max_returned: int
            name_contains: str
            name_ends_with: str
            name_range: NameRange
                from: str
                to: str
            name_starts_with: str
            owner_id: List[str]
            request_id: str
            to_modified_date: str

        Docs: https://docs.qubesync.com/api-reference/v2/customers/list-customers
        """
        return self._client._queue_operation("customer.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[CustomerUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update customer.

        Queues ``customer.update``: PUT /connections/{connection_id}/customers, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``CustomerUpdateParams``)::

            account_number: str
            additional_contact_ref: List[AdditionalContactRef]
                contact_name: str (required)
                contact_value: str (required)
            additional_notes_mod: List[AdditionalNotesMod]
                note: str (required)
                note_id: int (required)
            alt_contact: str
            alt_phone: str
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
            cc: str
            class_ref: Ref
                full_name: str
                list_id: str
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
            credit_card_info: CreditCardInfo
                credit_card_address: str
                credit_card_number: str
                credit_card_postal_code: str
                expiration_month: int
                expiration_year: int
                name_on_card: str
            credit_limit: float
            currency_ref: Ref
            customer_type_ref: Ref
            delivery_method: Literal["Email", "Fax", "Print"]
            edit_sequence: str (required)
            email: str
            fax: str
            first_name: str
            include_ret_element: List[Literal[...] (one of 66 values)]
            is_active: bool
            is_statement_with_parent: bool
            item_sales_tax_ref: Ref
            job_desc: str
            job_end_date: str
            job_projected_end_date: str
            job_start_date: str
            job_status: Literal["Awarded", "Closed", "InProgress", "None", "NotAwarded", "Pending"]
            job_title: str
            job_type_ref: Ref
            last_name: str
            list_id: str (required)
            middle_name: str
            mobile: str
            name: str
            notes: str
            pager: str
            parent_ref: Ref
            phone: str
            preferred_delivery_method: Literal["Email", "Fax", "None"]
            preferred_payment_method_ref: Ref
            price_level_ref: Ref
            print_as: str
            request_id: str
            resale_number: str
            sales_rep_ref: Ref
            sales_tax_code_ref: Ref
            sales_tax_country: Literal["Australia", "Canada", "UK", "US"]
            salutation: str
            ship_address: Address
            ship_to_address: List[ShipToAddress]
                addr1: str
                addr2: str
                addr3: str
                addr4: str
                addr5: str
                city: str
                country: str
                default_ship_to: bool
                name: str (required)
                note: str
                postal_code: str
                state: str
            suffix: str
            tax_registration_number: str
            terms_ref: Ref

        Docs: https://docs.qubesync.com/api-reference/v2/customers/update-customer
        """
        return self._client._queue_operation("customer.update", connection_id, params, webhook_url, idempotency_key)
