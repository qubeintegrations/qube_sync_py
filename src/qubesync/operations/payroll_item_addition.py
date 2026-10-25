# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks payroll item addition operations (``client.payroll_item_addition``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    Ref,
    Taxability,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _PayrollItemAdditionCreateParamsRequired(TypedDict):
    expense_account_ref: Ref
    name: str


class PayrollItemAdditionCreateParams(_PayrollItemAdditionCreateParamsRequired, total=False):
    """Params for ``payroll_item_addition.create`` (Create payroll item addition)."""
    calculated_based_on: Literal["HoursAll", "HoursWorked", "Quantity", "Rate"]
    include_ret_element: List[Literal["CalculatedBasedOn", "EditSequence", "ExpenseAccountRef", "IsActive", "IsTrackedByCustJob", "Limit", "LimitTimePeriod", "ListID", "Name", "NetOrGross", "PayrollItemDetailTypeValue", "Rate", "RatePercent", "Taxability", "TimeCreated", "TimeModified", "W2TrackingTypeValue"]]
    is_active: bool
    is_tracked_by_cust_job: bool
    limit: float
    limit_time_period: Literal["Annual", "Forever"]
    net_or_gross: Literal["Gross", "Net"]
    payroll_item_detail_type_value: int
    #: Choose at most one of: `rate`, or `rate_percent`.
    rate: float
    #: Choose at most one of: `rate`, or `rate_percent`.
    rate_percent: float
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    taxability: List[Taxability]
    w2_tracking_type_value: int


class _PayrollItemAdditionUpdateParamsRequired(TypedDict):
    edit_sequence: str
    list_id: str


class PayrollItemAdditionUpdateParams(_PayrollItemAdditionUpdateParamsRequired, total=False):
    """Params for ``payroll_item_addition.update`` (Update payroll item addition)."""
    calculated_based_on: Literal["HoursAll", "HoursWorked", "Quantity", "Rate"]
    expense_account_ref: Ref
    include_ret_element: List[Literal["CalculatedBasedOn", "EditSequence", "ExpenseAccountRef", "IsActive", "IsTrackedByCustJob", "Limit", "LimitTimePeriod", "ListID", "Name", "NetOrGross", "PayrollItemDetailTypeValue", "Rate", "RatePercent", "Taxability", "TimeCreated", "TimeModified", "W2TrackingTypeValue"]]
    is_active: bool
    is_tracked_by_cust_job: bool
    limit: float
    limit_time_period: Literal["Annual", "Forever"]
    name: str
    net_or_gross: Literal["Gross", "Net"]
    payroll_item_detail_type_value: int
    #: Choose at most one of: `rate`, or `rate_percent`.
    rate: float
    #: Choose at most one of: `rate`, or `rate_percent`.
    rate_percent: float
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    taxability: List[Taxability]
    w2_tracking_type_value: int


class PayrollItemAddition:
    """QuickBooks payroll item addition operations: create, update.

    Get it from ``client.payroll_item_addition``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[PayrollItemAdditionCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create payroll item addition.

        Queues ``payroll_item_addition.create``: POST /connections/{connection_id}/payroll-item-additions, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``PayrollItemAdditionCreateParams``)::

            calculated_based_on: Literal["HoursAll", "HoursWorked", "Quantity", "Rate"]
            expense_account_ref: Ref (required)
                full_name: str
                list_id: str
            include_ret_element: List[Literal[...] (one of 17 values)]
            is_active: bool
            is_tracked_by_cust_job: bool
            limit: float
            limit_time_period: Literal["Annual", "Forever"]
            name: str (required)
            net_or_gross: Literal["Gross", "Net"]
            payroll_item_detail_type_value: int
            rate: float
            rate_percent: float
            request_id: str
            taxability: List[Taxability]
                is_tax_applied: bool (required)
                payroll_item_tax_ref: Ref (required)
            w2_tracking_type_value: int

        Docs: https://docs.qubesync.com/api-reference/v2/payroll-item-additions/create-payroll-item-addition
        """
        return self._client._queue_operation("payroll_item_addition.create", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[PayrollItemAdditionUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update payroll item addition.

        Queues ``payroll_item_addition.update``: PUT /connections/{connection_id}/payroll-item-additions, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``PayrollItemAdditionUpdateParams``)::

            calculated_based_on: Literal["HoursAll", "HoursWorked", "Quantity", "Rate"]
            edit_sequence: str (required)
            expense_account_ref: Ref
                full_name: str
                list_id: str
            include_ret_element: List[Literal[...] (one of 17 values)]
            is_active: bool
            is_tracked_by_cust_job: bool
            limit: float
            limit_time_period: Literal["Annual", "Forever"]
            list_id: str (required)
            name: str
            net_or_gross: Literal["Gross", "Net"]
            payroll_item_detail_type_value: int
            rate: float
            rate_percent: float
            request_id: str
            taxability: List[Taxability]
                is_tax_applied: bool (required)
                payroll_item_tax_ref: Ref (required)
            w2_tracking_type_value: int

        Docs: https://docs.qubesync.com/api-reference/v2/payroll-item-additions/update-payroll-item-addition
        """
        return self._client._queue_operation("payroll_item_addition.update", connection_id, params, webhook_url, idempotency_key)
