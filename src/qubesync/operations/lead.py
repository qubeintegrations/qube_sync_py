# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks lead operations (``client.lead``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    AdditionalContactRef,
    NameFilter,
    NameRangeFilter,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _LeadContactsRequired(TypedDict):
    #: The first name of a customer, vendor, employee, or person on the “other names” list.
    first_name: str


class LeadContacts(_LeadContactsRequired, total=False):
    additional_contact_ref: List[AdditionalContactRef]
    #: Flag for if this is a primary contact on a lead.
    is_primary_contact: bool
    #: The job title of a customer, vendor, employee, or person on the “other names” list.
    job_title: str
    #: The last name of a customer, vendor, employee, or person on the “other names” list.
    last_name: str
    #: The middle name of a customer, vendor, employee, or person on the “other names” list.
    middle_name: str
    #: A formal reference, such as Mr. or Dr., that precedes a name.
    salutation: str


class LeadAddress(TypedDict, total=False):
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


class _LocationsRequired(TypedDict):
    #: Where the asset is located or has been placed into service.
    location: str


class Locations(_LocationsRequired, total=False):
    #: Address for the lead.
    lead_address: LeadAddress


class _LeadContactsModRequired(TypedDict):
    #: The first name of a customer, vendor, employee, or person on the “other names” list.
    first_name: str


class LeadContactsMod(_LeadContactsModRequired, total=False):
    additional_contact_ref: List[AdditionalContactRef]
    #: Flag for if this is a primary contact on a lead.
    is_primary_contact: bool
    #: The job title of a customer, vendor, employee, or person on the “other names” list.
    job_title: str
    #: The last name of a customer, vendor, employee, or person on the “other names” list.
    last_name: str
    #: `lead_contact_id` is a way to identify a lead contact object. When a lead contact object
    #: is added to QuickBooks through the SDK or through the QuickBooks user interface, the
    #: server assigns it a `lead_contact_id`.
    lead_contact_id: int
    #: The middle name of a customer, vendor, employee, or person on the “other names” list.
    middle_name: str
    #: A formal reference, such as Mr. or Dr., that precedes a name.
    salutation: str


class _LocationsModRequired(TypedDict):
    #: Where the asset is located or has been placed into service.
    location: str
    #: `location_id` is a way to identify a location object. When a location object is added to
    #: QuickBooks through the SDK or through the QuickBooks user interface, the server assigns
    #: it a `location_id`.
    location_id: int


class LocationsMod(_LocationsModRequired, total=False):
    #: Address for the lead.
    lead_address: LeadAddress


class _LeadCreateParamsRequired(TypedDict):
    #: `full_name` (along with `list_id`) is a way to identify a list object. The `full_name` is
    #: the name prefixed by the names of each ancestor, for example Jones:Kitchen:Cabinets.
    #: `full_name` values aren’t case-sensitive.
    full_name: str


class LeadCreateParams(_LeadCreateParamsRequired, total=False):
    """Params for ``lead.create`` (Create lead)."""
    additional_contact_ref: List[AdditionalContactRef]
    #: The name of the QuickBooks user’s business, as specified in QuickBooks. `company_name`
    #: and Address are used on invoices, checks, and other forms. (LegalCompanyName and
    #: LegalAddress, on the other hand, are used on a company’s tax forms and pay stubs.)
    company_name: str
    include_ret_element: List[Literal["AdditionalContactRef", "CompanyName", "EditSequence", "ExternalGUID", "FullName", "LeadContactsRet", "ListID", "LocationsRet", "MainPhone", "OwnerID", "Status", "TimeCreated", "TimeModified", "TxnID", "TxnNumber"]]
    lead_contacts: List[LeadContacts]
    locations: List[Locations]
    #: The main phone number.
    main_phone: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: The status of the lead.
    status: Literal["Cold", "Hot", "Warm"]


