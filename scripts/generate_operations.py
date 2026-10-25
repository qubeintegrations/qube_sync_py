#!/usr/bin/env python3
"""Generate qubesync's per-operation methods from the QuBe Sync operations manifest.

    python scripts/generate_operations.py           # write src/qubesync/operations/
    python scripts/generate_operations.py --check   # write nothing; fail when anything is stale

The manifest is tests/fixtures/operations.json, a copy of https://qubesync.com/libraries/operations.json
(CI's "operations" job fails when the two differ). Every file in src/qubesync/operations/ is
generated: re-running writes the same bytes, and --check also fails on a file the generator
wouldn't write.

It writes:
- __init__.py: the index (operation id -> method, path, params_in, paged, entity), and a module
  __getattr__ that imports an entity's module on first use.
- _accessors.py: OperationsMixin, the Client's entity properties (client.customer...), which
  import an entity's module when first used.
- _types.py: TypedDicts for nested objects that more than one entity uses (structurally equal,
  descriptions aside, become one type).
- <entity>.py: the entity's class (Customer, with create/query/update...), its own nested
  TypedDicts and each operation's params TypedDict.

Standard library only; Python 3.8+.
"""

import argparse
import json
import keyword
import os
import sys
import textwrap
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "tests", "fixtures", "operations.json")
OUT_DIR = os.path.join(ROOT, "src", "qubesync", "operations")
SCRIPT = "scripts/generate_operations.py"
HEADER = "# Generated from operations.json by %s: don't edit.\n" % SCRIPT
WIDTH = 96
PATH_PREFIX = "/connections/{connection_id}/"
RESERVED = {
    "Any", "Dict", "List", "Literal", "Optional", "TypedDict", "Union", "TYPE_CHECKING",
    "Client", "Operation", "OperationsMixin",
}
SCALARS = {"string": "str", "integer": "int", "number": "float", "boolean": "bool"}


# -- Names ---------------------------------------------------------------------------------


def pascal(name):
    return "".join(part[:1].upper() + part[1:] for part in name.replace(".", "_").split("_") if part)


def accessor(entity):
    name = entity.replace(".", "_")
    return name + "_" if keyword.iskeyword(name) else name


# -- Types ---------------------------------------------------------------------------------


class Obj:
    """An object schema with properties: fields are (name, type, required, description)."""

    def __init__(self, fields):
        self.fields = fields
        self.key = ("obj", tuple((n, req, t.key) for n, t, req, _ in fields))


class Ref:
    def __init__(self, kind, value=None):
        self.kind = kind  # scalar, literal, list, object, dict, union, any
        self.value = value
        if kind == "list":
            self.key = ("list", value.key)
        elif kind == "object":
            self.key = value.key
        elif kind == "union":
            self.key = ("union", tuple(v.key for v in value))
        else:
            self.key = (kind, value)


def convert(schema):
    """A JSON Schema (as the manifest writes it) -> Ref. `not` constraints are dropped; oneOf/anyOf
    alternatives that are objects merge into one object with every field optional (the
    schema's description says which ones exclude each other)."""
    alternatives = schema.get("oneOf") or schema.get("anyOf") or []
    type_ = schema.get("type")
    if isinstance(type_, dict):  # never: the manifest's types are strings
        type_ = None
    if "enum" in schema:
        return Ref("literal", tuple(schema["enum"]))
    if type_ in SCALARS:
        return Ref("scalar", SCALARS[type_])
    if type_ == "array":
        items = schema.get("items")
        return Ref("list", convert(items) if isinstance(items, dict) else Ref("any"))
    if type_ == "object" or "properties" in schema or alternatives:
        if alternatives and not all(a.get("type") == "object" or "properties" in a for a in alternatives):
            return Ref("union", tuple(convert(a) for a in alternatives))
        required = set(schema.get("required") or [])
        fields = OrderedDict()
        for name, sub in sorted((schema.get("properties") or {}).items()):
            fields[name] = (convert(sub), name in required, sub.get("description"))
        for alt in alternatives:
            for name, sub in sorted((alt.get("properties") or {}).items()):
                if name not in fields:
                    fields[name] = (convert(sub), False, sub.get("description"))
        if not fields:
            return Ref("dict")
        return Ref("object", Obj([(n, t, r, d) for n, (t, r, d) in sorted(fields.items())]))
    return Ref("any")


# -- The model -----------------------------------------------------------------------------


