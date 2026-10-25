# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks payroll item workers compensation operations (``client.payroll_item_workers_compensation``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    LiabilityPaymentSchedule,
    Ref,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _PayrollItemWorkersCompensationCreateParamsRequired(TypedDict):
    expense_account_ref: Ref
    liability_account_ref: Ref
    name: str
    payment_template_ref: Ref


class PayrollItemWorkersCompensationCreateParams(_PayrollItemWorkersCompensationCreateParamsRequired, total=False):
    """Params for ``payroll_item_workers_compensation.create`` (Create payroll item workers compensation)."""
    include_ret_element: List[Literal["EditSequence", "ExpenseAccountRef", "IsActive", "IsTrackedByCustJob", "LiabilityAccountRef", "LiabilityPaymentSchedule", "ListID", "Name", "PaymentTemplateRef", "PayrollItemDetailTypeValue", "TimeCreated", "TimeModified", "VendorAccountNumber", "VendorRef"]]
    is_active: bool
    is_tracked_by_cust_job: bool
    liability_payment_schedule: LiabilityPaymentSchedule
    payroll_item_detail_type_value: int
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    vendor_account_number: str
    vendor_ref: Ref


class _PayrollItemWorkersCompensationUpdateParamsRequired(TypedDict):
    edit_sequence: str
    list_id: str


class PayrollItemWorkersCompensationUpdateParams(_PayrollItemWorkersCompensationUpdateParamsRequired, total=False):
    """Params for ``payroll_item_workers_compensation.update`` (Update payroll item workers compensation)."""
    expense_account_ref: Ref
    include_ret_element: List[Literal["EditSequence", "ExpenseAccountRef", "IsActive", "IsTrackedByCustJob", "LiabilityAccountRef", "LiabilityPaymentSchedule", "ListID", "Name", "PaymentTemplateRef", "PayrollItemDetailTypeValue", "TimeCreated", "TimeModified", "VendorAccountNumber", "VendorRef"]]
    is_active: bool
    is_tracked_by_cust_job: bool
    liability_account_ref: Ref
    liability_payment_schedule: LiabilityPaymentSchedule
    name: str
    payment_template_ref: Ref
    payroll_item_detail_type_value: int
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    vendor_account_number: str
    vendor_ref: Ref


class PayrollItemWorkersCompensation:
    """QuickBooks payroll item workers compensation operations: create, update.

    Get it from ``client.payroll_item_workers_compensation``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[PayrollItemWorkersCompensationCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create payroll item workers compensation.

        Queues ``payroll_item_workers_compensation.create``: POST /connections/{connection_id}/payroll-item-workers-compensations, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``PayrollItemWorkersCompensationCreateParams``)::

            expense_account_ref: Ref (required)
                full_name: str
                list_id: str
            include_ret_element: List[Literal[...] (one of 14 values)]
            is_active: bool
            is_tracked_by_cust_job: bool
            liability_account_ref: Ref (required)
            liability_payment_schedule: LiabilityPaymentSchedule
                payment_due_date: str
                payment_due_num_days_after: int
                payment_schedule_type: Literal[...] (one of 10 values) (required)
            name: str (required)
            payment_template_ref: Ref (required)
            payroll_item_detail_type_value: int
            request_id: str
            vendor_account_number: str
            vendor_ref: Ref

        Docs: https://docs.qubesync.com/api-reference/v2/payroll-item-workers-compensations/create-payroll-item-workers-compensation
        """
        return self._client._queue_operation("payroll_item_workers_compensation.create", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[PayrollItemWorkersCompensationUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update payroll item workers compensation.

        Queues ``payroll_item_workers_compensation.update``: PUT /connections/{connection_id}/payroll-item-workers-compensations, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``PayrollItemWorkersCompensationUpdateParams``)::

            edit_sequence: str (required)
            expense_account_ref: Ref
                full_name: str
                list_id: str
            include_ret_element: List[Literal[...] (one of 14 values)]
            is_active: bool
            is_tracked_by_cust_job: bool
            liability_account_ref: Ref
            liability_payment_schedule: LiabilityPaymentSchedule
                payment_due_date: str
                payment_due_num_days_after: int
                payment_schedule_type: Literal[...] (one of 10 values) (required)
            list_id: str (required)
            name: str
            payment_template_ref: Ref
            payroll_item_detail_type_value: int
            request_id: str
            vendor_account_number: str
            vendor_ref: Ref

        Docs: https://docs.qubesync.com/api-reference/v2/payroll-item-workers-compensations/update-payroll-item-workers-compensation
        """
        return self._client._queue_operation("payroll_item_workers_compensation.update", connection_id, params, webhook_url, idempotency_key)
