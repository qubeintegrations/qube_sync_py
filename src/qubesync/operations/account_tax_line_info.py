# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks account tax line info operations (``client.account_tax_line_info``)."""

from typing import Any, Dict, Optional, TYPE_CHECKING, TypedDict


if TYPE_CHECKING:
    from ..v2 import Client


class AccountTaxLineInfoQueryParams(TypedDict, total=False):
    """Params for ``account_tax_line_info.query`` (List account tax line infos)."""
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class AccountTaxLineInfo:
    """QuickBooks account tax line info operations: query.

    Get it from ``client.account_tax_line_info``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def query(
        self,
        connection_id: str,
        params: Optional[AccountTaxLineInfoQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List account tax line infos.

        Queues ``account_tax_line_info.query``: GET /connections/{connection_id}/account-tax-line-infos, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``AccountTaxLineInfoQueryParams``)::

            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/account-tax-line-infos/list-account-tax-line-infos
        """
        return self._client._queue_operation("account_tax_line_info.query", connection_id, params, webhook_url, idempotency_key)
