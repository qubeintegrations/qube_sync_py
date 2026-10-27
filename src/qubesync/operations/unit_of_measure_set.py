# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks unit of measure set operations (``client.unit_of_measure_set``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    NameFilter,
    NameRangeFilter,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _BaseUnitRequired(TypedDict):
    #: The is the short “identifier” for a unit of measure that shows up in transaction line
    #: items in the U/M field in the QuickBooks UI.
    abbreviation: str
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because FullName remains distinct.
    name: str


class BaseUnit(_BaseUnitRequired, total=False):
    pass


class _DefaultUnitRequired(TypedDict):
    #: In a related unit within a unit of measure set, the name you want the unit to have. This
    #: name is displayed in the QuickBooks as an available unit for the item, if the company is
    #: enabled for multiple units of measure per item.
    unit: str
    #: In a default unit of measure, this specifies whether the default is to be used for
    #: purchase line items, sales line items, or shipping lines.
    unit_used_for: Literal["Purchase", "Sales", "Shipping"]


class DefaultUnit(_DefaultUnitRequired, total=False):
    pass


class _RelatedUnitRequired(TypedDict):
    #: The is the short “identifier” for a unit of measure that shows up in transaction line
    #: items in the U/M field in the QuickBooks UI.
    abbreviation: str
    #: Within a unit of measure set, in any of the related units in that set, this indicates how
    #: many base units are in the related unit. That is, if the base unit is “box”, and the
    #: related unit is “case” with a conversion ratio of 10, that means there are 10 boxes in a
    #: case.
    conversion_ratio: float
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because FullName remains distinct.
    name: str


class RelatedUnit(_RelatedUnitRequired, total=False):
    pass


class _UnitOfMeasureSetCreateParamsRequired(TypedDict):
    #: The unit of measure in a unit of measure set by which quantities of an item are tracked,
    #: priced, etc. If the company file is enabled for single unit of measure per item, the base
    #: unit is the only unit that is available for transaction line items.
    base_unit: BaseUnit
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because FullName remains distinct.
    name: str
    #: The type of the unit of measure. This can be one of the values you see in the QuickBooks
    #: UI when you create a new UOM set, such as Count, or it can be your own value, which in
    #: the UI you can specify by selecting “Other” then defining it.
    unit_of_measure_type: Literal["Area", "Count", "Length", "Other", "Time", "Volume", "Weight"]


class UnitOfMeasureSetCreateParams(_UnitOfMeasureSetCreateParamsRequired, total=False):
    """Params for ``unit_of_measure_set.create`` (Create unit of measure set)."""
    default_unit: List[DefaultUnit]
    include_ret_element: List[Literal["BaseUnit", "DefaultUnit", "EditSequence", "ExternalGUID", "IsActive", "ListID", "Name", "OwnerID", "RelatedUnit", "TimeCreated", "TimeModified", "TxnID", "TxnNumber", "UnitOfMeasureType"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    related_unit: List[RelatedUnit]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class UnitOfMeasureSetQueryParams(TypedDict, total=False):
    """Params for ``unit_of_measure_set.query`` (List unit of measure sets)."""
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
    include_ret_element: List[Literal["BaseUnit", "DefaultUnit", "EditSequence", "IsActive", "ListID", "Name", "RelatedUnit", "TimeCreated", "TimeModified", "UnitOfMeasureType"]]
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


class UnitOfMeasureSet:
    """QuickBooks unit of measure set operations: create, query.

    Get it from ``client.unit_of_measure_set``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[UnitOfMeasureSetCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create unit of measure set.

        Queues ``unit_of_measure_set.create``: POST /connections/{connection_id}/unit-of-measure-sets, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``UnitOfMeasureSetCreateParams``)::

            base_unit: BaseUnit (required)
                abbreviation: str (required)
                name: str (required)
            default_unit: List[DefaultUnit]
                unit: str (required)
                unit_used_for: Literal["Purchase", "Sales", "Shipping"] (required)
            include_ret_element: List[Literal[...] (one of 14 values)]
            is_active: bool
            name: str (required)
            related_unit: List[RelatedUnit]
                abbreviation: str (required)
                conversion_ratio: float (required)
                name: str (required)
            request_id: str
            unit_of_measure_type: Literal[...] (one of 7 values) (required)

        Docs: https://docs.qubesync.com/api-reference/v2/unit-of-measure-sets/create-unit-of-measure-set
        """
        return self._client._queue_operation("unit_of_measure_set.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[UnitOfMeasureSetQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List unit of measure sets.

        Queues ``unit_of_measure_set.query``: GET /connections/{connection_id}/unit-of-measure-sets, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``UnitOfMeasureSetQueryParams``)::

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

        Docs: https://docs.qubesync.com/api-reference/v2/unit-of-measure-sets/list-unit-of-measure-sets
        """
        return self._client._queue_operation("unit_of_measure_set.query", connection_id, params, webhook_url, idempotency_key)
