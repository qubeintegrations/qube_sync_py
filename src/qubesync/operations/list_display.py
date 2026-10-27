# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks list display operations (``client.list_display``)."""

from typing import Any, Dict, Literal, Optional, TYPE_CHECKING, TypedDict


if TYPE_CHECKING:
    from ..v2 import Client


class _ListDisplayCreateParamsRequired(TypedDict):
    #: Specifies the type of QuickBooks list for which to open an “add” form in the QuickBooks
    #: UI.
    list_display_add_type: Literal["Account", "Customer", "Employee", "Item", "OtherName", "Vendor"]


class ListDisplayCreateParams(_ListDisplayCreateParamsRequired, total=False):
    """Params for ``list_display.create`` (Create list display)."""
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class _ListDisplayUpdateParamsRequired(TypedDict):
    #: The type of QuickBooks list element to open for modification in the QuickBooks UI.
    #: (`list_id` specifies the particular list element.)
    list_display_mod_type: Literal["Account", "Customer", "Employee", "Item", "OtherName", "Vendor"]
    #: `list_id` and FullName both identify a list object. QuickBooks assigns `list_id` when the
    #: object is created. `list_id` values are unique within a list family, not across the
    #: company file: customers, vendors, employees and other names share one sequence, every
    #: item type shares another, and each other list has its own.
    list_id: str


class ListDisplayUpdateParams(_ListDisplayUpdateParamsRequired, total=False):
    """Params for ``list_display.update`` (Update list display)."""
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class ListDisplay:
    """QuickBooks list display operations: create, update.

    Get it from ``client.list_display``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[ListDisplayCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create list display.

        Queues ``list_display.create``: POST /connections/{connection_id}/list-displays, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``ListDisplayCreateParams``)::

            list_display_add_type: Literal["Account", "Customer", "Employee", "Item", "OtherName", "Vendor"] (required)
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/list-displays/create-list-display
        """
        return self._client._queue_operation("list_display.create", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[ListDisplayUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update list display.

        Queues ``list_display.update``: PUT /connections/{connection_id}/list-displays, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``ListDisplayUpdateParams``)::

            list_display_mod_type: Literal["Account", "Customer", "Employee", "Item", "OtherName", "Vendor"] (required)
            list_id: str (required)
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/list-displays/update-list-display
        """
        return self._client._queue_operation("list_display.update", connection_id, params, webhook_url, idempotency_key)
