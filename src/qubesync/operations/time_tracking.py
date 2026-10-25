# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks time tracking operations (``client.time_tracking``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    CurrencyFilter,
    DateRangeFilter,
    ModifiedDateRangeFilter,
    Ref,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _TimeTrackingCreateParamsRequired(TypedDict):
    #: Time spent doing the work. In a TimeTrackAdd request, notice that although you can
    #: specify seconds, seconds aren’t returned in the response because the UI doesn’t use
    #: seconds.
    duration: str
    #: A QuickBooks “entity” is a customer, vendor, employee, or person on the QuickBooks “other
    #: names” list. Special cases to note: In a BillToPayQuery message, `entity_ref` refers to
    #: the vendor name. In JournalCreditLine and JournalDebitLine messages for A/R accounts,
    #: `entity_ref` must refer to a customer, or else the transaction won’t be recorded.
    entity_ref: Ref


class TimeTrackingCreateParams(_TimeTrackingCreateParamsRequired, total=False):
    """Params for ``time_tracking.create`` (Create time tracking)."""
    #: The billing status of this item line or expense line.
    billable_status: Literal["Billable", "HasBeenBilled", "NotBillable"]
    #: Use classes to categorize transactions (for example, by department, location, or work
    #: type). Class tracking is off by default in QuickBooks. A `class_ref` points to one class;
    #: if both `full_name` and `list_id` are provided, `full_name` is ignored. In InvoiceAdd, a
    #: header-level `class_ref` is applied to line items unless you override or clear it on
    #: individual lines.
    class_ref: Ref
    #: `customer_ref` identifies a customer or customer job. If both `full_name` and `list_id`
    #: are provided, `full_name` is ignored. In SalesReceipt and ReceivePayment, it identifies
    #: who receives credit. In TimeTracking, it identifies who the time can be billed to and is
    #: required in TimeTrackingAdd when IsBillable is true.
    customer_ref: Ref
    #: `def_macro` lets you assign a reusable name to a returned `txn_id` or TxnLineID so later
    #: requests can reference it with `useMacro`. This feature requires SDK 2.0+.
    def_macro: str
    #: Allows for the attachment of a user defined GUID value.
    external_guid: str
    include_ret_element: List[Literal["BillableStatus", "ClassRef", "CustomerRef", "Duration", "EditSequence", "EntityRef", "ExternalGUID", "ItemServiceRef", "ListID", "Notes", "OwnerID", "PayrollItemWageRef", "Rate", "TimeCreated", "TimeModified", "TxnDate", "TxnID", "TxnNumber"]]
    #: A service item refers to services that a business charges for or purchases. Examples
    #: include specialized labor, consulting hours, and professional fees. An `item_service_ref`
    #: aggregate refers to an item on the ItemService list. In a request, if an
    #: `item_service_ref` aggregate includes both `full_name` and `list_id`, `full_name` will be
    #: ignored.
    item_service_ref: Ref
    #: Additional information.
    notes: str
    #: Each payroll wage item describes and names a payment scheme, for example, Regular Pay or
    #: Overtime Pay. A `payroll_item_wage_ref` aggregate refers to one of these wage items. In a
    #: request, if a `payroll_item_wage_ref` aggregate includes both `full_name` and `list_id`,
    #: `full_name` will be ignored.
    payroll_item_wage_ref: Ref
    rate: float
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: The date of the transaction. In some cases, if you leave `txn_date` out of an -Add
    #: message, QuickBooks will prefill `txn_date` with the date of the last-saved transaction
    #: of the same type.
    txn_date: str


class TimeTrackingQueryParams(TypedDict, total=False):
    """Params for ``time_tracking.query`` (List time trackings)."""
    include_ret_element: List[Literal["BillableStatus", "ClassRef", "CustomerRef", "Duration", "EditSequence", "EntityRef", "ExternalGUID", "ItemServiceRef", "Notes", "PayrollItemWageRef", "Rate", "TimeCreated", "TimeModified", "TxnDate", "TxnID", "TxnNumber"]]
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
    #: `modified_date_range_filter`, `time_tracking_entity_filter`, `txn_date_range_filter`).
    #: Members of a set combine with each other, not with the other choices.
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
    #: `modified_date_range_filter`, `time_tracking_entity_filter`, `txn_date_range_filter`).
    #: Members of a set combine with each other, not with the other choices.
    modified_date_range_filter: ModifiedDateRangeFilter
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: Allows you to query for one or more names on the QuickBooks Vendor list, Employee list,
    #: or Other Names list.
    #:
    #: Choose at most one of: `txn_id`, or the set (`max_returned`,
    #: `modified_date_range_filter`, `time_tracking_entity_filter`, `txn_date_range_filter`).
    #: Members of a set combine with each other, not with the other choices.
    time_tracking_entity_filter: CurrencyFilter
    #: Filters according to the original transaction dates.
    #:
    #: Choose at most one of: `txn_id`, or the set (`max_returned`,
    #: `modified_date_range_filter`, `time_tracking_entity_filter`, `txn_date_range_filter`).
    #: Members of a set combine with each other, not with the other choices.
    txn_date_range_filter: DateRangeFilter
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    #:
    #: Choose at most one of: `txn_id`, or the set (`max_returned`,
    #: `modified_date_range_filter`, `time_tracking_entity_filter`, `txn_date_range_filter`).
    #: Members of a set combine with each other, not with the other choices.
    txn_id: List[str]


