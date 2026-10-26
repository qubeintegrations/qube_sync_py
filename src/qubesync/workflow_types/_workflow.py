"""One workflow of a types document, as the renderer reads it: its names, its inputs and, when
its input is discriminated (an object with oneOf and a discriminator at the top), its branches,
each with the discriminator fixed."""

import keyword
import re
from typing import Any, Dict, List, NamedTuple, Optional, Tuple

from ..errors import QubeSyncError

# Workflow keys, input names and branch titles, as QuBe Sync allows them.
NAME = re.compile(r"\A[a-z][a-z0-9_]{0,63}\Z")
OPERATION = re.compile(r"\A[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*\Z")


class Error(QubeSyncError):
    """A document this version can't render: not a workflow types document, or a name that
    isn't one QuBe Sync allows."""


class Input(NamedTuple):
    name: str  # the input's name
    schema: Dict[str, Any]  # its JSON Schema
    required: bool  # whether the input must be given


class Branch(NamedTuple):
    title: str  # the branch's name in the document
    method: str  # its start method's name
    builder: str  # its input builder's name
    value: Any  # the discriminator's const
    inputs: List[Input]  # the others, sorted by name
    # The workflow's one operation-body input (a $operation in at least one branch), which every
    # branch's methods take positionally, or None when the workflow has none or several.
    body: Optional[Input]


def pascal(name):
    # type: (str) -> str
    """As scripts/generate_operations.py names types: item_service -> ItemService."""
    return "".join(part[:1].upper() + part[1:] for part in name.replace(".", "_").split("_") if part)


def as_list(value):
    # type: (Any) -> List[Any]
    if value is None:
        return []
    return list(value) if isinstance(value, list) else [value]


def operation(schema):
    # type: (Any) -> Optional[str]
    """A $operation reference's id, or None when schema isn't one."""
    id = schema.get("$operation") if isinstance(schema, dict) else None
    if not isinstance(id, str):
        return None
    if not OPERATION.match(id):
        raise Error("not an operation id: %r" % (id,))
    return id


def known_operation(id):
    # type: (str) -> Optional[Tuple[str, str]]
    """An operation id's client accessor and params TypedDict in this version's
    qubesync.operations (("invoice", "InvoiceCreateParams")), or None for one it doesn't know."""
    from ..operations import ENTITIES, OPERATIONS
    from ..operations._fields import PARAMS

    entry = OPERATIONS.get(id)
    if entry is None:
        return None
    return ENTITIES[entry.entity][0], PARAMS[id]


def operation_fields(id):
    # type: (str) -> Optional[Dict[str, Tuple[str, bool]]]
    """An operation's top-level params, {field: (type, required)}, or None for one this version
    doesn't know."""
    from ..operations._fields import FIELDS

    return FIELDS.get(id)


def set_by_workflow(schema):
    # type: (Dict[str, Any]) -> List[str]
    """The fields a $operation reference says its workflow sets itself."""
    return sorted({field for field in as_list(schema.get("set_by_workflow")) if isinstance(field, str)})


def discriminated(schema):
    # type: (Any) -> bool
    """An object schema discriminated by one of its properties: its oneOf branches."""
    return (
        isinstance(schema, dict)
        and bool(as_list(schema.get("oneOf")))
        and isinstance((schema.get("discriminator") or {}).get("propertyName"), str)
    )


def branch_schemas(schema):
    # type: (Dict[str, Any]) -> List[Tuple[str, Dict[str, Any], List[str]]]
    """A discriminated object's branches, as (title, properties merged over the base's,
    required), sorted by title."""
    base = schema.get("properties") or {}
    branches = []
    for branch in as_list(schema.get("oneOf")):
        branch = branch if isinstance(branch, dict) else {}
        properties = dict(base)
        properties.update(branch.get("properties") or {})
        required = sorted(set(as_list(schema.get("required"))) | set(as_list(branch.get("required"))))
        branches.append((str(branch.get("title", "")), properties, required))
    return sorted(branches, key=lambda branch: branch[0])


