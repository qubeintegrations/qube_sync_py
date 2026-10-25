# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks charge operations (``client.charge``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    DateRangeFilter,
    EntityFilter,
    ModifiedDateRangeFilter,
    Ref,
    RefNumberFilter,
    RefNumberRangeFilter,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _ChargeCreateParamsRequired(TypedDict):
    #: `customer_ref` identifies a customer or customer job. If both `full_name` and `list_id`
    #: are provided, `full_name` is ignored. In SalesReceipt and ReceivePayment, it identifies
    #: who receives credit. In TimeTracking, it identifies who the time can be billed to and is
    #: required in TimeTrackingAdd when IsBillable is true.
    customer_ref: Ref


class ChargeCreateParams(_ChargeCreateParamsRequired, total=False):
    """Params for ``charge.create`` (Create charge)."""
    #: A monetary amount.
    amount: float
    #: `ar_account_ref` points to an Accounts Receivable account. If both `full_name` and
    #: `list_id` are provided, `full_name` is ignored.
    ar_account_ref: Ref
    #: The date when the customer was billed for what is now being charged to their credit card.
    #: (`billed_date` is the same as the date listed on an invoice or, for a statement charge,
    #: the date entered in the Statement Date field when the statement was printed.)
    billed_date: str
    #: Use classes to categorize transactions (for example, by department, location, or work
    #: type). Class tracking is off by default in QuickBooks. A `class_ref` points to one class;
    #: if both `full_name` and `list_id` are provided, `full_name` is ignored. In InvoiceAdd, a
    #: header-level `class_ref` is applied to line items unless you override or clear it on
    #: individual lines.
    class_ref: Ref
    #: `def_macro` lets you assign a reusable name to a returned `txn_id` or `txn_line_id` so
    #: later requests can reference it with `useMacro`. This feature requires SDK 2.0+.
    def_macro: str
    #: A descriptive text field.
    desc: str
    #: The date on which payment is due.
    due_date: str
    #: Allows for the attachment of a user defined GUID value.
    external_guid: str
    include_ret_element: List[Literal["ARAccountRef", "Amount", "BalanceRemaining", "BilledDate", "ClassRef", "CustomerRef", "DataExtRet", "Desc", "DueDate", "EditSequence", "ExternalGUID", "InventorySiteLocationRef", "InventorySiteRef", "IsPaid", "ItemRef", "LinkedTxn", "ListID", "OverrideUOMSetRef", "OwnerID", "Quantity", "Rate", "RefNumber", "TimeCreated", "TimeModified", "TxnDate", "TxnID", "TxnNumber", "UnitOfMeasure"]]
    #: Location within the Inventory Site
    inventory_site_location_ref: Ref
    #: Site where inventory is located.
    inventory_site_ref: Ref
    #: `item_ref` may accept all item types or a restricted subset, depending on the request.
    #: Examples: PurchaseOrder and Bill do not allow discount or sales-tax items;
    #: VehicleMileageAdd requires a service or other-charge item; BillingRateAdd requires a
    #: service item. If both `full_name` and `list_id` are provided, `full_name` is ignored.
    item_ref: Ref
    #: Flag to override price rule conflict.
    option_for_price_rule_conflict: Literal["BasePrice", "Zero"]
    #: Refers to a QuickBooks account. If an `override_item_account_ref` aggregate includes both
    #: `full_name` and `list_id`, `full_name` will be ignored.
    override_item_account_ref: Ref
    #: On transaction lines, QuickBooks can derive one value from the other two among Quantity,
    #: Rate, and Amount. If you supply Quantity and Amount, QuickBooks calculates Rate. If you
    #: supply Quantity and Rate, QuickBooks calculates Amount.
    quantity: float
    #: Indicates the price of something.
    rate: float
    #: `ref_number` is a user-managed transaction reference (for example, a check number). It
    #: can be edited and is not guaranteed to be globally unique. Some transaction types
    #: auto-populate `ref_number` when omitted, based on QuickBooks preferences and numbering
    #: state.
    ref_number: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: The date of the transaction. In some cases, if you leave `txn_date` out of an -Add
    #: message, QuickBooks will prefill `txn_date` with the date of the last-saved transaction
    #: of the same type.
    txn_date: str
    #: In a transaction line item, the name of the unit of measure selected from within the
    #: item’s available units. If the company file is enabled only for single unit of measure
    #: per item, this must be the base unit!
    unit_of_measure: str


