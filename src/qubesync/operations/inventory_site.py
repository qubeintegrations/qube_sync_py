# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks inventory site operations (``client.inventory_site``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    NameFilter,
    NameRangeFilter,
    Ref,
)

if TYPE_CHECKING:
    from ..v2 import Client


class SiteAddress(TypedDict, total=False):
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
    #: The postal code in an address.
    postal_code: str
    #: The state name in an address.
    state: str


class _InventorySiteCreateParamsRequired(TypedDict):
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because `full_name` remains distinct.
    name: str


class InventorySiteCreateParams(_InventorySiteCreateParamsRequired, total=False):
    """Params for ``inventory_site.create`` (Create inventory site)."""
    #: The name of a contact person for a customer or vendor.
    contact: str
    #: E-mail address.
    email: str
    #: Fax number.
    fax: str
    include_ret_element: List[Literal["Contact", "EditSequence", "Email", "ExternalGUID", "Fax", "IsActive", "IsDefaultSite", "ListID", "Name", "OwnerID", "ParentSiteRef", "Phone", "SiteAddress", "SiteAddressBlock", "SiteDesc", "TimeCreated", "TimeModified", "TxnID", "TxnNumber"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: A reference to the list object that is one level above this one. For example, an
    #: inventory item with the `full_name` of GermanCars:Mercedes-Benz:CL500I99AA might have a
    #: parent object with the `full_name` of GermanCars:Mercedes-Benz. In a request, if a
    #: ParentRef aggregate includes both `full_name` and `list_id`, `full_name` will be ignored.
    parent_site_ref: Ref
    #: The telephone number.
    phone: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: This aggregate supports at most five address lines. You can provide a structured address
    #: (Addr1-Addr3 plus City/State/`postal_code`/etc.) or use block mode (Addr1-Addr5 only). Do
    #: not mix block mode with other address fields. In block mode, each Addr line prints as its
    #: own line and is returned in ShipAddressBlock or BillAddressBlock.
    site_address: SiteAddress
    #: Description of the site.
    site_desc: str


class InventorySiteQueryParams(TypedDict, total=False):
    """Params for ``inventory_site.query`` (List inventory sites)."""
    #: Used in filters to select list objects based on whether or not they are currently enabled
    #: for use by QuickBooks. The default value is asActiveOnly, which selects only list objects
    #: that are active.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `name_filter`, `name_range_filter`, `to_modified_date`). Members of
    #: a set combine with each other, not with the other choices.
    active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
    #: Filters results to objects modified on or after this timestamp. QuickBooks Desktop
    #: accepts 1970-01-01 through 2038-01-19T03:14:07. If only a date is provided, time defaults
    #: to 00:00:00.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `name_filter`, `name_range_filter`, `to_modified_date`). Members of
    #: a set combine with each other, not with the other choices.
    from_modified_date: str
    #: `full_name` (along with `list_id`) is a way to identify a list object. The `full_name` is
    #: the name prefixed by the names of each ancestor, for example Jones:Kitchen:Cabinets.
    #: `full_name` values aren’t case-sensitive.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `name_filter`, `name_range_filter`, `to_modified_date`). Members of
    #: a set combine with each other, not with the other choices.
    full_name: List[str]
    include_ret_element: List[Literal["Contact", "EditSequence", "Email", "Fax", "IsActive", "IsDefaultSite", "ListID", "Name", "ParentSiteRef", "Phone", "SiteAddress", "SiteAddressBlock", "SiteDesc", "TimeCreated", "TimeModified"]]
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list family, not across the
    #: company file: customers, vendors, employees and other names share one sequence, every
    #: item type shares another, and each other list has its own.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `name_filter`, `name_range_filter`, `to_modified_date`). Members of
    #: a set combine with each other, not with the other choices.
    list_id: List[str]
    #: Use the `meta_data` attribute to control whether query responses include counts. Options
    #: are NoMetaData (default), MetaDataOnly (count only), and MetaDataAndResponseData (count
    #: plus objects). Counts are approximate and may vary slightly if records are created or
    #: deleted during processing.
    meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
    #: Filters according to the object’s Name.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `name_filter`, `name_range_filter`, `to_modified_date`). Members of
    #: a set combine with each other, not with the other choices.
    name_filter: NameFilter
    #: Filters according to the object’s Name.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `name_filter`, `name_range_filter`, `to_modified_date`). Members of
    #: a set combine with each other, not with the other choices.
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
    #: `from_modified_date`, `name_filter`, `name_range_filter`, `to_modified_date`). Members of
    #: a set combine with each other, not with the other choices.
    to_modified_date: str


class _InventorySiteUpdateParamsRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list family, not across the
    #: company file: customers, vendors, employees and other names share one sequence, every
    #: item type shares another, and each other list has its own.
    list_id: str


class InventorySiteUpdateParams(_InventorySiteUpdateParamsRequired, total=False):
    """Params for ``inventory_site.update`` (Update inventory site)."""
    #: The name of a contact person for a customer or vendor.
    contact: str
    #: E-mail address.
    email: str
    #: Fax number.
    fax: str
    include_ret_element: List[Literal["Contact", "EditSequence", "Email", "ExternalGUID", "Fax", "IsActive", "IsDefaultSite", "ListID", "Name", "OwnerID", "ParentSiteRef", "Phone", "SiteAddress", "SiteAddressBlock", "SiteDesc", "TimeCreated", "TimeModified", "TxnID", "TxnNumber"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because `full_name` remains distinct.
    name: str
    #: A reference to the list object that is one level above this one. For example, an
    #: inventory item with the `full_name` of GermanCars:Mercedes-Benz:CL500I99AA might have a
    #: parent object with the `full_name` of GermanCars:Mercedes-Benz. In a request, if a
    #: ParentRef aggregate includes both `full_name` and `list_id`, `full_name` will be ignored.
    parent_site_ref: Ref
    #: The telephone number.
    phone: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: This aggregate supports at most five address lines. You can provide a structured address
    #: (Addr1-Addr3 plus City/State/`postal_code`/etc.) or use block mode (Addr1-Addr5 only). Do
    #: not mix block mode with other address fields. In block mode, each Addr line prints as its
    #: own line and is returned in ShipAddressBlock or BillAddressBlock.
    site_address: SiteAddress
    #: Description of the site.
    site_desc: str


class InventorySite:
    """QuickBooks inventory site operations: create, query, update.

    Get it from ``client.inventory_site``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[InventorySiteCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create inventory site.

        Queues ``inventory_site.create``: POST /connections/{connection_id}/inventory-sites, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``InventorySiteCreateParams``)::

            contact: str
            email: str
            fax: str
            include_ret_element: List[Literal[...] (one of 19 values)]
            is_active: bool
            name: str (required)
            parent_site_ref: Ref
                full_name: str
                list_id: str
            phone: str
            request_id: str
            site_address: SiteAddress
                addr1: str
                addr2: str
                addr3: str
                addr4: str
                addr5: str
                city: str
                country: str
                postal_code: str
                state: str
            site_desc: str

        Docs: https://docs.qubesync.com/api-reference/v2/inventory-sites/create-inventory-site
        """
        return self._client._queue_operation("inventory_site.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[InventorySiteQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List inventory sites.

        Queues ``inventory_site.query``: GET /connections/{connection_id}/inventory-sites, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``InventorySiteQueryParams``)::

            active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
            from_modified_date: str
            full_name: List[str]
            include_ret_element: List[Literal[...] (one of 15 values)]
            list_id: List[str]
            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            name_filter: NameFilter
                match_criterion: Literal["Contains", "EndsWith", "StartsWith"] (required)
                name: str (required)
            name_range_filter: NameRangeFilter
                from_name: str
                to_name: str
            request_id: str
            to_modified_date: str

        Docs: https://docs.qubesync.com/api-reference/v2/inventory-sites/list-inventory-sites
        """
        return self._client._queue_operation("inventory_site.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[InventorySiteUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update inventory site.

        Queues ``inventory_site.update``: PUT /connections/{connection_id}/inventory-sites, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``InventorySiteUpdateParams``)::

            contact: str
            edit_sequence: str (required)
            email: str
            fax: str
            include_ret_element: List[Literal[...] (one of 19 values)]
            is_active: bool
            list_id: str (required)
            name: str
            parent_site_ref: Ref
                full_name: str
                list_id: str
            phone: str
            request_id: str
            site_address: SiteAddress
                addr1: str
                addr2: str
                addr3: str
                addr4: str
                addr5: str
                city: str
                country: str
                postal_code: str
                state: str
            site_desc: str

        Docs: https://docs.qubesync.com/api-reference/v2/inventory-sites/update-inventory-site
        """
        return self._client._queue_operation("inventory_site.update", connection_id, params, webhook_url, idempotency_key)