class _TimeTrackingUpdateParamsRequired(TypedDict):
    #: Time spent doing the work. In a TimeTrackAdd request, notice that although you can
    #: specify seconds, seconds aren’t returned in the response because the UI doesn’t use
    #: seconds.
    duration: str
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: A QuickBooks “entity” is a customer, vendor, employee, or person on the QuickBooks “other
    #: names” list. Special cases to note: In a BillToPayQuery message, `entity_ref` refers to
    #: the vendor name. In JournalCreditLine and JournalDebitLine messages for A/R accounts,
    #: `entity_ref` must refer to a customer, or else the transaction won’t be recorded.
    entity_ref: Ref
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    txn_id: str


class TimeTrackingUpdateParams(_TimeTrackingUpdateParamsRequired, total=False):
    """Params for ``time_tracking.update`` (Update time tracking)."""
    #: The billing status of this item line or expense line.
    billable_status: Literal["Billable", "HasBeenBilled", "NotBillable"]
    #: Use classes to categorize transactions (for example, by department, location, or work
    #: type). Class tracking is off by default in QuickBooks. A `class_ref` points to one class;
    #: if both `full_name` and `list_id` are provided, `full_name` is ignored. In InvoiceAdd, a
    #: header-level `class_ref` is applied to line items unless you override or clear it on
    #: individual lines.
    class_ref: Ref
    #: `customer_ref` identifies a customer or customer job. If both `full_name` and `list_id`
    #: are provided, `full_name` is ignored. In SalesReceipt and ReceivePayment, it identifies
    #: who receives credit. In TimeTracking, it identifies who the time can be billed to and is
    #: required in TimeTrackingAdd when IsBillable is true.
    customer_ref: Ref
    include_ret_element: List[Literal["BillableStatus", "ClassRef", "CustomerRef", "Duration", "EditSequence", "EntityRef", "ExternalGUID", "ItemServiceRef", "ListID", "Notes", "OwnerID", "PayrollItemWageRef", "Rate", "TimeCreated", "TimeModified", "TxnDate", "TxnID", "TxnNumber"]]
    #: A service item refers to services that a business charges for or purchases. Examples
    #: include specialized labor, consulting hours, and professional fees. An `item_service_ref`
    #: aggregate refers to an item on the ItemService list. In a request, if an
    #: `item_service_ref` aggregate includes both `full_name` and `list_id`, `full_name` will be
    #: ignored.
    item_service_ref: Ref
    #: Additional information.
    notes: str
    #: Each payroll wage item describes and names a payment scheme, for example, Regular Pay or
    #: Overtime Pay. A `payroll_item_wage_ref` aggregate refers to one of these wage items. In a
    #: request, if a `payroll_item_wage_ref` aggregate includes both `full_name` and `list_id`,
    #: `full_name` will be ignored.
    payroll_item_wage_ref: Ref
    rate: float
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: The date of the transaction. In some cases, if you leave `txn_date` out of an -Add
    #: message, QuickBooks will prefill `txn_date` with the date of the last-saved transaction
    #: of the same type.
    txn_date: str


class TimeTracking:
    """QuickBooks time tracking operations: create, query, update.

    Get it from ``client.time_tracking``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[TimeTrackingCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create time tracking.

        Queues ``time_tracking.create``: POST /connections/{connection_id}/time-trackings, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``TimeTrackingCreateParams``)::

            billable_status: Literal["Billable", "HasBeenBilled", "NotBillable"]
            class_ref: Ref
                full_name: str
                list_id: str
            customer_ref: Ref
            def_macro: str
            duration: str (required)
            entity_ref: Ref (required)
            external_guid: str
            include_ret_element: List[Literal[...] (one of 18 values)]
            item_service_ref: Ref
            notes: str
            payroll_item_wage_ref: Ref
            rate: float
            request_id: str
            txn_date: str

        Docs: https://docs.qubesync.com/api-reference/v2/time-trackings/create-time-tracking
        """
        return self._client._queue_operation("time_tracking.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[TimeTrackingQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List time trackings.

        Queues ``time_tracking.query``: GET /connections/{connection_id}/time-trackings, params in the query string.
        QuickBooks answers in pages: each page comes to ``webhook_url`` as its own webhook.
        Returns the queued request.

        Params (``TimeTrackingQueryParams``)::

            include_ret_element: List[Literal[...] (one of 16 values)]
            iterator: bool
            max_returned: int
            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            modified_date_range_filter: ModifiedDateRangeFilter
                from_modified_date: str
                to_modified_date: str
            request_id: str
            time_tracking_entity_filter: CurrencyFilter
                full_name: List[str]
                list_id: List[str]
            txn_date_range_filter: DateRangeFilter
                date_macro: Literal[...] (one of 34 values)
                from_txn_date: str
                to_txn_date: str
            txn_id: List[str]

        Docs: https://docs.qubesync.com/api-reference/v2/time-trackings/list-time-trackings
        """
        return self._client._queue_operation("time_tracking.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[TimeTrackingUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update time tracking.

        Queues ``time_tracking.update``: PUT /connections/{connection_id}/time-trackings, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``TimeTrackingUpdateParams``)::

            billable_status: Literal["Billable", "HasBeenBilled", "NotBillable"]
            class_ref: Ref
                full_name: str
                list_id: str
            customer_ref: Ref
            duration: str (required)
            edit_sequence: str (required)
            entity_ref: Ref (required)
            include_ret_element: List[Literal[...] (one of 18 values)]
            item_service_ref: Ref
            notes: str
            payroll_item_wage_ref: Ref
            rate: float
            request_id: str
            txn_date: str
            txn_id: str (required)

        Docs: https://docs.qubesync.com/api-reference/v2/time-trackings/update-time-tracking
        """
        return self._client._queue_operation("time_tracking.update", connection_id, params, webhook_url, idempotency_key)
