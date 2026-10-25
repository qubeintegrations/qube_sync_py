# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks workers comp code operations (``client.workers_comp_code``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    NameFilter,
    NameRangeFilter,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _RateEntryRequired(TypedDict):
    #: Specifies the date at which the workers’ comp code and it’s related premium goes into
    #: effect.
    effective_date: str
    #: Indicates the price of something.
    rate: float


class RateEntry(_RateEntryRequired, total=False):
    pass


class _WorkersCompCodeCreateParamsRequired(TypedDict):
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because FullName remains distinct.
    name: str
    rate_entry: List[RateEntry]


class WorkersCompCodeCreateParams(_WorkersCompCodeCreateParamsRequired, total=False):
    """Params for ``workers_comp_code.create`` (Create workers comp code)."""
    #: A descriptive text field.
    desc: str
    include_ret_element: List[Literal["CurrentEffectiveDate", "CurrentRate", "Desc", "EditSequence", "ExternalGUID", "IsActive", "ListID", "Name", "NextEffectiveDate", "NextRate", "OwnerID", "RateHistory", "TimeCreated", "TimeModified", "TxnID", "TxnNumber"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class WorkersCompCodeQueryParams(TypedDict, total=False):
    """Params for ``workers_comp_code.query`` (List workers comp codes)."""
    #: Used in filters to select list objects based on whether or not they are currently enabled
    #: for use by QuickBooks. The default value is asActiveOnly, which selects only list objects
    #: that are active.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_effective_date`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_effective_date`, `to_modified_date`). Members of a set combine
    #: with each other, not with the other choices.
    active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
    #: The beginning of the range of effective dates to be searched.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_effective_date`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_effective_date`, `to_modified_date`). Members of a set combine
    #: with each other, not with the other choices.
    from_effective_date: str
    #: Filters results to objects modified on or after this timestamp. QuickBooks Desktop
    #: accepts 1970-01-01 through 2038-01-19T03:14:07. If only a date is provided, time defaults
    #: to 00:00:00.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_effective_date`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_effective_date`, `to_modified_date`). Members of a set combine
    #: with each other, not with the other choices.
    from_modified_date: str
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_effective_date`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_effective_date`, `to_modified_date`). Members of a set combine
    #: with each other, not with the other choices.
    full_name: List[str]
    include_ret_element: List[Literal["CurrentEffectiveDate", "CurrentRate", "Desc", "EditSequence", "IsActive", "ListID", "Name", "NextEffectiveDate", "NextRate", "RateHistory", "TimeCreated", "TimeModified"]]
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list type, not globally
    #: across all lists. If both `full_name` and `list_id` are supplied in a request, QuickBooks
    #: uses `list_id` and ignores `full_name`.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_effective_date`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_effective_date`, `to_modified_date`). Members of a set combine
    #: with each other, not with the other choices.
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
    #: `from_effective_date`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_effective_date`, `to_modified_date`). Members of a set combine
    #: with each other, not with the other choices.
    max_returned: int
    #: Use the `meta_data` attribute to control whether query responses include counts. Options
    #: are NoMetaData (default), MetaDataOnly (count only), and MetaDataAndResponseData (count
    #: plus objects). Counts are approximate and may vary slightly if records are created or
    #: deleted during processing.
    meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
    #: Filters according to the object’s Name.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_effective_date`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_effective_date`, `to_modified_date`). Members of a set combine
    #: with each other, not with the other choices.
    name_filter: NameFilter
    #: Filters according to the object’s Name.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_effective_date`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_effective_date`, `to_modified_date`). Members of a set combine
    #: with each other, not with the other choices.
    name_range_filter: NameRangeFilter
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: The end of the range of effective dates to be searched.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_effective_date`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_effective_date`, `to_modified_date`). Members of a set combine
    #: with each other, not with the other choices.
    to_effective_date: str
    #: Filters results to objects modified on or before this timestamp. QuickBooks Desktop
    #: accepts 1970-01-01 through 2038-01-19T03:14:07. If only a date is provided, time defaults
    #: to end-of-day (23:59:59).
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_effective_date`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_effective_date`, `to_modified_date`). Members of a set combine
    #: with each other, not with the other choices.
    to_modified_date: str


class _WorkersCompCodeUpdateParamsRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `list_id` and FullName both identify a list object. QuickBooks assigns `list_id` when the
    #: object is created. `list_id` values are unique within a list type, not globally across
    #: all lists. If both FullName and `list_id` are supplied in a request, QuickBooks uses
    #: `list_id` and ignores FullName.
    list_id: str


class WorkersCompCodeUpdateParams(_WorkersCompCodeUpdateParamsRequired, total=False):
    """Params for ``workers_comp_code.update`` (Update workers comp code)."""
    #: A descriptive text field.
    desc: str
    include_ret_element: List[Literal["CurrentEffectiveDate", "CurrentRate", "Desc", "EditSequence", "ExternalGUID", "IsActive", "ListID", "Name", "NextEffectiveDate", "NextRate", "OwnerID", "RateHistory", "TimeCreated", "TimeModified", "TxnID", "TxnNumber"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because FullName remains distinct.
    name: str
    rate_entry: List[RateEntry]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class WorkersCompCode:
    """QuickBooks workers comp code operations: create, query, update.

    Get it from ``client.workers_comp_code``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[WorkersCompCodeCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create workers comp code.

        Queues ``workers_comp_code.create``: POST /connections/{connection_id}/workers-comp-codes, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``WorkersCompCodeCreateParams``)::

            desc: str
            include_ret_element: List[Literal[...] (one of 16 values)]
            is_active: bool
            name: str (required)
            rate_entry: List[RateEntry] (required)
                effective_date: str (required)
                rate: float (required)
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/workers-comp-codes/create-workers-comp-code
        """
        return self._client._queue_operation("workers_comp_code.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[WorkersCompCodeQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List workers comp codes.

        Queues ``workers_comp_code.query``: GET /connections/{connection_id}/workers-comp-codes, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``WorkersCompCodeQueryParams``)::

            active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
            from_effective_date: str
            from_modified_date: str
            full_name: List[str]
            include_ret_element: List[Literal[...] (one of 12 values)]
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
            to_effective_date: str
            to_modified_date: str

        Docs: https://docs.qubesync.com/api-reference/v2/workers-comp-codes/list-workers-comp-codes
        """
        return self._client._queue_operation("workers_comp_code.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[WorkersCompCodeUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update workers comp code.

        Queues ``workers_comp_code.update``: PUT /connections/{connection_id}/workers-comp-codes, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``WorkersCompCodeUpdateParams``)::

            desc: str
            edit_sequence: str (required)
            include_ret_element: List[Literal[...] (one of 16 values)]
            is_active: bool
            list_id: str (required)
            name: str
            rate_entry: List[RateEntry]
                effective_date: str (required)
                rate: float (required)
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/workers-comp-codes/update-workers-comp-code
        """
        return self._client._queue_operation("workers_comp_code.update", connection_id, params, webhook_url, idempotency_key)
