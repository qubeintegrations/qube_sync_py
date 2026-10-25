# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks item assemblies can build operations (``client.item_assemblies_can_build``)."""

from typing import Any, Dict, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    Ref,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _ItemAssembliesCanBuildQueryParamsRequired(TypedDict):
    #: An inventory assembly item is one that is assembled or manufactured from inventory items.
    #: The items and/or assemblies that make up the assembly are called components. For Premier,
    #: an assembly can have a maximum of 100 components. For Enterprise, the maximum is 500
    #: components.
    item_inventory_assembly_ref: Ref
    #: The date of the transaction. In some cases, if you leave `txn_date` out of an -Add
    #: message, QuickBooks will prefill `txn_date` with the date of the last-saved transaction
    #: of the same type.
    txn_date: str


class ItemAssembliesCanBuildQueryParams(_ItemAssembliesCanBuildQueryParamsRequired, total=False):
    """Params for ``item_assemblies_can_build.query`` (List item assemblies can builds)."""
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class ItemAssembliesCanBuild:
    """QuickBooks item assemblies can build operations: query.

    Get it from ``client.item_assemblies_can_build``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def query(
        self,
        connection_id: str,
        params: Optional[ItemAssembliesCanBuildQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List item assemblies can builds.

        Queues ``item_assemblies_can_build.query``: GET /connections/{connection_id}/item-assemblies-can-builds, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``ItemAssembliesCanBuildQueryParams``)::

            item_inventory_assembly_ref: Ref (required)
                full_name: str
                list_id: str
            request_id: str
            txn_date: str (required)

        Docs: https://docs.qubesync.com/api-reference/v2/item-assemblies-can-builds/list-item-assemblies-can-builds
        """
        return self._client._queue_operation("item_assemblies_can_build.query", connection_id, params, webhook_url, idempotency_key)
