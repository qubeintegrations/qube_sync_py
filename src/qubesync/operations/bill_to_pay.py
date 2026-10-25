# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks bill to pay operations (``client.bill_to_pay``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    CurrencyFilter,
    Ref,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _BillToPayQueryParamsRequired(TypedDict):
    #: `payee_entity_ref` identifies the payee (customer, vendor, employee, or Other Name). If
    #: both `full_name` and `list_id` are provided, `full_name` is ignored.
    payee_entity_ref: Ref


class BillToPayQueryParams(_BillToPayQueryParamsRequired, total=False):
    """Params for ``bill_to_pay.query`` (List bill to pays)."""
    #: Refers to an accounts payable account in the QuickBooks file. (The AccountType of this
    #: account will be AccountsPayable.) If `ap_account_ref` is missing, the SDK will use the
    #: QuickBooks default AP account. In a request, if an `ap_account_ref` aggregate includes
    #: both `full_name` and `list_id`, `full_name` will be ignored.
    ap_account_ref: Ref
    #: Filters by the specified currency.
    currency_filter: CurrencyFilter
    #: The date on which payment is due.
    due_date: str
    include_ret_element: List[Literal["BillToPay", "CreditToApply"]]
    #: Use the `meta_data` attribute to control whether query responses include counts. Options
    #: are NoMetaData (default), MetaDataOnly (count only), and MetaDataAndResponseData (count
    #: plus objects). Counts are approximate and may vary slightly if records are created or
    #: deleted during processing.
    meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class BillToPay:
    """QuickBooks bill to pay operations: query.

    Get it from ``client.bill_to_pay``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def query(
        self,
        connection_id: str,
        params: Optional[BillToPayQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List bill to pays.

        Queues ``bill_to_pay.query``: GET /connections/{connection_id}/bill-to-pays, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``BillToPayQueryParams``)::

            ap_account_ref: Ref
                full_name: str
                list_id: str
            currency_filter: CurrencyFilter
                full_name: List[str]
                list_id: List[str]
            due_date: str
            include_ret_element: List[Literal["BillToPay", "CreditToApply"]]
            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            payee_entity_ref: Ref (required)
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/bill-to-pays/list-bill-to-pays
        """
        return self._client._queue_operation("bill_to_pay.query", connection_id, params, webhook_url, idempotency_key)
