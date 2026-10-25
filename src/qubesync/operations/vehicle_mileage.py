# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks vehicle mileage operations (``client.vehicle_mileage``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    DateRangeFilter,
    ModifiedDateRangeFilter,
    Ref,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _VehicleMileageCreateParamsRequired(TypedDict):
    #: A vehicle for use in VehicleMileage transactions. Each vehicle name must be unique.
    vehicle_ref: Ref


class VehicleMileageCreateParams(_VehicleMileageCreateParamsRequired, total=False):
    """Params for ``vehicle_mileage.create`` (Create vehicle mileage)."""
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
    include_ret_element: List[Literal["BillableAmount", "BillableRate", "BillableStatus", "ClassRef", "CustomerRef", "EditSequence", "ExternalGUID", "ItemRef", "ListID", "Notes", "OdometerEnd", "OdometerStart", "OwnerID", "StandardMileageRate", "StandardMileageTotalAmount", "TimeCreated", "TimeModified", "TotalMiles", "TripEndDate", "TripStartDate", "TxnID", "TxnNumber", "VehicleRef"]]
    #: `item_ref` may accept all item types or a restricted subset, depending on the request.
    #: Examples: PurchaseOrder and Bill do not allow discount or sales-tax items;
    #: VehicleMileageAdd requires a service or other-charge item; BillingRateAdd requires a
    #: service item. If both `full_name` and `list_id` are provided, `full_name` is ignored.
    item_ref: Ref
    #: Additional information.
    notes: str
    #: Odometer reading at the end of the trip. `odometer_start` and `odometer_end` must both be
    #: specified if `total_miles` isn’t specified. QuickBooks will calculate the total trip
    #: miles from these two values. If `total_miles` is specified, you can’t specify
    #: `odometer_start` and `odometer_end`.
    odometer_end: float
    #: Odometer reading at the start of the trip. `odometer_start` and `odometer_end` must both
    #: be specified if `total_miles` isn’t specified. QuickBooks will calculate the total trip
    #: miles from these two values. If `total_miles` is specified, you can’t specify
    #: `odometer_start` and `odometer_end`.
    odometer_start: float
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: Total trip miles. If `total_miles` is specified, you can’t specify `odometer_start` and
    #: `odometer_end`. If you use `odometer_start` and `odometer_end` instead of `total_miles`,
    #: QuickBooks will calculate the total trip miles from these two values.
    total_miles: float
    #: Date the trip ended. If left blank, the current date at the time of transaction will be
    #: used. Notice that only dates are supported for vehicle mileage, so make sure you enter
    #: any datetime values with dates only, no time values. That is, 2002-02-02 will work for
    #: trip end date or start date, but 2002-02-02T12:20:20 won’t work.
    trip_end_date: str
    #: Date the trip began. If left blank, the current date at the time of transaction will be
    #: used. Notice that only dates are supported for vehicle mileage, so make sure you enter
    #: any datetime values with dates only, no time values. That is, 2002-02-02 will work for
    #: trip end date or start date, but 2002-02-02T12:20:20 won’t work.
    trip_start_date: str


class VehicleMileageQueryParams(TypedDict, total=False):
    """Params for ``vehicle_mileage.query`` (List vehicle mileages)."""
    include_ret_element: List[Literal["BillableAmount", "BillableRate", "BillableStatus", "ClassRef", "CustomerRef", "EditSequence", "ItemRef", "Notes", "OdometerEnd", "OdometerStart", "StandardMileageRate", "StandardMileageTotalAmount", "TimeCreated", "TimeModified", "TotalMiles", "TripEndDate", "TripStartDate", "TxnID", "VehicleRef"]]
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


class VehicleMileage:
    """QuickBooks vehicle mileage operations: create, query.

    Get it from ``client.vehicle_mileage``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[VehicleMileageCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create vehicle mileage.

        Queues ``vehicle_mileage.create``: POST /connections/{connection_id}/vehicle-mileages, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``VehicleMileageCreateParams``)::

            billable_status: Literal["Billable", "HasBeenBilled", "NotBillable"]
            class_ref: Ref
                full_name: str
                list_id: str
            customer_ref: Ref
            def_macro: str
            include_ret_element: List[Literal[...] (one of 23 values)]
            item_ref: Ref
            notes: str
            odometer_end: float
            odometer_start: float
            request_id: str
            total_miles: float
            trip_end_date: str
            trip_start_date: str
            vehicle_ref: Ref (required)

        Docs: https://docs.qubesync.com/api-reference/v2/vehicle-mileages/create-vehicle-mileage
        """
        return self._client._queue_operation("vehicle_mileage.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[VehicleMileageQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List vehicle mileages.

        Queues ``vehicle_mileage.query``: GET /connections/{connection_id}/vehicle-mileages, params in the query string.
        QuickBooks answers in pages: each page comes to ``webhook_url`` as its own webhook.
        Returns the queued request.

        Params (``VehicleMileageQueryParams``)::

            include_ret_element: List[Literal[...] (one of 19 values)]
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

        Docs: https://docs.qubesync.com/api-reference/v2/vehicle-mileages/list-vehicle-mileages
        """
        return self._client._queue_operation("vehicle_mileage.query", connection_id, params, webhook_url, idempotency_key)
