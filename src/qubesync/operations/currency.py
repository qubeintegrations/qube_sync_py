# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks currency operations (``client.currency``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    NameFilter,
    NameRangeFilter,
)

if TYPE_CHECKING:
    from ..v2 import Client


class CurrencyFormat(TypedDict, total=False):
    #: This enumerated value controls the display of the decimal value, for example, 1.00. The
    #: default is 2 which means 2 decimals are displayed to the right of the decimal point, but
    #: you can specify 0 (zero) if you don’t want’ decimals to be displayed.
    decimal_places: Literal["0", "2"]
    #: This enumerated value controls the display of the decimal point, for example, 1.00 or
    #: 1,00. The default is Period but you could alternatively specify a value of Comma.
    decimal_separator: Literal["Comma", "Period"]
    #: This enumerated value controls how the thousandth’s place is separated from the next
    #: thousand, for example, 1,000,000. The default is Comma, as shown, but you can replace
    #: this with one of these values: Period, Space, Apostrophe .
    thousand_separator: Literal["Apostrophe", "Comma", "Period", "Space"]
    #: This enumerated value controls how the display of the currency value is grouped, for
    #: example, 10,000,000. The default is XX_XXX_XXX but you could replace this with
    #: X_XX_XX_XXX
    thousand_separator_grouping: Literal["XX_XXX_XXX", "X_XX_XX_XXX"]


class _CurrencyCreateParamsRequired(TypedDict):
    #: For built-in currencies, the currency code and name is the generally accepted code and
    #: name. These are based on the standard ISO 4217 code/name for a country’s currency. In
    #: most cases, the currency code is composed of the country’s two-character Internet country
    #: code plus an extra character representing the currency unit.
    currency_code: str
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because FullName remains distinct.
    name: str


class CurrencyCreateParams(_CurrencyCreateParamsRequired, total=False):
    """Params for ``currency.create`` (Create currency)."""
    #: The aggregate controlling the appearance of the currency with regard to comma and
    #: decimal.
    currency_format: CurrencyFormat
    include_ret_element: List[Literal["AsOfDate", "CurrencyCode", "CurrencyFormat", "EditSequence", "ExchangeRate", "ExternalGUID", "IsActive", "IsUserDefinedCurrency", "ListID", "Name", "OwnerID", "TimeCreated", "TimeModified", "TxnID", "TxnNumber"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class CurrencyQueryParams(TypedDict, total=False):
    """Params for ``currency.query`` (List currencies)."""
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
    include_ret_element: List[Literal["AsOfDate", "CurrencyCode", "CurrencyFormat", "EditSequence", "ExchangeRate", "IsActive", "IsUserDefinedCurrency", "ListID", "Name", "TimeCreated", "TimeModified"]]
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


class _CurrencyUpdateParamsRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `list_id` and FullName both identify a list object. QuickBooks assigns `list_id` when the
    #: object is created. `list_id` values are unique within a list family, not across the
    #: company file: customers, vendors, employees and other names share one sequence, every
    #: item type shares another, and each other list has its own.
    list_id: str


class CurrencyUpdateParams(_CurrencyUpdateParamsRequired, total=False):
    """Params for ``currency.update`` (Update currency)."""
    #: For built-in currencies, the currency code and name is the generally accepted code and
    #: name. These are based on the standard ISO 4217 code/name for a country’s currency. In
    #: most cases, the currency code is composed of the country’s two-character Internet country
    #: code plus an extra character representing the currency unit.
    currency_code: str
    #: The aggregate controlling the appearance of the currency with regard to comma and
    #: decimal.
    currency_format: CurrencyFormat
    include_ret_element: List[Literal["AsOfDate", "CurrencyCode", "CurrencyFormat", "EditSequence", "ExchangeRate", "ExternalGUID", "IsActive", "IsUserDefinedCurrency", "ListID", "Name", "OwnerID", "TimeCreated", "TimeModified", "TxnID", "TxnNumber"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because FullName remains distinct.
    name: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class Currency:
    """QuickBooks currency operations: create, query, update.

    Get it from ``client.currency``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[CurrencyCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create currency.

        Queues ``currency.create``: POST /connections/{connection_id}/currencies, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``CurrencyCreateParams``)::

            currency_code: str (required)
            currency_format: CurrencyFormat
                decimal_places: Literal["0", "2"]
                decimal_separator: Literal["Comma", "Period"]
                thousand_separator: Literal["Apostrophe", "Comma", "Period", "Space"]
                thousand_separator_grouping: Literal["XX_XXX_XXX", "X_XX_XX_XXX"]
            include_ret_element: List[Literal[...] (one of 15 values)]
            is_active: bool
            name: str (required)
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/currencies/create-currency
        """
        return self._client._queue_operation("currency.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[CurrencyQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List currencies.

        Queues ``currency.query``: GET /connections/{connection_id}/currencies, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``CurrencyQueryParams``)::

            active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
            from_modified_date: str
            full_name: List[str]
            include_ret_element: List[Literal[...] (one of 11 values)]
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

        Docs: https://docs.qubesync.com/api-reference/v2/currencies/list-currencies
        """
        return self._client._queue_operation("currency.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[CurrencyUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update currency.

        Queues ``currency.update``: PUT /connections/{connection_id}/currencies, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``CurrencyUpdateParams``)::

            currency_code: str
            currency_format: CurrencyFormat
                decimal_places: Literal["0", "2"]
                decimal_separator: Literal["Comma", "Period"]
                thousand_separator: Literal["Apostrophe", "Comma", "Period", "Space"]
                thousand_separator_grouping: Literal["XX_XXX_XXX", "X_XX_XX_XXX"]
            edit_sequence: str (required)
            include_ret_element: List[Literal[...] (one of 15 values)]
            is_active: bool
            list_id: str (required)
            name: str
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/currencies/update-currency
        """
        return self._client._queue_operation("currency.update", connection_id, params, webhook_url, idempotency_key)