class ChargeQueryParams(TypedDict, total=False):
    """Params for ``charge.query`` (List charges)."""
    #: Filters according to the account name or `list_id`. If the “Use account numbers”
    #: preference is enabled in the QuickBooks company file, you can specify an account number
    #: (instead of an account name) for `full_name` and get the account you’re looking for. But
    #: if numbers have been used as account names, confusion could arise.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `paid_status`, `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`).
    #: Members of a set combine with each other, not with the other choices.
    account_filter: EntityFilter
    #: An entity refers to a person on the QuickBooks Customer list, Vendor list, Employee list,
    #: or Other Names list. You can use an EntityQuery request to get information about all the
    #: entities that are set up in the QuickBooks file. In an ARRefundCreditCard query, this
    #: must be a customer/customer job.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `paid_status`, `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`).
    #: Members of a set combine with each other, not with the other choices.
    entity_filter: EntityFilter
    #: If you set `include_linked_txns` to true, then the returned object will include a list of
    #: all the transactions linked to the queried object. (This list is similar to the History
    #: view of a transaction in the user interface, but not identical, as the SDK list contains
    #: only linked transactions, not items.) Each linked transaction will be represented by a
    #: `linked_txn` aggregate.
    include_linked_txns: bool
    include_ret_element: List[Literal["ARAccountRef", "Amount", "BalanceRemaining", "BilledDate", "ClassRef", "CustomerRef", "DataExtRet", "Desc", "DueDate", "EditSequence", "ExternalGUID", "InventorySiteLocationRef", "InventorySiteRef", "IsPaid", "ItemRef", "LinkedTxn", "OverrideUOMSetRef", "Quantity", "Rate", "RefNumber", "TimeCreated", "TimeModified", "TxnDate", "TxnID", "TxnNumber", "UnitOfMeasure"]]
    #: Page through every match: QuBe Sync asks QuickBooks for each page in turn and sends each
    #: to your `webhook_url` as it arrives, all with the same `id`. On by default, with pages of
    #: 100 records (25 with `include_linked_txns`); send `iterator=true` with `max_returned` for
    #: another size. Off when you send `iterator=false` (every match in one answer) or
    #: `max_returned` alone (at most that many, in one answer). It pages a filtered query only:
    #: with `ref_number`, `ref_number_case_sensitive` or `txn_id` every match comes back in one
    #: answer, so leave `iterator` out.
    iterator: bool
    #: Limits the number of objects that a query returns. (To get a count of how many objects
    #: could possibly be returned, use the `meta_data` query attribute.) If you include a
    #: `max_returned` value, it must be at least 1.
    #:
    #: The page size, with `iterator=true`. Sent without `iterator`, or with `iterator=false`,
    #: it's a cap instead: at most this many records come back, in one answer, and QuickBooks
    #: doesn't say whether more matched.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `paid_status`, `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`).
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
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `paid_status`, `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`).
    #: Members of a set combine with each other, not with the other choices.
    modified_date_range_filter: ModifiedDateRangeFilter
    #: `owner_id` identifies who owns the data extension. Use 0 for QuickBooks custom fields
    #: that appear in the UI, or use a GUID for private extensions owned by an app. Keep private
    #: GUIDs confidential unless you intentionally share extensions across apps. If you do share
    #: them, both apps must use the same `owner_id` and `data_ext_name`, because that pair
    #: uniquely identifies the extension.
    owner_id: List[str]
    #: Allows you to filter for transactions according to whether or not they are paid.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `paid_status`, `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`).
    #: Members of a set combine with each other, not with the other choices.
    paid_status: Literal["All", "NotPaidOnly", "PaidOnly"]
    #: `ref_number` is a user-managed transaction reference (for example, a check number). It
    #: can be edited and is not guaranteed to be globally unique. Some transaction types
    #: auto-populate `ref_number` when omitted, based on QuickBooks preferences and numbering
    #: state.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `paid_status`, `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`).
    #: Members of a set combine with each other, not with the other choices.
    ref_number: List[str]
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `paid_status`, `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`).
    #: Members of a set combine with each other, not with the other choices.
    ref_number_case_sensitive: List[str]
    #: Filters by `ref_number` range. Numeric-only bounds are compared numerically; otherwise
    #: comparison is lexicographic.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `paid_status`, `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`).
    #: Members of a set combine with each other, not with the other choices.
    ref_number_filter: RefNumberFilter
    #: Filters by `ref_number` range. Numeric-only bounds are compared numerically; otherwise
    #: comparison is lexicographic.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `paid_status`, `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`).
    #: Members of a set combine with each other, not with the other choices.
    ref_number_range_filter: RefNumberRangeFilter
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: Filters according to the original transaction dates.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `paid_status`, `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`).
    #: Members of a set combine with each other, not with the other choices.
    txn_date_range_filter: DateRangeFilter
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    #:
    #: Choose at most one of: `txn_id`, or `ref_number`, or `ref_number_case_sensitive`, or the
    #: set (`account_filter`, `entity_filter`, `max_returned`, `modified_date_range_filter`,
    #: `paid_status`, `ref_number_filter`, `ref_number_range_filter`, `txn_date_range_filter`).
    #: Members of a set combine with each other, not with the other choices.
    txn_id: List[str]


