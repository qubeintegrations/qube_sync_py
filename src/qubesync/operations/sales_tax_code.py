# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks sales tax code operations (``client.sales_tax_code``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    NameFilter,
    NameRangeFilter,
    Ref,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _SalesTaxCodeCreateParamsRequired(TypedDict):
    #: Indicates whether this sales-tax code is tracking taxable sales. For any particular
    #: sales-tax code, `is_taxable` can’t be modified once the sales-tax code has been used in a
    #: transaction. If the “Do You Charge Sales Tax?” preference is set to Yes within
    #: QuickBooks, the default value of `is_taxable` is true.
    is_taxable: bool
    #: Short name that will appear on sales forms to identify the tax status of an item. The
    #: Desc element gives a longer explanation of Name. Name must be unique, and it isn’t
    #: case-sensitive.
    name: str


class SalesTaxCodeCreateParams(_SalesTaxCodeCreateParamsRequired, total=False):
    """Params for ``sales_tax_code.create`` (Create sales tax code)."""
    #: Desc gives a longer explanation of Name.
    desc: str
    include_ret_element: List[Literal["Desc", "EditSequence", "ExternalGUID", "IsActive", "IsTaxable", "ItemPurchaseTaxRef", "ItemSalesTaxRef", "ListID", "Name", "OwnerID", "TimeCreated", "TimeModified", "TxnID", "TxnNumber"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: For future use with international versions of QuickBooks.
    item_purchase_tax_ref: Ref
    #: An ItemSalesTax entry represents one tax rate paid to one tax agency. Use it when a
    #: transaction needs a single tax calculation. For multi-rate scenarios, use a sales-tax
    #: group instead. If both `full_name` and `list_id` are provided for `item_sales_tax_ref`,
    #: `list_id` is used.
    item_sales_tax_ref: Ref
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class SalesTaxCodeQueryParams(TypedDict, total=False):
    """Params for ``sales_tax_code.query`` (List sales tax codes)."""
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
    include_ret_element: List[Literal["Desc", "EditSequence", "IsActive", "IsTaxable", "ItemPurchaseTaxRef", "ItemSalesTaxRef", "ListID", "Name", "TimeCreated", "TimeModified"]]
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


class _SalesTaxCodeUpdateParamsRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list family, not across the
    #: company file: customers, vendors, employees and other names share one sequence, every
    #: item type shares another, and each other list has its own.
    list_id: str


class SalesTaxCodeUpdateParams(_SalesTaxCodeUpdateParamsRequired, total=False):
    """Params for ``sales_tax_code.update`` (Update sales tax code)."""
    #: Desc gives a longer explanation of Name.
    desc: str
    include_ret_element: List[Literal["Desc", "EditSequence", "ExternalGUID", "IsActive", "IsTaxable", "ItemPurchaseTaxRef", "ItemSalesTaxRef", "ListID", "Name", "OwnerID", "TimeCreated", "TimeModified", "TxnID", "TxnNumber"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: Indicates whether this sales-tax code is tracking taxable sales. For any particular
    #: sales-tax code, `is_taxable` can’t be modified once the sales-tax code has been used in a
    #: transaction. If the “Do You Charge Sales Tax?” preference is set to Yes within
    #: QuickBooks, the default value of `is_taxable` is true.
    is_taxable: bool
    #: For future use with international versions of QuickBooks.
    item_purchase_tax_ref: Ref
    #: An ItemSalesTax entry represents one tax rate paid to one tax agency. Use it when a
    #: transaction needs a single tax calculation. For multi-rate scenarios, use a sales-tax
    #: group instead. If both `full_name` and `list_id` are provided for `item_sales_tax_ref`,
    #: `list_id` is used.
    item_sales_tax_ref: Ref
    #: Short name that will appear on sales forms to identify the tax status of an item. The
    #: Desc element gives a longer explanation of Name. Name must be unique, and it isn’t
    #: case-sensitive.
    name: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class SalesTaxCode:
    """QuickBooks sales tax code operations: create, query, update.

    Get it from ``client.sales_tax_code``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[SalesTaxCodeCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create sales tax code.

        Queues ``sales_tax_code.create``: POST /connections/{connection_id}/sales-tax-codes, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``SalesTaxCodeCreateParams``)::

            desc: str
            include_ret_element: List[Literal[...] (one of 14 values)]
            is_active: bool
            is_taxable: bool (required)
            item_purchase_tax_ref: Ref
                full_name: str
                list_id: str
            item_sales_tax_ref: Ref
            name: str (required)
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/sales-tax-codes/create-sales-tax-code
        """
        return self._client._queue_operation("sales_tax_code.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[SalesTaxCodeQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List sales tax codes.

        Queues ``sales_tax_code.query``: GET /connections/{connection_id}/sales-tax-codes, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``SalesTaxCodeQueryParams``)::

            active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
            from_modified_date: str
            full_name: List[str]
            include_ret_element: List[Literal[...] (one of 10 values)]
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

        Docs: https://docs.qubesync.com/api-reference/v2/sales-tax-codes/list-sales-tax-codes
        """
        return self._client._queue_operation("sales_tax_code.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[SalesTaxCodeUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update sales tax code.

        Queues ``sales_tax_code.update``: PUT /connections/{connection_id}/sales-tax-codes, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``SalesTaxCodeUpdateParams``)::

            desc: str
            edit_sequence: str (required)
            include_ret_element: List[Literal[...] (one of 14 values)]
            is_active: bool
            is_taxable: bool
            item_purchase_tax_ref: Ref
                full_name: str
                list_id: str
            item_sales_tax_ref: Ref
            list_id: str (required)
            name: str
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/sales-tax-codes/update-sales-tax-code
        """
        return self._client._queue_operation("sales_tax_code.update", connection_id, params, webhook_url, idempotency_key)
