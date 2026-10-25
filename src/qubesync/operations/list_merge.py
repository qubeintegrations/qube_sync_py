# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks list merge operations (``client.list_merge``)."""

from typing import Any, Dict, Literal, Optional, TYPE_CHECKING, TypedDict


if TYPE_CHECKING:
    from ..v2 import Client


class _MergeFromRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list type, not globally
    #: across all lists. If both `full_name` and `list_id` are supplied in a request, QuickBooks
    #: uses `list_id` and ignores `full_name`.
    list_id: str


class MergeFrom(_MergeFromRequired, total=False):
    pass


class _ListMergeExecuteParamsRequired(TypedDict):
    #: The type of the objects to be merged. Both of the objects must be the same type, for
    #: example both must be customers, because you can’t merge a vendor with a customer.
    list_merge_type: Literal["Account", "Class", "Customer", "ItemDiscount", "ItemGroup", "ItemInventory", "ItemNonInventory", "ItemOtherCharge", "ItemPayment", "ItemSalesTax", "ItemSalesTaxGroup", "ItemService", "ItemSubtotal", "Vendor"]
    #: The object to be merged into another object.
    merge_from: MergeFrom
    #: The object into which you are merging another object.
    merge_to: MergeFrom


class ListMergeExecuteParams(_ListMergeExecuteParamsRequired, total=False):
    """Params for ``list_merge.execute`` (Execute list merge)."""
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: A new tag (SameshipAddressOk) is added to ListMerge request. If true is supplied in this
    #: tag then the merge will go through even if elements have same default shipto address.
    same_ship_addr_ok: bool


class ListMerge:
    """QuickBooks list merge operations: execute.

    Get it from ``client.list_merge``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def execute(
        self,
        connection_id: str,
        params: Optional[ListMergeExecuteParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute list merge.

        Queues ``list_merge.execute``: POST /connections/{connection_id}/list-merge, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``ListMergeExecuteParams``)::

            list_merge_type: Literal[...] (one of 14 values) (required)
            merge_from: MergeFrom (required)
                edit_sequence: str (required)
                list_id: str (required)
            merge_to: MergeFrom (required)
            request_id: str
            same_ship_addr_ok: bool

        Docs: https://docs.qubesync.com/api-reference/v2/list-merge/execute-list-merge
        """
        return self._client._queue_operation("list_merge.execute", connection_id, params, webhook_url, idempotency_key)
