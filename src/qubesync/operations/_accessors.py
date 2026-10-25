# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""The Client's entity properties (``client.customer``), each importing its module on first use."""

import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .account import Account
    from .account_tax_line_info import AccountTaxLineInfo
    from .aging_report import AgingReport
    from .alert import Alert
    from .ar_refund_credit_card import ArRefundCreditCard
    from .bar_code import BarCode
    from .bill import Bill
    from .bill_payment_check import BillPaymentCheck
    from .bill_payment_credit_card import BillPaymentCreditCard
    from .bill_to_pay import BillToPay
    from .billing_rate import BillingRate
    from .budget_summary_report import BudgetSummaryReport
    from .build_assembly import BuildAssembly
    from .charge import Charge
    from .check import Check
    from .class_ import Class
    from .cleared_status import ClearedStatus
    from .company import Company
    from .company_activity import CompanyActivity
    from .credit_card_charge import CreditCardCharge
    from .credit_card_credit import CreditCardCredit
    from .credit_memo import CreditMemo
    from .currency import Currency
    from .custom_detail_report import CustomDetailReport
    from .custom_summary_report import CustomSummaryReport
    from .customer import Customer
    from .customer_msg import CustomerMsg
    from .customer_type import CustomerType
    from .data_event_recovery_info import DataEventRecoveryInfo
    from .data_ext import DataExt
    from .data_ext_def import DataExtDef
    from .date_driven_terms import DateDrivenTerms
    from .deposit import Deposit
    from .employee import Employee
    from .employee_default import EmployeeDefault
    from .entity import Entity
    from .estimate import Estimate
    from .form1099_category_account_mapping import Form1099CategoryAccountMapping
    from .general_detail_report import GeneralDetailReport
    from .general_summary_report import GeneralSummaryReport
    from .host import Host
    from .inventory_adjustment import InventoryAdjustment
    from .inventory_site import InventorySite
    from .invoice import Invoice
    from .item import Item
    from .item_assemblies_can_build import ItemAssembliesCanBuild
    from .item_discount import ItemDiscount
    from .item_fixed_asset import ItemFixedAsset
    from .item_group import ItemGroup
    from .item_inventory import ItemInventory
    from .item_inventory_assembly import ItemInventoryAssembly
    from .item_non_inventory import ItemNonInventory
    from .item_other_charge import ItemOtherCharge
    from .item_payment import ItemPayment
    from .item_receipt import ItemReceipt
    from .item_sales_tax import ItemSalesTax
    from .item_sales_tax_group import ItemSalesTaxGroup
    from .item_service import ItemService
    from .item_sites import ItemSites
    from .item_subtotal import ItemSubtotal
    from .job_report import JobReport
    from .job_type import JobType
    from .journal_entry import JournalEntry
    from .lead import Lead
    from .list import ListOperations
    from .list_deleted import ListDeleted
    from .list_display import ListDisplay
    from .list_merge import ListMerge
    from .other_name import OtherName
    from .paycheck import Paycheck
    from .payment_method import PaymentMethod
    from .payroll_detail_report import PayrollDetailReport
    from .payroll_item import PayrollItem
    from .payroll_item_addition import PayrollItemAddition
    from .payroll_item_company_contribution import PayrollItemCompanyContribution
    from .payroll_item_deduction import PayrollItemDeduction
    from .payroll_item_direct_deposit import PayrollItemDirectDeposit
    from .payroll_item_non_wage import PayrollItemNonWage
    from .payroll_item_tax import PayrollItemTax
    from .payroll_item_wage import PayrollItemWage
    from .payroll_item_workers_compensation import PayrollItemWorkersCompensation
    from .payroll_last_period import PayrollLastPeriod
    from .payroll_liability_adjustment import PayrollLiabilityAdjustment
    from .payroll_liability_check import PayrollLiabilityCheck
    from .payroll_prior_payment import PayrollPriorPayment
    from .payroll_summary_report import PayrollSummaryReport
    from .payroll_year_to_date_adjustment import PayrollYearToDateAdjustment
    from .preferences import Preferences
    from .price_level import PriceLevel
    from .purchase_order import PurchaseOrder
    from .qb_command_exec import QbCommandExec
    from .receive_payment import ReceivePayment
    from .receive_payment_to_deposit import ReceivePaymentToDeposit
    from .sales_order import SalesOrder
    from .sales_receipt import SalesReceipt
    from .sales_rep import SalesRep
    from .sales_tax_code import SalesTaxCode
    from .sales_tax_payable import SalesTaxPayable
    from .sales_tax_payment_check import SalesTaxPaymentCheck
    from .sales_tax_return import SalesTaxReturn
    from .sales_tax_return_line import SalesTaxReturnLine
    from .ship_method import ShipMethod
    from .special_account import SpecialAccount
    from .special_item import SpecialItem
    from .standard_terms import StandardTerms
    from .template import Template
    from .terms import Terms
    from .time_report import TimeReport
    from .time_tracking import TimeTracking
    from .to_do import ToDo
    from .transaction import Transaction
    from .transfer import Transfer
    from .transfer_inventory import TransferInventory
    from .txn import Txn
    from .txn_deleted import TxnDeleted
    from .txn_display import TxnDisplay
    from .txn_void import TxnVoid
    from .unit_of_measure_set import UnitOfMeasureSet
    from .vehicle import Vehicle
    from .vehicle_mileage import VehicleMileage
    from .vendor import Vendor
    from .vendor_credit import VendorCredit
    from .vendor_type import VendorType
    from .workers_comp_code import WorkersCompCode


