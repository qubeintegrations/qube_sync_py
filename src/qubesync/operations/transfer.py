# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks transfer operations (``client.transfer``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    DateRangeFilter,
    ModifiedDateRangeFilter,
    Ref,
)

if TYPE_CHECKING:
    from ..v2 import Client


class TransferCreateParams(TypedDict, total=False):
    """Params for ``transfer.create`` (Create transfer)."""
    #: A monetary amount.
    amount: float
    #: Use classes to categorize transactions (for example, by department, location, or work
    #: type). Class tracking is off by default in QuickBooks. A `class_ref` points to one class;
    #: if both `full_name` and `list_id` are provided, `full_name` is ignored. In InvoiceAdd, a
    #: header-level `class_ref` is applied to line items unless you override or clear it on
    #: individual lines.
    class_ref: Ref
    #: `def_macro` lets you assign a reusable name to a returned `txn_id` or TxnLineID so later
    #: requests can reference it with `useMacro`. This feature requires SDK 2.0+.
    def_macro: str
    include_ret_element: List[Literal["Amount", "ClassRef", "EditSequence", "FromAccountBalance", "Memo", "TimeCreated", "TimeModified", "ToAccountBalance", "TransferFromAccountRef", "TransferToAccountRef", "TxnDate", "TxnID", "TxnNumber"]]
    #: Additional information.
    memo: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: Account that money will be transferred from.
    transfer_from_account_ref: Ref
    #: Account that money will be transferred to.
    transfer_to_account_ref: Ref
    #: The date of the transaction. In some cases, if you leave `txn_date` out of an -Add
    #: message, QuickBooks will prefill `txn_date` with the date of the last-saved transaction
    #: of the same type.
    txn_date: str


class TransferQueryParams(TypedDict, total=False):
    """Params for ``transfer.query`` (List transfers)."""
    include_ret_element: List[Literal["Amount", "ClassRef", "EditSequence", "FromAccountBalance", "Memo", "TimeCreated", "TimeModified", "ToAccountBalance", "TransferFromAccountRef", "TransferToAccountRef", "TxnDate", "TxnID", "TxnNumber"]]
    #: Page through every match: QuBe Sync asks QuickBooks for each page in turn and sends each
    #: to your `webhook_url` as it arrives, all with the same `id`. On by default, with pages of
    #: 100 records; send `iterator=true` with `max_returned` for another size. Off when you send
    #: `iterator=false` (every match in one answer) or `max_returned` alone (at most that many,
    #: in one answer). It pages a filtered query only: with `txn_id` every match comes back in
    #: one answer, so leave `iterator` out.
    iterator: bool
    #: Limits the number of objects that a query returns. (To get a count of how many objects
    #: could possibly be returned, use the `meta_data` query attribute.) If you include a
    #: `max_returned` value, it must be at least 1.
    #:
    #: The page size, with `iterator=true`. Sent without `iterator`, or with `iterator=false`,
    #: it's a cap instead: at most this many records come back, in one answer, and QuickBooks
    #: doesn't say whether more matched.
    #:
    #: Choose at most one of: `txn_id`, or the set (`max_returned`,
    #: `modified_date_range_filter`, `txn_date_range_filter`). Members of a set combine with
    #: each other, not with the other choices.
    max_returned: int
    #: Use the `meta_data` attribute to control whether query responses include counts. Options
    #: are NoMetaData (default), MetaDataOnly (count only), and MetaDataAndResponseData (count
    #: plus objects). Counts are approximate and may vary slightly if records are created or
    #: deleted during processing.
    meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
    #: Filters according to the dates when transactions were last modified. The
    #: `modified_date_range_filter` aggregate isn’t required to contain any elements, but if it
    #: is empty, we recommend that you leave it out altogether. Note that the time portion of
    #: the `from_modified_date` and `to_modified_date` fields wasn’t supported in qbXML version
    #: 1.0 or 1.1.
    #:
    #: Choose at most one of: `txn_id`, or the set (`max_returned`,
    #: `modified_date_range_filter`, `txn_date_range_filter`). Members of a set combine with
    #: each other, not with the other choices.
    modified_date_range_filter: ModifiedDateRangeFilter
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: Filters according to the original transaction dates.
    #:
    #: Choose at most one of: `txn_id`, or the set (`max_returned`,
    #: `modified_date_range_filter`, `txn_date_range_filter`). Members of a set combine with
    #: each other, not with the other choices.
    txn_date_range_filter: DateRangeFilter
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    #:
    #: Choose at most one of: `txn_id`, or the set (`max_returned`,
    #: `modified_date_range_filter`, `txn_date_range_filter`). Members of a set combine with
    #: each other, not with the other choices.
    txn_id: List[str]


