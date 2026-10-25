# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks host operations (``client.host``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict


if TYPE_CHECKING:
    from ..v2 import Client


class _IncludeListMetaDataRequired(TypedDict):
    #: Specify the value “true” to return max list limits for each object type, or “false” to
    #: not return these in the query response. By default, this is “false” for HostQuery.
    include_max_capacity: bool


class IncludeListMetaData(_IncludeListMetaDataRequired, total=False):
    pass


class HostQueryParams(TypedDict, total=False):
    """Params for ``host.query`` (List hosts)."""
    #: Use this aggregate if you want the query to return list capacity metadata for each object
    #: type in QuickBooks.
    include_list_meta_data: IncludeListMetaData
    include_ret_element: List[Literal["Country", "IsAutomaticLogin", "ListMetaData", "MajorVersion", "MinorVersion", "ProductName", "QBFileMode", "SupportedQBXMLVersion"]]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class Host:
    """QuickBooks host operations: query.

    Get it from ``client.host``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def query(
        self,
        connection_id: str,
        params: Optional[HostQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List hosts.

        Queues ``host.query``: GET /connections/{connection_id}/hosts, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``HostQueryParams``)::

            include_list_meta_data: IncludeListMetaData
                include_max_capacity: bool (required)
            include_ret_element: List[Literal[...] (one of 8 values)]
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/hosts/list-hosts
        """
        return self._client._queue_operation("host.query", connection_id, params, webhook_url, idempotency_key)