class Model:
    def __init__(self, manifest):
        self.ops = sorted(manifest["operations"], key=lambda o: o["id"])
        self.entities = OrderedDict()
        for op in self.ops:
            self.entities.setdefault(op["entity"], []).append(op)
        self.names = set(RESERVED)
        self.class_names = {}
        for entity in self.entities:
            name = pascal(entity)
            # `list` would shadow typing.List in its own module.
            self.class_names[entity] = self._claim(name + "Operations" if name in RESERVED else name)
        self.params = {}  # op id -> (name, Obj or None)
        self.structs = OrderedDict()  # key -> {obj, field, entity, action, entities}
        for op in self.ops:
            ref = convert(op["params"] or {})
            obj = ref.value if ref.kind == "object" else None
            name = self._claim(pascal(op["entity"]) + pascal(op["action"]) + "Params")
            self.params[op["id"]] = (name, obj)
            if obj:
                self._collect(obj, op)
        self.struct_names = {}
        for key, info in self.structs.items():
            self.struct_names[key] = self._name_for(info)

    def _claim(self, name):
        if name in self.names:
            raise SystemExit("name collision: %s" % name)
        self.names.add(name)
        return name

    def _collect(self, obj, op):
        for field, ref, _, _ in obj.fields:
            self._collect_ref(ref, field, op)

    def _collect_ref(self, ref, field, op):
        if ref.kind == "list":
            self._collect_ref(ref.value, field, op)
        elif ref.kind == "union":
            for v in ref.value:
                self._collect_ref(v, field, op)
        elif ref.kind == "object":
            info = self.structs.get(ref.key)
            if info is None:
                info = self.structs[ref.key] = {
                    "obj": ref.value,
                    "field": field,
                    "entity": op["entity"],
                    "action": op["action"],
                    "entities": set(),
                    "fields": {},
                }
            info["entities"].add(op["entity"])
            info["fields"][field] = info["fields"].get(field, 0) + 1
            self._collect(ref.value, op)

    def _name_for(self, info):
        """The field's name in PascalCase. A type used under several field names takes their
        common ending (`customer_ref`, `class_ref` -> `Ref`; `bill_address`, `ship_address` ->
        `Address`) unless that's a bare filter/add/mod/line, else the most used field name."""
        fields = info["fields"]
        common = max(fields.items(), key=lambda kv: (kv[1], [-ord(c) for c in kv[0]]))[0]
        base = pascal(common)
        candidates = []
        if len(fields) > 1:
            parts = [f.split("_") for f in sorted(fields)]
            suffix = []
            while all(len(p) > len(suffix) for p in parts) and len({p[-1 - len(suffix)] for p in parts}) == 1:
                suffix.insert(0, parts[0][-1 - len(suffix)])
            if suffix and suffix not in (["filter"], ["add"], ["mod"], ["line"]):
                candidates.append(pascal("_".join(suffix)))
        candidates += [
            base,
            pascal(info["entity"]) + base,
            pascal(info["entity"]) + pascal(info["action"]) + base,
        ]
        for candidate in candidates:
            if candidate not in self.names:
                return self._claim(candidate)
        n = 2
        while candidates[-1] + str(n) in self.names:
            n += 1
        return self._claim(candidates[-1] + str(n))

    def shared(self, key):
        return len(self.structs[key]["entities"]) > 1

    def module_of(self, key):
        return "_types" if self.shared(key) else accessor(self.structs[key]["entity"])


# -- Rendering -----------------------------------------------------------------------------


def comment(text, indent):
    """A description as `#:` lines, one paragraph after another."""
    if not text:
        return []
    prefix = " " * indent + "#: "
    lines = []
    for i, para in enumerate(p for p in text.strip().split("\n\n") if p.strip()):
        if i:
            lines.append(" " * indent + "#:")
        wrapped = textwrap.wrap(" ".join(para.split()), WIDTH - len(prefix), break_on_hyphens=False, break_long_words=False)
        lines.extend(prefix + line for line in wrapped)
    return lines


