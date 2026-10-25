# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks payroll year to date adjustment operations (``client.payroll_year_to_date_adjustment``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    DateRangeFilter,
    EntityFilter,
    ModifiedDateRangeFilter,
    PayrollDateRangeFilter,
    Ref,
    RefNumberFilter,
    RefNumberRangeFilter,
)

if TYPE_CHECKING:
    from ..v2 import Client


class PayrollYearToDateAdjustmentLineAdd(TypedDict, total=False):
    account_ref: Ref
    amount: float
    calculated_amount: float
    class_ref: Ref
    company_paid_attribute: Literal["IsExpense", "IsLiability", "IsLiabilityAndExpense", "NotApplicable"]
    experience_mod_rate_amount: float
    hours_worked: str
    income_subject_to_tax_amount: float
    is_amount_overridden: bool
    memo: str
    other_account_ref: Ref
    payroll_item_ref: Ref
    #: Choose at most one of: `rate`, or `rate_percent`.
    rate: float
    #: Choose at most one of: `rate`, or `rate_percent`.
    rate_percent: float
    wage_base_amount: float
    workers_comp_amount: float
    workers_comp_code_ref: Ref


class _PayrollYearToDateAdjustmentCreateParamsRequired(TypedDict):
    employee_ref: Ref
    is_affecting_accounts: bool
    payroll_year_to_date_adjustment_line_add: List[PayrollYearToDateAdjustmentLineAdd]


class PayrollYearToDateAdjustmentCreateParams(_PayrollYearToDateAdjustmentCreateParamsRequired, total=False):
    """Params for ``payroll_year_to_date_adjustment.create`` (Create payroll year to date adjustment)."""
    account_ref: Ref
    class_ref: Ref
    def_macro: str
    include_ret_element: List[Literal["AccountRef", "Amount", "ClassRef", "EditSequence", "EmployeeRef", "IsAffectingAccounts", "Memo", "PayPeriodBeginDate", "PayPeriodEndDate", "PayrollDate", "PayrollYearToDateAdjustmentLineRet", "RefNumber", "TaxTableVersion", "TimeCreated", "TimeModified", "TxnDate", "TxnID", "TxnNumber"]]
    memo: str
    pay_period_begin_date: str
    pay_period_end_date: str
    payroll_date: str
    ref_number: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    tax_table_version: int
    txn_date: str


class PayrollYearToDateAdjustmentQueryParams(TypedDict, total=False):
    """Params for ``payroll_year_to_date_adjustment.query`` (List payroll year to date adjustments)."""
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `payroll_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    account_filter: EntityFilter
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `payroll_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    entity_filter: EntityFilter
    include_line_items: bool
    include_ret_element: List[Literal["AccountRef", "Amount", "ClassRef", "EditSequence", "EmployeeRef", "IsAffectingAccounts", "Memo", "PayPeriodBeginDate", "PayPeriodEndDate", "PayrollDate", "PayrollYearToDateAdjustmentLineRet", "RefNumber", "TaxTableVersion", "TimeCreated", "TimeModified", "TxnDate", "TxnID", "TxnNumber"]]
    #: QuickBooks doesn't page this query: at most this many records come back, in one answer,
    #: with no sign of whether more matched. Leave it out for every match, in one answer; one
    #: over 4 MB as the Web Connector sends it, about 3 MB of qbXML isn't kept (`error_type`
    #: `response_too_large`), so narrow a large one with its filters.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `payroll_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    max_returned: int
    meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `payroll_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    modified_date_range_filter: ModifiedDateRangeFilter
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `payroll_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    payroll_date_range_filter: PayrollDateRangeFilter
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `payroll_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    ref_number: List[str]
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `payroll_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    ref_number_case_sensitive: List[str]
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `payroll_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    ref_number_filter: RefNumberFilter
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `payroll_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    ref_number_range_filter: RefNumberRangeFilter
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `payroll_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    txn_date_range_filter: DateRangeFilter
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `payroll_date_range_filter`, `ref_number_filter`, `ref_number_range_filter`,
    #: `txn_date_range_filter`). Members of a set combine with each other, not with the other
    #: choices.
    txn_id: List[str]


class PayrollYearToDateAdjustment:
    """QuickBooks payroll year to date adjustment operations: create, query.

    Get it from ``client.payroll_year_to_date_adjustment``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[PayrollYearToDateAdjustmentCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create payroll year to date adjustment.

        Queues ``payroll_year_to_date_adjustment.create``: POST /connections/{connection_id}/payroll-year-to-date-adjustments, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``PayrollYearToDateAdjustmentCreateParams``)::

            account_ref: Ref
                full_name: str
                list_id: str
            class_ref: Ref
            def_macro: str
            employee_ref: Ref (required)
            include_ret_element: List[Literal[...] (one of 18 values)]
            is_affecting_accounts: bool (required)
            memo: str
            pay_period_begin_date: str
            pay_period_end_date: str
            payroll_date: str
            payroll_year_to_date_adjustment_line_add: List[PayrollYearToDateAdjustmentLineAdd] (required)
                account_ref: Ref
                amount: float
                calculated_amount: float
                class_ref: Ref
                company_paid_attribute: Literal["IsExpense", "IsLiability", "IsLiabilityAndExpense", "NotApplicable"]
                experience_mod_rate_amount: float
                hours_worked: str
                income_subject_to_tax_amount: float
                is_amount_overridden: bool
                memo: str
                other_account_ref: Ref
                payroll_item_ref: Ref
                rate: float
                rate_percent: float
                wage_base_amount: float
                workers_comp_amount: float
                workers_comp_code_ref: Ref
            ref_number: str
            request_id: str
            tax_table_version: int
            txn_date: str

        Docs: https://docs.qubesync.com/api-reference/v2/payroll-year-to-date-adjustments/create-payroll-year-to-date-adjustment
        """
        return self._client._queue_operation("payroll_year_to_date_adjustment.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[PayrollYearToDateAdjustmentQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List payroll year to date adjustments.

        Queues ``payroll_year_to_date_adjustment.query``: GET /connections/{connection_id}/payroll-year-to-date-adjustments, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``PayrollYearToDateAdjustmentQueryParams``)::

            account_filter: EntityFilter
                full_name: List[str]
                full_name_with_children: str
                list_id: List[str]
                list_id_with_children: str
            entity_filter: EntityFilter
            include_line_items: bool
            include_ret_element: List[Literal[...] (one of 18 values)]
            max_returned: int
            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            modified_date_range_filter: ModifiedDateRangeFilter
                from_modified_date: str
                to_modified_date: str
            payroll_date_range_filter: PayrollDateRangeFilter
                date_macro: Literal[...] (one of 34 values)
                from_payroll_date: str
                to_payroll_date: str
            ref_number: List[str]
            ref_number_case_sensitive: List[str]
            ref_number_filter: RefNumberFilter
                match_criterion: Literal["Contains", "EndsWith", "StartsWith"] (required)
                ref_number: str (required)
            ref_number_range_filter: RefNumberRangeFilter
                from_ref_number: str
                to_ref_number: str
            request_id: str
            txn_date_range_filter: DateRangeFilter
                date_macro: Literal[...] (one of 34 values)
                from_txn_date: str
                to_txn_date: str
            txn_id: List[str]

        Docs: https://docs.qubesync.com/api-reference/v2/payroll-year-to-date-adjustments/list-payroll-year-to-date-adjustments
        """
        return self._client._queue_operation("payroll_year_to_date_adjustment.query", connection_id, params, webhook_url, idempotency_key)
