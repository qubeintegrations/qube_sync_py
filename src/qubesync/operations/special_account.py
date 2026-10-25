# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks special account operations (``client.special_account``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    Ref,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _SpecialAccountCreateParamsRequired(TypedDict):
    #: If `special_account_type` returns a value, then QuickBooks automatically created this
    #: account when it was needed. Some special accounts can’t be overridden, because QuickBooks
    #: uses them exclusively for special purposes.
    special_account_type: Literal["AccountsPayable", "AccountsReceivable", "CondenseItemAdjustmentExpenses", "CostOfGoodsSold", "DirectDepositLiabilities", "Estimates", "ExchangeGainLoss", "InventoryAssets", "ItemReceiptAccount", "OpeningBalanceEquity", "PayrollExpenses", "PayrollLiabilities", "PettyCash", "PurchaseOrders", "ReconciliationDifferences", "RetainedEarnings", "SalesOrders", "SalesTaxPayable", "UncategorizedExpenses", "UncategorizedIncome", "UndepositedFunds"]


class SpecialAccountCreateParams(_SpecialAccountCreateParamsRequired, total=False):
    """Params for ``special_account.create`` (Create special account)."""
    #: A currency record defines how QuickBooks stores and displays a currency. Built-in
    #: currency name/code values are fixed; formatting and active status can vary by settings
    #: and workflow.
    currency_ref: Ref
    include_ret_element: List[Literal["AccountNumber", "AccountType", "Balance", "BankNumber", "CashFlowClassification", "CurrencyRef", "DataExtRet", "Desc", "DetailAccountType", "EditSequence", "ExternalGUID", "FullName", "IsActive", "IsTaxAccount", "LastCheckNumber", "ListID", "Name", "OwnerID", "ParentRef", "SalesTaxCodeRef", "SpecialAccountType", "Sublevel", "TaxLineInfoRet", "TimeCreated", "TimeModified", "TotalBalance", "TxnID", "TxnNumber"]]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class SpecialAccount:
    """QuickBooks special account operations: create.

    Get it from ``client.special_account``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[SpecialAccountCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create special account.

        Queues ``special_account.create``: POST /connections/{connection_id}/special-accounts, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``SpecialAccountCreateParams``)::

            currency_ref: Ref
                full_name: str
                list_id: str
            include_ret_element: List[Literal[...] (one of 28 values)]
            request_id: str
            special_account_type: Literal[...] (one of 21 values) (required)

        Docs: https://docs.qubesync.com/api-reference/v2/special-accounts/create-special-account
        """
        return self._client._queue_operation("special_account.create", connection_id, params, webhook_url, idempotency_key)
