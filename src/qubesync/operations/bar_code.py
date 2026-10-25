# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks bar code operations (``client.bar_code``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict


if TYPE_CHECKING:
    from ..v2 import Client


class BarCodeQueryParams(TypedDict, total=False):
    """Params for ``bar_code.query`` (List bar codes)."""
    bar_code_value: List[str]
    #: Page through every result: QuBe Sync asks QuickBooks for each page in turn and sends each
    #: to your `webhook_url` as it arrives, all with the same `id`.
    iterator: bool
    #: Use the `meta_data` attribute to control whether query responses include counts. Options
    #: are NoMetaData (default), MetaDataOnly (count only), and MetaDataAndResponseData (count
    #: plus objects). Counts are approximate and may vary slightly if records are created or
    #: deleted during processing.
    meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class BarCode:
    """QuickBooks bar code operations: query.

    Get it from ``client.bar_code``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def query(
        self,
        connection_id: str,
        params: Optional[BarCodeQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List bar codes.

        Queues ``bar_code.query``: GET /connections/{connection_id}/bar-codes, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``BarCodeQueryParams``)::

            bar_code_value: List[str]
            iterator: bool
            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/bar-codes/list-bar-codes
        """
        return self._client._queue_operation("bar_code.query", connection_id, params, webhook_url, idempotency_key)