class OperationsMixin:
    """``client.<entity>.<action>(...)`` for every QuickBooks operation."""

    __slots__ = ()

    def _operations_entity(self, module: str, cls: str) -> Any:
        cache = self.__dict__.setdefault("_operation_entities", {})
        entity = cache.get(module)
        if entity is None:
            mod = importlib.import_module("qubesync.operations." + module)
            entity = cache[module] = getattr(mod, cls)(self)
        return entity

    @property
    def account(self) -> "Account":
        """QuickBooks account operations: create, query, update."""
        return self._operations_entity("account", "Account")  # type: ignore[no-any-return]

    @property
    def account_tax_line_info(self) -> "AccountTaxLineInfo":
        """QuickBooks account tax line info operations: query."""
        return self._operations_entity("account_tax_line_info", "AccountTaxLineInfo")  # type: ignore[no-any-return]

    @property
    def aging_report(self) -> "AgingReport":
        """QuickBooks aging report operations: query."""
        return self._operations_entity("aging_report", "AgingReport")  # type: ignore[no-any-return]

    @property
    def alert(self) -> "Alert":
        """QuickBooks alert operations: create, delete, query."""
        return self._operations_entity("alert", "Alert")  # type: ignore[no-any-return]

    @property
    def ar_refund_credit_card(self) -> "ArRefundCreditCard":
        """QuickBooks ar refund credit card operations: create, query."""
        return self._operations_entity("ar_refund_credit_card", "ArRefundCreditCard")  # type: ignore[no-any-return]

    @property
    def bar_code(self) -> "BarCode":
        """QuickBooks bar code operations: query."""
        return self._operations_entity("bar_code", "BarCode")  # type: ignore[no-any-return]

    @property
    def bill(self) -> "Bill":
        """QuickBooks bill operations: create, query, update."""
        return self._operations_entity("bill", "Bill")  # type: ignore[no-any-return]

    @property
    def bill_payment_check(self) -> "BillPaymentCheck":
        """QuickBooks bill payment check operations: create, query, update."""
        return self._operations_entity("bill_payment_check", "BillPaymentCheck")  # type: ignore[no-any-return]

    @property
    def bill_payment_credit_card(self) -> "BillPaymentCreditCard":
        """QuickBooks bill payment credit card operations: create, query."""
        return self._operations_entity("bill_payment_credit_card", "BillPaymentCreditCard")  # type: ignore[no-any-return]

    @property
    def bill_to_pay(self) -> "BillToPay":
        """QuickBooks bill to pay operations: query."""
        return self._operations_entity("bill_to_pay", "BillToPay")  # type: ignore[no-any-return]

    @property
    def billing_rate(self) -> "BillingRate":
        """QuickBooks billing rate operations: create, query."""
        return self._operations_entity("billing_rate", "BillingRate")  # type: ignore[no-any-return]

    @property
    def budget_summary_report(self) -> "BudgetSummaryReport":
        """QuickBooks budget summary report operations: query."""
        return self._operations_entity("budget_summary_report", "BudgetSummaryReport")  # type: ignore[no-any-return]

    @property
    def build_assembly(self) -> "BuildAssembly":
        """QuickBooks build assembly operations: create, query, update."""
        return self._operations_entity("build_assembly", "BuildAssembly")  # type: ignore[no-any-return]

    @property
    def charge(self) -> "Charge":
        """QuickBooks charge operations: create, query, update."""
        return self._operations_entity("charge", "Charge")  # type: ignore[no-any-return]

    @property
    def check(self) -> "Check":
        """QuickBooks check operations: create, query, update."""
        return self._operations_entity("check", "Check")  # type: ignore[no-any-return]

    @property
    def class_(self) -> "Class":
        """QuickBooks class operations: create, query, update."""
        return self._operations_entity("class_", "Class")  # type: ignore[no-any-return]

    @property
    def cleared_status(self) -> "ClearedStatus":
        """QuickBooks cleared status operations: update."""
        return self._operations_entity("cleared_status", "ClearedStatus")  # type: ignore[no-any-return]

    @property
    def company(self) -> "Company":
        """QuickBooks company operations: query."""
        return self._operations_entity("company", "Company")  # type: ignore[no-any-return]

    @property
    def company_activity(self) -> "CompanyActivity":
        """QuickBooks company activity operations: query."""
        return self._operations_entity("company_activity", "CompanyActivity")  # type: ignore[no-any-return]

    @property
    def credit_card_charge(self) -> "CreditCardCharge":
        """QuickBooks credit card charge operations: create, query, update."""
        return self._operations_entity("credit_card_charge", "CreditCardCharge")  # type: ignore[no-any-return]

    @property
    def credit_card_credit(self) -> "CreditCardCredit":
        """QuickBooks credit card credit operations: create, query, update."""
        return self._operations_entity("credit_card_credit", "CreditCardCredit")  # type: ignore[no-any-return]

    @property
    def credit_memo(self) -> "CreditMemo":
        """QuickBooks credit memo operations: create, query, update."""
        return self._operations_entity("credit_memo", "CreditMemo")  # type: ignore[no-any-return]

    @property
    def currency(self) -> "Currency":
        """QuickBooks currency operations: create, query, update."""
        return self._operations_entity("currency", "Currency")  # type: ignore[no-any-return]

    @property
    def custom_detail_report(self) -> "CustomDetailReport":
        """QuickBooks custom detail report operations: query."""
        return self._operations_entity("custom_detail_report", "CustomDetailReport")  # type: ignore[no-any-return]

    @property
    def custom_summary_report(self) -> "CustomSummaryReport":
        """QuickBooks custom summary report operations: query."""
        return self._operations_entity("custom_summary_report", "CustomSummaryReport")  # type: ignore[no-any-return]

    @property
    def customer(self) -> "Customer":
        """QuickBooks customer operations: create, query, update."""
        return self._operations_entity("customer", "Customer")  # type: ignore[no-any-return]

    @property
    def customer_msg(self) -> "CustomerMsg":
        """QuickBooks customer msg operations: create, query."""
        return self._operations_entity("customer_msg", "CustomerMsg")  # type: ignore[no-any-return]

    @property
    def customer_type(self) -> "CustomerType":
        """QuickBooks customer type operations: create, query."""
        return self._operations_entity("customer_type", "CustomerType")  # type: ignore[no-any-return]

    @property
    def data_event_recovery_info(self) -> "DataEventRecoveryInfo":
        """QuickBooks data event recovery info operations: delete, query."""
        return self._operations_entity("data_event_recovery_info", "DataEventRecoveryInfo")  # type: ignore[no-any-return]

    @property
    def data_ext(self) -> "DataExt":
        """QuickBooks data ext operations: create, delete, update."""
        return self._operations_entity("data_ext", "DataExt")  # type: ignore[no-any-return]

    @property
    def data_ext_def(self) -> "DataExtDef":
        """QuickBooks data ext def operations: create, delete, query, update."""
        return self._operations_entity("data_ext_def", "DataExtDef")  # type: ignore[no-any-return]

    @property
    def date_driven_terms(self) -> "DateDrivenTerms":
        """QuickBooks date driven terms operations: create, query."""
        return self._operations_entity("date_driven_terms", "DateDrivenTerms")  # type: ignore[no-any-return]

    @property
    def deposit(self) -> "Deposit":
        """QuickBooks deposit operations: create, query, update."""
        return self._operations_entity("deposit", "Deposit")  # type: ignore[no-any-return]

    @property
    def employee(self) -> "Employee":
        """QuickBooks employee operations: create, query, update."""
        return self._operations_entity("employee", "Employee")  # type: ignore[no-any-return]

    @property
    def employee_default(self) -> "EmployeeDefault":
        """QuickBooks employee default operations: query, update."""
        return self._operations_entity("employee_default", "EmployeeDefault")  # type: ignore[no-any-return]

    @property
    def entity(self) -> "Entity":
        """QuickBooks entity operations: query."""
        return self._operations_entity("entity", "Entity")  # type: ignore[no-any-return]

    @property
    def estimate(self) -> "Estimate":
        """QuickBooks estimate operations: create, query, update."""
        return self._operations_entity("estimate", "Estimate")  # type: ignore[no-any-return]

    @property
    def form1099_category_account_mapping(self) -> "Form1099CategoryAccountMapping":
        """QuickBooks form1099 category account mapping operations: query, update."""
        return self._operations_entity("form1099_category_account_mapping", "Form1099CategoryAccountMapping")  # type: ignore[no-any-return]

    @property
    def general_detail_report(self) -> "GeneralDetailReport":
        """QuickBooks general detail report operations: query."""
        return self._operations_entity("general_detail_report", "GeneralDetailReport")  # type: ignore[no-any-return]

    @property
    def general_summary_report(self) -> "GeneralSummaryReport":
        """QuickBooks general summary report operations: query."""
        return self._operations_entity("general_summary_report", "GeneralSummaryReport")  # type: ignore[no-any-return]

    @property
    def host(self) -> "Host":
        """QuickBooks host operations: query."""
        return self._operations_entity("host", "Host")  # type: ignore[no-any-return]

    @property
    def inventory_adjustment(self) -> "InventoryAdjustment":
        """QuickBooks inventory adjustment operations: create, query, update."""
        return self._operations_entity("inventory_adjustment", "InventoryAdjustment")  # type: ignore[no-any-return]

    @property
    def inventory_site(self) -> "InventorySite":
        """QuickBooks inventory site operations: create, query, update."""
        return self._operations_entity("inventory_site", "InventorySite")  # type: ignore[no-any-return]

    @property
    def invoice(self) -> "Invoice":
        """QuickBooks invoice operations: create, query, update."""
        return self._operations_entity("invoice", "Invoice")  # type: ignore[no-any-return]

    @property
    def item(self) -> "Item":
        """QuickBooks item operations: query."""
        return self._operations_entity("item", "Item")  # type: ignore[no-any-return]

    @property
    def item_assemblies_can_build(self) -> "ItemAssembliesCanBuild":
        """QuickBooks item assemblies can build operations: query."""
        return self._operations_entity("item_assemblies_can_build", "ItemAssembliesCanBuild")  # type: ignore[no-any-return]

    @property
    def item_discount(self) -> "ItemDiscount":
        """QuickBooks item discount operations: create, query, update."""
        return self._operations_entity("item_discount", "ItemDiscount")  # type: ignore[no-any-return]

    @property
    def item_fixed_asset(self) -> "ItemFixedAsset":
        """QuickBooks item fixed asset operations: create, query, update."""
        return self._operations_entity("item_fixed_asset", "ItemFixedAsset")  # type: ignore[no-any-return]

    @property
    def item_group(self) -> "ItemGroup":
        """QuickBooks item group operations: create, query, update."""
        return self._operations_entity("item_group", "ItemGroup")  # type: ignore[no-any-return]

    @property
    def item_inventory(self) -> "ItemInventory":
        """QuickBooks item inventory operations: create, query, update."""
        return self._operations_entity("item_inventory", "ItemInventory")  # type: ignore[no-any-return]

    @property
    def item_inventory_assembly(self) -> "ItemInventoryAssembly":
        """QuickBooks item inventory assembly operations: create, query, update."""
        return self._operations_entity("item_inventory_assembly", "ItemInventoryAssembly")  # type: ignore[no-any-return]

    @property
    def item_non_inventory(self) -> "ItemNonInventory":
        """QuickBooks item non inventory operations: create, query, update."""
        return self._operations_entity("item_non_inventory", "ItemNonInventory")  # type: ignore[no-any-return]

    @property
    def item_other_charge(self) -> "ItemOtherCharge":
        """QuickBooks item other charge operations: create, query, update."""
        return self._operations_entity("item_other_charge", "ItemOtherCharge")  # type: ignore[no-any-return]

    @property
    def item_payment(self) -> "ItemPayment":
        """QuickBooks item payment operations: create, query, update."""
        return self._operations_entity("item_payment", "ItemPayment")  # type: ignore[no-any-return]

    @property
    def item_receipt(self) -> "ItemReceipt":
        """QuickBooks item receipt operations: create, query, update."""
        return self._operations_entity("item_receipt", "ItemReceipt")  # type: ignore[no-any-return]

    @property
    def item_sales_tax(self) -> "ItemSalesTax":
        """QuickBooks item sales tax operations: create, query, update."""
        return self._operations_entity("item_sales_tax", "ItemSalesTax")  # type: ignore[no-any-return]

    @property
    def item_sales_tax_group(self) -> "ItemSalesTaxGroup":
        """QuickBooks item sales tax group operations: create, query, update."""
        return self._operations_entity("item_sales_tax_group", "ItemSalesTaxGroup")  # type: ignore[no-any-return]

    @property
    def item_service(self) -> "ItemService":
        """QuickBooks item service operations: create, query, update."""
        return self._operations_entity("item_service", "ItemService")  # type: ignore[no-any-return]

    @property
    def item_sites(self) -> "ItemSites":
        """QuickBooks item sites operations: query."""
        return self._operations_entity("item_sites", "ItemSites")  # type: ignore[no-any-return]

    @property
    def item_subtotal(self) -> "ItemSubtotal":
        """QuickBooks item subtotal operations: create, query, update."""
        return self._operations_entity("item_subtotal", "ItemSubtotal")  # type: ignore[no-any-return]

    @property
    def job_report(self) -> "JobReport":
        """QuickBooks job report operations: query."""
        return self._operations_entity("job_report", "JobReport")  # type: ignore[no-any-return]

    @property
    def job_type(self) -> "JobType":
        """QuickBooks job type operations: create, query."""
        return self._operations_entity("job_type", "JobType")  # type: ignore[no-any-return]

    @property
    def journal_entry(self) -> "JournalEntry":
        """QuickBooks journal entry operations: create, query, update."""
        return self._operations_entity("journal_entry", "JournalEntry")  # type: ignore[no-any-return]

    @property
    def lead(self) -> "Lead":
        """QuickBooks lead operations: create, query, update."""
        return self._operations_entity("lead", "Lead")  # type: ignore[no-any-return]

    @property
    def list(self) -> "ListOperations":
        """QuickBooks list operations: delete."""
        return self._operations_entity("list", "ListOperations")  # type: ignore[no-any-return]

    @property
    def list_deleted(self) -> "ListDeleted":
        """QuickBooks list deleted operations: query."""
        return self._operations_entity("list_deleted", "ListDeleted")  # type: ignore[no-any-return]

    @property
    def list_display(self) -> "ListDisplay":
        """QuickBooks list display operations: create, update."""
        return self._operations_entity("list_display", "ListDisplay")  # type: ignore[no-any-return]

    @property
    def list_merge(self) -> "ListMerge":
        """QuickBooks list merge operations: execute."""
        return self._operations_entity("list_merge", "ListMerge")  # type: ignore[no-any-return]

    @property
    def other_name(self) -> "OtherName":
        """QuickBooks other name operations: create, query, update."""
        return self._operations_entity("other_name", "OtherName")  # type: ignore[no-any-return]

    @property
    def paycheck(self) -> "Paycheck":
        """QuickBooks paycheck operations: query."""
        return self._operations_entity("paycheck", "Paycheck")  # type: ignore[no-any-return]

    @property
    def payment_method(self) -> "PaymentMethod":
        """QuickBooks payment method operations: create, query."""
        return self._operations_entity("payment_method", "PaymentMethod")  # type: ignore[no-any-return]

    @property
    def payroll_detail_report(self) -> "PayrollDetailReport":
        """QuickBooks payroll detail report operations: query."""
        return self._operations_entity("payroll_detail_report", "PayrollDetailReport")  # type: ignore[no-any-return]

    @property
    def payroll_item(self) -> "PayrollItem":
        """QuickBooks payroll item operations: query."""
        return self._operations_entity("payroll_item", "PayrollItem")  # type: ignore[no-any-return]

    @property
    def payroll_item_addition(self) -> "PayrollItemAddition":
        """QuickBooks payroll item addition operations: create, update."""
        return self._operations_entity("payroll_item_addition", "PayrollItemAddition")  # type: ignore[no-any-return]

    @property
    def payroll_item_company_contribution(self) -> "PayrollItemCompanyContribution":
        """QuickBooks payroll item company contribution operations: create, update."""
        return self._operations_entity("payroll_item_company_contribution", "PayrollItemCompanyContribution")  # type: ignore[no-any-return]

    @property
    def payroll_item_deduction(self) -> "PayrollItemDeduction":
        """QuickBooks payroll item deduction operations: create, update."""
        return self._operations_entity("payroll_item_deduction", "PayrollItemDeduction")  # type: ignore[no-any-return]

    @property
    def payroll_item_direct_deposit(self) -> "PayrollItemDirectDeposit":
        """QuickBooks payroll item direct deposit operations: create, update."""
        return self._operations_entity("payroll_item_direct_deposit", "PayrollItemDirectDeposit")  # type: ignore[no-any-return]

    @property
    def payroll_item_non_wage(self) -> "PayrollItemNonWage":
        """QuickBooks payroll item non wage operations: query."""
        return self._operations_entity("payroll_item_non_wage", "PayrollItemNonWage")  # type: ignore[no-any-return]

    @property
    def payroll_item_tax(self) -> "PayrollItemTax":
        """QuickBooks payroll item tax operations: create, update."""
        return self._operations_entity("payroll_item_tax", "PayrollItemTax")  # type: ignore[no-any-return]

    @property
    def payroll_item_wage(self) -> "PayrollItemWage":
        """QuickBooks payroll item wage operations: create, query, update."""
        return self._operations_entity("payroll_item_wage", "PayrollItemWage")  # type: ignore[no-any-return]

    @property
    def payroll_item_workers_compensation(self) -> "PayrollItemWorkersCompensation":
        """QuickBooks payroll item workers compensation operations: create, update."""
        return self._operations_entity("payroll_item_workers_compensation", "PayrollItemWorkersCompensation")  # type: ignore[no-any-return]

    @property
    def payroll_last_period(self) -> "PayrollLastPeriod":
        """QuickBooks payroll last period operations: query."""
        return self._operations_entity("payroll_last_period", "PayrollLastPeriod")  # type: ignore[no-any-return]

    @property
    def payroll_liability_adjustment(self) -> "PayrollLiabilityAdjustment":
        """QuickBooks payroll liability adjustment operations: create, query."""
        return self._operations_entity("payroll_liability_adjustment", "PayrollLiabilityAdjustment")  # type: ignore[no-any-return]

    @property
    def payroll_liability_check(self) -> "PayrollLiabilityCheck":
        """QuickBooks payroll liability check operations: query."""
        return self._operations_entity("payroll_liability_check", "PayrollLiabilityCheck")  # type: ignore[no-any-return]

    @property
    def payroll_prior_payment(self) -> "PayrollPriorPayment":
        """QuickBooks payroll prior payment operations: create, query."""
        return self._operations_entity("payroll_prior_payment", "PayrollPriorPayment")  # type: ignore[no-any-return]

    @property
    def payroll_summary_report(self) -> "PayrollSummaryReport":
        """QuickBooks payroll summary report operations: query."""
        return self._operations_entity("payroll_summary_report", "PayrollSummaryReport")  # type: ignore[no-any-return]

    @property
    def payroll_year_to_date_adjustment(self) -> "PayrollYearToDateAdjustment":
        """QuickBooks payroll year to date adjustment operations: create, query."""
        return self._operations_entity("payroll_year_to_date_adjustment", "PayrollYearToDateAdjustment")  # type: ignore[no-any-return]

    @property
    def preferences(self) -> "Preferences":
        """QuickBooks preferences operations: query, update."""
        return self._operations_entity("preferences", "Preferences")  # type: ignore[no-any-return]

    @property
    def price_level(self) -> "PriceLevel":
        """QuickBooks price level operations: create, query, update."""
        return self._operations_entity("price_level", "PriceLevel")  # type: ignore[no-any-return]

    @property
    def purchase_order(self) -> "PurchaseOrder":
        """QuickBooks purchase order operations: create, query, update."""
        return self._operations_entity("purchase_order", "PurchaseOrder")  # type: ignore[no-any-return]

    @property
    def qb_command_exec(self) -> "QbCommandExec":
        """QuickBooks qb command exec operations: execute."""
        return self._operations_entity("qb_command_exec", "QbCommandExec")  # type: ignore[no-any-return]

    @property
    def receive_payment(self) -> "ReceivePayment":
        """QuickBooks receive payment operations: create, query, update."""
        return self._operations_entity("receive_payment", "ReceivePayment")  # type: ignore[no-any-return]

    @property
    def receive_payment_to_deposit(self) -> "ReceivePaymentToDeposit":
        """QuickBooks receive payment to deposit operations: query."""
        return self._operations_entity("receive_payment_to_deposit", "ReceivePaymentToDeposit")  # type: ignore[no-any-return]

    @property
    def sales_order(self) -> "SalesOrder":
        """QuickBooks sales order operations: create, query, update."""
        return self._operations_entity("sales_order", "SalesOrder")  # type: ignore[no-any-return]

    @property
    def sales_receipt(self) -> "SalesReceipt":
        """QuickBooks sales receipt operations: create, query, update."""
        return self._operations_entity("sales_receipt", "SalesReceipt")  # type: ignore[no-any-return]

    @property
    def sales_rep(self) -> "SalesRep":
        """QuickBooks sales rep operations: create, query, update."""
        return self._operations_entity("sales_rep", "SalesRep")  # type: ignore[no-any-return]

    @property
    def sales_tax_code(self) -> "SalesTaxCode":
        """QuickBooks sales tax code operations: create, query, update."""
        return self._operations_entity("sales_tax_code", "SalesTaxCode")  # type: ignore[no-any-return]

    @property
    def sales_tax_payable(self) -> "SalesTaxPayable":
        """QuickBooks sales tax payable operations: query."""
        return self._operations_entity("sales_tax_payable", "SalesTaxPayable")  # type: ignore[no-any-return]

    @property
    def sales_tax_payment_check(self) -> "SalesTaxPaymentCheck":
        """QuickBooks sales tax payment check operations: create, query, update."""
        return self._operations_entity("sales_tax_payment_check", "SalesTaxPaymentCheck")  # type: ignore[no-any-return]

    @property
    def sales_tax_return(self) -> "SalesTaxReturn":
        """QuickBooks sales tax return operations: query."""
        return self._operations_entity("sales_tax_return", "SalesTaxReturn")  # type: ignore[no-any-return]

    @property
    def sales_tax_return_line(self) -> "SalesTaxReturnLine":
        """QuickBooks sales tax return line operations: query."""
        return self._operations_entity("sales_tax_return_line", "SalesTaxReturnLine")  # type: ignore[no-any-return]

    @property
    def ship_method(self) -> "ShipMethod":
        """QuickBooks ship method operations: create, query."""
        return self._operations_entity("ship_method", "ShipMethod")  # type: ignore[no-any-return]

    @property
    def special_account(self) -> "SpecialAccount":
        """QuickBooks special account operations: create."""
        return self._operations_entity("special_account", "SpecialAccount")  # type: ignore[no-any-return]

    @property
    def special_item(self) -> "SpecialItem":
        """QuickBooks special item operations: create."""
        return self._operations_entity("special_item", "SpecialItem")  # type: ignore[no-any-return]

    @property
    def standard_terms(self) -> "StandardTerms":
        """QuickBooks standard terms operations: create, query."""
        return self._operations_entity("standard_terms", "StandardTerms")  # type: ignore[no-any-return]

    @property
    def template(self) -> "Template":
        """QuickBooks template operations: query."""
        return self._operations_entity("template", "Template")  # type: ignore[no-any-return]

    @property
    def terms(self) -> "Terms":
        """QuickBooks terms operations: query."""
        return self._operations_entity("terms", "Terms")  # type: ignore[no-any-return]

    @property
    def time_report(self) -> "TimeReport":
        """QuickBooks time report operations: query."""
        return self._operations_entity("time_report", "TimeReport")  # type: ignore[no-any-return]

    @property
    def time_tracking(self) -> "TimeTracking":
        """QuickBooks time tracking operations: create, query, update."""
        return self._operations_entity("time_tracking", "TimeTracking")  # type: ignore[no-any-return]

    @property
    def to_do(self) -> "ToDo":
        """QuickBooks to do operations: create, query, update."""
        return self._operations_entity("to_do", "ToDo")  # type: ignore[no-any-return]

    @property
    def transaction(self) -> "Transaction":
        """QuickBooks transaction operations: query."""
        return self._operations_entity("transaction", "Transaction")  # type: ignore[no-any-return]

    @property
    def transfer(self) -> "Transfer":
        """QuickBooks transfer operations: create, query, update."""
        return self._operations_entity("transfer", "Transfer")  # type: ignore[no-any-return]

    @property
    def transfer_inventory(self) -> "TransferInventory":
        """QuickBooks transfer inventory operations: create, query, update."""
        return self._operations_entity("transfer_inventory", "TransferInventory")  # type: ignore[no-any-return]

    @property
    def txn(self) -> "Txn":
        """QuickBooks txn operations: delete."""
        return self._operations_entity("txn", "Txn")  # type: ignore[no-any-return]

    @property
    def txn_deleted(self) -> "TxnDeleted":
        """QuickBooks txn deleted operations: query."""
        return self._operations_entity("txn_deleted", "TxnDeleted")  # type: ignore[no-any-return]

    @property
    def txn_display(self) -> "TxnDisplay":
        """QuickBooks txn display operations: create, update."""
        return self._operations_entity("txn_display", "TxnDisplay")  # type: ignore[no-any-return]

    @property
    def txn_void(self) -> "TxnVoid":
        """QuickBooks txn void operations: execute."""
        return self._operations_entity("txn_void", "TxnVoid")  # type: ignore[no-any-return]

    @property
    def unit_of_measure_set(self) -> "UnitOfMeasureSet":
        """QuickBooks unit of measure set operations: create, query."""
        return self._operations_entity("unit_of_measure_set", "UnitOfMeasureSet")  # type: ignore[no-any-return]

    @property
    def vehicle(self) -> "Vehicle":
        """QuickBooks vehicle operations: create, query, update."""
        return self._operations_entity("vehicle", "Vehicle")  # type: ignore[no-any-return]

    @property
    def vehicle_mileage(self) -> "VehicleMileage":
        """QuickBooks vehicle mileage operations: create, query."""
        return self._operations_entity("vehicle_mileage", "VehicleMileage")  # type: ignore[no-any-return]

    @property
    def vendor(self) -> "Vendor":
        """QuickBooks vendor operations: create, query, update."""
        return self._operations_entity("vendor", "Vendor")  # type: ignore[no-any-return]

    @property
    def vendor_credit(self) -> "VendorCredit":
        """QuickBooks vendor credit operations: create, query, update."""
        return self._operations_entity("vendor_credit", "VendorCredit")  # type: ignore[no-any-return]

    @property
    def vendor_type(self) -> "VendorType":
        """QuickBooks vendor type operations: create, query."""
        return self._operations_entity("vendor_type", "VendorType")  # type: ignore[no-any-return]

    @property
    def workers_comp_code(self) -> "WorkersCompCode":
        """QuickBooks workers comp code operations: create, query, update."""
        return self._operations_entity("workers_comp_code", "WorkersCompCode")  # type: ignore[no-any-return]
