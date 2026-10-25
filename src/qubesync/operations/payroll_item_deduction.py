# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks payroll item deduction operations (``client.payroll_item_deduction``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    LiabilityPaymentSchedule,
    Ref,
    Taxability,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _PayrollItemDeductionCreateParamsRequired(TypedDict):
    liability_account_ref: Ref
    name: str
    payment_template_ref: Ref


class PayrollItemDeductionCreateParams(_PayrollItemDeductionCreateParamsRequired, total=False):
    """Params for ``payroll_item_deduction.create`` (Create payroll item deduction)."""
    calculated_based_on: Literal["HoursAll", "HoursWorked", "Quantity", "Rate"]
    include_ret_element: List[Literal["CalculatedBasedOn", "EditSequence", "IsActive", "LiabilityAccountRef", "LiabilityPaymentSchedule", "Limit", "LimitTimePeriod", "ListID", "Name", "NetOrGross", "PaymentTemplateRef", "PayrollItemDetailTypeValue", "Rate", "RatePercent", "Taxability", "TimeCreated", "TimeModified", "VendorAccountNumber", "VendorRef", "W2TrackingTypeValue"]]
    is_active: bool
    liability_payment_schedule: LiabilityPaymentSchedule
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
    vendor_account_number: str
    vendor_ref: Ref
    w2_tracking_type_value: int


class _PayrollItemDeductionUpdateParamsRequired(TypedDict):
    edit_sequence: str
    list_id: str


class PayrollItemDeductionUpdateParams(_PayrollItemDeductionUpdateParamsRequired, total=False):
    """Params for ``payroll_item_deduction.update`` (Update payroll item deduction)."""
    calculated_based_on: Literal["HoursAll", "HoursWorked", "Quantity", "Rate"]
    include_ret_element: List[Literal["CalculatedBasedOn", "EditSequence", "IsActive", "LiabilityAccountRef", "LiabilityPaymentSchedule", "Limit", "LimitTimePeriod", "ListID", "Name", "NetOrGross", "PaymentTemplateRef", "PayrollItemDetailTypeValue", "Rate", "RatePercent", "Taxability", "TimeCreated", "TimeModified", "VendorAccountNumber", "VendorRef", "W2TrackingTypeValue"]]
    is_active: bool
    liability_account_ref: Ref
    liability_payment_schedule: LiabilityPaymentSchedule
    limit: float
    limit_time_period: Literal["Annual", "Forever"]
    name: str
    net_or_gross: Literal["Gross", "Net"]
    payment_template_ref: Ref
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
    vendor_account_number: str
    vendor_ref: Ref
    w2_tracking_type_value: int


class PayrollItemDeduction:
    """QuickBooks payroll item deduction operations: create, update.

    Get it from ``client.payroll_item_deduction``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[PayrollItemDeductionCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create payroll item deduction.

        Queues ``payroll_item_deduction.create``: POST /connections/{connection_id}/payroll-item-deductions, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``PayrollItemDeductionCreateParams``)::

            calculated_based_on: Literal["HoursAll", "HoursWorked", "Quantity", "Rate"]
            include_ret_element: List[Literal[...] (one of 20 values)]
            is_active: bool
            liability_account_ref: Ref (required)
                full_name: str
                list_id: str
            liability_payment_schedule: LiabilityPaymentSchedule
                payment_due_date: str
                payment_due_num_days_after: int
                payment_schedule_type: Literal[...] (one of 10 values) (required)
            limit: float
            limit_time_period: Literal["Annual", "Forever"]
            name: str (required)
            net_or_gross: Literal["Gross", "Net"]
            payment_template_ref: Ref (required)
            payroll_item_detail_type_value: int
            rate: float
            rate_percent: float
            request_id: str
            taxability: List[Taxability]
                is_tax_applied: bool (required)
                payroll_item_tax_ref: Ref (required)
            vendor_account_number: str
            vendor_ref: Ref
            w2_tracking_type_value: int

        Docs: https://docs.qubesync.com/api-reference/v2/payroll-item-deductions/create-payroll-item-deduction
        """
        return self._client._queue_operation("payroll_item_deduction.create", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[PayrollItemDeductionUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update payroll item deduction.

        Queues ``payroll_item_deduction.update``: PUT /connections/{connection_id}/payroll-item-deductions, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``PayrollItemDeductionUpdateParams``)::

            calculated_based_on: Literal["HoursAll", "HoursWorked", "Quantity", "Rate"]
            edit_sequence: str (required)
            include_ret_element: List[Literal[...] (one of 20 values)]
            is_active: bool
            liability_account_ref: Ref
                full_name: str
                list_id: str
            liability_payment_schedule: LiabilityPaymentSchedule
                payment_due_date: str
                payment_due_num_days_after: int
                payment_schedule_type: Literal[...] (one of 10 values) (required)
            limit: float
            limit_time_period: Literal["Annual", "Forever"]
            list_id: str (required)
            name: str
            net_or_gross: Literal["Gross", "Net"]
            payment_template_ref: Ref
            payroll_item_detail_type_value: int
            rate: float
            rate_percent: float
            request_id: str
            taxability: List[Taxability]
                is_tax_applied: bool (required)
                payroll_item_tax_ref: Ref (required)
            vendor_account_number: str
            vendor_ref: Ref
            w2_tracking_type_value: int

        Docs: https://docs.qubesync.com/api-reference/v2/payroll-item-deductions/update-payroll-item-deduction
        """
        return self._client._queue_operation("payroll_item_deduction.update", connection_id, params, webhook_url, idempotency_key)
