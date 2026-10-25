# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks special item operations (``client.special_item``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    ItemDiscountBarCode,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _SpecialItemCreateParamsRequired(TypedDict):
    #: Identifies the type of special item. See type for possible enum values.
    special_item_type: Literal["FinanceCharge", "ReimbursableExpenseGroup", "ReimbursableExpenseSubtotal"]


class SpecialItemCreateParams(_SpecialItemCreateParamsRequired, total=False):
    """Params for ``special_item.create`` (Create special item)."""
    #: Barcode reference information.
    bar_code: ItemDiscountBarCode
    #: Allows for the attachment of a user defined GUID value.
    external_guid: str
    include_ret_element: List[Literal["BarCodeValue", "ClassRef", "DataExtRet", "EditSequence", "ExternalGUID", "FullName", "IsActive", "IsPrintItemsInGroup", "IsTaxIncluded", "ItemDesc", "ItemGroupLine", "ListID", "Name", "ParentRef", "SalesAndPurchase", "SalesOrPurchase", "SalesTaxCodeRef", "SpecialItemType", "Sublevel", "TimeCreated", "TimeModified", "UnitOfMeasureSetRef"]]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class SpecialItem:
    """QuickBooks special item operations: create.

    Get it from ``client.special_item``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[SpecialItemCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create special item.

        Queues ``special_item.create``: POST /connections/{connection_id}/special-items, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``SpecialItemCreateParams``)::

            bar_code: ItemDiscountBarCode
                allow_override: bool
                assign_even_if_used: bool
                bar_code_value: str
            external_guid: str
            include_ret_element: List[Literal[...] (one of 22 values)]
            request_id: str
            special_item_type: Literal["FinanceCharge", "ReimbursableExpenseGroup", "ReimbursableExpenseSubtotal"] (required)

        Docs: https://docs.qubesync.com/api-reference/v2/special-items/create-special-item
        """
        return self._client._queue_operation("special_item.create", connection_id, params, webhook_url, idempotency_key)
