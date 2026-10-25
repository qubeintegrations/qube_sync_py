# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks qb command exec operations (``client.qb_command_exec``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict


if TYPE_CHECKING:
    from ..v2 import Client


class _ArgumentRequired(TypedDict):
    arg_name: str


class Argument(_ArgumentRequired, total=False):
    #: Choose exactly one of: `arg_value`, or `list_id`, or `txn_id`.
    arg_value: str
    #: Choose exactly one of: `arg_value`, or `list_id`, or `txn_id`.
    list_id: str
    #: Choose exactly one of: `arg_value`, or `list_id`, or `txn_id`.
    txn_id: str


class _QbCommandExecExecuteParamsRequired(TypedDict):
    qb_command: Literal["Backup", "ExportQBDT2QBO", "ExportReport", "IIFImport", "MobiLinkSync", "Restore", "ScheduledReport"]


class QbCommandExecExecuteParams(_QbCommandExecExecuteParamsRequired, total=False):
    """Params for ``qb_command_exec.execute`` (Execute QB command exec)."""
    argument: List[Argument]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class QbCommandExec:
    """QuickBooks qb command exec operations: execute.

    Get it from ``client.qb_command_exec``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def execute(
        self,
        connection_id: str,
        params: Optional[QbCommandExecExecuteParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute QB command exec.

        Queues ``qb_command_exec.execute``: POST /connections/{connection_id}/qb-command-exec, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``QbCommandExecExecuteParams``)::

            argument: List[Argument]
                arg_name: str (required)
                arg_value: str
                list_id: str
                txn_id: str
            qb_command: Literal[...] (one of 7 values) (required)
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/qb-command-exec/execute-qb-command-exec
        """
        return self._client._queue_operation("qb_command_exec.execute", connection_id, params, webhook_url, idempotency_key)
