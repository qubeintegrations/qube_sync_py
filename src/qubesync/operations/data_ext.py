# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks data ext operations (``client.data_ext``)."""

from typing import Any, Dict, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    Ref,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _DataExtDelRequired(TypedDict):
    #: The name of the data extension. If this is a custom field, `data_ext_name` will be
    #: visible as a label in the QuickBooks user interface. Also because `owner_id` and
    #: `data_ext_name` together make the data extension unique, and because custom fields all
    #: have the same `owner_id` of zero, the `data_ext_name` must be a unique value among
    #: existing custom fields.
    data_ext_name: str
    #: `owner_id` identifies who owns the data extension. Use 0 for QuickBooks custom fields
    #: that appear in the UI, or use a GUID for private extensions owned by an app. Keep private
    #: GUIDs confidential unless you intentionally share extensions across apps. If you do share
    #: them, both apps must use the same `owner_id` and `data_ext_name`, because that pair
    #: uniquely identifies the extension.
    owner_id: str


class DataExtDel(_DataExtDelRequired, total=False):
    #: The type of list object (e.g. Customer) that this data extension is attached to.
    list_data_ext_type: Literal["Account", "Customer", "Employee", "Item", "OtherName", "Vendor"]
    #: Refers to a list object. In a DataExtAdd request, the list object ref must be the same
    #: type as the type specified in `list_data_ext_type`. If a `list_obj_ref` aggregate
    #: includes both `full_name` and `list_id`, `full_name` will be ignored.
    list_obj_ref: Ref
    #: Not supported.
    other_data_ext_type: Literal["Company"]
    #: The type of transaction that the data extension belongs to.
    txn_data_ext_type: Literal["ARRefundCreditCard", "Bill", "BillPaymentCheck", "BillPaymentCreditCard", "BuildAssembly", "Charge", "Check", "CreditCardCharge", "CreditCardCredit", "CreditMemo", "Deposit", "Estimate", "InventoryAdjustment", "Invoice", "ItemReceipt", "JournalEntry", "PurchaseOrder", "ReceivePayment", "SalesOrder", "SalesReceipt", "SalesTaxPaymentCheck", "VendorCredit"]
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    txn_id: str
    #: Identification number of the transaction line. (`txn_line_id` is supported as of v2.0 of
    #: the SDK. With qbXML v1.0 and v1.1, `txn_line_id` is always returned as zero.) If you need
    #: to add a new transaction line in a transaction Mod request, you can do so by setting the
    #: `txn_line_id` to -1.
    txn_line_id: str


class _DataExtCreateParamsRequired(TypedDict):
    #: The name of the data extension. If this is a custom field, `data_ext_name` will be
    #: visible as a label in the QuickBooks user interface. Also because `owner_id` and
    #: `data_ext_name` together make the data extension unique, and because custom fields all
    #: have the same `owner_id` of zero, the `data_ext_name` must be a unique value among
    #: existing custom fields.
    data_ext_name: str
    #: The data in this field. The maximum length of `data_ext_value` will depend on the
    #: `data_ext_type` of this data extension. For example, if `data_ext_type` is STR255TYPE,
    #: the maximum length of `data_ext_value` is 255 characters. If `data_ext_type` is
    #: STR1024TYPE, the maximum size of `data_ext_value` is 1KB.
    data_ext_value: str
    #: `owner_id` identifies who owns the data extension. Use 0 for QuickBooks custom fields
    #: that appear in the UI, or use a GUID for private extensions owned by an app. Keep private
    #: GUIDs confidential unless you intentionally share extensions across apps. If you do share
    #: them, both apps must use the same `owner_id` and `data_ext_name`, because that pair
    #: uniquely identifies the extension.
    owner_id: str


class DataExtCreateParams(_DataExtCreateParamsRequired, total=False):
    """Params for ``data_ext.create`` (Create data ext)."""
    #: The type of list object (e.g. Customer) that this data extension is attached to.
    list_data_ext_type: Literal["Account", "Customer", "Employee", "Item", "OtherName", "Vendor"]
    #: Refers to a list object. In a DataExtAdd request, the list object ref must be the same
    #: type as the type specified in `list_data_ext_type`. If a `list_obj_ref` aggregate
    #: includes both `full_name` and `list_id`, `full_name` will be ignored.
    list_obj_ref: Ref
    #: Not supported.
    other_data_ext_type: Literal["Company"]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: The type of transaction that the data extension belongs to.
    txn_data_ext_type: Literal["ARRefundCreditCard", "Bill", "BillPaymentCheck", "BillPaymentCreditCard", "BuildAssembly", "Charge", "Check", "CreditCardCharge", "CreditCardCredit", "CreditMemo", "Deposit", "Estimate", "InventoryAdjustment", "Invoice", "ItemReceipt", "JournalEntry", "PurchaseOrder", "ReceivePayment", "SalesOrder", "SalesReceipt", "SalesTaxPaymentCheck", "VendorCredit"]
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    txn_id: str
    #: Identification number of the transaction line. (`txn_line_id` is supported as of v2.0 of
    #: the SDK. With qbXML v1.0 and v1.1, `txn_line_id` is always returned as zero.) If you need
    #: to add a new transaction line in a transaction Mod request, you can do so by setting the
    #: `txn_line_id` to -1.
    txn_line_id: str


class _DataExtDeleteParamsRequired(TypedDict):
    #: DataExt The DataExtAdd request writes data to the specified data extension for the
    #: specified object. Before you can use a DataExtAdd message to populate a data-extension
    #: field with data, the field must be defined, either through the SDK via a DataExtDefAdd
    #: request or via the QuickBooks UI by the interactive user.
    data_ext_del: DataExtDel


