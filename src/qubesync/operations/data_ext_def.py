# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks data ext def operations (``client.data_ext_def``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict


if TYPE_CHECKING:
    from ..v2 import Client


class _DataExtDefCreateParamsRequired(TypedDict):
    #: The name of the data extension. If this is a custom field, `data_ext_name` will be
    #: visible as a label in the QuickBooks user interface. Also because `owner_id` and
    #: `data_ext_name` together make the data extension unique, and because custom fields all
    #: have the same `owner_id` of zero, the `data_ext_name` must be a unique value among
    #: existing custom fields.
    data_ext_name: str
    #: The field’s data type, which corresponds to a qbXML data type. In an IDataExtDefAdd
    #: request object, if this is a custom field, `data_ext_type` must be detSTR255TYPE.
    data_ext_type: Literal["AMTTYPE", "DATETIMETYPE", "INTTYPE", "PERCENTTYPE", "PRICETYPE", "QUANTYPE", "STR1024TYPE", "STR255TYPE"]
    #: `owner_id` identifies who owns the data extension. Use 0 for QuickBooks custom fields
    #: that appear in the UI, or use a GUID for private extensions owned by an app. Keep private
    #: GUIDs confidential unless you intentionally share extensions across apps. If you do share
    #: them, both apps must use the same `owner_id` and `data_ext_name`, because that pair
    #: uniquely identifies the extension.
    owner_id: str


class DataExtDefCreateParams(_DataExtDefCreateParamsRequired, total=False):
    """Params for ``data_ext_def.create`` (Create data ext def)."""
    assign_to_object: List[Literal["ARRefundCreditCard", "Account", "Bill", "BillPaymentCheck", "BillPaymentCreditCard", "BuildAssembly", "Charge", "Check", "Company", "CreditCardCharge", "CreditCardCredit", "CreditMemo", "Customer", "Deposit", "Employee", "Estimate", "InventoryAdjustment", "Invoice", "Item", "ItemReceipt", "JournalEntry", "OtherName", "PurchaseOrder", "ReceivePayment", "SalesOrder", "SalesReceipt", "SalesTaxPaymentCheck", "Vendor", "VendorCredit"]]
    #: The string format required for the data extension.
    data_ext_format_string: str
    #: If `data_ext_list_require` is true, this data extension field is required to be entered
    #: in lists. The default value is false.
    data_ext_list_require: bool
    #: If `data_ext_txn_require` is true, this data extension field is required to be entered in
    #: transaction. The default value is false.
    data_ext_txn_require: bool
    include_ret_element: List[Literal["AssignToObject", "DataExtFormatString", "DataExtID", "DataExtListRequire", "DataExtName", "DataExtTxnRequire", "DataExtType", "EditSequence", "ExternalGUID", "ListID", "OwnerID", "TxnID", "TxnNumber"]]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class _DataExtDefDeleteParamsRequired(TypedDict):
    #: The name of the data extension. If this is a custom field, `data_ext_name` will be
    #: visible as a label in the QuickBooks user interface. Also because `owner_id` and
    #: `data_ext_name` together make the data extension unique, and because custom fields all
    #: have the same `owner_id` of zero, the `data_ext_name` must be a unique value among
    #: existing custom fields.
    data_ext_name: str
    #: `owner_id` identifies the extension owner. `owner_id` 0 means a public custom field
    #: visible in the QuickBooks UI. A GUID means a private app extension that is not shown in
    #: the UI. `owner_id` matching is case-insensitive. To share private extensions across apps,
    #: both apps must use the same `owner_id` and `data_ext_name`.
    owner_id: str


class DataExtDefDeleteParams(_DataExtDefDeleteParamsRequired, total=False):
    """Params for ``data_ext_def.delete`` (Delete data ext def)."""
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class DataExtDefQueryParams(TypedDict, total=False):
    """Params for ``data_ext_def.query`` (List data ext defs)."""
    #: Choose at most one of: `owner_id`, or `assign_to_object`.
    assign_to_object: List[Literal["ARRefundCreditCard", "Account", "Bill", "BillPaymentCheck", "BillPaymentCreditCard", "BuildAssembly", "Charge", "Check", "Company", "CreditCardCharge", "CreditCardCredit", "CreditMemo", "Customer", "Deposit", "Employee", "Estimate", "InventoryAdjustment", "Invoice", "Item", "ItemReceipt", "JournalEntry", "OtherName", "PurchaseOrder", "ReceivePayment", "SalesOrder", "SalesReceipt", "SalesTaxPaymentCheck", "Vendor", "VendorCredit"]]
    include_ret_element: List[Literal["AssignToObject", "DataExtFormatString", "DataExtID", "DataExtListRequire", "DataExtName", "DataExtTxnRequire", "DataExtType", "OwnerID"]]
    #: Use the `meta_data` attribute to control whether query responses include counts. Options
    #: are NoMetaData (default), MetaDataOnly (count only), and MetaDataAndResponseData (count
    #: plus objects). Counts are approximate and may vary slightly if records are created or
    #: deleted during processing.
    meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
    #: `owner_id` identifies who owns the data extension. Use 0 for QuickBooks custom fields
    #: that appear in the UI, or use a GUID for private extensions owned by an app. Keep private
    #: GUIDs confidential unless you intentionally share extensions across apps. If you do share
    #: them, both apps must use the same `owner_id` and `data_ext_name`, because that pair
    #: uniquely identifies the extension.
    #:
    #: Choose at most one of: `owner_id`, or `assign_to_object`.
    owner_id: List[str]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class _DataExtDefUpdateParamsRequired(TypedDict):
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


