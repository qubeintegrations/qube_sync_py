# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks payroll item tax operations (``client.payroll_item_tax``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    LiabilityPaymentSchedule,
    Ref,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _RateChangeRequired(TypedDict):
    rate_percent: float
    sunset_date: str


class RateChange(_RateChangeRequired, total=False):
    pass


class _PayrollItemTaxCreateParamsRequired(TypedDict):
    liability_account_ref: Ref
    name: str
    payment_template_ref: Ref
    payroll_item_detail_type_value: int


class PayrollItemTaxCreateParams(_PayrollItemTaxCreateParamsRequired, total=False):
    """Params for ``payroll_item_tax.create`` (Create payroll item tax)."""
    expense_account_ref: Ref
    include_ret_element: List[Literal["EditSequence", "ExpenseAccountRef", "IsActive", "LiabilityAccountRef", "LiabilityPaymentSchedule", "Limit", "ListID", "Name", "PaymentTemplateRef", "PayrollItemDetailTypeValue", "Rate", "RateChange", "RatePercent", "State", "TaxCalculatedBasedOn", "TimeCreated", "TimeModified", "VendorAccountNumber", "VendorRef", "W2TrackingTypeValue"]]
    is_active: bool
    liability_payment_schedule: LiabilityPaymentSchedule
    limit: float
    #: Choose at most one of: `rate`, or `rate_percent`.
    rate: float
    rate_change: List[RateChange]
    #: Choose at most one of: `rate`, or `rate_percent`.
    rate_percent: float
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    state: str
    tax_calculated_based_on: Literal["Compensation", "HoursAll", "HoursWorked", "Quantity"]
    vendor_account_number: str
    vendor_ref: Ref
    w2_tracking_type_value: int


class _PayrollItemTaxUpdateParamsRequired(TypedDict):
    edit_sequence: str
    list_id: str


class PayrollItemTaxUpdateParams(_PayrollItemTaxUpdateParamsRequired, total=False):
    """Params for ``payroll_item_tax.update`` (Update payroll item tax)."""
    expense_account_ref: Ref
    include_ret_element: List[Literal["EditSequence", "ExpenseAccountRef", "IsActive", "LiabilityAccountRef", "LiabilityPaymentSchedule", "Limit", "ListID", "Name", "PaymentTemplateRef", "PayrollItemDetailTypeValue", "Rate", "RateChange", "RatePercent", "State", "TaxCalculatedBasedOn", "TimeCreated", "TimeModified", "VendorAccountNumber", "VendorRef", "W2TrackingTypeValue"]]
    is_active: bool
    liability_account_ref: Ref
    liability_payment_schedule: LiabilityPaymentSchedule
    limit: float
    name: str
    payment_template_ref: Ref
    #: Choose at most one of: `rate`, or `rate_percent`.
    rate: float
    rate_change: List[RateChange]
    #: Choose at most one of: `rate`, or `rate_percent`.
    rate_percent: float
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    state: str
    tax_calculated_based_on: Literal["Compensation", "HoursAll", "HoursWorked", "Quantity"]
    vendor_account_number: str
    vendor_ref: Ref
    w2_tracking_type_value: int


class PayrollItemTax:
    """QuickBooks payroll item tax operations: create, update.

    Get it from ``client.payroll_item_tax``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[PayrollItemTaxCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create payroll item tax.

        Queues ``payroll_item_tax.create``: POST /connections/{connection_id}/payroll-item-taxes, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``PayrollItemTaxCreateParams``)::

            expense_account_ref: Ref
                full_name: str
                list_id: str
            include_ret_element: List[Literal[...] (one of 20 values)]
            is_active: bool
            liability_account_ref: Ref (required)
            liability_payment_schedule: LiabilityPaymentSchedule
                payment_due_date: str
                payment_due_num_days_after: int
                payment_schedule_type: Literal[...] (one of 10 values) (required)
            limit: float
            name: str (required)
            payment_template_ref: Ref (required)
            payroll_item_detail_type_value: int (required)
            rate: float
            rate_change: List[RateChange]
                rate_percent: float (required)
                sunset_date: str (required)
            rate_percent: float
            request_id: str
            state: str
            tax_calculated_based_on: Literal["Compensation", "HoursAll", "HoursWorked", "Quantity"]
            vendor_account_number: str
            vendor_ref: Ref
            w2_tracking_type_value: int

        Docs: https://docs.qubesync.com/api-reference/v2/payroll-item-taxes/create-payroll-item-tax
        """
        return self._client._queue_operation("payroll_item_tax.create", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[PayrollItemTaxUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update payroll item tax.

        Queues ``payroll_item_tax.update``: PUT /connections/{connection_id}/payroll-item-taxes, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``PayrollItemTaxUpdateParams``)::

            edit_sequence: str (required)
            expense_account_ref: Ref
                full_name: str
                list_id: str
            include_ret_element: List[Literal[...] (one of 20 values)]
            is_active: bool
            liability_account_ref: Ref
            liability_payment_schedule: LiabilityPaymentSchedule
                payment_due_date: str
                payment_due_num_days_after: int
                payment_schedule_type: Literal[...] (one of 10 values) (required)
            limit: float
            list_id: str (required)
            name: str
            payment_template_ref: Ref
            rate: float
            rate_change: List[RateChange]
                rate_percent: float (required)
                sunset_date: str (required)
            rate_percent: float
            request_id: str
            state: str
            tax_calculated_based_on: Literal["Compensation", "HoursAll", "HoursWorked", "Quantity"]
            vendor_account_number: str
            vendor_ref: Ref
            w2_tracking_type_value: int

        Docs: https://docs.qubesync.com/api-reference/v2/payroll-item-taxes/update-payroll-item-tax
        """
        return self._client._queue_operation("payroll_item_tax.update", connection_id, params, webhook_url, idempotency_key)
