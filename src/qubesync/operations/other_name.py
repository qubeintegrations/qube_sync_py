# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks other name operations (``client.other_name``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    Address,
    NameFilter,
    NameRangeFilter,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _OtherNameCreateParamsRequired(TypedDict):
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because FullName remains distinct.
    name: str


class OtherNameCreateParams(_OtherNameCreateParamsRequired, total=False):
    """Params for ``other_name.create`` (Create other name)."""
    #: Account numbers appear in the QuickBooks chart of accounts, Account fields, and reports
    #: and graphs. If the IsUsingAccountNumber preference is false (that is, if the QuickBooks
    #: user has the account numbers Preference turned off), you can still set account numbers
    #: through the SDK, but the numbers won’t be visible in the user interface.
    account_number: str
    #: The name of an alternate contact person for a vendor, customer, or “other name” entry.
    alt_contact: str
    #: A telephone number given as an alternative to Phone.
    alt_phone: str
    #: The name of the QuickBooks user’s business, as specified in QuickBooks. `company_name`
    #: and Address are used on invoices, checks, and other forms. (LegalCompanyName and
    #: LegalAddress, on the other hand, are used on a company’s tax forms and pay stubs.)
    company_name: str
    #: The name of a contact person for a customer or vendor.
    contact: str
    #: E-mail address.
    email: str
    #: Allows for the attachment of a user defined GUID value.
    external_guid: str
    #: Fax number.
    fax: str
    #: The first name of a customer, vendor, employee, or person on the “other names” list.
    first_name: str
    include_ret_element: List[Literal["AccountNumber", "AltContact", "AltPhone", "CompanyName", "Contact", "DataExtRet", "EditSequence", "Email", "ExternalGUID", "Fax", "FirstName", "IsActive", "LastName", "ListID", "MiddleName", "Name", "Notes", "OtherNameAddress", "OtherNameAddressBlock", "OwnerID", "Phone", "Salutation", "TimeCreated", "TimeModified", "TxnID", "TxnNumber"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: The last name of a customer, vendor, employee, or person on the “other names” list.
    last_name: str
    #: The middle name of a customer, vendor, employee, or person on the “other names” list.
    middle_name: str
    #: Additional information.
    notes: str
    #: If an address request fails, some combination of address fields might be too long.
    other_name_address: Address
    #: The telephone number.
    phone: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: A formal reference, such as Mr. or Dr., that precedes a name.
    salutation: str


class OtherNameQueryParams(TypedDict, total=False):
    """Params for ``other_name.query`` (List other names)."""
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
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    full_name: List[str]
    include_ret_element: List[Literal["AccountNumber", "AltContact", "AltPhone", "CompanyName", "Contact", "DataExtRet", "EditSequence", "Email", "ExternalGUID", "Fax", "FirstName", "IsActive", "LastName", "ListID", "MiddleName", "Name", "Notes", "OtherNameAddress", "OtherNameAddressBlock", "Phone", "Salutation", "TimeCreated", "TimeModified"]]
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list type, not globally
    #: across all lists. If both `full_name` and `list_id` are supplied in a request, QuickBooks
    #: uses `list_id` and ignores `full_name`.
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


class _OtherNameUpdateParamsRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `list_id` and FullName both identify a list object. QuickBooks assigns `list_id` when the
    #: object is created. `list_id` values are unique within a list type, not globally across
    #: all lists. If both FullName and `list_id` are supplied in a request, QuickBooks uses
    #: `list_id` and ignores FullName.
    list_id: str


class OtherNameUpdateParams(_OtherNameUpdateParamsRequired, total=False):
    """Params for ``other_name.update`` (Update other name)."""
    #: Account numbers appear in the QuickBooks chart of accounts, Account fields, and reports
    #: and graphs. If the IsUsingAccountNumber preference is false (that is, if the QuickBooks
    #: user has the account numbers Preference turned off), you can still set account numbers
    #: through the SDK, but the numbers won’t be visible in the user interface.
    account_number: str
    #: The name of an alternate contact person for a vendor, customer, or “other name” entry.
    alt_contact: str
    #: A telephone number given as an alternative to Phone.
    alt_phone: str
    #: The name of the QuickBooks user’s business, as specified in QuickBooks. `company_name`
    #: and Address are used on invoices, checks, and other forms. (LegalCompanyName and
    #: LegalAddress, on the other hand, are used on a company’s tax forms and pay stubs.)
    company_name: str
    #: The name of a contact person for a customer or vendor.
    contact: str
    #: E-mail address.
    email: str
    #: Fax number.
    fax: str
    #: The first name of a customer, vendor, employee, or person on the “other names” list.
    first_name: str
    include_ret_element: List[Literal["AccountNumber", "AltContact", "AltPhone", "CompanyName", "Contact", "DataExtRet", "EditSequence", "Email", "ExternalGUID", "Fax", "FirstName", "IsActive", "LastName", "ListID", "MiddleName", "Name", "Notes", "OtherNameAddress", "OtherNameAddressBlock", "OwnerID", "Phone", "Salutation", "TimeCreated", "TimeModified", "TxnID", "TxnNumber"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: The last name of a customer, vendor, employee, or person on the “other names” list.
    last_name: str
    #: The middle name of a customer, vendor, employee, or person on the “other names” list.
    middle_name: str
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because FullName remains distinct.
    name: str
    #: Additional information.
    notes: str
    #: If an address request fails, some combination of address fields might be too long.
    other_name_address: Address
    #: The telephone number.
    phone: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: A formal reference, such as Mr. or Dr., that precedes a name.
    salutation: str


class OtherName:
    """QuickBooks other name operations: create, query, update.

    Get it from ``client.other_name``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[OtherNameCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create other name.

        Queues ``other_name.create``: POST /connections/{connection_id}/other-names, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``OtherNameCreateParams``)::

            account_number: str
            alt_contact: str
            alt_phone: str
            company_name: str
            contact: str
            email: str
            external_guid: str
            fax: str
            first_name: str
            include_ret_element: List[Literal[...] (one of 26 values)]
            is_active: bool
            last_name: str
            middle_name: str
            name: str (required)
            notes: str
            other_name_address: Address
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
            phone: str
            request_id: str
            salutation: str

        Docs: https://docs.qubesync.com/api-reference/v2/other-names/create-other-name
        """
        return self._client._queue_operation("other_name.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[OtherNameQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List other names.

        Queues ``other_name.query``: GET /connections/{connection_id}/other-names, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``OtherNameQueryParams``)::

            active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
            from_modified_date: str
            full_name: List[str]
            include_ret_element: List[Literal[...] (one of 23 values)]
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

        Docs: https://docs.qubesync.com/api-reference/v2/other-names/list-other-names
        """
        return self._client._queue_operation("other_name.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[OtherNameUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update other name.

        Queues ``other_name.update``: PUT /connections/{connection_id}/other-names, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``OtherNameUpdateParams``)::

            account_number: str
            alt_contact: str
            alt_phone: str
            company_name: str
            contact: str
            edit_sequence: str (required)
            email: str
            fax: str
            first_name: str
            include_ret_element: List[Literal[...] (one of 26 values)]
            is_active: bool
            last_name: str
            list_id: str (required)
            middle_name: str
            name: str
            notes: str
            other_name_address: Address
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
            phone: str
            request_id: str
            salutation: str

        Docs: https://docs.qubesync.com/api-reference/v2/other-names/update-other-name
        """
        return self._client._queue_operation("other_name.update", connection_id, params, webhook_url, idempotency_key)