class DataExtDefUpdateParams(_DataExtDefUpdateParamsRequired, total=False):
    """Params for ``data_ext_def.update`` (Update data ext def)."""
    assign_to_object: List[Literal["ARRefundCreditCard", "Account", "Bill", "BillPaymentCheck", "BillPaymentCreditCard", "BuildAssembly", "Charge", "Check", "Company", "CreditCardCharge", "CreditCardCredit", "CreditMemo", "Customer", "Deposit", "Employee", "Estimate", "InventoryAdjustment", "Invoice", "Item", "ItemReceipt", "JournalEntry", "OtherName", "PurchaseOrder", "ReceivePayment", "SalesOrder", "SalesReceipt", "SalesTaxPaymentCheck", "Vendor", "VendorCredit"]]
    #: The string format required for the data extension.
    data_ext_format_string: str
    #: If `data_ext_list_require` is true, this data extension field is required to be entered
    #: in lists. The default value is false.
    data_ext_list_require: bool
    #: The new name for this field. Note that in the case of custom fields, `data_ext_new_name`
    #: can run into name conflicts, because the name space of custom fields (data extensions
    #: with an `owner_id` of 0) is shared by all applications.
    data_ext_new_name: str
    #: If `data_ext_txn_require` is true, this data extension field is required to be entered in
    #: transaction. The default value is false.
    data_ext_txn_require: bool
    include_ret_element: List[Literal["AssignToObject", "DataExtFormatString", "DataExtID", "DataExtListRequire", "DataExtName", "DataExtTxnRequire", "DataExtType", "EditSequence", "ExternalGUID", "ListID", "OwnerID", "TxnID", "TxnNumber"]]
    remove_from_object: List[Literal["ARRefundCreditCard", "Account", "Bill", "BillPaymentCheck", "BillPaymentCreditCard", "BuildAssembly", "Charge", "Check", "Company", "CreditCardCharge", "CreditCardCredit", "CreditMemo", "Customer", "Deposit", "Employee", "Estimate", "InventoryAdjustment", "Invoice", "Item", "ItemReceipt", "JournalEntry", "OtherName", "PurchaseOrder", "ReceivePayment", "SalesOrder", "SalesReceipt", "SalesTaxPaymentCheck", "Vendor", "VendorCredit"]]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class DataExtDef:
    """QuickBooks data ext def operations: create, delete, query, update.

    Get it from ``client.data_ext_def``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[DataExtDefCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create data ext def.

        Queues ``data_ext_def.create``: POST /connections/{connection_id}/data-ext-defs, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``DataExtDefCreateParams``)::

            assign_to_object: List[Literal[...] (one of 29 values)]
            data_ext_format_string: str
            data_ext_list_require: bool
            data_ext_name: str (required)
            data_ext_txn_require: bool
            data_ext_type: Literal[...] (one of 8 values) (required)
            include_ret_element: List[Literal[...] (one of 13 values)]
            owner_id: str (required)
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/data-ext-defs/create-data-ext-def
        """
        return self._client._queue_operation("data_ext_def.create", connection_id, params, webhook_url, idempotency_key)

    def delete(
        self,
        connection_id: str,
        params: Optional[DataExtDefDeleteParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Delete data ext def.

        Queues ``data_ext_def.delete``: DELETE /connections/{connection_id}/data-ext-defs, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``DataExtDefDeleteParams``)::

            data_ext_name: str (required)
            owner_id: str (required)
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/data-ext-defs/delete-data-ext-def
        """
        return self._client._queue_operation("data_ext_def.delete", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[DataExtDefQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List data ext defs.

        Queues ``data_ext_def.query``: GET /connections/{connection_id}/data-ext-defs, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``DataExtDefQueryParams``)::

            assign_to_object: List[Literal[...] (one of 29 values)]
            include_ret_element: List[Literal[...] (one of 8 values)]
            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            owner_id: List[str]
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/data-ext-defs/list-data-ext-defs
        """
        return self._client._queue_operation("data_ext_def.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[DataExtDefUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update data ext def.

        Queues ``data_ext_def.update``: PUT /connections/{connection_id}/data-ext-defs, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``DataExtDefUpdateParams``)::

            assign_to_object: List[Literal[...] (one of 29 values)]
            data_ext_format_string: str
            data_ext_list_require: bool
            data_ext_name: str (required)
            data_ext_new_name: str
            data_ext_txn_require: bool
            include_ret_element: List[Literal[...] (one of 13 values)]
            owner_id: str (required)
            remove_from_object: List[Literal[...] (one of 29 values)]
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/data-ext-defs/update-data-ext-def
        """
        return self._client._queue_operation("data_ext_def.update", connection_id, params, webhook_url, idempotency_key)
