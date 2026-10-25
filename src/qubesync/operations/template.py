# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks template operations (``client.template``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict


if TYPE_CHECKING:
    from ..v2 import Client


class TemplateQueryParams(TypedDict, total=False):
    """Params for ``template.query`` (List templates)."""
    include_ret_element: List[Literal["EditSequence", "IsActive", "ListID", "Name", "TemplateType", "TimeCreated", "TimeModified"]]
    #: Use the `meta_data` attribute to control whether query responses include counts. Options
    #: are NoMetaData (default), MetaDataOnly (count only), and MetaDataAndResponseData (count
    #: plus objects). Counts are approximate and may vary slightly if records are created or
    #: deleted during processing.
    meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class Template:
    """QuickBooks template operations: query.

    Get it from ``client.template``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def query(
        self,
        connection_id: str,
        params: Optional[TemplateQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List templates.

        Queues ``template.query``: GET /connections/{connection_id}/templates, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``TemplateQueryParams``)::

            include_ret_element: List[Literal[...] (one of 7 values)]
            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/templates/list-templates
        """
        return self._client._queue_operation("template.query", connection_id, params, webhook_url, idempotency_key)
