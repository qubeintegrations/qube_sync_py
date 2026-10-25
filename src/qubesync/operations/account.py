# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks account operations (``client.account``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    CurrencyFilter,
    NameFilter,
    NameRangeFilter,
    Ref,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _AccountCreateParamsRequired(TypedDict):
    #: The type of QuickBooks account. You can’t create or modify a non-posting account through
    #: the SDK, because QuickBooks creates these accounts behind the scenes. This means that you
    #: can’t send an AccountAdd request with an `account_type` of NonPosting.
    account_type: Literal["AccountsPayable", "AccountsReceivable", "Bank", "CostOfGoodsSold", "CreditCard", "Equity", "Expense", "FixedAsset", "Income", "LongTermLiability", "NonPosting", "OtherAsset", "OtherCurrentAsset", "OtherCurrentLiability", "OtherExpense", "OtherIncome"]
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because `full_name` remains distinct.
    name: str


class AccountCreateParams(_AccountCreateParamsRequired, total=False):
    """Params for ``account.create`` (Create account)."""
    #: Account numbers appear in the QuickBooks chart of accounts, Account fields, and reports
    #: and graphs. If the IsUsingAccountNumber preference is false (that is, if the QuickBooks
    #: user has the account numbers Preference turned off), you can still set account numbers
    #: through the SDK, but the numbers won’t be visible in the user interface.
    account_number: str
    #: The bank account number or an identifying note about the account. If a `bank_number`
    #: exists in a QuickBooks company file, it will only be returned to applications that have
    #: been granted permission to access sensitive data and that are using SDK v2.0 or greater.
    bank_number: str
    #: A currency record defines how QuickBooks stores and displays a currency. Built-in
    #: currency name/code values are fixed; formatting and active status can vary by settings
    #: and workflow.
    currency_ref: Ref
    #: A descriptive text field.
    desc: str
    detail_account_type: Literal["AP", "AR", "AccumulatedAdjustment", "AccumulatedAmortization", "AccumulatedAmortizationOfOtherAssets", "AccumulatedDepletion", "AccumulatedDepreciation", "AdvertisingOrPromotional", "AllowanceForBadDebts", "Amortization", "Auto", "BadDebts", "BankCharges", "Buildings", "CashOnHand", "CharitableContributions", "Checking", "CommonStock", "CostOfLabor", "CostOfLaborCOS", "CreditCard", "DepletableAssets", "Depreciation", "DevelopmentCosts", "DiscountsOrRefundsGiven", "DividendIncome", "DuesAndSubscriptions", "EmployeeCashAdvances", "Entertainment", "EntertainmentMeals", "EquipmentRental", "EquipmentRentalCOS", "FederalIncomeTaxPayable", "FurnitureAndFixtures", "Goodwill", "Insurance", "InsurancePayable", "IntangibleAssets", "InterestEarned", "InterestPaid", "Inventory", "InvestmentMortgageOrRealEstateLoans", "InvestmentOther", "InvestmentTaxExemptSecurities", "InvestmentUSGovObligations", "Land", "LeaseBuyout", "LeaseholdImprovements", "LegalAndProfessionalFees", "Licenses", "LineOfCredit", "LoanPayable", "LoansToOfficers", "LoansToOthers", "LoansToStockholders", "MachineryAndEquipment", "MoneyMarket", "NonProfitIncome", "NotesPayable", "OfficeOrGeneralAdministrativeExpenses", "OpeningBalanceEquity", "OrganizationalCosts", "OtherCostsOfServiceCOS", "OtherCurrentAssets", "OtherCurrentLiab", "OtherFixedAssets", "OtherInvestmentIncome", "OtherLongTermAssets", "OtherLongTermLiab", "OtherMiscExpense", "OtherMiscIncome", "OtherMiscServiceCost", "OtherPrimaryIncome", "OwnersEquity", "PaidInCapitalOrSurplus", "PartnerContributions", "PartnerDistributions", "PartnersEquity", "PayrollClearing", "PayrollExpenses", "PayrollTaxPayable", "PenaltiesAndSettlements", "PreferredStock", "PrepaidExpenses", "PrepaidExpensesPayable", "PromotionalMeals", "RentOrLeaseOfBuildings", "RentsHeldInTrust", "RentsInTrustLiab", "RepairAndMaintenance", "Retainage", "RetainedEarnings", "SalesOfProductIncome", "SalesTaxPayable", "Savings", "SecurityDeposits", "ServiceOrFeeIncome", "ShareholderNotesPayable", "ShippingFreightAndDelivery", "ShippingFreightAndDeliveryCOS", "StateOrLocalIncomeTaxPayable", "SuppliesAndMaterials", "SuppliesAndMaterialsCOGS", "TaxExemptInterest", "TaxesPaid", "Travel", "TravelMeals", "TreasuryStock", "TrustAccounts", "TrustAccountsLiab", "UndepositedFunds", "Utilities", "Vehicles"]
    include_ret_element: List[Literal["AccountNumber", "AccountType", "Balance", "BankNumber", "CashFlowClassification", "CurrencyRef", "DataExtRet", "Desc", "DetailAccountType", "EditSequence", "ExternalGUID", "FullName", "IsActive", "IsTaxAccount", "LastCheckNumber", "ListID", "Name", "OwnerID", "ParentRef", "SalesTaxCodeRef", "SpecialAccountType", "Sublevel", "TaxLineInfoRet", "TimeCreated", "TimeModified", "TotalBalance", "TxnID", "TxnNumber"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: The amount of money in, or the value of, this account as of `open_balance_date`. On a
    #: bank statement, the amount of money in the account at the beginning of the statement
    #: period.
    open_balance: float
    #: The date when an opening balance was entered for this account.
    open_balance_date: str
    #: A reference to the list object that is one level above this one. For example, an
    #: inventory item with the `full_name` of GermanCars:Mercedes-Benz:CL500I99AA might have a
    #: parent object with the `full_name` of GermanCars:Mercedes-Benz. In a request, if a
    #: `parent_ref` aggregate includes both `full_name` and `list_id`, `full_name` will be
    #: ignored.
    parent_ref: Ref
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: `sales_tax_code_ref` points to the sales-tax code used for an item or customer context.
    #: QuickBooks includes default TAX and NON codes, and a code can be deleted only when
    #: nothing references it. If sales tax is disabled, QuickBooks assigns the default
    #: non-taxable code. If both `full_name` and `list_id` are provided in `sales_tax_code_ref`,
    #: `full_name` is ignored.
    sales_tax_code_ref: Ref
    #: An internal representation of the tax line associated with this account.
    tax_line_id: int


class AccountQueryParams(TypedDict, total=False):
    """Params for ``account.query`` (List accounts)."""
    #: The type of QuickBooks account. You can’t create or modify a non-posting account through
    #: the SDK, because QuickBooks creates these accounts behind the scenes. This means that you
    #: can’t send an AccountAdd request with an `account_type` of NonPosting.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`account_type`,
    #: `active_status`, `currency_filter`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    account_type: List[Literal["AccountsPayable", "AccountsReceivable", "Bank", "CostOfGoodsSold", "CreditCard", "Equity", "Expense", "FixedAsset", "Income", "LongTermLiability", "NonPosting", "OtherAsset", "OtherCurrentAsset", "OtherCurrentLiability", "OtherExpense", "OtherIncome"]]
    #: Used in filters to select list objects based on whether or not they are currently enabled
    #: for use by QuickBooks. The default value is asActiveOnly, which selects only list objects
    #: that are active.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`account_type`,
    #: `active_status`, `currency_filter`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
    #: Filters by the specified currency.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`account_type`,
    #: `active_status`, `currency_filter`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    currency_filter: CurrencyFilter
    #: Filters results to objects modified on or after this timestamp. QuickBooks Desktop
    #: accepts 1970-01-01 through 2038-01-19T03:14:07. If only a date is provided, time defaults
    #: to 00:00:00.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`account_type`,
    #: `active_status`, `currency_filter`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    from_modified_date: str
    #: `full_name` (along with `list_id`) is a way to identify a list object. The `full_name` is
    #: the name prefixed by the names of each ancestor, for example Jones:Kitchen:Cabinets.
    #: `full_name` values aren’t case-sensitive.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`account_type`,
    #: `active_status`, `currency_filter`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    full_name: List[str]
    include_ret_element: List[Literal["AccountNumber", "AccountType", "Balance", "BankNumber", "CashFlowClassification", "CurrencyRef", "DataExtRet", "Desc", "DetailAccountType", "EditSequence", "FullName", "IsActive", "IsTaxAccount", "LastCheckNumber", "ListID", "Name", "ParentRef", "SalesTaxCodeRef", "SpecialAccountType", "Sublevel", "TaxLineInfoRet", "TimeCreated", "TimeModified", "TotalBalance"]]
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list type, not globally
    #: across all lists. If both `full_name` and `list_id` are supplied in a request, QuickBooks
    #: uses `list_id` and ignores `full_name`.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`account_type`,
    #: `active_status`, `currency_filter`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
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
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`account_type`,
    #: `active_status`, `currency_filter`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    max_returned: int
    #: Use the `meta_data` attribute to control whether query responses include counts. Options
    #: are NoMetaData (default), MetaDataOnly (count only), and MetaDataAndResponseData (count
    #: plus objects). Counts are approximate and may vary slightly if records are created or
    #: deleted during processing.
    meta_data: Literal["MetaDataAndResponseData", "MetaDataOnly", "NoMetaData"]
    #: Filters according to the object’s Name.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`account_type`,
    #: `active_status`, `currency_filter`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    name_filter: NameFilter
    #: Filters according to the object’s Name.
    #:
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`account_type`,
    #: `active_status`, `currency_filter`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
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
    #: Choose at most one of: `list_id`, or `full_name`, or the set (`account_type`,
    #: `active_status`, `currency_filter`, `from_modified_date`, `max_returned`, `name_filter`,
    #: `name_range_filter`, `to_modified_date`). Members of a set combine with each other, not
    #: with the other choices.
    to_modified_date: str


class _AccountUpdateParamsRequired(TypedDict):
    #: `edit_sequence` is a server-generated revision token. It changes each time the object is
    #: updated. To modify an existing object, you must send the current `edit_sequence`. If your
    #: value is stale, the update is rejected to prevent overwriting newer changes.
    edit_sequence: str
    #: `list_id` and `full_name` both identify a list object. QuickBooks assigns `list_id` when
    #: the object is created. `list_id` values are unique within a list type, not globally
    #: across all lists. If both `full_name` and `list_id` are supplied in a request, QuickBooks
    #: uses `list_id` and ignores `full_name`.
    list_id: str


class AccountUpdateParams(_AccountUpdateParamsRequired, total=False):
    """Params for ``account.update`` (Update account)."""
    #: Account numbers appear in the QuickBooks chart of accounts, Account fields, and reports
    #: and graphs. If the IsUsingAccountNumber preference is false (that is, if the QuickBooks
    #: user has the account numbers Preference turned off), you can still set account numbers
    #: through the SDK, but the numbers won’t be visible in the user interface.
    account_number: str
    #: The type of QuickBooks account. You can’t create or modify a non-posting account through
    #: the SDK, because QuickBooks creates these accounts behind the scenes. This means that you
    #: can’t send an AccountAdd request with an `account_type` of NonPosting.
    account_type: Literal["AccountsPayable", "AccountsReceivable", "Bank", "CostOfGoodsSold", "CreditCard", "Equity", "Expense", "FixedAsset", "Income", "LongTermLiability", "NonPosting", "OtherAsset", "OtherCurrentAsset", "OtherCurrentLiability", "OtherExpense", "OtherIncome"]
    #: The bank account number or an identifying note about the account. If a `bank_number`
    #: exists in a QuickBooks company file, it will only be returned to applications that have
    #: been granted permission to access sensitive data and that are using SDK v2.0 or greater.
    bank_number: str
    #: A currency record defines how QuickBooks stores and displays a currency. Built-in
    #: currency name/code values are fixed; formatting and active status can vary by settings
    #: and workflow.
    currency_ref: Ref
    #: A descriptive text field.
    desc: str
    include_ret_element: List[Literal["AccountNumber", "AccountType", "Balance", "BankNumber", "CashFlowClassification", "CurrencyRef", "DataExtRet", "Desc", "DetailAccountType", "EditSequence", "ExternalGUID", "FullName", "IsActive", "IsTaxAccount", "LastCheckNumber", "ListID", "Name", "OwnerID", "ParentRef", "SalesTaxCodeRef", "SpecialAccountType", "Sublevel", "TaxLineInfoRet", "TimeCreated", "TimeModified", "TotalBalance", "TxnID", "TxnNumber"]]
    #: If `is_active` is true, this object is currently enabled for use by QuickBooks. The
    #: default value is true.
    is_active: bool
    #: Name is the case-insensitive short name of a list object (without ancestors). It must be
    #: unique within its hierarchy scope. Hierarchical lists can reuse the same Name in
    #: different branches because `full_name` remains distinct.
    name: str
    #: The amount of money in, or the value of, this account as of `open_balance_date`. On a
    #: bank statement, the amount of money in the account at the beginning of the statement
    #: period.
    open_balance: float
    #: The date when an opening balance was entered for this account.
    open_balance_date: str
    #: A reference to the list object that is one level above this one. For example, an
    #: inventory item with the `full_name` of GermanCars:Mercedes-Benz:CL500I99AA might have a
    #: parent object with the `full_name` of GermanCars:Mercedes-Benz. In a request, if a
    #: `parent_ref` aggregate includes both `full_name` and `list_id`, `full_name` will be
    #: ignored.
    parent_ref: Ref
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str
    #: `sales_tax_code_ref` points to the sales-tax code used for an item or customer context.
    #: QuickBooks includes default TAX and NON codes, and a code can be deleted only when
    #: nothing references it. If sales tax is disabled, QuickBooks assigns the default
    #: non-taxable code. If both `full_name` and `list_id` are provided in `sales_tax_code_ref`,
    #: `full_name` is ignored.
    sales_tax_code_ref: Ref
    #: An internal representation of the tax line associated with this account.
    tax_line_id: int


class Account:
    """QuickBooks account operations: create, query, update.

    Get it from ``client.account``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def create(
        self,
        connection_id: str,
        params: Optional[AccountCreateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create account.

        Queues ``account.create``: POST /connections/{connection_id}/accounts, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``AccountCreateParams``)::

            account_number: str
            account_type: Literal[...] (one of 16 values) (required)
            bank_number: str
            currency_ref: Ref
                full_name: str
                list_id: str
            desc: str
            detail_account_type: Literal[...] (one of 113 values)
            include_ret_element: List[Literal[...] (one of 28 values)]
            is_active: bool
            name: str (required)
            open_balance: float
            open_balance_date: str
            parent_ref: Ref
            request_id: str
            sales_tax_code_ref: Ref
            tax_line_id: int

        Docs: https://docs.qubesync.com/api-reference/v2/accounts/create-account
        """
        return self._client._queue_operation("account.create", connection_id, params, webhook_url, idempotency_key)

    def query(
        self,
        connection_id: str,
        params: Optional[AccountQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List accounts.

        Queues ``account.query``: GET /connections/{connection_id}/accounts, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``AccountQueryParams``)::

            account_type: List[Literal[...] (one of 16 values)]
            active_status: Literal["ActiveOnly", "All", "InactiveOnly"]
            currency_filter: CurrencyFilter
                full_name: List[str]
                list_id: List[str]
            from_modified_date: str
            full_name: List[str]
            include_ret_element: List[Literal[...] (one of 24 values)]
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

        Docs: https://docs.qubesync.com/api-reference/v2/accounts/list-accounts
        """
        return self._client._queue_operation("account.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[AccountUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update account.

        Queues ``account.update``: PUT /connections/{connection_id}/accounts, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``AccountUpdateParams``)::

            account_number: str
            account_type: Literal[...] (one of 16 values)
            bank_number: str
            currency_ref: Ref
                full_name: str
                list_id: str
            desc: str
            edit_sequence: str (required)
            include_ret_element: List[Literal[...] (one of 28 values)]
            is_active: bool
            list_id: str (required)
            name: str
            open_balance: float
            open_balance_date: str
            parent_ref: Ref
            request_id: str
            sales_tax_code_ref: Ref
            tax_line_id: int

        Docs: https://docs.qubesync.com/api-reference/v2/accounts/update-account
        """
        return self._client._queue_operation("account.update", connection_id, params, webhook_url, idempotency_key)
