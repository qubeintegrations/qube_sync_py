# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks payroll last period operations (``client.payroll_last_period``)."""

from typing import Any, Dict, Optional, TYPE_CHECKING, TypedDict


if TYPE_CHECKING:
    from ..v2 import Client


class PayrollLastPeriodQueryParams(TypedDict, total=False):
    """Params for ``payroll_last_period.query`` (List payroll last periods)."""
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class PayrollLastPeriod:
    """QuickBooks payroll last period operations: query.

    Get it from ``client.payroll_last_period``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def query(
        self,
        connection_id: str,
        params: Optional[PayrollLastPeriodQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List payroll last periods.

        Queues ``payroll_last_period.query``: GET /connections/{connection_id}/payroll-last-periods, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``PayrollLastPeriodQueryParams``)::

            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/payroll-last-periods/list-payroll-last-periods
        """
        return self._client._queue_operation("payroll_last_period.query", connection_id, params, webhook_url, idempotency_key)
