# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks employee default operations (``client.employee_default``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    Earnings,
    Ref,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _TaxInfoRequired(TypedDict):
    tax_info_category: str
    tax_info_value: str


class TaxInfo(_TaxInfoRequired, total=False):
    pass


class _EmployeeTaxRequired(TypedDict):
    payroll_item_tax_ref: Ref


class EmployeeTax(_EmployeeTaxRequired, total=False):
    is_subject_to_tax: bool
    tax_info: List[TaxInfo]
    tax_law_version: int


class EmployeeTaxInfo(TypedDict, total=False):
    employee_tax: List[EmployeeTax]
    is_standard_taxation_required: bool
    state_lived: str
    state_worked: str


class _NonEarningsRequired(TypedDict):
    payroll_item_non_wage_ref: Ref


class NonEarnings(_NonEarningsRequired, total=False):
    #: Choose at most one of: `amount`, or `rate_percent`.
    amount: float
    limit: float
    #: Choose at most one of: `amount`, or `rate_percent`.
    rate_percent: float


class HoursDefault(TypedDict, total=False):
    accrual_period: Literal["BeginningOfYear", "EveryHourOnPaycheck", "EveryPaycheck"]
    hours_accrued: str
    is_resetting_hours_each_new_year: bool
    maximum_hours: str


class EmployeeDefaultPayrollInfoMod(TypedDict, total=False):
    class_ref: Ref
    #: Choose at most one of: `clear_earnings`, or `earnings`.
    clear_earnings: bool
    #: Choose at most one of: `clear_non_earnings`, or `non_earnings`.
    clear_non_earnings: bool
    #: Choose at most one of: `clear_earnings`, or `earnings`.
    earnings: List[Earnings]
    employee_tax_info: EmployeeTaxInfo
    is_covered_by_qualified_pension_plan: bool
    #: Choose at most one of: `clear_non_earnings`, or `non_earnings`.
    non_earnings: List[NonEarnings]
    pay_period: Literal["Biweekly", "Daily", "Monthly", "Quarterly", "Semimonthly", "Weekly", "Yearly"]
    sick_hours_default: HoursDefault
    use_time_data_to_create_paychecks: Literal["DoNotUseTimeData", "NotSet", "UseTimeData"]
    vacation_hours_default: HoursDefault


class EmployeeDefaultQueryParams(TypedDict, total=False):
    """Params for ``employee_default.query`` (List employee defaults)."""
    include_ret_element: List[Literal["EmployeeDefaultPayrollInfo"]]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class EmployeeDefaultUpdateParams(TypedDict, total=False):
    """Params for ``employee_default.update`` (Update employee default)."""
    employee_default_payroll_info_mod: EmployeeDefaultPayrollInfoMod
    include_ret_element: List[Literal["EmployeeDefaultPayrollInfo"]]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class EmployeeDefault:
    """QuickBooks employee default operations: query, update.

    Get it from ``client.employee_default``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def query(
        self,
        connection_id: str,
        params: Optional[EmployeeDefaultQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List employee defaults.

        Queues ``employee_default.query``: GET /connections/{connection_id}/employee-defaults, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``EmployeeDefaultQueryParams``)::

            include_ret_element: List[Literal["EmployeeDefaultPayrollInfo"]]
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/employee-defaults/list-employee-defaults
        """
        return self._client._queue_operation("employee_default.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[EmployeeDefaultUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update employee default.

        Queues ``employee_default.update``: PUT /connections/{connection_id}/employee-defaults, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``EmployeeDefaultUpdateParams``)::

            employee_default_payroll_info_mod: EmployeeDefaultPayrollInfoMod
                class_ref: Ref
                    full_name: str
                    list_id: str
                clear_earnings: bool
                clear_non_earnings: bool
                earnings: List[Earnings]
                    payroll_item_wage_ref: Ref (required)
                    rate: float
                    rate_percent: float
                employee_tax_info: EmployeeTaxInfo
                    employee_tax: List[EmployeeTax]
                        is_subject_to_tax: bool
                        payroll_item_tax_ref: Ref (required)
                        tax_info: List[TaxInfo]
                            tax_info_category: str (required)
                            tax_info_value: str (required)
                        tax_law_version: int
                    is_standard_taxation_required: bool
                    state_lived: str
                    state_worked: str
                is_covered_by_qualified_pension_plan: bool
                non_earnings: List[NonEarnings]
                    amount: float
                    limit: float
                    payroll_item_non_wage_ref: Ref (required)
                    rate_percent: float
                pay_period: Literal[...] (one of 7 values)
                sick_hours_default: HoursDefault
                    accrual_period: Literal["BeginningOfYear", "EveryHourOnPaycheck", "EveryPaycheck"]
                    hours_accrued: str
                    is_resetting_hours_each_new_year: bool
                    maximum_hours: str
                use_time_data_to_create_paychecks: Literal["DoNotUseTimeData", "NotSet", "UseTimeData"]
                vacation_hours_default: HoursDefault
            include_ret_element: List[Literal["EmployeeDefaultPayrollInfo"]]
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/employee-defaults/update-employee-default
        """
        return self._client._queue_operation("employee_default.update", connection_id, params, webhook_url, idempotency_key)