class Renderer:
    def __init__(self, model):
        self.model = model

    def type_str(self, ref, used):
        if ref.kind == "scalar":
            return ref.value
        if ref.kind == "literal":
            used.add("Literal")
            return "Literal[%s]" % ", ".join(json.dumps(v, ensure_ascii=False) for v in ref.value)
        if ref.kind == "list":
            used.add("List")
            return "List[%s]" % self.type_str(ref.value, used)
        if ref.kind == "object":
            name = self.model.struct_names[ref.key]
            used.add(name)
            return name
        if ref.kind == "dict":
            used.update(("Dict", "Any"))
            return "Dict[str, Any]"
        if ref.kind == "union":
            used.add("Union")
            return "Union[%s]" % ", ".join(self.type_str(v, used) for v in ref.value)
        used.add("Any")
        return "Any"

    def typeddict(self, name, obj, doc, used):
        """Python 3.8 TypedDicts: required keys in a total=True base, the rest in a total=False
        class. A key that isn't an identifier (`from`) goes in a functional-syntax base."""
        used.add("TypedDict")
        fields = obj.fields if obj else []
        groups = {(r, kw): [] for r in (True, False) for kw in (True, False)}
        for f in fields:
            groups[(f[2], not f[0].isidentifier() or keyword.iskeyword(f[0]))].append(f)
        out = []
        bases = []

        def body(items, indent):
            lines = []
            for field, ref, _, desc in items:
                lines.extend(comment(desc, indent))
                lines.append(" " * indent + "%s: %s" % (field, self.type_str(ref, used)))
            return lines

        def functional(base_name, items, total):
            lines = ["%s = TypedDict(" % base_name, '    "%s",' % base_name, "    {"]
            for field, ref, _, desc in items:
                lines.extend(comment(desc, 8))
                lines.append("        %s: %s," % (json.dumps(field), self.type_str(ref, used)))
            lines.extend(["    },", "    total=%s," % total, ")", "", ""])
            return lines

        if groups[(True, False)]:
            bases.append("_%sRequired" % name)
            out.append("class _%sRequired(TypedDict):" % name)
            out.extend(body(groups[(True, False)], 4))
            out.extend(["", ""])
        if groups[(True, True)]:
            bases.append("_%sRequiredKeys" % name)
            out.extend(functional("_%sRequiredKeys" % name, groups[(True, True)], True))
        if groups[(False, True)]:
            bases.append("_%sOptionalKeys" % name)
            out.extend(functional("_%sOptionalKeys" % name, groups[(False, True)], False))
        out.append("class %s(%s, total=False):" % (name, ", ".join(bases) or "TypedDict"))
        lines = []
        if doc:
            lines.append('    """%s"""' % doc)
        lines.extend(body(groups[(False, False)], 4))
        out.extend(lines or ["    pass"])
        out.extend(["", ""])
        return out

    def struct_order(self, keys):
        """Children before parents, then first-seen order."""
        order, seen = [], set()

        def visit(key):
            if key in seen:
                return
            seen.add(key)
            for _, ref, _, _ in self.model.structs[key]["obj"].fields:
                for child in self.children(ref):
                    if child in keys:
                        visit(child)
            order.append(key)

        for key in self.model.structs:
            if key in keys:
                visit(key)
        return order

    def children(self, ref):
        if ref.kind == "object":
            return [ref.key]
        if ref.kind == "list":
            return self.children(ref.value)
        if ref.kind == "union":
            return [k for v in ref.value for k in self.children(v)]
        return []

    def doc_type(self, ref, used):
        """A field's type for a docstring: a long enum is summarised (its type lists the values)."""
        if ref.kind == "literal" and len(ref.value) > 6:
            return "Literal[...] (one of %d values)" % len(ref.value)
        if ref.kind == "list":
            return "List[%s]" % self.doc_type(ref.value, used)
        return self.type_str(ref, used)

    def field_lines(self, obj, indent, used, expanded):
        """Every field, a nested type's fields indented under it the first time it appears."""
        lines = []
        for field, ref, required, _ in obj.fields:
            lines.append(" " * indent + "%s: %s%s" % (field, self.doc_type(ref, used), " (required)" if required else ""))
            for child in self.children(ref):
                if child in expanded:
                    continue
                expanded.add(child)
                lines.extend(self.field_lines(self.model.structs[child]["obj"], indent + 4, used, expanded))
        return lines

    def typing_import(self, used):
        names = sorted(n for n in used if n in ("Any", "Dict", "List", "Literal", "Optional", "TypedDict", "Union", "TYPE_CHECKING"))
        return "from typing import %s\n" % ", ".join(names) if names else ""

    # -- files --

    def types_module(self):
        keys = {k for k in self.model.structs if self.model.shared(k)}
        used = set()
        body = []
        for key in self.struct_order(keys):
            body.extend(self.typeddict(self.model.struct_names[key], self.model.structs[key]["obj"], None, used))
        head = HEADER + '"""Nested params types more than one entity uses."""\n\n' + self.typing_import(used) + "\n\n"
        return head + "\n".join(body).rstrip() + "\n", len(keys)

    def entity_module(self, entity, ops):
        model = self.model
        cls = model.class_names[entity]
        used = {"Any", "Dict", "Optional", "TYPE_CHECKING"}
        local = {k for k, info in model.structs.items() if not model.shared(k) and info["entity"] == entity}
        body = []
        for key in self.struct_order(local):
            body.extend(self.typeddict(model.struct_names[key], model.structs[key]["obj"], None, used))
        for op in ops:
            name, obj = model.params[op["id"]]
            body.extend(self.typeddict(name, obj, "Params for ``%s`` (%s)." % (op["id"], op["summary"]), used))

        actions = ", ".join(op["action"] for op in ops)
        body.append("class %s:" % cls)
        body.append('    """QuickBooks %s operations: %s.' % (entity.replace("_", " "), actions))
        body.append("")
        body.append("    Get it from ``client.%s``. Each method queues the operation and returns the queued" % accessor(entity))
        body.append("    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.")
        body.append('    """')
        body.append("")
        body.append("    def __init__(self, client: \"Client\") -> None:")
        body.append("        self._client = client")
        for op in ops:
            name, obj = model.params[op["id"]]
            body.append("")
            body.append("    def %s(" % op["action"])
            body.append("        self,")
            body.append("        connection_id: str,")
            body.append("        params: Optional[%s] = None," % name)
            body.append("        *,")
            body.append("        webhook_url: str,")
            body.append("        idempotency_key: Optional[str] = None,")
            body.append("    ) -> Dict[str, Any]:")
            where = "as the JSON body" if op["params_in"] == "body" else "in the query string"
            doc = [
                '        """%s.' % op["summary"],
                "",
                "        Queues ``%s``: %s %s, params %s." % (op["id"], op["method"], op["path"], where),
            ]
            if op["paged"]:
                doc.append("        QuickBooks answers in pages: each page comes to ``webhook_url`` as its own webhook.")
            else:
                doc.append("        The answer comes to ``webhook_url`` in one webhook.")
            doc.append("        Returns the queued request.")
            if obj and obj.fields:
                doc.append("")
                doc.append("        Params (``%s``)::" % name)
                doc.append("")
                doc.extend(self.field_lines(obj, 12, used, set()))
            doc.append("")
            doc.append("        Docs: %s" % op["docs_url"])
            doc.append('        """')
            body.extend(doc)
            body.append("        return self._client._queue_operation(%s, connection_id, params, webhook_url, idempotency_key)" % json.dumps(op["id"]))
        shared = sorted(n for n in used if n in {model.struct_names[k] for k in model.structs if model.shared(k)})
        head = HEADER + '"""QuickBooks %s operations (``client.%s``)."""\n\n' % (entity.replace("_", " "), accessor(entity))
        head += self.typing_import(used) + "\n"
        if shared:
            head += "from ._types import (\n" + "".join("    %s,\n" % n for n in shared) + ")\n"
        head += "\nif TYPE_CHECKING:\n    from ..v2 import Client\n\n\n"
        return head + "\n".join(body).rstrip() + "\n"

    def index_module(self):
        model = self.model
        lines = [
            HEADER.rstrip("\n"),
            '"""The operations this version knows, and their entities\' modules.',
            "",
            "``OPERATIONS`` maps an operation id (``customer.create``) to its HTTP method, its path after",
            "the connection, where its params go (``body`` or ``query``), whether QuickBooks pages its",
            "answers, and its entity. Each entity's module (``qubesync.operations.customer``) is",
            "imported only when first used.",
            '"""',
            "",
            "import importlib",
            "from typing import Any, Dict, NamedTuple, Tuple",
            "",
            "",
            "class Operation(NamedTuple):",
            "    method: str",
            "    path: str",
            "    params_in: str",
            "    paged: bool",
            "    entity: str",
            "",
            "",
            "OPERATIONS = {",
        ]
        for op in model.ops:
            if not op["path"].startswith(PATH_PREFIX):
                raise SystemExit("unexpected path %s" % op["path"])
            lines.append(
                "    %s: Operation(%s, %s, %s, %s, %s),"
                % (
                    json.dumps(op["id"]),
                    json.dumps(op["method"]),
                    json.dumps(op["path"][len(PATH_PREFIX):]),
                    json.dumps(op["params_in"]),
                    "True" if op["paged"] else "False",
                    json.dumps(op["entity"]),
                )
            )
        lines.append("}  # type: Dict[str, Operation]")
        lines.append("")
        lines.append("# entity -> (module and client attribute, class)")
        lines.append("ENTITIES = {")
        for entity in model.entities:
            lines.append("    %s: (%s, %s)," % (json.dumps(entity), json.dumps(accessor(entity)), json.dumps(model.class_names[entity])))
        lines.append("}  # type: Dict[str, Tuple[str, str]]")
        lines.append("")
        lines.append("_MODULES = frozenset(module for module, _ in ENTITIES.values())")
        lines.append("")
        lines.append("")
        lines.append("def __getattr__(name: str) -> Any:")
        lines.append("    if name in _MODULES:")
        lines.append('        return importlib.import_module("." + name, __name__)')
        lines.append('    raise AttributeError("module %r has no attribute %r" % (__name__, name))')
        lines.append("")
        lines.append("")
        lines.append("def __dir__() -> Any:")
        lines.append('    return sorted(set(globals()) | _MODULES)')
        return "\n".join(lines) + "\n"

    def accessors_module(self):
        model = self.model
        lines = [
            HEADER.rstrip("\n"),
            '"""The Client\'s entity properties (``client.customer``), each importing its module on first use."""',
            "",
            "import importlib",
            "from typing import TYPE_CHECKING, Any",
            "",
            "if TYPE_CHECKING:",
        ]
        for entity in model.entities:
            lines.append("    from .%s import %s" % (accessor(entity), model.class_names[entity]))
        lines += [
            "",
            "",
            "class OperationsMixin:",
            '    """``client.<entity>.<action>(...)`` for every QuickBooks operation."""',
            "",
            "    __slots__ = ()",
            "",
            "    def _operations_entity(self, module: str, cls: str) -> Any:",
            '        cache = self.__dict__.setdefault("_operation_entities", {})',
            "        entity = cache.get(module)",
            "        if entity is None:",
            '            mod = importlib.import_module("qubesync.operations." + module)',
            "            entity = cache[module] = getattr(mod, cls)(self)",
            "        return entity",
        ]
        for entity, ops in model.entities.items():
            name = accessor(entity)
            cls = model.class_names[entity]
            lines += [
                "",
                "    @property",
                '    def %s(self) -> "%s":' % (name, cls),
                '        """QuickBooks %s operations: %s."""' % (entity.replace("_", " "), ", ".join(o["action"] for o in ops)),
                "        return self._operations_entity(%s, %s)  # type: ignore[no-any-return]" % (json.dumps(name), json.dumps(cls)),
            ]
        return "\n".join(lines) + "\n"


