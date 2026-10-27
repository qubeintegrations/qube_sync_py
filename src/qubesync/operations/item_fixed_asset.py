# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks item fixed asset operations (``client.item_fixed_asset``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    EntityFilter,
    ItemDiscountBarCode,
    NameFilter,
    NameRangeFilter,
    Ref,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _FixedAssetSalesInfoRequired(TypedDict):
    #: Date when a fixed asset was sold.
    sales_date: str
    #: Appears in the Description column of a sales form when the QuickBooks user sells this
    #: item. For a fixed asset, describes the sale of the asset (for accounting purposes).
    sales_desc: str


class FixedAssetSalesInfo(_FixedAssetSalesInfoRequired, total=False):
    #: Any expenses that were incurred during the sale of a fixed asset.
    sales_expense: float
    #: Price charged for this item.
    sales_price: float


class FixedAssetSalesInfoMod(TypedDict, total=False):
    #: Date when a fixed asset was sold.
    sales_date: str
    #: Appears in the Description column of a sales form when the QuickBooks user sells this
    #: item. For a fixed asset, describes the sale of the asset (for accounting purposes).
    sales_desc: str
    #: Any expenses that were incurred during the sale of a fixed asset.
    sales_expense: float
    #: Price charged for this item.
    sales_price: float


class _ItemFixedAssetCreateParamsRequired(TypedDict):
    #: Indicates whether this item was new or used when the business acquired it.
    acquired_as: Literal["New", "Old"]
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because `full_name` remains distinct.
    name: str
    #: The date when this asset was purchased.
    purchase_date: str
    #: Description that appears in the Description column of checks, bills, credit card charges,
    #: and item receipts (when an item is reordered). For a fixed asset, a description of the
    #: item as it was when it was purchased.
    purchase_desc: str


