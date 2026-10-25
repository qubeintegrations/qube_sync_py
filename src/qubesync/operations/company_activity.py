# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks company activity operations (``client.company_activity``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict


if TYPE_CHECKING:
    from ..v2 import Client


class CompanyActivityQueryParams(TypedDict, total=False):
    """Params for ``company_activity.query`` (List company activities)."""
    include_ret_element: List[Literal["LastCondenseTime", "LastRestoreTime"]]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class CompanyActivity:
    """QuickBooks company activity operations: query.

    Get it from ``client.company_activity``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def query(
        self,
        connection_id: str,
        params: Optional[CompanyActivityQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List company activities.

        Queues ``company_activity.query``: GET /connections/{connection_id}/company-activities, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``CompanyActivityQueryParams``)::

            include_ret_element: List[Literal["LastCondenseTime", "LastRestoreTime"]]
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/company-activities/list-company-activities
        """
        return self._client._queue_operation("company_activity.query", connection_id, params, webhook_url, idempotency_key)