def render_all(manifest):
    model = Model(manifest)
    r = Renderer(model)
    files = OrderedDict()
    files["__init__.py"] = r.index_module()
    files["_accessors.py"] = r.accessors_module()
    files["_types.py"], shared = r.types_module()
    for entity, ops in model.entities.items():
        files[accessor(entity) + ".py"] = r.entity_module(entity, ops)
    stats = {"entities": len(model.entities), "shared_types": shared, "types": len(model.structs), "operations": len(model.ops)}
    return files, stats


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--check", action="store_true", help="write nothing; exit 1 when a file is stale or extra")
    args = parser.parse_args(argv)
    with open(MANIFEST, encoding="utf-8") as f:
        manifest = json.load(f)
    if manifest.get("version") != 1:
        raise SystemExit("operations.json version %r: this generator knows version 1" % manifest.get("version"))
    files, stats = render_all(manifest)
    existing = set()
    if os.path.isdir(OUT_DIR):
        existing = {n for n in os.listdir(OUT_DIR) if os.path.isfile(os.path.join(OUT_DIR, n)) and n != "py.typed"}
    stale = []
    for name, content in files.items():
        path = os.path.join(OUT_DIR, name)
        current = None
        if os.path.exists(path):
            with open(path, encoding="utf-8", newline="") as f:
                current = f.read()
        if current != content:
            stale.append(name)
            if not args.check:
                os.makedirs(OUT_DIR, exist_ok=True)
                with open(path, "w", encoding="utf-8", newline="\n") as f:
                    f.write(content)
    orphans = sorted(existing - set(files))
    if args.check:
        if stale or orphans:
            for name in stale:
                print("stale: src/qubesync/operations/%s" % name, file=sys.stderr)
            for name in orphans:
                print("not generated: src/qubesync/operations/%s" % name, file=sys.stderr)
            print("run: python %s" % SCRIPT, file=sys.stderr)
            return 1
        print("src/qubesync/operations/ is up to date (%(operations)d operations, %(entities)d entities, %(shared_types)d shared types)" % stats)
        return 0
    for name in orphans:
        os.remove(os.path.join(OUT_DIR, name))
    print("wrote %d of %d files, removed %d (%d operations, %d entities, %d shared types of %d nested)" % (
        len(stale), len(files), len(orphans), stats["operations"], stats["entities"], stats["shared_types"], stats["types"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
