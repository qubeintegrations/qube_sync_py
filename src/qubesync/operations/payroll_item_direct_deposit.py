# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks payroll item direct deposit operations (``client.payroll_item_direct_deposit``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    Ref,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _PayrollItemDirectDepositCreateParamsRequired(TypedDict):
    liability_account_ref: Ref
    name: str


class PayrollItemDirectDepositCreateParams(_PayrollItemDirectDepositCreateParamsRequired, total=False):
    """Params for ``payroll_item_direct_deposit.create`` (Create payroll item direct deposit)."""
    include_ret_element: List[Literal["EditSequence", "IsActive", "LiabilityAccountRef", "ListID", "Name", "PayrollItemDetailTypeValue", "TimeCreated", "TimeModified"]]
    is_active: bool
    payroll_item_detail_type_value: int
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class _PayrollItemDirectDepositUpdateParamsRequired(TypedDict):
    edit_sequence: str
    list_id: str


class PayrollItemDirectDepositUpdateParams(_PayrollItemDirectDepositUpdateParamsRequired, total=False):
    """Params for ``payroll_item_direct_deposit.update`` (Update payroll item direct deposit)."""
    include_ret_element: List[Literal["EditSequence", "IsActive", "LiabilityAccountRef", "ListID", "Name", "PayrollItemDetailTypeValue", "TimeCreated", "TimeModified"]]
    is_active: bool
    liability_account_ref: Ref
    name: str
    payroll_item_detail_type_value: int
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class PayrollItemDirectDeposit:
    """QuickBooks payroll item direct deposit operations: create, update.

    Get it from ``client.payroll_item_direct_deposit``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[PayrollItemDirectDepositCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create payroll item direct deposit.

        Queues ``payroll_item_direct_deposit.create``: POST /connections/{connection_id}/payroll-item-direct-deposits, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``PayrollItemDirectDepositCreateParams``)::

            include_ret_element: List[Literal[...] (one of 8 values)]
            is_active: bool
            liability_account_ref: Ref (required)
                full_name: str
                list_id: str
            name: str (required)
            payroll_item_detail_type_value: int
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/payroll-item-direct-deposits/create-payroll-item-direct-deposit
        """
        return self._client._queue_operation("payroll_item_direct_deposit.create", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[PayrollItemDirectDepositUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update payroll item direct deposit.

        Queues ``payroll_item_direct_deposit.update``: PUT /connections/{connection_id}/payroll-item-direct-deposits, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``PayrollItemDirectDepositUpdateParams``)::

            edit_sequence: str (required)
            include_ret_element: List[Literal[...] (one of 8 values)]
            is_active: bool
            liability_account_ref: Ref
                full_name: str
                list_id: str
            list_id: str (required)
            name: str
            payroll_item_detail_type_value: int
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/payroll-item-direct-deposits/update-payroll-item-direct-deposit
        """
        return self._client._queue_operation("payroll_item_direct_deposit.update", connection_id, params, webhook_url, idempotency_key)