class DataExtDeleteParams(_DataExtDeleteParamsRequired, total=False):
    """Params for ``data_ext.delete`` (Delete data ext)."""
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class _DataExtUpdateParamsRequired(TypedDict):
    #: The name of the data extension. If this is a custom field, `data_ext_name` will be
    #: visible as a label in the QuickBooks user interface. Also because `owner_id` and
    #: `data_ext_name` together make the data extension unique, and because custom fields all
    #: have the same `owner_id` of zero, the `data_ext_name` must be a unique value among
    #: existing custom fields.
    data_ext_name: str
    #: The data in this field. The maximum length of `data_ext_value` will depend on the
    #: `data_ext_type` of this data extension. For example, if `data_ext_type` is STR255TYPE,
    #: the maximum length of `data_ext_value` is 255 characters. If `data_ext_type` is
    #: STR1024TYPE, the maximum size of `data_ext_value` is 1KB.
    data_ext_value: str
    #: `owner_id` identifies who owns the data extension. Use 0 for QuickBooks custom fields
    #: that appear in the UI, or use a GUID for private extensions owned by an app. Keep private
    #: GUIDs confidential unless you intentionally share extensions across apps. If you do share
    #: them, both apps must use the same `owner_id` and `data_ext_name`, because that pair
    #: uniquely identifies the extension.
    owner_id: str


class DataExtUpdateParams(_DataExtUpdateParamsRequired, total=False):
    """Params for ``data_ext.update`` (Update data ext)."""
    #: The type of list object (e.g. Customer) that this data extension is attached to.
    list_data_ext_type: Literal["Account", "Customer", "Employee", "Item", "OtherName", "Vendor"]
    #: Refers to a list object. In a DataExtAdd request, the list object ref must be the same
    #: type as the type specified in `list_data_ext_type`. If a `list_obj_ref` aggregate
    #: includes both `full_name` and `list_id`, `full_name` will be ignored.
    list_obj_ref: Ref
    #: Not supported.
    other_data_ext_type: Literal["Company"]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: The type of transaction that the data extension belongs to.
    txn_data_ext_type: Literal["ARRefundCreditCard", "Bill", "BillPaymentCheck", "BillPaymentCreditCard", "BuildAssembly", "Charge", "Check", "CreditCardCharge", "CreditCardCredit", "CreditMemo", "Deposit", "Estimate", "InventoryAdjustment", "Invoice", "ItemReceipt", "JournalEntry", "PurchaseOrder", "ReceivePayment", "SalesOrder", "SalesReceipt", "SalesTaxPaymentCheck", "VendorCredit"]
    #: `txn_id` is the unique QuickBooks identifier for a transaction. Use it to reference that
    #: transaction in later requests. `txn_id` values are transaction-specific and should not be
    #: reused across unrelated transaction types.
    txn_id: str
    #: Identification number of the transaction line. (`txn_line_id` is supported as of v2.0 of
    #: the SDK. With qbXML v1.0 and v1.1, `txn_line_id` is always returned as zero.) If you need
    #: to add a new transaction line in a transaction Mod request, you can do so by setting the
    #: `txn_line_id` to -1.
    txn_line_id: str


class DataExt:
    """QuickBooks data ext operations: create, delete, update.

    Get it from ``client.data_ext``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[DataExtCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create data ext.

        Queues ``data_ext.create``: POST /connections/{connection_id}/data-exts, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``DataExtCreateParams``)::

            data_ext_name: str (required)
            data_ext_value: str (required)
            list_data_ext_type: Literal["Account", "Customer", "Employee", "Item", "OtherName", "Vendor"]
            list_obj_ref: Ref
                full_name: str
                list_id: str
            other_data_ext_type: Literal["Company"]
            owner_id: str (required)
            request_id: str
            txn_data_ext_type: Literal[...] (one of 22 values)
            txn_id: str
            txn_line_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/data-exts/create-data-ext
        """
        return self._client._queue_operation("data_ext.create", connection_id, params, webhook_url, idempotency_key)

    def delete(
        self,
        connection_id: str,
        params: Optional[DataExtDeleteParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Delete data ext.

        Queues ``data_ext.delete``: DELETE /connections/{connection_id}/data-exts, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``DataExtDeleteParams``)::

            data_ext_del: DataExtDel (required)
                data_ext_name: str (required)
                list_data_ext_type: Literal["Account", "Customer", "Employee", "Item", "OtherName", "Vendor"]
                list_obj_ref: Ref
                    full_name: str
                    list_id: str
                other_data_ext_type: Literal["Company"]
                owner_id: str (required)
                txn_data_ext_type: Literal[...] (one of 22 values)
                txn_id: str
                txn_line_id: str
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/data-exts/delete-data-ext
        """
        return self._client._queue_operation("data_ext.delete", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[DataExtUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update data ext.

        Queues ``data_ext.update``: PUT /connections/{connection_id}/data-exts, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``DataExtUpdateParams``)::

            data_ext_name: str (required)
            data_ext_value: str (required)
            list_data_ext_type: Literal["Account", "Customer", "Employee", "Item", "OtherName", "Vendor"]
            list_obj_ref: Ref
                full_name: str
                list_id: str
            other_data_ext_type: Literal["Company"]
            owner_id: str (required)
            request_id: str
            txn_data_ext_type: Literal[...] (one of 22 values)
            txn_id: str
            txn_line_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/data-exts/update-data-ext
        """
        return self._client._queue_operation("data_ext.update", connection_id, params, webhook_url, idempotency_key)