class _TransferUpdateParamsRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    txn_id: str


class TransferUpdateParams(_TransferUpdateParamsRequired, total=False):
    """Params for ``transfer.update`` (Update transfer)."""
    #: A monetary amount.
    amount: float
    #: Use classes to categorize transactions (for example, by department, location, or work
    #: type). Class tracking is off by default in QuickBooks. A `class_ref` points to one class;
    #: if both `full_name` and `list_id` are provided, `full_name` is ignored. In InvoiceAdd, a
    #: header-level `class_ref` is applied to line items unless you override or clear it on
    #: individual lines.
    class_ref: Ref
    include_ret_element: List[Literal["Amount", "ClassRef", "EditSequence", "FromAccountBalance", "Memo", "TimeCreated", "TimeModified", "ToAccountBalance", "TransferFromAccountRef", "TransferToAccountRef", "TxnDate", "TxnID", "TxnNumber"]]
    #: Additional information.
    memo: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: Account that money will be transferred from.
    transfer_from_account_ref: Ref
    #: Account that money will be transferred to.
    transfer_to_account_ref: Ref
    #: The date of the transaction. In some cases, if you leave `txn_date` out of an -Add
    #: message, QuickBooks will prefill `txn_date` with the date of the last-saved transaction
    #: of the same type.
    txn_date: str


class Transfer:
    """QuickBooks transfer operations: create, query, update.

    Get it from ``client.transfer``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[TransferCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create transfer.

        Queues ``transfer.create``: POST /connections/{connection_id}/transfers, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``TransferCreateParams``)::

            amount: float
            class_ref: Ref
                full_name: str
                list_id: str
            def_macro: str
            include_ret_element: List[Literal[...] (one of 13 values)]
            memo: str
            request_id: str
            transfer_from_account_ref: Ref
            transfer_to_account_ref: Ref
            txn_date: str

        Docs: https://docs.qubesync.com/api-reference/v2/transfers/create-transfer
        """
        return self._client._queue_operation("transfer.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[TransferQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List transfers.

        Queues ``transfer.query``: GET /connections/{connection_id}/transfers, params in the query string.
        QuickBooks answers in pages: each page comes to ``webhook_url`` as its own webhook.
        Returns the queued request.

        Params (``TransferQueryParams``)::

            include_ret_element: List[Literal[...] (one of 13 values)]
            iterator: bool
            max_returned: int
            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            modified_date_range_filter: ModifiedDateRangeFilter
                from_modified_date: str
                to_modified_date: str
            request_id: str
            txn_date_range_filter: DateRangeFilter
                date_macro: Literal[...] (one of 34 values)
                from_txn_date: str
                to_txn_date: str
            txn_id: List[str]

        Docs: https://docs.qubesync.com/api-reference/v2/transfers/list-transfers
        """
        return self._client._queue_operation("transfer.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[TransferUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update transfer.

        Queues ``transfer.update``: PUT /connections/{connection_id}/transfers, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``TransferUpdateParams``)::

            amount: float
            class_ref: Ref
                full_name: str
                list_id: str
            edit_sequence: str (required)
            include_ret_element: List[Literal[...] (one of 13 values)]
            memo: str
            request_id: str
            transfer_from_account_ref: Ref
            transfer_to_account_ref: Ref
            txn_date: str
            txn_id: str (required)

        Docs: https://docs.qubesync.com/api-reference/v2/transfers/update-transfer
        """
        return self._client._queue_operation("transfer.update", connection_id, params, webhook_url, idempotency_key)
