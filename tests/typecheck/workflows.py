"""Type-checked by mypy in CI (python 3.13) against the golden generated module: a body is its
operation's params, a branch fixes its discriminator, a misspelled field or input doesn't check.

    MYPYPATH=tests/fixtures/workflow_types mypy --strict --warn-unused-ignores tests/typecheck/workflows.py

Every `# type: ignore[...]` here must be needed: --warn-unused-ignores fails the run when a
mistake stops being an error.
"""

import qube_workflows
from qube_workflows import AddTransactionInput, AddTransactionInvoiceInput, RecordPaymentPaymentBody, UpsertInput
from qubesync import Client
from qubesync.operations.invoice import InvoiceCreateParams

qube_workflows.client = Client(api_key="key")

params: InvoiceCreateParams = {"customer_ref": {"full_name": "Acme Ltd"}, "ref_number": "1042"}
run = qube_workflows.add_transaction.invoice(
    "c1",
    params,
    adds=[{"kind": "customer", "add": {"name": "Acme Ltd"}, "accept": "strong"}],
    references={"customer": "create"},
    reference="invoice-1042",
    webhook_url="https://app.test/runs",
)

# What a qubesync.kit Operation's input returns.
built: AddTransactionInvoiceInput = qube_workflows.add_transaction.invoice_input(params)
any_input: AddTransactionInput = built
qube_workflows.add_transaction.start("c1", any_input, reference="r", webhook_url="https://app.test/runs")
literal: AddTransactionInvoiceInput = {"operation": "invoice.create", "params": params}

# The workflow fills in customer_ref, so a payment needs none.
payment: RecordPaymentPaymentBody = {"memo": "Check 1001"}
qube_workflows.record_payment.start("c1", payment=payment, reference="p", webhook_url="https://app.test/runs")
upsert: UpsertInput = qube_workflows.upsert.customer_input(add={"name": "Acme"}, update={"phone": "512-555-0100"})

wrong_body: AddTransactionInvoiceInput = {
    "operation": "invoice.create",
    "params": {"customer_ref": {"full_name": "Acme"}, "ref_nmber": "1"},  # type: ignore[typeddict-unknown-key]
}
wrong_operation: AddTransactionInvoiceInput = {"operation": "bill.create", "params": params}  # type: ignore[typeddict-item]
wrong_kind = qube_workflows.add_transaction.invoice_input(params, adds=[{"kind": "vendor", "add": {}}])  # type: ignore[misc, list-item]
qube_workflows.add_transaction.invoice("c1", params, reference="r")  # type: ignore[call-arg]
qube_workflows.record_payment.input(payment={"memo": 1})  # type: ignore[typeddict-item]
qube_workflows.upsert.customer_input(add={"name": "x"}, update={}, klass="x")  # type: ignore[call-arg]
qube_workflows.no_such_workflow  # type: ignore[attr-defined]
