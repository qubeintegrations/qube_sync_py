"""Type-checked by mypy in CI (python 3.13): nested params check, a misspelled field doesn't.

    mypy --strict --warn-unused-ignores tests/typecheck/sample.py

Every `# type: ignore[...]` here must be needed: --warn-unused-ignores fails the run when a
misspelling stops being an error.
"""

from qubesync import Client
from qubesync.operations.invoice import InvoiceCreateParams
from qubesync.operations._types import Ref

qube = Client(api_key="key")

customer: Ref = {"full_name": "Acme Ltd"}
invoice: InvoiceCreateParams = {
    "customer_ref": customer,
    "ref_number": "1042",
    "invoice_line_add": [
        {"item_ref": {"full_name": "Widget"}, "quantity": 2, "rate": 9.5},
    ],
}
queued = qube.invoice.create("c1", invoice, webhook_url="https://app.test/hook")
queued_id: object = queued["id"]

qube.customer.query(
    "c1",
    {"name_range": {"from": "A", "to": "M"}, "active_status": "ActiveOnly", "list_id": ["80000001-1"]},
    webhook_url="https://app.test/hook",
)
qube.customer.query("c1", {"active_status": "Sometimes"}, webhook_url="https://app.test/hook")  # type: ignore[arg-type]
qube.class_.query("c1", {"max_returned": 10}, webhook_url="https://app.test/hook")

misspelled: InvoiceCreateParams = {
    "customer_ref": {"ful_name": "Acme Ltd"},  # type: ignore[typeddict-unknown-key]
}
missing_required: InvoiceCreateParams = {"ref_number": "1"}  # type: ignore[typeddict-item]
wrong_enum: InvoiceCreateParams = {
    "customer_ref": customer,
    "include_ret_element": ["NoSuchElement"],  # type: ignore[list-item]
}
qube.invoice.create("c1", invoice)  # type: ignore[call-arg]
qube.invoice.nope  # type: ignore[attr-defined]