def fixed_value(properties, discriminator):
    # type: (Dict[str, Any], str) -> Any
    """The value a branch fixes its discriminator to: its const, or its enum's first."""
    fixed = properties.get(discriminator) or {}
    if "const" in fixed:
        return fixed["const"]
    values = as_list(fixed.get("enum"))
    return values[0] if values else None


def checked_name(name, what):
    # type: (Any, str) -> str
    if not (isinstance(name, str) and NAME.match(name)):
        raise Error("%s isn't a name QuBe Sync allows: %r" % (what, name))
    return name


class Workflow(object):
    def __init__(self, key, entry):
        # type: (str, Dict[str, Any]) -> None
        self.key = checked_name(key, "workflow key")
        self.pascal = pascal(key)
        self.name = str(entry.get("name") or "")
        self.description = str(entry.get("description") or "")
        version = entry.get("version")
        self.version = version if isinstance(version, int) and not isinstance(version, bool) else None
        self.draft = entry.get("draft") is True
        self.schema = entry["input"] if isinstance(entry.get("input"), dict) else {}  # type: Dict[str, Any]
        self.discriminator = None  # type: Optional[str]
        if as_list(self.schema.get("oneOf")):
            self.discriminator = (self.schema.get("discriminator") or {}).get("propertyName")
        self.inputs = []  # type: List[Input]
        self.branches = []  # type: List[Branch]
        if self.discriminator is not None:
            checked_name(self.discriminator, "%s's discriminator" % key)
            # The inputs that are an operation body in at least one branch. Only when there's one
            # is it positional, in every branch, so every branch's method takes the same shape.
            bodies = set()
            for branch in as_list(self.schema.get("oneOf")):
                for name, sub in ((branch or {}).get("properties") or {}).items():
                    if operation(sub):
                        bodies.add(name)
            for name, sub in (self.schema.get("properties") or {}).items():
                if operation(sub):
                    bodies.add(name)
            self._body_name = bodies.pop() if len(bodies) == 1 else None
            self.branches = sorted(
                (self._branch_for(branch or {}) for branch in as_list(self.schema.get("oneOf"))),
                key=lambda branch: branch.method,
            )
            methods = [name for branch in self.branches for name in (branch.method, branch.builder)]
            for name in methods:
                if methods.count(name) > 1:
                    raise Error("%s's branches give two methods named %s" % (key, name))
        else:
            self.inputs = self._inputs_of(self.schema.get("properties"), self.schema.get("required"))

    @property
    def discriminated(self):
        # type: () -> bool
        return self.discriminator is not None

    def _branch_for(self, branch):
        # type: (Dict[str, Any]) -> Branch
        title = checked_name(branch.get("title"), "a branch title in %s" % self.key)
        properties = dict(self.schema.get("properties") or {})
        properties.update(branch.get("properties") or {})
        discriminator = self.discriminator or ""
        value = fixed_value(properties, discriminator)
        if value is None:
            raise Error("%s's %s branch doesn't fix %s to a value" % (self.key, title, discriminator))
        required = set(as_list(self.schema.get("required"))) | set(as_list(branch.get("required")))
        inputs = self._inputs_of({n: s for n, s in properties.items() if n != discriminator}, sorted(required))
        body = next((input for input in inputs if input.name == self._body_name), None)
        # `start` is the method every discriminated workflow has; a keyword can't be a name.
        method = title + "_" if keyword.iskeyword(title) or title == "start" else title
        return Branch(title, method, title + "_input", value, inputs, body)

    def _inputs_of(self, properties, required):
        # type: (Any, Any) -> List[Input]
        required = as_list(required)
        return [
            Input(
                checked_name(name, "an input of %s" % self.key),
                sub if isinstance(sub, dict) else {},
                name in required,
            )
            for name, sub in sorted((properties or {}).items())
        ]
