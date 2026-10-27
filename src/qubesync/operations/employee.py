# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks employee operations (``client.employee``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    AdditionalContactRef,
    AdditionalNotes,
    AdditionalNotesMod,
    Earnings,
    NameFilter,
    NameRangeFilter,
    Ref,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _ContactRequired(TypedDict):
    #: The name of the contact.
    contact_name: str
    #: The value of the contact field.
    contact_value: str


class Contact(_ContactRequired, total=False):
    #: Relationship of emergency contact information to the employee.
    relation: Literal["Brother", "Daughter", "Father", "Friend", "Mother", "Other", "Partner", "Sister", "Son", "Spouse"]


class EmergencyContacts(TypedDict, total=False):
    #: Primary emergency contact information for the employee.
    primary_contact: Contact
    #: Secondary emergency contact information for the employee.
    secondary_contact: Contact


class EmployeeAddress(TypedDict, total=False):
    #: The first line of an address.
    addr1: str
    #: The second line of an address (if a second line is needed).
    addr2: str
    addr3: str
    addr4: str
    #: The city name in an address.
    city: str
    country: str
    #: The postal code in an address.
    postal_code: str
    #: When it appears in the `employee_address` aggregate, the State element acts like an
    #: ENUMTYPE with the following possible values: None, AA (military), AE (military), AK, AL,
    #: AP (military), AR, AZ, CA, CO, CT, DC, DE, FL, GA, HI, IA, ID, IL, IN, KS, KY, LA, MA,
    #: MD, ME, MI, MN, MO, MS, MT, NC, ND, NE, NH, NJ, NM, NV, NY, OH, OK, OR, PA, PR, RI, SC,
    #: SD, TN, TX, UT, VA, VT, WA, WI, WV, and WY.
    state: str


class Hours(TypedDict, total=False):
    #: Indicates how an employee accrues time off. If you include a blank `accrual_period`
    #: element in an EmployeeMod message, you’ll receive an error. The default value is whatever
    #: the QuickBooks user has set in the QuickBooks Employee Preferences.
    accrual_period: Literal["BeginningOfYear", "EveryHourOnPaycheck", "EveryPaycheck"]
    #: When used in the `sick_hours` or `vacation_hours` aggregates, refers to the date on which
    #: sick leave or vacation hours in the current year began to accrue.
    accrual_start_date: str
    #: The number of hours that the employee will accrue per accrual period. The default value
    #: is whatever the QuickBooks user has set in the QuickBooks Employee Preferences.
    hours_accrued: str
    #: The total number of hours currently available for the employee to use. If this value is
    #: empty, it will default to 0.
    hours_available: str
    #: When used in the `sick_hours` or `vacation_hours` aggregates, refers to the number of
    #: sick leave or vacation hours used in the current year.
    hours_used: str
    #: Indicates whether or not the hours accrued resets to zero at the beginning of the new
    #: year. If you include a blank `is_resetting_hours_each_new_year` element in an EmployeeMod
    #: message, you’ll receive an error.
    is_resetting_hours_each_new_year: bool
    #: The maximum number of hours that the employee can accrue. (QuickBooks itself doesn’t
    #: enforce this limit, however. `hours_available` can be greater than `maximum_hours`.) The
    #: default value is whatever the QuickBooks user has set in the QuickBooks Employee
    #: Preferences.
    maximum_hours: str


class EmployeePayrollInfoMod(TypedDict, total=False):
    #: Use classes to categorize transactions (for example, by department, location, or work
    #: type). Class tracking is off by default in QuickBooks. A `class_ref` points to one class;
    #: if both `full_name` and `list_id` are provided, `full_name` is ignored. In InvoiceAdd, a
    #: header-level `class_ref` is applied to line items unless you override or clear it on
    #: individual lines.
    class_ref: Ref
    #: If `clear_earnings` is set to true, the earnings will be deleted for this employee.
    #:
    #: Choose at most one of: `clear_earnings`, or `earnings`.
    clear_earnings: bool
    #: Choose at most one of: `clear_earnings`, or `earnings`.
    earnings: List[Earnings]
    #: Indicates how often employees are paid. If you include a blank `pay_period` element in an
    #: EmployeeMod message, you’ll receive an error. The default value is whatever the
    #: QuickBooks user has set in the QuickBooks Employee Preferences.
    pay_period: Literal["Biweekly", "Daily", "Monthly", "Quarterly", "Semimonthly", "Weekly", "Yearly"]
    #: Describes how “sick time” is accrued for this employee, along with how many sick hours
    #: the employee has accrued.
    sick_hours: Hours
    #: Indicates whether time data is used to create paychecks for this employee.
    use_time_data_to_create_paychecks: Literal["DoNotUseTimeData", "NotSet", "UseTimeData"]
    #: Describes how vacation time is accrued for this employee, along with how many vacation
    #: hours the employee has accrued.
    vacation_hours: Hours


