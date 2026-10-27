# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks entity operations (``client.entity``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    NameFilter,
    NameRangeFilter,
)

if TYPE_CHECKING:
    from ..v2 import Client


class EntityQueryParams(TypedDict, total=False):
    """Params for ``entity.query`` (List entities)."""
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
    include_ret_element: List[Literal["AccountNumber", "AdditionalContactRef", "AdditionalNotesRet", "AdjustedServiceDate", "AltContact", "AltPhone", "Balance", "BillAddress", "BillAddressBlock", "BillingRateRef", "BirthDate", "Cc", "ClassRef", "CompanyName", "Contact", "ContactsRet", "CreditCardInfo", "CreditLimit", "CurrencyRef", "CustomerTypeRef", "DataExtRet", "DeliveryMethod", "Department", "Description", "DisabilityDesc", "Disabled", "EditSequence", "Email", "EmergencyContacts", "EmployeeAddress", "EmployeePayrollInfo", "EmployeeType", "Ethnicity", "Exempt", "ExternalGUID", "Fax", "FirstName", "FullName", "Gender", "HiredDate", "IsActive", "IsSalesTaxAgency", "IsStatementWithParent", "IsTaxAgency", "IsTaxOnTax", "IsTaxTrackedOnPurchases", "IsTaxTrackedOnSales", "IsVendorEligibleFor1099", "ItemSalesTaxRef", "JobDesc", "JobEndDate", "JobProjectedEndDate", "JobStartDate", "JobStatus", "JobTitle", "JobTypeRef", "KeyEmployee", "LastName", "ListID", "MiddleName", "MilitaryStatus", "Mobile", "Name", "NameOnCheck", "Notes", "OnFile", "OriginalHireDate", "OtherNameAddress", "OtherNameAddressBlock", "Pager", "PagerPIN", "ParentRef", "PartOrFullTime", "Phone", "PreferredDeliveryMethod", "PreferredPaymentMethodRef", "PrefillAccountRef", "PriceLevelRef", "PrintAs", "ReleasedDate", "ReportingPeriod", "ResaleNumber", "SSN", "SalesRepRef", "SalesTaxCodeRef", "SalesTaxCountry", "SalesTaxReturnRef", "Salutation", "ShipAddress", "ShipAddressBlock", "ShipToAddress", "Sublevel", "Suffix", "SupervisorRef", "TargetBonus", "TaxOnPurchasesAccountRef", "TaxOnSalesAccountRef", "TaxRegistrationNumber", "TermsRef", "TimeCreated", "TimeModified", "TotalBalance", "USCitizen", "USVeteran", "VendorAddress", "VendorAddressBlock", "VendorTaxIdent", "VendorTypeRef", "WorkAuthExpireDate"]]
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
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
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


class Entity:
    """QuickBooks entity operations: query.

    Get it from ``client.entity``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def query(
        self,
        connection_id: str,
        params: Optional[EntityQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List entities.

        Queues ``entity.query``: GET /connections/{connection_id}/entities, params in the query string.
        QuickBooks answers in pages: each page comes to ``webhook_url`` as its own webhook.
        Returns the queued request.

        Params (``EntityQueryParams``)::

            active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
            from_modified_date: str
            full_name: List[str]
            include_ret_element: List[Literal[...] (one of 109 values)]
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
            request_id: str
            to_modified_date: str

        Docs: https://docs.qubesync.com/api-reference/v2/entities/list-entities
        """
        return self._client._queue_operation("entity.query", connection_id, params, webhook_url, idempotency_key)