class LeadQueryParams(TypedDict, total=False):
    """Params for ``lead.query`` (List leads)."""
    #: Filters results to objects modified on or after this timestamp. QuickBooks Desktop
    #: accepts 1970-01-01 through 2038-01-19T03:14:07. If only a date is provided, time defaults
    #: to 00:00:00.
    #:
    #: Choose at most one of: `list_id`, or `name`, or the set (`from_modified_date`,
    #: `max_returned`, `name_filter`, `name_range_filter`, `to_modified_date`). Members of a set
    #: combine with each other, not with the other choices.
    from_modified_date: str
    include_ret_element: List[Literal["AdditionalContactRef", "CompanyName", "EditSequence", "FullName", "LeadContactsRet", "ListID", "LocationsRet", "MainPhone", "Status", "TimeCreated", "TimeModified"]]
    #: Page through every match: QuBe Sync asks QuickBooks for each page in turn and sends each
    #: to your `webhook_url` as it arrives, all with the same `id`. On by default, with pages of
    #: 100 records; send `iterator=true` with `max_returned` for another size. Off when you send
    #: `iterator=false` (every match in one answer) or `max_returned` alone (at most that many,
    #: in one answer). It pages a filtered query only: with `list_id` or `name` every match
    #: comes back in one answer, so leave `iterator` out.
    iterator: bool
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list family, not across the
    #: company file: customers, vendors, employees and other names share one sequence, every
    #: item type shares another, and each other list has its own.
    #:
    #: Choose at most one of: `list_id`, or `name`, or the set (`from_modified_date`,
    #: `max_returned`, `name_filter`, `name_range_filter`, `to_modified_date`). Members of a set
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
    #: Choose at most one of: `list_id`, or `name`, or the set (`from_modified_date`,
    #: `max_returned`, `name_filter`, `name_range_filter`, `to_modified_date`). Members of a set
    #: combine with each other, not with the other choices.
    max_returned: int
    #: Use the `meta_data` attribute to control whether query responses include counts. Options
    #: are NoMetaData (default), MetaDataOnly (count only), and MetaDataAndResponseData (count
    #: plus objects). Counts are approximate and may vary slightly if records are created or
    #: deleted during processing.
    meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
    #: The string to match.
    #:
    #: Choose at most one of: `list_id`, or `name`, or the set (`from_modified_date`,
    #: `max_returned`, `name_filter`, `name_range_filter`, `to_modified_date`). Members of a set
    #: combine with each other, not with the other choices.
    name: List[str]
    #: Filters according to the object’s Name.
    #:
    #: Choose at most one of: `list_id`, or `name`, or the set (`from_modified_date`,
    #: `max_returned`, `name_filter`, `name_range_filter`, `to_modified_date`). Members of a set
    #: combine with each other, not with the other choices.
    name_filter: NameFilter
    #: Filters according to the object’s Name.
    #:
    #: Choose at most one of: `list_id`, or `name`, or the set (`from_modified_date`,
    #: `max_returned`, `name_filter`, `name_range_filter`, `to_modified_date`). Members of a set
    #: combine with each other, not with the other choices.
    name_range_filter: NameRangeFilter
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: Filters results to objects modified on or before this timestamp. QuickBooks Desktop
    #: accepts 1970-01-01 through 2038-01-19T03:14:07. If only a date is provided, time defaults
    #: to end-of-day (23:59:59).
    #:
    #: Choose at most one of: `list_id`, or `name`, or the set (`from_modified_date`,
    #: `max_returned`, `name_filter`, `name_range_filter`, `to_modified_date`). Members of a set
    #: combine with each other, not with the other choices.
    to_modified_date: str


class _LeadUpdateParamsRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `full_name` (along with `list_id`) is a way to identify a list object. The `full_name` is
    #: the name prefixed by the names of each ancestor, for example Jones:Kitchen:Cabinets.
    #: `full_name` values aren’t case-sensitive.
    full_name: str
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list family, not across the
    #: company file: customers, vendors, employees and other names share one sequence, every
    #: item type shares another, and each other list has its own.
    list_id: str