class ItemFixedAssetCreateParams(_ItemFixedAssetCreateParamsRequired, total=False):
    """Params for ``item_fixed_asset.create`` (Create item fixed asset)."""
    #: Refers to the account QuickBooks uses to track the current value of the company’s
    #: inventory. (The AccountType of this account will be FixedAsset, OtherAsset, or
    #: OtherCurrentAsset.) In a request, if an `asset_account_ref` aggregate includes both
    #: `full_name` and `list_id`, `full_name` will be ignored.
    asset_account_ref: Ref
    #: Description of the asset—maker, brand, and so on.
    asset_desc: str
    #: The number used by the QuickBooks Fixed Asset Manager to identify this asset.
    asset_number: str
    #: Barcode reference information.
    bar_code: ItemDiscountBarCode
    #: Use classes to categorize transactions (for example, by department, location, or work
    #: type). Class tracking is off by default in QuickBooks. A `class_ref` points to one class;
    #: if both `full_name` and `list_id` are provided, `full_name` is ignored. In InvoiceAdd, a
    #: header-level `class_ref` is applied to line items unless you override or clear it on
    #: individual lines.
    class_ref: Ref
    #: The total cost of the fixed asset. This can include the cost of improvements or repairs.
    #: This amount is used to figure depreciation.
    cost_basis: float
    #: Allows for the attachment of a user defined GUID value.
    external_guid: str
    #: Sales information, if this fixed asset was sold.
    fixed_asset_sales_info: FixedAssetSalesInfo
    include_ret_element: List[Literal["AcquiredAs", "AssetAccountRef", "AssetDesc", "AssetNumber", "BarCodeValue", "ClassRef", "CostBasis", "DataExtRet", "EditSequence", "ExternalGUID", "FixedAssetSalesInfo", "IsActive", "ListID", "Location", "Name", "Notes", "OwnerID", "PONumber", "PurchaseCost", "PurchaseDate", "PurchaseDesc", "SerialNumber", "TimeCreated", "TimeModified", "TxnID", "TxnNumber", "VendorOrPayeeName", "WarrantyExpDate", "YearEndAccumulatedDepreciation", "YearEndBookValue"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: Where the asset is located or has been placed into service.
    location: str
    #: Additional information.
    notes: str
    #: Purchase order number.
    po_number: str
    #: Amount that the QuickBooks user expects to pay when ordering or buying this item, or the
    #: amount that was actually paid for this item.
    purchase_cost: float
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: The serial number of the asset.
    serial_number: str
    #: The name of the vendor from whom this asset was purchased.
    vendor_or_payee_name: str
    #: The date when the warranty for this asset expires.
    warranty_exp_date: str
    #: The amount the fixed asset has lost in value since it was purchased, as of the end of the
    #: year.
    year_end_accumulated_depreciation: float
    #: A reasonable estimate of the sales value of the fixed asset, as of the end of the year.
    year_end_book_value: float


class ItemFixedAssetQueryParams(TypedDict, total=False):
    """Params for ``item_fixed_asset.query`` (List item fixed assets)."""
    #: Used in filters to select list objects based on whether or not they are currently enabled
    #: for use by QuickBooks. The default value is asActiveOnly, which selects only list objects
    #: that are active.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
    #: Filters according to the object’s class.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    class_filter: EntityFilter
    #: Filters results to objects modified on or after this timestamp. QuickBooks Desktop
    #: accepts 1970-01-01 through 2038-01-19T03:14:07. If only a date is provided, time defaults
    #: to 00:00:00.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    from_modified_date: str
    #: `full_name` (along with `list_id`) is a way to identify a list object. The `full_name` is
    #: the name prefixed by the names of each ancestor, for example Jones:Kitchen:Cabinets.
    #: `full_name` values aren’t case-sensitive.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    full_name: List[str]
    include_ret_element: List[Literal["AcquiredAs", "AssetAccountRef", "AssetDesc", "AssetNumber", "BarCodeValue", "ClassRef", "CostBasis", "DataExtRet", "EditSequence", "ExternalGUID", "FixedAssetSalesInfo", "IsActive", "ListID", "Location", "Name", "Notes", "PONumber", "PurchaseCost", "PurchaseDate", "PurchaseDesc", "SerialNumber", "TimeCreated", "TimeModified", "VendorOrPayeeName", "WarrantyExpDate", "YearEndAccumulatedDepreciation", "YearEndBookValue"]]
    #: Page through every match: QuBe Sync asks QuickBooks for each page in turn and sends each
    #: to your `webhook_url` as it arrives, all with the same `id`. On by default, with pages of
    #: 100 records; send `iterator=true` with `max_returned` for another size. Off when you send
    #: `iterator=false` (every match in one answer) or `max_returned` alone (at most that many,
    #: in one answer). It pages a filtered query only: with `full_name` or `list_id` every match
    #: comes back in one answer, so leave `iterator` out.
    iterator: bool
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list family, not across the
    #: company file: customers, vendors, employees and other names share one sequence, every
    #: item type shares another, and each other list has its own.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    list_id: List[str]
    #: Limits the number of objects that a query returns. (To get a count of how many objects
    #: could possibly be returned, use the `meta_data` query attribute.) If you include a
    #: `max_returned` value, it must be at least 1.
    #:
    #: The page size, with `iterator=true`. Sent without `iterator`, or with `iterator=false`,
    #: it's a cap instead: at most this many records come back, in one answer, and QuickBooks
    #: doesn't say whether more matched.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
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
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    name_filter: NameFilter
    #: Filters according to the object’s Name.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    name_range_filter: NameRangeFilter
    #: `owner_id` identifies who owns the data extension. Use 0 for QuickBooks custom fields
    #: that appear in the UI, or use a GUID for private extensions owned by an app. Keep private
    #: GUIDs confidential unless you intentionally share extensions across apps. If you do share
    #: them, both apps must use the same `owner_id` and `data_ext_name`, because that pair
    #: uniquely identifies the extension.
    owner_id: List[str]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: Filters results to objects modified on or before this timestamp. QuickBooks Desktop
    #: accepts 1970-01-01 through 2038-01-19T03:14:07. If only a date is provided, time defaults
    #: to end-of-day (23:59:59).
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`active_status`,
    #: `class_filter`, `from_modified_date`, `max_returned`, `name_filter`, `name_range_filter`,
    #: `to_modified_date`). Members of a set combine with each other, not with the other
    #: choices.
    to_modified_date: str


class _ItemFixedAssetUpdateParamsRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list family, not across the
    #: company file: customers, vendors, employees and other names share one sequence, every
    #: item type shares another, and each other list has its own.
    list_id: str


class ItemFixedAssetUpdateParams(_ItemFixedAssetUpdateParamsRequired, total=False):
    """Params for ``item_fixed_asset.update`` (Update item fixed asset)."""
    #: Indicates whether this item was new or used when the business acquired it.
    acquired_as: Literal["New", "Old"]
    #: Refers to the account QuickBooks uses to track the current value of the company’s
    #: inventory. (The AccountType of this account will be FixedAsset, OtherAsset, or
    #: OtherCurrentAsset.) In a request, if an `asset_account_ref` aggregate includes both
    #: `full_name` and `list_id`, `full_name` will be ignored.
    asset_account_ref: Ref
    #: Description of the asset—maker, brand, and so on.
    asset_desc: str
    #: The number used by the QuickBooks Fixed Asset Manager to identify this asset.
    asset_number: str
    #: Barcode reference information.
    bar_code: ItemDiscountBarCode
    #: Use classes to categorize transactions (for example, by department, location, or work
    #: type). Class tracking is off by default in QuickBooks. A `class_ref` points to one class;
    #: if both `full_name` and `list_id` are provided, `full_name` is ignored. In InvoiceAdd, a
    #: header-level `class_ref` is applied to line items unless you override or clear it on
    #: individual lines.
    class_ref: Ref
    #: The total cost of the fixed asset. This can include the cost of improvements or repairs.
    #: This amount is used to figure depreciation.
    cost_basis: float
    #: Sales information, if this fixed asset was sold.
    fixed_asset_sales_info_mod: FixedAssetSalesInfoMod
    include_ret_element: List[Literal["AcquiredAs", "AssetAccountRef", "AssetDesc", "AssetNumber", "BarCodeValue", "ClassRef", "CostBasis", "DataExtRet", "EditSequence", "ExternalGUID", "FixedAssetSalesInfo", "IsActive", "ListID", "Location", "Name", "Notes", "OwnerID", "PONumber", "PurchaseCost", "PurchaseDate", "PurchaseDesc", "SerialNumber", "TimeCreated", "TimeModified", "TxnID", "TxnNumber", "VendorOrPayeeName", "WarrantyExpDate", "YearEndAccumulatedDepreciation", "YearEndBookValue"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: Where the asset is located or has been placed into service.
    location: str
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because `full_name` remains distinct.
    name: str
    #: Additional information.
    notes: str
    #: Purchase order number.
    po_number: str
    #: Amount that the QuickBooks user expects to pay when ordering or buying this item, or the
    #: amount that was actually paid for this item.
    purchase_cost: float
    #: The date when this asset was purchased.
    purchase_date: str
    #: Description that appears in the Description column of checks, bills, credit card charges,
    #: and item receipts (when an item is reordered). For a fixed asset, a description of the
    #: item as it was when it was purchased.
    purchase_desc: str
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: The serial number of the asset.
    serial_number: str
    #: The name of the vendor from whom this asset was purchased.
    vendor_or_payee_name: str
    #: The date when the warranty for this asset expires.
    warranty_exp_date: str
    #: The amount the fixed asset has lost in value since it was purchased, as of the end of the
    #: year.
    year_end_accumulated_depreciation: float
    #: A reasonable estimate of the sales value of the fixed asset, as of the end of the year.
    year_end_book_value: float


class ItemFixedAsset:
    """QuickBooks item fixed asset operations: create, query, update.

    Get it from ``client.item_fixed_asset``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[ItemFixedAssetCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create item fixed asset.

        Queues ``item_fixed_asset.create``: POST /connections/{connection_id}/item-fixed-assets, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``ItemFixedAssetCreateParams``)::

            acquired_as: Literal["New", "Old"] (required)
            asset_account_ref: Ref
                full_name: str
                list_id: str
            asset_desc: str
            asset_number: str
            bar_code: ItemDiscountBarCode
                allow_override: bool
                assign_even_if_used: bool
                bar_code_value: str
            class_ref: Ref
            cost_basis: float
            external_guid: str
            fixed_asset_sales_info: FixedAssetSalesInfo
                sales_date: str (required)
                sales_desc: str (required)
                sales_expense: float
                sales_price: float
            include_ret_element: List[Literal[...] (one of 30 values)]
            is_active: bool
            location: str
            name: str (required)
            notes: str
            po_number: str
            purchase_cost: float
            purchase_date: str (required)
            purchase_desc: str (required)
            request_id: str
            serial_number: str
            vendor_or_payee_name: str
            warranty_exp_date: str
            year_end_accumulated_depreciation: float
            year_end_book_value: float

        Docs: https://docs.qubesync.com/api-reference/v2/item-fixed-assets/create-item-fixed-asset
        """
        return self._client._queue_operation("item_fixed_asset.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[ItemFixedAssetQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List item fixed assets.

        Queues ``item_fixed_asset.query``: GET /connections/{connection_id}/item-fixed-assets, params in the query string.
        QuickBooks answers in pages: each page comes to ``webhook_url`` as its own webhook.
        Returns the queued request.

        Params (``ItemFixedAssetQueryParams``)::

            active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
            class_filter: EntityFilter
                full_name: List[str]
                full_name_with_children: str
                list_id: List[str]
                list_id_with_children: str
            from_modified_date: str
            full_name: List[str]
            include_ret_element: List[Literal[...] (one of 27 values)]
            iterator: bool
            list_id: List[str]
            max_returned: int
            meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
            name_filter: NameFilter
                match_criterion: Literal["Contains", "EndsWith", "StartsWith"] (required)
                name: str (required)
            name_range_filter: NameRangeFilter
                from_name: str
                to_name: str
            owner_id: List[str]
            request_id: str
            to_modified_date: str

        Docs: https://docs.qubesync.com/api-reference/v2/item-fixed-assets/list-item-fixed-assets
        """
        return self._client._queue_operation("item_fixed_asset.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[ItemFixedAssetUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update item fixed asset.

        Queues ``item_fixed_asset.update``: PUT /connections/{connection_id}/item-fixed-assets, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``ItemFixedAssetUpdateParams``)::

            acquired_as: Literal["New", "Old"]
            asset_account_ref: Ref
                full_name: str
                list_id: str
            asset_desc: str
            asset_number: str
            bar_code: ItemDiscountBarCode
                allow_override: bool
                assign_even_if_used: bool
                bar_code_value: str
            class_ref: Ref
            cost_basis: float
            edit_sequence: str (required)
            fixed_asset_sales_info_mod: FixedAssetSalesInfoMod
                sales_date: str
                sales_desc: str
                sales_expense: float
                sales_price: float
            include_ret_element: List[Literal[...] (one of 30 values)]
            is_active: bool
            list_id: str (required)
            location: str
            name: str
            notes: str
            po_number: str
            purchase_cost: float
            purchase_date: str
            purchase_desc: str
            request_id: str
            serial_number: str
            vendor_or_payee_name: str
            warranty_exp_date: str
            year_end_accumulated_depreciation: float
            year_end_book_value: float

        Docs: https://docs.qubesync.com/api-reference/v2/item-fixed-assets/update-item-fixed-asset
        """
        return self._client._queue_operation("item_fixed_asset.update", connection_id, params, webhook_url, idempotency_key)