class _ChargeUpdateParamsRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    txn_id: str


class ChargeUpdateParams(_ChargeUpdateParamsRequired, total=False):
    """Params for ``charge.update`` (Update charge)."""
    #: A monetary amount.
    amount: float
    #: `ar_account_ref` points to an Accounts Receivable account. If both `full_name` and
    #: `list_id` are provided, `full_name` is ignored.
    ar_account_ref: Ref
    #: The date when the customer was billed for what is now being charged to their credit card.
    #: (`billed_date` is the same as the date listed on an invoice or, for a statement charge,
    #: the date entered in the Statement Date field when the statement was printed.)
    billed_date: str
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
    #: A descriptive text field.
    desc: str
    #: The date on which payment is due.
    due_date: str
    include_ret_element: List[Literal["ARAccountRef", "Amount", "BalanceRemaining", "BilledDate", "ClassRef", "CustomerRef", "DataExtRet", "Desc", "DueDate", "EditSequence", "ExternalGUID", "InventorySiteLocationRef", "InventorySiteRef", "IsPaid", "ItemRef", "LinkedTxn", "ListID", "OverrideUOMSetRef", "OwnerID", "Quantity", "Rate", "RefNumber", "TimeCreated", "TimeModified", "TxnDate", "TxnID", "TxnNumber", "UnitOfMeasure"]]
    #: Location within the Inventory Site.
    inventory_site_location_ref: Ref
    #: Site where inventory is located.
    inventory_site_ref: Ref
    #: `item_ref` may accept all item types or a restricted subset, depending on the request.
    #: Examples: PurchaseOrder and Bill do not allow discount or sales-tax items;
    #: VehicleMileageAdd requires a service or other-charge item; BillingRateAdd requires a
    #: service item. If both `full_name` and `list_id` are provided, `full_name` is ignored.
    item_ref: Ref
    #: Flag to override price rule conflict
    option_for_price_rule_conflict: Literal["BasePrice", "Zero"]
    #: Refers to a QuickBooks account. If an `override_item_account_ref` aggregate includes both
    #: `full_name` and `list_id`, `full_name` will be ignored.
    override_item_account_ref: Ref
    #: When you modify a transaction line to change the unit of measure used in that line, you
    #: use this aggregate to specify the UOM set within which you are choosing an available unit
    #: of measure. The “override” here refers to the unit within the set, not the UOM Set
    #: itself, which you can’t change or override–the UOM set that can be set or changed only in
    #: the item itself via an Item Mod request.
    override_uom_set_ref: Ref
    #: On transaction lines, QuickBooks can derive one value from the other two among Quantity,
    #: Rate, and Amount. If you supply Quantity and Amount, QuickBooks calculates Rate. If you
    #: supply Quantity and Rate, QuickBooks calculates Amount.
    quantity: float
    #: Indicates the price of something.
    rate: float
    #: `ref_number` is a user-managed transaction reference (for example, a check number). It
    #: can be edited and is not guaranteed to be globally unique. Some transaction types
    #: auto-populate `ref_number` when omitted, based on QuickBooks preferences and numbering
    #: state.
    ref_number: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: The date of the transaction. In some cases, if you leave `txn_date` out of an -Add
    #: message, QuickBooks will prefill `txn_date` with the date of the last-saved transaction
    #: of the same type.
    txn_date: str
    #: In a transaction line item, the name of the unit of measure selected from within the
    #: item’s available units. If the company file is enabled only for single unit of measure
    #: per item, this must be the base unit!
    unit_of_measure: str


