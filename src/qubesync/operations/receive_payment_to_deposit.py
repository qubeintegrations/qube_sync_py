# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks receive payment to deposit operations (``client.receive_payment_to_deposit``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict


if TYPE_CHECKING:
    from ..v2 import Client


class ReceivePaymentToDepositQueryParams(TypedDict, total=False):
    """Params for ``receive_payment_to_deposit.query`` (List receive payment to deposits)."""
    include_ret_element: List[Literal["Amount", "AmountInHomeCurrency", "CurrencyRef", "CustomerRef", "ExchangeRate", "RefNumber", "TxnDate", "TxnID", "TxnLineID", "TxnType"]]
    #: Use the `meta_data` attribute to control whether query responses include counts. Options
    #: are NoMetaData (default), MetaDataOnly (count only), and MetaDataAndResponseData (count
    #: plus objects). Counts are approximate and may vary slightly if records are created or
    #: deleted during processing.
    meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class ReceivePaymentToDeposit:
    """QuickBooks receive payment to deposit operations: query.

    Get it from ``client.receive_payment_to_deposit``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def query(
        self,
        connection_id: str,
        params: Optional[ReceivePaymentToDepositQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List receive payment to deposits.

        Queues ``receive_payment_to_deposit.query``: GET /connections/{connection_id}/receive-payment-to-deposits, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``ReceivePaymentToDepositQueryParams``)::

            include_ret_element: List[Literal[...] (one of 10 values)]
            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/receive-payment-to-deposits/list-receive-payment-to-deposits
        """
        return self._client._queue_operation("receive_payment_to_deposit.query", connection_id, params, webhook_url, idempotency_key)
