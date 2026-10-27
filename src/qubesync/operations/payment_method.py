# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks payment method operations (``client.payment_method``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    NameFilter,
    NameRangeFilter,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _PaymentMethodCreateParamsRequired(TypedDict):
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because FullName remains distinct.
    name: str


class PaymentMethodCreateParams(_PaymentMethodCreateParamsRequired, total=False):
    """Params for ``payment_method.create`` (Create payment method)."""
    include_ret_element: List[Literal["EditSequence", "ExternalGUID", "IsActive", "ListID", "Name", "OwnerID", "PaymentMethodType", "TimeCreated", "TimeModified", "TxnID", "TxnNumber"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: The payment method, such as check, cash, debit card, Visa, etc.
    payment_method_type: Literal["AmericanExpress", "Cash", "Check", "DebitCard", "Discover", "ECheck", "GiftCard", "MasterCard", "Other", "OtherCreditCard", "Visa"]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class PaymentMethodQueryParams(TypedDict, total=False):
    """Params for ``payment_method.query`` (List payment methods)."""
    #: Used in filters to select list objects based on whether or not they are currently enabled
    #: for use by QuickBooks. The default value is asActiveOnly, which selects only list objects
    #: that are active.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `payment_method_type`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
    #: Filters results to objects modified on or after this timestamp. QuickBooks Desktop
    #: accepts 1970-01-01 through 2038-01-19T03:14:07. If only a date is provided, time defaults
    #: to 00:00:00.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `payment_method_type`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    from_modified_date: str
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `payment_method_type`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    full_name: List[str]
    include_ret_element: List[Literal["EditSequence", "IsActive", "ListID", "Name", "PaymentMethodType", "TimeCreated", "TimeModified"]]
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list family, not across the
    #: company file: customers, vendors, employees and other names share one sequence, every
    #: item type shares another, and each other list has its own.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `payment_method_type`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
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
    #: `payment_method_type`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
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
    #: `payment_method_type`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    name_filter: NameFilter
    #: Filters according to the object’s Name.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `payment_method_type`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    name_range_filter: NameRangeFilter
    #: The payment method, such as check, cash, debit card, Visa, etc.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `payment_method_type`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    payment_method_type: List[Literal["AmericanExpress", "Cash", "Check", "DebitCard", "Discover", "ECheck", "GiftCard", "MasterCard", "Other", "OtherCreditCard", "Visa"]]
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
    #: `payment_method_type`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    to_modified_date: str


class PaymentMethod:
    """QuickBooks payment method operations: create, query.

    Get it from ``client.payment_method``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[PaymentMethodCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create payment method.

        Queues ``payment_method.create``: POST /connections/{connection_id}/payment-methods, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``PaymentMethodCreateParams``)::

            include_ret_element: List[Literal[...] (one of 11 values)]
            is_active: bool
            name: str (required)
            payment_method_type: Literal[...] (one of 11 values)
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/payment-methods/create-payment-method
        """
        return self._client._queue_operation("payment_method.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[PaymentMethodQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List payment methods.

        Queues ``payment_method.query``: GET /connections/{connection_id}/payment-methods, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``PaymentMethodQueryParams``)::

            active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
            from_modified_date: str
            full_name: List[str]
            include_ret_element: List[Literal[...] (one of 7 values)]
            list_id: List[str]
            max_returned: int
            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            name_filter: NameFilter
                match_criterion: Literal["Contains", "EndsWith", "StartsWith"] (required)
                name: str (required)
            name_range_filter: NameRangeFilter
                from_name: str
                to_name: str
            payment_method_type: List[Literal[...] (one of 11 values)]
            request_id: str
            to_modified_date: str

        Docs: https://docs.qubesync.com/api-reference/v2/payment-methods/list-payment-methods
        """
        return self._client._queue_operation("payment_method.query", connection_id, params, webhook_url, idempotency_key)