class Charge:
    """QuickBooks charge operations: create, query, update.

    Get it from ``client.charge``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[ChargeCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create charge.

        Queues ``charge.create``: POST /connections/{connection_id}/charges, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``ChargeCreateParams``)::

            amount: float
            ar_account_ref: Ref
                full_name: str
                list_id: str
            billed_date: str
            class_ref: Ref
            customer_ref: Ref (required)
            def_macro: str
            desc: str
            due_date: str
            external_guid: str
            include_ret_element: List[Literal[...] (one of 28 values)]
            inventory_site_location_ref: Ref
            inventory_site_ref: Ref
            item_ref: Ref
            option_for_price_rule_conflict: Literal["BasePrice", "Zero"]
            override_item_account_ref: Ref
            quantity: float
            rate: float
            ref_number: str
            request_id: str
            txn_date: str
            unit_of_measure: str

        Docs: https://docs.qubesync.com/api-reference/v2/charges/create-charge
        """
        return self._client._queue_operation("charge.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[ChargeQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List charges.

        Queues ``charge.query``: GET /connections/{connection_id}/charges, params in the query string.
        QuickBooks answers in pages: each page comes to ``webhook_url`` as its own webhook.
        Returns the queued request.

        Params (``ChargeQueryParams``)::

            account_filter: EntityFilter
                full_name: List[str]
                full_name_with_children: str
                list_id: List[str]
                list_id_with_children: str
            entity_filter: EntityFilter
            include_linked_txns: bool
            include_ret_element: List[Literal[...] (one of 26 values)]
            iterator: bool
            max_returned: int
            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            modified_date_range_filter: ModifiedDateRangeFilter
                from_modified_date: str
                to_modified_date: str
            owner_id: List[str]
            paid_status: Literal["All", "NotPaidOnly", "PaidOnly"]
            ref_number: List[str]
            ref_number_case_sensitive: List[str]
            ref_number_filter: RefNumberFilter
                match_criterion: Literal["Contains", "EndsWith", "StartsWith"] (required)
                ref_number: str (required)
            ref_number_range_filter: RefNumberRangeFilter
                from_ref_number: str
                to_ref_number: str
            request_id: str
            txn_date_range_filter: DateRangeFilter
                date_macro: Literal[...] (one of 34 values)
                from_txn_date: str
                to_txn_date: str
            txn_id: List[str]

        Docs: https://docs.qubesync.com/api-reference/v2/charges/list-charges
        """
        return self._client._queue_operation("charge.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[ChargeUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update charge.

        Queues ``charge.update``: PUT /connections/{connection_id}/charges, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``ChargeUpdateParams``)::

            amount: float
            ar_account_ref: Ref
                full_name: str
                list_id: str
            billed_date: str
            class_ref: Ref
            customer_ref: Ref
            desc: str
            due_date: str
            edit_sequence: str (required)
            include_ret_element: List[Literal[...] (one of 28 values)]
            inventory_site_location_ref: Ref
            inventory_site_ref: Ref
            item_ref: Ref
            option_for_price_rule_conflict: Literal["BasePrice", "Zero"]
            override_item_account_ref: Ref
            override_uom_set_ref: Ref
            quantity: float
            rate: float
            ref_number: str
            request_id: str
            txn_date: str
            txn_id: str (required)
            unit_of_measure: str

        Docs: https://docs.qubesync.com/api-reference/v2/charges/update-charge
        """
        return self._client._queue_operation("charge.update", connection_id, params, webhook_url, idempotency_key)
