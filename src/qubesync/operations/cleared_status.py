# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks cleared status operations (``client.cleared_status``)."""

from typing import Any, Dict, Literal, Optional, TYPE_CHECKING, TypedDict


if TYPE_CHECKING:
    from ..v2 import Client


class _ClearedStatusUpdateParamsRequired(TypedDict):
    #: Indicates whether a transaction or transaction line has been cleared.
    cleared_status: Literal["Cleared", "NotCleared", "Pending"]
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    txn_id: str


class ClearedStatusUpdateParams(_ClearedStatusUpdateParamsRequired, total=False):
    """Params for ``cleared_status.update`` (Update cleared status)."""
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: Identification number of the transaction line. (`txn_line_id` is supported as of v2.0 of
    #: the SDK. With qbXML v1.0 and v1.1, `txn_line_id` is always returned as zero.) G/p>If you
    #: need to add a new transaction line in a transaction Mod request, you can do so by setting
    #: the `txn_line_id` to -1.
    txn_line_id: str


class ClearedStatus:
    """QuickBooks cleared status operations: update.

    Get it from ``client.cleared_status``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def update(
        self,
        connection_id: str,
        params: Optional[ClearedStatusUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update cleared status.

        Queues ``cleared_status.update``: PUT /connections/{connection_id}/cleared-statuses, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``ClearedStatusUpdateParams``)::

            cleared_status: Literal["Cleared", "NotCleared", "Pending"] (required)
            request_id: str
            txn_id: str (required)
            txn_line_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/cleared-statuses/update-cleared-status
        """
        return self._client._queue_operation("cleared_status.update", connection_id, params, webhook_url, idempotency_key)
