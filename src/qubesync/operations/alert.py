# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks alert operations (``client.alert``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict


if TYPE_CHECKING:
    from ..v2 import Client


class _AlertPermissionRequired(TypedDict):
    permission_level: List[Literal["AccountsPayable", "AccountsReceivable", "Banking", "Finance", "Inventory", "TimeTracking"]]
    permission_needed: Literal["All", "Any"]


class AlertPermission(_AlertPermissionRequired, total=False):
    pass


class _ComCallbackInfoRequired(TypedDict):
    app_name: str


class ComCallbackInfo(_ComCallbackInfoRequired, total=False):
    clsid: str
    prog_id: str


class _HttpCallbackInfoRequired(TypedDict):
    url: str


class HttpCallbackInfo(_HttpCallbackInfoRequired, total=False):
    pass


class _AlertCreateParamsRequired(TypedDict):
    alert_tag: str
    desc: str
    help_text: str
    message_text: str
    owner_id: str


class AlertCreateParams(_AlertCreateParamsRequired, total=False):
    """Params for ``alert.create`` (Create alert)."""
    activation_date: str
    alert_permission: AlertPermission
    com_callback_info: ComCallbackInfo
    expiration_date: str
    http_callback_info: HttpCallbackInfo
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    ui_context: List[Literal["AlertsManager", "CompanyNavigator"]]


class _AlertDeleteParamsRequired(TypedDict):
    alert_tag: str
    owner_id: str


class AlertDeleteParams(_AlertDeleteParamsRequired, total=False):
    """Params for ``alert.delete`` (Delete alert)."""
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class _AlertQueryParamsRequired(TypedDict):
    owner_id: List[str]


class AlertQueryParams(_AlertQueryParamsRequired, total=False):
    """Params for ``alert.query`` (List alerts)."""
    meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class Alert:
    """QuickBooks alert operations: create, delete, query.

    Get it from ``client.alert``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[AlertCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create alert.

        Queues ``alert.create``: POST /connections/{connection_id}/alerts, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``AlertCreateParams``)::

            activation_date: str
            alert_permission: AlertPermission
                permission_level: List[Literal["AccountsPayable", "AccountsReceivable", "Banking", "Finance", "Inventory", "TimeTracking"]] (required)
                permission_needed: Literal["All", "Any"] (required)
            alert_tag: str (required)
            com_callback_info: ComCallbackInfo
                app_name: str (required)
                clsid: str
                prog_id: str
            desc: str (required)
            expiration_date: str
            help_text: str (required)
            http_callback_info: HttpCallbackInfo
                url: str (required)
            message_text: str (required)
            owner_id: str (required)
            request_id: str
            ui_context: List[Literal["AlertsManager", "CompanyNavigator"]]

        Docs: https://docs.qubesync.com/api-reference/v2/alerts/create-alert
        """
        return self._client._queue_operation("alert.create", connection_id, params, webhook_url, idempotency_key)

    def delete(
        self,
        connection_id: str,
        params: Optional[AlertDeleteParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Delete alert.

        Queues ``alert.delete``: DELETE /connections/{connection_id}/alerts, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``AlertDeleteParams``)::

            alert_tag: str (required)
            owner_id: str (required)
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/alerts/delete-alert
        """
        return self._client._queue_operation("alert.delete", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[AlertQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List alerts.

        Queues ``alert.query``: GET /connections/{connection_id}/alerts, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``AlertQueryParams``)::

            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            owner_id: List[str] (required)
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/alerts/list-alerts
        """
        return self._client._queue_operation("alert.query", connection_id, params, webhook_url, idempotency_key)