class EmployeeCreateParams(TypedDict, total=False):
    """Params for ``employee.create`` (Create employee)."""
    #: Account numbers appear in the QuickBooks chart of accounts, Account fields, and reports
    #: and graphs. If the IsUsingAccountNumber preference is false (that is, if the QuickBooks
    #: user has the account numbers Preference turned off), you can still set account numbers
    #: through the SDK, but the numbers won’t be visible in the user interface.
    account_number: str
    additional_contact_ref: List[AdditionalContactRef]
    additional_notes: List[AdditionalNotes]
    #: Adjusted service date for the employee.
    adjusted_service_date: str
    #: A telephone number given as an alternative to Phone.
    alt_phone: str
    #: Billing rates are used to override the service item rate in a time transaction
    #: (TimeTrackingAdd) based on the employee or vendor performing the work. Billing rates are
    #: assigned to an employee or a vendor to specify overrides to service items.
    billing_rate_ref: Ref
    #: Date of birth.
    birth_date: str
    #: The name of the department in the employment job details section.
    department: str
    #: The description details in the employment job details section.
    description: str
    #: Description of employee’s disablitily.
    disability_desc: str
    #: Is employee disabled?
    disabled: Literal["No", "Yes"]
    #: E-mail address.
    email: str
    #: Emergency Contact information for the employee.
    emergency_contacts: EmergencyContacts
    #: If an address request fails, some combination of address fields might be too long. If you
    #: use payroll, you must specify the employee’s city, state (or province), ZIP (or postal)
    #: code, and at least one line of the street address. (Note that the State element has
    #: restrictions when it’s used in the `employee_address` aggregate. For more information,
    #: click State in the table.)
    employee_address: EmployeeAddress
    #: Pay information for this employee.
    employee_payroll_info: EmployeePayrollInfoMod
    #: `employee_type` can affect payroll taxes for an employee. A statutory employee is a
    #: person who is defined as an employee by statute. Usually an owner or partner will be on
    #: the Other Names list, but if they are on the Employee list, their `employee_type` will be
    #: Owner.
    employee_type: Literal["Officer", "Owner", "Regular", "Statutory"]
    #: Ethnicity of employee from AmericianIndian, Asian, Black, Hawaiian, Hispanic, White,
    #: TwoOrMoreRaces
    ethnicity: Literal["AmericianIndian", "Asian", "Black", "Hawaiian", "Hispanic", "TwoOrMoreRaces", "White"]
    #: Exempt or Non-exempt status of the employee.
    exempt: Literal["Exempt", "NonExempt"]
    #: Allows for the attachment of a user defined GUID value.
    external_guid: str
    #: Fax number.
    fax: str
    #: The first name of a customer, vendor, employee, or person on the “other names” list.
    first_name: str
    #: The gender of this employee.
    gender: Literal["Female", "Male"]
    #: An employee’s date of hire.
    hired_date: str
    include_ret_element: List[Literal["AccountNumber", "AdditionalContactRef", "AdditionalNotesRet", "AdjustedServiceDate", "AltPhone", "BillingRateRef", "BirthDate", "DataExtRet", "Department", "Description", "DisabilityDesc", "Disabled", "EditSequence", "Email", "EmergencyContacts", "EmployeeAddress", "EmployeePayrollInfo", "EmployeeType", "Ethnicity", "Exempt", "ExternalGUID", "Fax", "FirstName", "Gender", "HiredDate", "IsActive", "JobTitle", "KeyEmployee", "LastName", "ListID", "MiddleName", "MilitaryStatus", "Mobile", "Name", "Notes", "OnFile", "OriginalHireDate", "OwnerID", "Pager", "PagerPIN", "PartOrFullTime", "Phone", "PrintAs", "ReleasedDate", "SSN", "Salutation", "Suffix", "SupervisorRef", "TargetBonus", "TimeCreated", "TimeModified", "TxnID", "TxnNumber", "USCitizen", "USVeteran", "WorkAuthExpireDate"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: The job title of a customer, vendor, employee, or person on the “other names” list.
    job_title: str
    #: Is employee a key or critical employee.
    key_employee: Literal["No", "Yes"]
    #: The last name of a customer, vendor, employee, or person on the “other names” list.
    last_name: str
    #: The middle name of a customer, vendor, employee, or person on the “other names” list.
    middle_name: str
    #: Military status if the employee is a US veteran.
    military_status: Literal["Active", "Reserve"]
    #: Mobile telephone number.
    mobile: str
    #: A concatenation of `first_name`, `middle_name`, and `last_name`.
    name: str
    #: Additional information.
    notes: str
    #: Is the employee’s I-9 on file?
    on_file: Literal["No", "Yes"]
    #: Original hire date the employee was hired.
    original_hire_date: str
    #: The pager number.
    pager: str
    #: A personal identification number for this employee’s pager.
    pager_pin: str
    #: Full or Part time status of the employee.
    part_or_full_time: Literal["FullTime", "PartTime"]
    #: The telephone number.
    phone: str
    #: By default within QuickBooks, the `print_as` element is the same as the Name element.
    print_as: str
    #: The date on which this person’s employment with the company ended.
    released_date: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: A formal reference, such as Mr. or Dr., that precedes a name.
    salutation: str
    #: Social security number. When you add an SSN value to an employee record, it doesn’t have
    #: to include dashes; for example, either 123-45-6789 or 123456789 would be valid.
    ssn: str
    suffix: str
    #: The name of a customer, vendor, employee, or person on the “other names” list in the
    #: employment job details section.
    supervisor_ref: Ref
    #: The target bonus amount in the employment job details section.
    target_bonus: float
    #: Is employee a US citizen?
    us_citizen: Literal["No", "Yes"]
    #: Is employee a US veteran?
    us_veteran: Literal["No", "Yes"]
    #: Date the employee’s work authorization expires.
    work_auth_expire_date: str


class EmployeeQueryParams(TypedDict, total=False):
    """Params for ``employee.query`` (List employees)."""
    #: Used in filters to select list objects based on whether or not they are currently enabled
    #: for use by QuickBooks. The default value is asActiveOnly, which selects only list objects
    #: that are active.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
    #: Filters results to objects modified on or after this timestamp. QuickBooks Desktop
    #: accepts 1970-01-01 through 2038-01-19T03:14:07. If only a date is provided, time defaults
    #: to 00:00:00.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    from_modified_date: str
    #: `full_name` (along with `list_id`) is a way to identify a list object. The `full_name` is
    #: the name prefixed by the names of each ancestor, for example Jones:Kitchen:Cabinets.
    #: `full_name` values aren’t case-sensitive.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    full_name: List[str]
    include_ret_element: List[Literal["AccountNumber", "AdditionalContactRef", "AdditionalNotesRet", "AdjustedServiceDate", "AltPhone", "BillingRateRef", "BirthDate", "DataExtRet", "Department", "Description", "DisabilityDesc", "Disabled", "EditSequence", "Email", "EmergencyContacts", "EmployeeAddress", "EmployeePayrollInfo", "EmployeeType", "Ethnicity", "Exempt", "ExternalGUID", "Fax", "FirstName", "Gender", "HiredDate", "IsActive", "JobTitle", "KeyEmployee", "LastName", "ListID", "MiddleName", "MilitaryStatus", "Mobile", "Name", "Notes", "OnFile", "OriginalHireDate", "Pager", "PagerPIN", "PartOrFullTime", "Phone", "PrintAs", "ReleasedDate", "SSN", "Salutation", "Suffix", "SupervisorRef", "TargetBonus", "TimeCreated", "TimeModified", "USCitizen", "USVeteran", "WorkAuthExpireDate"]]
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list family, not across the
    #: company file: customers, vendors, employees and other names share one sequence, every
    #: item type shares another, and each other list has its own.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    list_id: List[str]
    #: Limits the number of objects that a query returns. (To get a count of how many objects
    #: could possibly be returned, use the `meta_data` query attribute.) If you include a
    #: `max_returned` value, it must be at least 1.
    #:
    #: QuickBooks doesn't page this query: at most this many records come back, in one answer,
    #: with no sign of whether more matched. Leave it out for every match, in one answer; one
    #: over 4 MB as the Web Connector sends it, about 3 MB of qbXML isn't kept (`error_type`
    #: `response_too_large`), so narrow a large one with its filters.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    max_returned: int
    #: Use the `meta_data` attribute to control whether query responses include counts. Options
    #: are NoMetaData (default), MetaDataOnly (count only), and MetaDataAndResponseData (count
    #: plus objects). Counts are approximate and may vary slightly if records are created or
    #: deleted during processing.
    meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
    #: Filters according to the object’s Name.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    name_filter: NameFilter
    #: Filters according to the object’s Name.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
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
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    to_modified_date: str


class _EmployeeUpdateParamsRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list family, not across the
    #: company file: customers, vendors, employees and other names share one sequence, every
    #: item type shares another, and each other list has its own.
    list_id: str


class EmployeeUpdateParams(_EmployeeUpdateParamsRequired, total=False):
    """Params for ``employee.update`` (Update employee)."""
    #: Account numbers appear in the QuickBooks chart of accounts, Account fields, and reports
    #: and graphs. If the IsUsingAccountNumber preference is false (that is, if the QuickBooks
    #: user has the account numbers Preference turned off), you can still set account numbers
    #: through the SDK, but the numbers won’t be visible in the user interface.
    account_number: str
    additional_contact_ref: List[AdditionalContactRef]
    additional_notes_mod: List[AdditionalNotesMod]
    #: Adjusted service date for the employee.
    adjusted_service_date: str
    #: A telephone number given as an alternative to Phone.
    alt_phone: str
    #: Billing rates are used to override the service item rate in a time transaction
    #: (TimeTrackingAdd) based on the employee or vendor performing the work. Billing rates are
    #: assigned to an employee or a vendor to specify overrides to service items.
    billing_rate_ref: Ref
    #: Date of birth.
    birth_date: str
    #: The name of the department in the employment job details section.
    department: str
    #: The description details in the employment job details section.
    description: str
    #: Description of employee’s disablitily.
    disability_desc: str
    #: Is employee disabled?
    disabled: Literal["No", "Yes"]
    #: E-mail address.
    email: str
    #: Emergency Contact information for the employee.
    emergency_contacts: EmergencyContacts
    #: If an address request fails, some combination of address fields might be too long. If you
    #: use payroll, you must specify the employee’s city, state (or province), ZIP (or postal)
    #: code, and at least one line of the street address. (Note that the State element has
    #: restrictions when it’s used in the `employee_address` aggregate. For more information,
    #: click State in the table.)
    employee_address: EmployeeAddress
    #: Pay information for this employee.
    employee_payroll_info_mod: EmployeePayrollInfoMod
    #: `employee_type` can affect payroll taxes for an employee. A statutory employee is a
    #: person who is defined as an employee by statute. Usually an owner or partner will be on
    #: the Other Names list, but if they are on the Employee list, their `employee_type` will be
    #: Owner.
    employee_type: Literal["Officer", "Owner", "Regular", "Statutory"]
    #: Ethnicity of employee from AmericianIndian, Asian, Black, Hawaiian, Hispanic, White,
    #: TwoOrMoreRaces.
    ethnicity: Literal["AmericianIndian", "Asian", "Black", "Hawaiian", "Hispanic", "TwoOrMoreRaces", "White"]
    #: Exempt or Non-exempt status of the employee.
    exempt: Literal["Exempt", "NonExempt"]
    #: Fax number.
    fax: str
    #: The first name of a customer, vendor, employee, or person on the “other names” list.
    first_name: str
    #: An employee’s date of hire.
    hired_date: str
    include_ret_element: List[Literal["AccountNumber", "AdditionalContactRef", "AdditionalNotesRet", "AdjustedServiceDate", "AltPhone", "BillingRateRef", "BirthDate", "DataExtRet", "Department", "Description", "DisabilityDesc", "Disabled", "EditSequence", "Email", "EmergencyContacts", "EmployeeAddress", "EmployeePayrollInfo", "EmployeeType", "Ethnicity", "Exempt", "ExternalGUID", "Fax", "FirstName", "Gender", "HiredDate", "IsActive", "JobTitle", "KeyEmployee", "LastName", "ListID", "MiddleName", "MilitaryStatus", "Mobile", "Name", "Notes", "OnFile", "OriginalHireDate", "OwnerID", "Pager", "PagerPIN", "PartOrFullTime", "Phone", "PrintAs", "ReleasedDate", "SSN", "Salutation", "Suffix", "SupervisorRef", "TargetBonus", "TimeCreated", "TimeModified", "TxnID", "TxnNumber", "USCitizen", "USVeteran", "WorkAuthExpireDate"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: The job title of a customer, vendor, employee, or person on the “other names” list.
    job_title: str
    #: Is employee a key or critical employee.
    key_employee: Literal["No", "Yes"]
    #: The last name of a customer, vendor, employee, or person on the “other names” list.
    last_name: str
    #: The middle name of a customer, vendor, employee, or person on the “other names” list.
    middle_name: str
    #: Military status if the employee is a US veteran.
    military_status: Literal["Active", "Reserve"]
    #: Mobile telephone number.
    mobile: str
    #: A concatenation of `first_name`, `middle_name`, and `last_name`.
    name: str
    #: Additional information.
    notes: str
    #: Is the employee’s I-9 on file?
    on_file: Literal["No", "Yes"]
    #: Original hire date the employee was hired.
    original_hire_date: str
    #: The pager number.
    pager: str
    #: A personal identification number for this employee’s pager.
    pager_pin: str
    #: Full or Part time status of the employee.
    part_or_full_time: Literal["FullTime", "PartTime"]
    #: The telephone number.
    phone: str
    #: By default within QuickBooks, the `print_as` element is the same as the Name element.
    print_as: str
    #: The date on which this person’s employment with the company ended.
    released_date: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: A formal reference, such as Mr. or Dr., that precedes a name.
    salutation: str
    suffix: str
    #: The name of a customer, vendor, employee, or person on the “other names” list in the
    #: employment job details section.
    supervisor_ref: Ref
    #: The target bonus amount in the employment job details section.
    target_bonus: float
    #: Is employee a US citizen?
    us_citizen: Literal["No", "Yes"]
    #: Is employee a US veteran?
    us_veteran: Literal["No", "Yes"]
    #: Date the employee’s work authorization expires.
    work_auth_expire_date: str


class Employee:
    """QuickBooks employee operations: create, query, update.

    Get it from ``client.employee``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[EmployeeCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create employee.

        Queues ``employee.create``: POST /connections/{connection_id}/employees, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``EmployeeCreateParams``)::

            account_number: str
            additional_contact_ref: List[AdditionalContactRef]
                contact_name: str (required)
                contact_value: str (required)
            additional_notes: List[AdditionalNotes]
                note: str (required)
            adjusted_service_date: str
            alt_phone: str
            billing_rate_ref: Ref
                full_name: str
                list_id: str
            birth_date: str
            department: str
            description: str
            disability_desc: str
            disabled: Literal["No", "Yes"]
            email: str
            emergency_contacts: EmergencyContacts
                primary_contact: Contact
                    contact_name: str (required)
                    contact_value: str (required)
                    relation: Literal[...] (one of 10 values)
                secondary_contact: Contact
            employee_address: EmployeeAddress
                addr1: str
                addr2: str
                addr3: str
                addr4: str
                city: str
                country: str
                postal_code: str
                state: str
            employee_payroll_info: EmployeePayrollInfoMod
                class_ref: Ref
                clear_earnings: bool
                earnings: List[Earnings]
                    payroll_item_wage_ref: Ref (required)
                    rate: float
                    rate_percent: float
                pay_period: Literal[...] (one of 7 values)
                sick_hours: Hours
                    accrual_period: Literal["BeginningOfYear", "EveryHourOnPaycheck", "EveryPaycheck"]
                    accrual_start_date: str
                    hours_accrued: str
                    hours_available: str
                    hours_used: str
                    is_resetting_hours_each_new_year: bool
                    maximum_hours: str
                use_time_data_to_create_paychecks: Literal["DoNotUseTimeData", "NotSet", "UseTimeData"]
                vacation_hours: Hours
            employee_type: Literal["Officer", "Owner", "Regular", "Statutory"]
            ethnicity: Literal[...] (one of 7 values)
            exempt: Literal["Exempt", "NonExempt"]
            external_guid: str
            fax: str
            first_name: str
            gender: Literal["Female", "Male"]
            hired_date: str
            include_ret_element: List[Literal[...] (one of 56 values)]
            is_active: bool
            job_title: str
            key_employee: Literal["No", "Yes"]
            last_name: str
            middle_name: str
            military_status: Literal["Active", "Reserve"]
            mobile: str
            name: str
            notes: str
            on_file: Literal["No", "Yes"]
            original_hire_date: str
            pager: str
            pager_pin: str
            part_or_full_time: Literal["FullTime", "PartTime"]
            phone: str
            print_as: str
            released_date: str
            request_id: str
            salutation: str
            ssn: str
            suffix: str
            supervisor_ref: Ref
            target_bonus: float
            us_citizen: Literal["No", "Yes"]
            us_veteran: Literal["No", "Yes"]
            work_auth_expire_date: str

        Docs: https://docs.qubesync.com/api-reference/v2/employees/create-employee
        """
        return self._client._queue_operation("employee.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[EmployeeQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List employees.

        Queues ``employee.query``: GET /connections/{connection_id}/employees, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``EmployeeQueryParams``)::

            active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
            from_modified_date: str
            full_name: List[str]
            include_ret_element: List[Literal[...] (one of 53 values)]
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

        Docs: https://docs.qubesync.com/api-reference/v2/employees/list-employees
        """
        return self._client._queue_operation("employee.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[EmployeeUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update employee.

        Queues ``employee.update``: PUT /connections/{connection_id}/employees, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``EmployeeUpdateParams``)::

            account_number: str
            additional_contact_ref: List[AdditionalContactRef]
                contact_name: str (required)
                contact_value: str (required)
            additional_notes_mod: List[AdditionalNotesMod]
                note: str (required)
                note_id: int (required)
            adjusted_service_date: str
            alt_phone: str
            billing_rate_ref: Ref
                full_name: str
                list_id: str
            birth_date: str
            department: str
            description: str
            disability_desc: str
            disabled: Literal["No", "Yes"]
            edit_sequence: str (required)
            email: str
            emergency_contacts: EmergencyContacts
                primary_contact: Contact
                    contact_name: str (required)
                    contact_value: str (required)
                    relation: Literal[...] (one of 10 values)
                secondary_contact: Contact
            employee_address: EmployeeAddress
                addr1: str
                addr2: str
                addr3: str
                addr4: str
                city: str
                country: str
                postal_code: str
                state: str
            employee_payroll_info_mod: EmployeePayrollInfoMod
                class_ref: Ref
                clear_earnings: bool
                earnings: List[Earnings]
                    payroll_item_wage_ref: Ref (required)
                    rate: float
                    rate_percent: float
                pay_period: Literal[...] (one of 7 values)
                sick_hours: Hours
                    accrual_period: Literal["BeginningOfYear", "EveryHourOnPaycheck", "EveryPaycheck"]
                    accrual_start_date: str
                    hours_accrued: str
                    hours_available: str
                    hours_used: str
                    is_resetting_hours_each_new_year: bool
                    maximum_hours: str
                use_time_data_to_create_paychecks: Literal["DoNotUseTimeData", "NotSet", "UseTimeData"]
                vacation_hours: Hours
            employee_type: Literal["Officer", "Owner", "Regular", "Statutory"]
            ethnicity: Literal[...] (one of 7 values)
            exempt: Literal["Exempt", "NonExempt"]
            fax: str
            first_name: str
            hired_date: str
            include_ret_element: List[Literal[...] (one of 56 values)]
            is_active: bool
            job_title: str
            key_employee: Literal["No", "Yes"]
            last_name: str
            list_id: str (required)
            middle_name: str
            military_status: Literal["Active", "Reserve"]
            mobile: str
            name: str
            notes: str
            on_file: Literal["No", "Yes"]
            original_hire_date: str
            pager: str
            pager_pin: str
            part_or_full_time: Literal["FullTime", "PartTime"]
            phone: str
            print_as: str
            released_date: str
            request_id: str
            salutation: str
            suffix: str
            supervisor_ref: Ref
            target_bonus: float
            us_citizen: Literal["No", "Yes"]
            us_veteran: Literal["No", "Yes"]
            work_auth_expire_date: str

        Docs: https://docs.qubesync.com/api-reference/v2/employees/update-employee
        """
        return self._client._queue_operation("employee.update", connection_id, params, webhook_url, idempotency_key)