class LeadUpdateParams(_LeadUpdateParamsRequired, total=False):
    """Params for ``lead.update`` (Update lead)."""
    additional_contact_ref: List[AdditionalContactRef]
    #: The name of the QuickBooks user’s business, as specified in QuickBooks. `company_name`
    #: and Address are used on invoices, checks, and other forms. (LegalCompanyName and
    #: LegalAddress, on the other hand, are used on a company’s tax forms and pay stubs.)
    company_name: str
    include_ret_element: List[Literal["AdditionalContactRef", "CompanyName", "EditSequence", "ExternalGUID", "FullName", "LeadContactsRet", "ListID", "LocationsRet", "MainPhone", "OwnerID", "Status", "TimeCreated", "TimeModified", "TxnID", "TxnNumber"]]
    lead_contacts_mod: List[LeadContactsMod]
    locations_mod: List[LocationsMod]
    #: The main phone number.
    main_phone: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: The status of the lead.
    status: Literal["Cold", "Hot", "Warm"]


class Lead:
    """QuickBooks lead operations: create, query, update.

    Get it from ``client.lead``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[LeadCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create lead.

        Queues ``lead.create``: POST /connections/{connection_id}/leads, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``LeadCreateParams``)::

            additional_contact_ref: List[AdditionalContactRef]
                contact_name: str (required)
                contact_value: str (required)
            company_name: str
            full_name: str (required)
            include_ret_element: List[Literal[...] (one of 15 values)]
            lead_contacts: List[LeadContacts]
                additional_contact_ref: List[AdditionalContactRef]
                first_name: str (required)
                is_primary_contact: bool
                job_title: str
                last_name: str
                middle_name: str
                salutation: str
            locations: List[Locations]
                lead_address: LeadAddress
                    addr1: str
                    addr2: str
                    addr3: str
                    addr4: str
                    addr5: str
                location: str (required)
            main_phone: str
            request_id: str
            status: Literal["Cold", "Hot", "Warm"]

        Docs: https://docs.qubesync.com/api-reference/v2/leads/create-lead
        """
        return self._client._queue_operation("lead.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[LeadQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List leads.

        Queues ``lead.query``: GET /connections/{connection_id}/leads, params in the query string.
        QuickBooks answers in pages: each page comes to ``webhook_url`` as its own webhook.
        Returns the queued request.

        Params (``LeadQueryParams``)::

            from_modified_date: str
            include_ret_element: List[Literal[...] (one of 11 values)]
            iterator: bool
            list_id: List[str]
            max_returned: int
            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            name: List[str]
            name_filter: NameFilter
                match_criterion: Literal["Contains", "EndsWith", "StartsWith"] (required)
                name: str (required)
            name_range_filter: NameRangeFilter
                from_name: str
                to_name: str
            request_id: str
            to_modified_date: str

        Docs: https://docs.qubesync.com/api-reference/v2/leads/list-leads
        """
        return self._client._queue_operation("lead.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[LeadUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update lead.

        Queues ``lead.update``: PUT /connections/{connection_id}/leads, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``LeadUpdateParams``)::

            additional_contact_ref: List[AdditionalContactRef]
                contact_name: str (required)
                contact_value: str (required)
            company_name: str
            edit_sequence: str (required)
            full_name: str (required)
            include_ret_element: List[Literal[...] (one of 15 values)]
            lead_contacts_mod: List[LeadContactsMod]
                additional_contact_ref: List[AdditionalContactRef]
                first_name: str (required)
                is_primary_contact: bool
                job_title: str
                last_name: str
                lead_contact_id: int
                middle_name: str
                salutation: str
            list_id: str (required)
            locations_mod: List[LocationsMod]
                lead_address: LeadAddress
                    addr1: str
                    addr2: str
                    addr3: str
                    addr4: str
                    addr5: str
                location: str (required)
                location_id: int (required)
            main_phone: str
            request_id: str
            status: Literal["Cold", "Hot", "Warm"]

        Docs: https://docs.qubesync.com/api-reference/v2/leads/update-lead
        """
        return self._client._queue_operation("lead.update", connection_id, params, webhook_url, idempotency_key)
