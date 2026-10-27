# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks to do operations (``client.to_do``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    NameFilter,
    NameRangeFilter,
    Ref,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _ToDoCreateParamsRequired(TypedDict):
    #: Additional information.
    notes: str


class ToDoCreateParams(_ToDoCreateParamsRequired, total=False):
    """Params for ``to_do.create`` (Create to do)."""
    #: `customer_ref` identifies a customer or customer job. If both `full_name` and `list_id`
    #: are provided, `full_name` is ignored. In SalesReceipt and ReceivePayment, it identifies
    #: who receives credit. In TimeTracking, it identifies who the time can be billed to and is
    #: required in TimeTrackingAdd when IsBillable is true.
    #:
    #: Choose at most one of: `customer_ref`, or `employee_ref`, or `lead_ref`, or `vendor_ref`.
    customer_ref: Ref
    #: The employee list contains payroll information about each of the company’s employees.
    #:
    #: Choose at most one of: `customer_ref`, or `employee_ref`, or `lead_ref`, or `vendor_ref`.
    employee_ref: Ref
    include_ret_element: List[Literal["CustomerRef", "EditSequence", "EmployeeRef", "ExternalGUID", "IsActive", "IsDone", "LeadRef", "ListID", "Notes", "OwnerID", "Priority", "ReminderDate", "ReminderTime", "TimeCreated", "TimeModified", "TxnID", "TxnNumber", "Type", "VendorRef"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: If `is_done` is true, this “to do” task has been completed. The default value of
    #: `is_done` is false.
    is_done: bool
    #: The lead list contains information about leads for a company.
    #:
    #: Choose at most one of: `customer_ref`, or `employee_ref`, or `lead_ref`, or `vendor_ref`.
    lead_ref: Ref
    #: Priority may have one of the following values: Low [DEFAULT], Medium, High
    priority: Literal["High", "Low", "Medium"]
    #: The date on which the contents of the Notes string will appear on the Reminder list
    #: within QuickBooks.
    reminder_date: str
    #: The time on which the contents of the Notes string will appear on the Reminder list
    #: within QuickBooks.
    reminder_time: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: Type may have one of the following values: Task [DEFAULT], Call, Fax, Email, Meeting,
    #: Appointment
    type: Literal["Appointment", "Call", "Email", "Fax", "Meeting", "Task"]
    #: A vendor is any person or company from whom a small business owner buys goods and
    #: services. (Banks and tax agencies usually are included on the vendor list.) A company’s
    #: vendor list contains information such as account balance and contact information about
    #: each vendor. A `vendor_ref` aggregate refers to one of the vendors on the list.
    #:
    #: Choose at most one of: `customer_ref`, or `employee_ref`, or `lead_ref`, or `vendor_ref`.
    vendor_ref: Ref


class ToDoQueryParams(TypedDict, total=False):
    """Params for ``to_do.query`` (List to dos)."""
    #: Used in filters to select list objects based on whether or not they are currently enabled
    #: for use by QuickBooks. The default value is asActiveOnly, which selects only list objects
    #: that are active.
    #:
    #: Choose at most one of: `list_id`, or the set (`active_status`, `done_status`,
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
    #: Selects all the relevant “to do” notes (dsAll), only those that are done (dsDoneOnly), or
    #: only those that aren’t done (dsNotDoneOnly).
    #:
    #: Choose at most one of: `list_id`, or the set (`active_status`, `done_status`,
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    done_status: Literal["All", "DoneOnly", "NotDoneOnly"]
    #: Filters results to objects modified on or after this timestamp. QuickBooks Desktop
    #: accepts 1970-01-01 through 2038-01-19T03:14:07. If only a date is provided, time defaults
    #: to 00:00:00.
    #:
    #: Choose at most one of: `list_id`, or the set (`active_status`, `done_status`,
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    from_modified_date: str
    include_ret_element: List[Literal["CustomerRef", "EditSequence", "EmployeeRef", "IsActive", "IsDone", "LeadRef", "ListID", "Notes", "Priority", "ReminderDate", "ReminderTime", "TimeCreated", "TimeModified", "Type", "VendorRef"]]
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list family, not across the
    #: company file: customers, vendors, employees and other names share one sequence, every
    #: item type shares another, and each other list has its own.
    #:
    #: Choose at most one of: `list_id`, or the set (`active_status`, `done_status`,
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    list_id: List[str]
    #: Limits the number of objects that a query returns. (To get a count of how many objects
    #: could possibly be returned, use the `meta_data` query attribute.) If you include a
    #: `max_returned` value, it must be at least 1.
    #:
    #: QuickBooks doesn't page this query: at most this many records come back, in one answer,
    #: with no sign of whether more matched. Leave it out for every match, in one answer; one
    #: over 4 MB as the Web Connector sends it, about 3 MB of qbXML isn't kept (`error_type`
    #: `response_too_large`), so narrow a large one with its filters.
    #:
    #: Choose at most one of: `list_id`, or the set (`active_status`, `done_status`,
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    max_returned: int
    #: Use the `meta_data` attribute to control whether query responses include counts. Options
    #: are NoMetaData (default), MetaDataOnly (count only), and MetaDataAndResponseData (count
    #: plus objects). Counts are approximate and may vary slightly if records are created or
    #: deleted during processing.
    meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
    #: Filters according to the object’s Name.
    #:
    #: Choose at most one of: `list_id`, or the set (`active_status`, `done_status`,
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    name_filter: NameFilter
    #: Filters according to the object’s Name.
    #:
    #: Choose at most one of: `list_id`, or the set (`active_status`, `done_status`,
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    name_range_filter: NameRangeFilter
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: Filters results to objects modified on or before this timestamp. QuickBooks Desktop
    #: accepts 1970-01-01 through 2038-01-19T03:14:07. If only a date is provided, time defaults
    #: to end-of-day (23:59:59).
    #:
    #: Choose at most one of: `list_id`, or the set (`active_status`, `done_status`,
    #: `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    to_modified_date: str


class _ToDoUpdateParamsRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list family, not across the
    #: company file: customers, vendors, employees and other names share one sequence, every
    #: item type shares another, and each other list has its own.
    list_id: str


class ToDoUpdateParams(_ToDoUpdateParamsRequired, total=False):
    """Params for ``to_do.update`` (Update to do)."""
    #: `customer_ref` identifies a customer or customer job. If both `full_name` and `list_id`
    #: are provided, `full_name` is ignored. In SalesReceipt and ReceivePayment, it identifies
    #: who receives credit. In TimeTracking, it identifies who the time can be billed to and is
    #: required in TimeTrackingAdd when IsBillable is true.
    #:
    #: Choose at most one of: `customer_ref`, or `employee_ref`, or `lead_ref`, or `vendor_ref`.
    customer_ref: Ref
    #: The employee list contains payroll information about each of the company’s employees.
    #:
    #: Choose at most one of: `customer_ref`, or `employee_ref`, or `lead_ref`, or `vendor_ref`.
    employee_ref: Ref
    include_ret_element: List[Literal["CustomerRef", "EditSequence", "EmployeeRef", "ExternalGUID", "IsActive", "IsDone", "LeadRef", "ListID", "Notes", "OwnerID", "Priority", "ReminderDate", "ReminderTime", "TimeCreated", "TimeModified", "TxnID", "TxnNumber", "Type", "VendorRef"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: If `is_done` is true, this “to do” task has been completed. The default value of
    #: `is_done` is false.
    is_done: bool
    #: The lead list contains information about leads for a company.
    #:
    #: Choose at most one of: `customer_ref`, or `employee_ref`, or `lead_ref`, or `vendor_ref`.
    lead_ref: Ref
    #: Additional information.
    notes: str
    #: Priority may have one of the following values: Low [DEFAULT], Medium, High
    priority: Literal["High", "Low", "Medium"]
    #: The date on which the contents of the Notes string will appear on the Reminder list
    #: within QuickBooks.
    reminder_date: str
    #: The time on which the contents of the Notes string will appear on the Reminder list
    #: within QuickBooks.
    reminder_time: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: Type may have one of the following values: Task [DEFAULT], Call, Fax, Email, Meeting,
    #: Appointment
    type: Literal["Appointment", "Call", "Email", "Fax", "Meeting", "Task"]
    #: A vendor is any person or company from whom a small business owner buys goods and
    #: services. (Banks and tax agencies usually are included on the vendor list.) A company’s
    #: vendor list contains information such as account balance and contact information about
    #: each vendor. A `vendor_ref` aggregate refers to one of the vendors on the list.
    #:
    #: Choose at most one of: `customer_ref`, or `employee_ref`, or `lead_ref`, or `vendor_ref`.
    vendor_ref: Ref


class ToDo:
    """QuickBooks to do operations: create, query, update.

    Get it from ``client.to_do``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[ToDoCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create to do.

        Queues ``to_do.create``: POST /connections/{connection_id}/to-dos, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``ToDoCreateParams``)::

            customer_ref: Ref
                full_name: str
                list_id: str
            employee_ref: Ref
            include_ret_element: List[Literal[...] (one of 19 values)]
            is_active: bool
            is_done: bool
            lead_ref: Ref
            notes: str (required)
            priority: Literal["High", "Low", "Medium"]
            reminder_date: str
            reminder_time: str
            request_id: str
            type: Literal["Appointment", "Call", "Email", "Fax", "Meeting", "Task"]
            vendor_ref: Ref

        Docs: https://docs.qubesync.com/api-reference/v2/to-dos/create-to-do
        """
        return self._client._queue_operation("to_do.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[ToDoQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List to dos.

        Queues ``to_do.query``: GET /connections/{connection_id}/to-dos, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``ToDoQueryParams``)::

            active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
            done_status: Literal["All", "DoneOnly", "NotDoneOnly"]
            from_modified_date: str
            include_ret_element: List[Literal[...] (one of 15 values)]
            list_id: List[str]
            max_returned: int
            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            name_filter: NameFilter
                match_criterion: Literal["Contains", "EndsWith", "StartsWith"] (required)
                name: str (required)
            name_range_filter: NameRangeFilter
                from_name: str
                to_name: str
            request_id: str
            to_modified_date: str

        Docs: https://docs.qubesync.com/api-reference/v2/to-dos/list-to-dos
        """
        return self._client._queue_operation("to_do.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[ToDoUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update to do.

        Queues ``to_do.update``: PUT /connections/{connection_id}/to-dos, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``ToDoUpdateParams``)::

            customer_ref: Ref
                full_name: str
                list_id: str
            edit_sequence: str (required)
            employee_ref: Ref
            include_ret_element: List[Literal[...] (one of 19 values)]
            is_active: bool
            is_done: bool
            lead_ref: Ref
            list_id: str (required)
            notes: str
            priority: Literal["High", "Low", "Medium"]
            reminder_date: str
            reminder_time: str
            request_id: str
            type: Literal["Appointment", "Call", "Email", "Fax", "Meeting", "Task"]
            vendor_ref: Ref

        Docs: https://docs.qubesync.com/api-reference/v2/to-dos/update-to-do
        """
        return self._client._queue_operation("to_do.update", connection_id, params, webhook_url, idempotency_key)
