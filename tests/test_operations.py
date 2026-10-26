"""The generated per-operation methods (client.customer.create...) and queue by operation id."""

import importlib
import json
import os
import subprocess
import sys
import uuid

import pytest

from qubesync import Client
from qubesync.operations import ENTITIES, OPERATIONS
from qubesync.operations import _types

from test_client_v2 import API_KEY, FakeQube

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "tests", "fixtures", "operations.json")
GENERATOR = os.path.join(ROOT, "scripts", "generate_operations.py")
HOOK = "https://app.test/hook"


@pytest.fixture(scope="module")
def server():
    fake = FakeQube()
    yield fake
    fake.server.shutdown()
    fake.server.server_close()


@pytest.fixture
def fake(server):
    server.reset()
    return server


@pytest.fixture
def client(fake):
    return Client(API_KEY, base_url=fake.base_url, sleep=lambda s: None)


def body_of(req):
    return json.loads(req["body"].decode()) if req["body"] else None


# -- The generator -------------------------------------------------------------------------


def test_generated_files_are_up_to_date():
    result = subprocess.run([sys.executable, GENERATOR, "--check"], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_the_index_matches_the_manifest():
    with open(MANIFEST, encoding="utf-8") as f:
        manifest = json.load(f)
    assert manifest["version"] == 1
    ops = {op["id"]: op for op in manifest["operations"]}
    assert set(OPERATIONS) == set(ops)
    for op_id, op in ops.items():
        entry = OPERATIONS[op_id]
        assert entry.method == op["method"]
        assert "/connections/{connection_id}/" + entry.path == op["path"]
        assert entry.params_in == op["params_in"]
        assert entry.paged == op["paged"]
        assert entry.entity == op["entity"]
    assert set(ENTITIES) == {op["entity"] for op in ops.values()}


def test_the_digest_is_the_manifests():
    import hashlib

    from qubesync.operations import DIGEST

    with open(MANIFEST, "rb") as f:
        assert DIGEST == "sha256:" + hashlib.sha256(f.read()).hexdigest()


def test_the_field_index_matches_the_params_types():
    from qubesync.operations import _fields

    assert set(_fields.PARAMS) == set(OPERATIONS) == set(_fields.FIELDS)
    for op_id, name in _fields.PARAMS.items():
        module = importlib.import_module("qubesync.operations." + _fields.MODULES[name])
        params = getattr(module, name)
        annotations = {}
        for klass in reversed(params.__mro__):
            annotations.update(getattr(klass, "__annotations__", {}))
        assert set(_fields.FIELDS[op_id]) == set(annotations), op_id
    for name, module in _fields.MODULES.items():
        assert hasattr(importlib.import_module("qubesync.operations." + module), name), name
    assert _fields.FIELDS["receive_payment.create"]["customer_ref"] == ("Ref", True)
    assert _fields.FIELDS["receive_payment.create"]["applied_to_txn_add"] == ("List[AppliedToTxnAdd]", False)


# -- Every operation, through its entity ---------------------------------------------------


def test_every_operation_is_reachable_and_sent_right(client, fake):
    for op_id, op in sorted(OPERATIONS.items()):
        module, _cls = ENTITIES[op.entity]
        action = op_id.rsplit(".", 1)[1]
        method = getattr(getattr(client, module), action)
        fake.reset()
        method("conn 1", {"probe": "x"}, webhook_url=HOOK, idempotency_key="k-" + op_id)
        req = fake.last
        assert req["method"] == op.method, op_id
        assert req["path"] == "/api/v2/connections/conn%201/" + op.path, op_id
        assert req["headers"]["idempotency-key"] == "k-" + op_id
        if op.params_in == "body":
            assert body_of(req) == {"probe": "x"}, op_id
            assert req["query"] == {"webhook_url": [HOOK]}, op_id
        else:
            assert req["body"] == b"", op_id
            assert req["query"] == {"probe": ["x"], "webhook_url": [HOOK]}, op_id


def test_a_body_operation(client, fake):
    fake.answer({"status": 201, "json": {"data": {"id": "q1", "state": "waiting"}}})
    queued = client.customer.create("c1", {"name": "Acme", "bill_address": {"city": "Austin"}}, webhook_url=HOOK)
    assert queued == {"id": "q1", "state": "waiting"}
    req = fake.last
    assert (req["method"], req["path"]) == ("POST", "/api/v2/connections/c1/customers")
    assert req["headers"]["content-type"] == "application/json"
    assert body_of(req) == {"name": "Acme", "bill_address": {"city": "Austin"}}
    assert req["query"] == {"webhook_url": [HOOK]}
    assert uuid.UUID(req["headers"]["idempotency-key"]).version == 4


def test_a_paged_query_is_just_a_query(client, fake):
    paged = [op_id for op_id, op in sorted(OPERATIONS.items()) if op.paged]
    assert "invoice.query" in paged
    client.invoice.query("c1", {"max_returned": 50, "ref_number": ["1", "2"]}, webhook_url=HOOK)
    req = fake.last
    assert (req["method"], req["path"]) == ("GET", "/api/v2/connections/c1/invoices")
    assert req["query"] == {"max_returned": ["50"], "ref_number": ["1", "2"], "webhook_url": [HOOK]}
    assert req["body"] == b""
    assert len(fake.requests) == 1


def test_params_are_optional(client, fake):
    client.company.query("c1", webhook_url=HOOK)
    assert fake.last["query"] == {"webhook_url": [HOOK]}


def test_webhook_url_is_required(client, fake):
    with pytest.raises(TypeError):
        client.customer.create("c1", {})  # type: ignore[call-arg]
    with pytest.raises(ValueError):
        client.customer.create("c1", {}, webhook_url="")
    assert fake.requests == []


def test_class_is_class_(client, fake):
    client.class_.query("c1", webhook_url=HOOK)
    assert fake.last["path"] == "/api/v2/connections/c1/classes"


def test_an_entity_is_memoized_per_client(client, fake):
    assert client.customer is client.customer
    other = Client(API_KEY, base_url=fake.base_url)
    assert other.customer is not client.customer
    assert other.customer._client is other


# -- queue by operation id -----------------------------------------------------------------


def wire(req):
    return (req["method"], req["path"], req["query"], req["body"], req["headers"]["idempotency-key"])


def test_queue_by_id_matches_the_method(client, fake):
    params = {"name": "Acme"}
    client.queue("customer.create", "c1", params, webhook_url=HOOK, idempotency_key="k1")
    client.customer.create("c1", params, webhook_url=HOOK, idempotency_key="k1")
    client.queue("invoice.query", "c1", {"ref_number": ["7"]}, webhook_url=HOOK, idempotency_key="k2")
    client.invoice.query("c1", {"ref_number": ["7"]}, webhook_url=HOOK, idempotency_key="k2")
    a, b, c, d = fake.requests
    assert wire(a) == wire(b)
    assert wire(c) == wire(d)


def test_queue_an_unknown_id_needs_method_and_path(client, fake):
    for kwargs in ({}, {"method": "post"}, {"path": "widgets"}):
        with pytest.raises(ValueError) as info:
            client.queue("widget.create", "c1", {"name": "W"}, webhook_url=HOOK, **kwargs)
        assert "method=" in str(info.value) and "path=" in str(info.value)
    assert fake.requests == []


def test_queue_an_unknown_id_with_method_and_path(client, fake):
    client.queue("widget.create", "c1", {"name": "W"}, webhook_url=HOOK, method="post", path="/widgets")
    req = fake.last
    assert (req["method"], req["path"]) == ("POST", "/api/v2/connections/c1/widgets")
    assert body_of(req) == {"name": "W"}
    assert req["query"] == {"webhook_url": [HOOK]}
    assert uuid.UUID(req["headers"]["idempotency-key"]).version == 4

    client.queue("widget.query", "c1", {"name": "W"}, webhook_url=HOOK, method="get", path="widgets")
    assert fake.last["method"] == "GET"
    assert fake.last["query"] == {"name": ["W"], "webhook_url": [HOOK]}


def test_queue_refuses_a_bad_method(client, fake):
    with pytest.raises(ValueError):
        client.queue("widget.create", "c1", {}, webhook_url=HOOK, method="patch", path="widgets")


# -- Lazy loading --------------------------------------------------------------------------


def test_entity_modules_load_on_first_use():
    code = "\n".join(
        [
            "import sys",
            "import qubesync",
            "c = qubesync.Client('k')",
            "loaded = lambda: sorted(m for m in sys.modules if m.startswith('qubesync.operations.') and m != 'qubesync.operations._accessors')",
            "assert loaded() == [], loaded()",
            "c.customer",
            "assert loaded() == ['qubesync.operations._types', 'qubesync.operations.customer'], loaded()",
            "import qubesync.operations as ops",
            "ops.invoice",
            "assert 'qubesync.operations.invoice' in sys.modules",
            "assert 'qubesync.operations.vendor' not in sys.modules",
            "print('ok')",
        ]
    )
    env = dict(os.environ)
    env["PYTHONPATH"] = os.path.join(ROOT, "src") + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "ok"


def test_an_unknown_module_attribute_raises():
    import qubesync.operations as ops

    with pytest.raises(AttributeError):
        ops.no_such_entity  # noqa: B018


# -- Types ---------------------------------------------------------------------------------


def test_every_entity_module_and_type_imports():
    for entity, (module, cls) in sorted(ENTITIES.items()):
        mod = importlib.import_module("qubesync.operations." + module)
        klass = getattr(mod, cls)
        for op_id, op in OPERATIONS.items():
            if op.entity == entity:
                action = op_id.rsplit(".", 1)[1]
                assert callable(getattr(klass, action))
                assert getattr(klass, action).__doc__
    assert _types.Ref.__annotations__.keys() >= {"full_name", "list_id"}


def test_typed_dicts_mark_required_keys():
    from qubesync.operations import invoice
    from qubesync.operations.invoice import InvoiceCreateParams

    assert InvoiceCreateParams.__total__ is False
    assert "customer_ref" in InvoiceCreateParams.__annotations__
    required = invoice._InvoiceCreateParamsRequired
    assert required.__total__ is True
    assert list(required.__annotations__) == ["customer_ref"]
    if sys.version_info >= (3, 9):
        assert "customer_ref" in InvoiceCreateParams.__required_keys__
        assert "memo" in InvoiceCreateParams.__optional_keys__


def test_a_keyword_field_name_is_kept():
    found = [
        name
        for mod in (importlib.import_module("qubesync.operations." + m) for m, _ in ENTITIES.values())
        for name, value in vars(mod).items()
        if isinstance(value, type) and "from" in getattr(value, "__annotations__", {})
    ]
    assert found


def test_method_docs_name_the_operation():
    doc = Client("k").customer.create.__doc__
    assert "Create customer" in doc
    assert "customer.create" in doc
    assert "https://docs.qubesync.com/api-reference/v2/" in doc
    assert "Params (``CustomerCreateParams``)" in doc
    paged = Client("k").invoice.query.__doc__
    assert "pages" in paged
