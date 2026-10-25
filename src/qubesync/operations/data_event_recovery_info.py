# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks data event recovery info operations (``client.data_event_recovery_info``)."""

from typing import Any, Dict, Optional, TYPE_CHECKING, TypedDict


if TYPE_CHECKING:
    from ..v2 import Client


class _DataEventRecoveryInfoDeleteParamsRequired(TypedDict):
    #: A unique identifier that an application sets when it adds a subscription so that the
    #: application can later query or delete the subscription.
    subscriber_id: str


class DataEventRecoveryInfoDeleteParams(_DataEventRecoveryInfoDeleteParamsRequired, total=False):
    """Params for ``data_event_recovery_info.delete`` (Delete data event recovery info)."""
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class _DataEventRecoveryInfoQueryParamsRequired(TypedDict):
    #: A unique identifier that an application sets when it adds a subscription so that the
    #: application can later query or delete the subscription.
    subscriber_id: str


class DataEventRecoveryInfoQueryParams(_DataEventRecoveryInfoQueryParamsRequired, total=False):
    """Params for ``data_event_recovery_info.query`` (List data event recovery infos)."""
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class DataEventRecoveryInfo:
    """QuickBooks data event recovery info operations: delete, query.

    Get it from ``client.data_event_recovery_info``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def delete(
        self,
        connection_id: str,
        params: Optional[DataEventRecoveryInfoDeleteParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Delete data event recovery info.

        Queues ``data_event_recovery_info.delete``: DELETE /connections/{connection_id}/data-event-recovery-infos, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``DataEventRecoveryInfoDeleteParams``)::

            request_id: str
            subscriber_id: str (required)

        Docs: https://docs.qubesync.com/api-reference/v2/data-event-recovery-infos/delete-data-event-recovery-info
        """
        return self._client._queue_operation("data_event_recovery_info.delete", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[DataEventRecoveryInfoQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List data event recovery infos.

        Queues ``data_event_recovery_info.query``: GET /connections/{connection_id}/data-event-recovery-infos, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``DataEventRecoveryInfoQueryParams``)::

            request_id: str
            subscriber_id: str (required)

        Docs: https://docs.qubesync.com/api-reference/v2/data-event-recovery-infos/list-data-event-recovery-infos
        """
        return self._client._queue_operation("data_event_recovery_info.query", connection_id, params, webhook_url, idempotency_key)
