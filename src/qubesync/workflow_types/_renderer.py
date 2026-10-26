"""Writes a render: one Python module with a namespace per workflow (``add_transaction``), its
start and input methods, documented in their docstrings, and a TypedDict per input. JSON Schema
maps to Python types as scripts/generate_operations.py maps it, and the TypedDicts are written
as it writes them, so the module runs on Python 3.8 and imports only qubesync and typing."""

import builtins
import json
import keyword
import re
import textwrap
from typing import Any, Dict, List, NamedTuple, Optional, Set, Tuple

from ._workflow import (
    Error,
    Input,
    Workflow,
    as_list,
    branch_schemas,
    discriminated,
    fixed_value,
    known_operation,
    operation,
    operation_fields,
    pascal,
    set_by_workflow,
)

WIDTH = 96
SCALARS = {"string": "str", "integer": "int", "number": "float", "boolean": "bool"}
TYPING = ("Any", "Dict", "List", "Literal", "Optional", "Protocol", "TypedDict", "Union")
# A start method's own parameters: an input named after one takes a trailing underscore in its
# methods (``version_=``), and keeps its name in the input.
RUN_PARAMS = ("connection", "reference", "webhook_url", "version", "client")
# The module's own lowercase names: a workflow named after one (or after a builtin, which the
# module's code and annotations use) is reached by a trailing underscore, as QuickBooks' class
# entity is client.class_.
MODULE_NAMES = ("client", "connection_id")
_STRING = re.compile(r'"(?:[^"\\]|\\.)*"')
_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_CONTROL = re.compile(r"[\x00-\x1f\x7f]")


class Param(NamedTuple):
    input: Input
    name: str  # its parameter's name
    positional: bool


def params_for(inputs, body):
    # type: (List[Input], Optional[Input]) -> List[Param]
    """The body first (positional), then the other inputs as keywords, sorted. A name that's a
    start's own, or a Python keyword, takes a trailing underscore."""
    taken = [input.name for input in inputs]
    ordered = ([body] + [input for input in inputs if input is not body]) if body else list(inputs)
    params = []
    for input in ordered:
        name = input.name
        if name in RUN_PARAMS or keyword.iskeyword(name):
            name += "_"
            while name in taken:
                name += "_"
            taken.append(name)
        params.append(Param(input, name, input is body))
    return params


def accessor_for(key, taken):
    # type: (str, Set[str]) -> str
    name = key
    if keyword.iskeyword(name) or name in MODULE_NAMES or hasattr(builtins, name):
        name += "_"
    while name in taken:
        name += "_"
    taken.add(name)
    return name


def one_line(text):
    # type: (Any) -> str
    """Text for a comment or a docstring: on one line (so a newline can't end a comment), without
    control characters."""
    return " ".join(_CONTROL.sub(" ", "" if text is None else str(text)).split())


def docstring_text(text):
    # type: (str) -> str
    """Text that can't end a docstring: its backslashes and triple quotes escaped."""
    return text.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')


def wrap(text, first, rest):
    # type: (str, str, str) -> List[str]
    """Word-wraps text to WIDTH: the first line starts with ``first``, the others with ``rest``."""
    lines = textwrap.wrap(
        text,
        WIDTH,
        initial_indent=first,
        subsequent_indent=rest,
        break_long_words=False,
        break_on_hyphens=False,
    )
    return [line.rstrip() for line in lines] or [first.rstrip()]


def comment(text, indent):
    # type: (str, int) -> List[str]
    """A description as ``#:`` lines, as the operations' TypedDicts write theirs."""
    text = one_line(text)
    if not text:
        return []
    prefix = " " * indent + "#: "
    return wrap(text, prefix, prefix)


def literal_text(value):
    # type: (Any) -> str
    """A value as Python writes it: "a", 3, True, None."""
    if value is None:
        return "None"
    if isinstance(value, bool):
        return "True" if value else "False"
    return json.dumps(value, ensure_ascii=False)


class Renderer(object):
    """Renders a list of Workflows, sorted by key, under a header."""

    def __init__(self, workflows, header):
        # type: (List[Workflow], List[str]) -> None
        from ..operations._fields import MODULES

        self.workflows = workflows
        self.header = header
        self.library = MODULES  # type: Dict[str, str]
        # Every name the module defines or could import: a type named after one gets a number.
        self.names = set(TYPING) | set(dir(builtins)) | set(keyword.kwlist) | set(MODULES)
        self.names |= {"Client", "TYPE_CHECKING", "cast"}
        self.imports = {}  # type: Dict[str, Set[str]]
        self.typing = {"Any", "Dict", "Optional", "Protocol", "Union"}  # the helpers'
        self.accessors = {}  # type: Dict[str, str]
        taken = set()  # type: Set[str]
        # The names the integration kit refers to, kept exactly: a clash is an error.
        self.classes = {}  # type: Dict[str, str]
        self.input_names = {}  # type: Dict[Tuple[str, str], str]
        for workflow in workflows:
            self.accessors[workflow.key] = accessor_for(workflow.key, taken)
            self.classes[workflow.key] = self.claim_exact(workflow.pascal + "Workflow", workflow.key)
            self.input_names[(workflow.key, "")] = self.claim_exact(workflow.pascal + "Input", workflow.key)
            for branch in workflow.branches:
                name = workflow.pascal + pascal(branch.title) + "Input"
                self.input_names[(workflow.key, branch.title)] = self.claim_exact(name, workflow.key)

    def render(self):
        # type: () -> str
        sections = []
        for workflow in self.workflows:
            sections.append(self.workflow_section(workflow))
        lines = list(self.header)
        lines.extend(self.module_doc())
        lines.append("")
        lines.extend(self.import_lines())
        lines.extend(["", ""])
        lines.extend(self.helpers())
        for section in sections:
            lines.extend(["", ""])
            lines.extend(section)
        return "\n".join(lines).rstrip() + "\n"

    # -- Names ------------------------------------------------------------------------------

    def claim(self, name):
        # type: (str) -> str
        base = name
        n = 2
        while name in self.names:
            name = "%s%d" % (base, n)
            n += 1
        self.names.add(name)
        return name

    def claim_exact(self, name, key):
        # type: (str, str) -> str
        if name in self.names:
            raise Error("workflow %s's type %s would clash with another name in the module" % (key, name))
        self.names.add(name)
        return name

    def use(self, *names):
        # type: (*str) -> None
        self.typing.update(names)

    def library_type(self, text):
        # type: (str) -> str
        """A type as qubesync.operations writes it, its names imported."""
        for name in _IDENTIFIER.findall(_STRING.sub("", text)):
            if name in TYPING:
                self.use(name)
            elif name in self.library:
                self.imports.setdefault(self.library[name], set()).add(name)
        return text

    # -- The module -------------------------------------------------------------------------

    def module_doc(self):
        # type: () -> List[str]
        paragraphs = [
            "Your app's QuBe Sync workflows, from their input types: each workflow is a namespace "
            "(``add_transaction``) with a start method per branch of its input "
            "(``<workflow>.<branch>(connection, body, ..., reference=, webhook_url=)``), or "
            "``<workflow>.start(connection, <inputs>, reference=, webhook_url=)`` for a workflow "
            "whose input has no branches. Each ``<branch>_input`` (or ``input``) returns the input "
            "alone, as a dict without its None values: for ``start``, or a qubesync.kit Operation's "
            "``input``. connection is a connection's QuBe Sync id, or anything with a ``qube_id`` "
            "(a qubesync.kit Connection).",
            "A start uses this module's ``client`` unless it's passed another as ``client=``. Set it "
            "once, at boot: ``qube_workflows.client = qubesync.Client(api_key=os.environ[\"QUBE_API_KEY\"])``.",
            "Each input is a TypedDict: ``<Workflow><Branch>Input`` for a branch's "
            "(``AddTransactionInvoiceInput``), and ``<Workflow>Input`` for any of a workflow's. An "
            "operation's body is typed as that operation's params (``InvoiceCreateParams``), except "
            "that a field the workflow sets itself is optional (and a value given for it is "
            "overwritten): QuBe Sync checks an input's fields and types when the run starts, and "
            "required fields when it sends the request.",
        ]
        return self.docstring(paragraphs, 0)

    def import_lines(self):
        # type: () -> List[str]
        names = sorted(name for name in self.typing if name in TYPING) + ["cast as _cast"]
        lines = self.import_line("typing", names)
        lines.append("")
        lines.extend(self.import_line("qubesync", ["Client"]))
        for module in sorted(self.imports):
            lines.extend(self.import_line("qubesync.operations." + module, sorted(self.imports[module])))
        return lines

    def import_line(self, module, names):
        # type: (str, List[str]) -> List[str]
        line = "from %s import %s" % (module, ", ".join(names))
        if len(line) <= WIDTH:
            return [line]
        return ["from %s import (" % module] + ["    %s," % name for name in names] + [")"]

    def helpers(self):
        # type: () -> List[str]
        return [
            "#: The qubesync.Client a start uses unless it's given client=. Set it once, at boot.",
            "client = None  # type: Optional[Client]",
            "",
            "",
            "class _HasQubeId(Protocol):",
            "    @property",
            "    def qube_id(self) -> Optional[str]: ...",
            "",
            "",
            "# A connection's QuBe Sync id, or anything with a qube_id (a qubesync.kit Connection).",
            "_Connection = Union[str, _HasQubeId]",
            "",
            "",
            "def connection_id(connection: _Connection) -> Optional[str]:",
            '    """A connection\'s QuBe Sync id: connection itself, or its qube_id (a qubesync.kit',
            '    Connection)."""',
            "    if isinstance(connection, str):",
            "        return connection",
            "    return connection.qube_id",
            "",
            "",
            "def _start(",
            "    connection: _Connection,",
            "    workflow: str,",
            "    input: Any,",
            "    reference: str,",
            "    webhook_url: str,",
            "    version: Optional[int],",
            "    given: Optional[Client],",
            ") -> Any:",
            "    chosen = given if given is not None else client",
            "    if chosen is None:",
            "        raise ValueError(",
            "            \"%s.client isn't set: set it once, at boot (%s.client = qubesync.Client(api_key=...)), \"",
            '            "or pass client=" % (__name__, __name__)',
            "        )",
            "    qube_id = connection_id(connection)",
            "    if not qube_id:",
            "        raise ValueError(\"%r has no QuBe Sync id: the customer finishes onboarding first\" % (connection,))",
            "    return chosen.start_run(",
            "        qube_id, workflow, input, reference=reference, webhook_url=webhook_url, version=version",
            "    )",
            "",
            "",
            "def _compact(values: Dict[str, Any]) -> Dict[str, Any]:",
            "    return {key: value for key, value in values.items() if value is not None}",
        ]

    # -- A workflow -------------------------------------------------------------------------

    def workflow_section(self, workflow):
        # type: (Workflow) -> List[str]
        self.workflow = workflow
        self.memo = {}  # type: Dict[Any, str]
        self.prefix = None  # type: Optional[str]
        self.defs = []  # type: List[str]
        cls = self.classes[workflow.key]
        methods = []  # type: List[str]
        if workflow.discriminated:
            for branch in workflow.branches:
                # A body's own TypedDict is named for its branch.
                self.prefix = branch.title
                name = self.input_names[(workflow.key, branch.title)]
                rows = [(workflow.discriminator, self.literal_type([branch.value]), True, "")]
                rows += [self.row(input) for input in branch.inputs]
                doc = "%s's input with ``%s`` %s." % (
                    workflow.key,
                    workflow.discriminator,
                    literal_text(branch.value),
                )
                self.typeddict(name, rows, doc)
                params = params_for(branch.inputs, branch.body)
                methods.extend([""] + self.branch_method(workflow, branch, params))
                methods.extend([""] + self.branch_builder(workflow, branch, params))
            self.prefix = None
            union = [self.input_names[(workflow.key, branch.title)] for branch in workflow.branches]
            self.alias(self.input_names[(workflow.key, "")], union)
            methods.extend([""] + self.start_any_method(workflow))
        else:
            name = self.input_names[(workflow.key, "")]
            rows = [self.row(input) for input in workflow.inputs]
            self.typeddict(name, rows, "%s's input." % workflow.key)
            params = params_for(workflow.inputs, None)
            methods.extend([""] + self.start_method(workflow, params))
            methods.extend([""] + self.input_method(workflow, params))

        title = self.title(workflow)
        lines = [("# -- %s " % workflow.key).ljust(WIDTH, "-"), ""]
        lines.extend(self.defs)
        version = "a draft, not published yet" if workflow.draft else "version %s" % literal_text(workflow.version)
        intro = "%s (``%s``, %s)." % (title, workflow.key, version)
        description = one_line(workflow.description)
        paragraphs = [intro + (" " + description if description else "")]
        if workflow.discriminated:
            names = ", ".join("%s (%s)" % (b.method, literal_text(b.value)) for b in workflow.branches)
            paragraphs.append(
                "A start method per ``%s``: %s. ``start`` takes any of their inputs." % (workflow.discriminator, names)
            )
        lines.append("class %s:" % cls)
        lines.extend(self.docstring(paragraphs, 4))
        lines.append("")
        lines.append("    WORKFLOW = %s" % json.dumps(workflow.key))
        lines.append("    #: The version these types describe (None for a draft). A start runs the published")
        lines.append("    #: version unless given version=.")
        lines.append("    VERSION: Optional[int] = %s" % literal_text(workflow.version))
        lines.extend(methods)
        lines.extend(["", ""])
        lines.append("#: %s (``%s``)." % (title, workflow.key))
        lines.append("%s = %s" % (self.accessors[workflow.key], cls))
        return lines

    def title(self, workflow):
        # type: (Workflow) -> str
        return one_line(workflow.name) or workflow.key

    def row(self, input):
        # type: (Input) -> Tuple[str, str, bool, str]
        return (input.name, self.type_of(input.schema, input.name), input.required, self.input_text(input.schema))

    # -- Methods ----------------------------------------------------------------------------

    def branch_method(self, workflow, branch, params):
        # type: (Workflow, Any, List[Param]) -> List[str]
        cls = self.classes[workflow.key]
        paragraphs = ["Starts %s with ``%s`` %s." % (workflow.key, workflow.discriminator, literal_text(branch.value))]
        paragraphs.extend(self.workflow_paragraph(workflow))
        args = [self.connection_arg()] + self.input_args(params) + self.run_args()
        lines = self.signature(branch.method, ["connection: _Connection"] + self.param_list(params, run=True), "Any")
        lines.extend(self.method_doc(paragraphs, args, ["The run, as ``Client.start_run`` returns it."]))
        built = "%s.%s(%s)" % (cls, branch.builder, self.call_args(params))
        lines.extend(self.start_call(workflow, built))
        return lines

    def branch_builder(self, workflow, branch, params):
        # type: (Workflow, Any, List[Param]) -> List[str]
        name = self.input_names[(workflow.key, branch.title)]
        paragraphs = [
            "%s's input with ``%s`` %s, without its None values: for ``start``, or a qubesync.kit "
            "Operation's ``input``." % (workflow.key, workflow.discriminator, literal_text(branch.value))
        ]
        lines = self.signature(branch.builder, self.param_list(params, run=False), name)
        lines.extend(self.method_doc(paragraphs, self.input_args(params), ["The input (``%s``)." % name]))
        pairs = [(workflow.discriminator, literal_text(branch.value))] + [(p.input.name, p.name) for p in params]
        lines.extend(self.build(name, pairs))
        return lines

    def start_any_method(self, workflow):
        # type: (Workflow) -> List[str]
        name = self.input_names[(workflow.key, "")]
        builders = " or ".join("``%s``" % branch.builder for branch in workflow.branches)
        paragraphs = ["Starts %s with any of its inputs: a dict as %s returns it." % (workflow.key, builders)]
        paragraphs.extend(self.workflow_paragraph(workflow))
        args = [self.connection_arg(), ("input", "the input (``%s``)." % name)] + self.run_args()
        params = ["connection: _Connection", "input: %s" % name, "*"] + self.run_params()
        lines = self.signature("start", params, "Any")
        lines.extend(self.method_doc(paragraphs, args, ["The run, as ``Client.start_run`` returns it."]))
        lines.extend(self.start_call(workflow, "input"))
        return lines

    def start_method(self, workflow, params):
        # type: (Workflow, List[Param]) -> List[str]
        cls = self.classes[workflow.key]
        paragraphs = ["Starts %s." % workflow.key] + self.workflow_paragraph(workflow)
        args = [self.connection_arg()] + self.input_args(params) + self.run_args()
        lines = self.signature("start", ["connection: _Connection"] + self.param_list(params, run=True), "Any")
        lines.extend(self.method_doc(paragraphs, args, ["The run, as ``Client.start_run`` returns it."]))
        lines.extend(self.start_call(workflow, "%s.input(%s)" % (cls, self.call_args(params))))
        return lines

    def input_method(self, workflow, params):
        # type: (Workflow, List[Param]) -> List[str]
        name = self.input_names[(workflow.key, "")]
        paragraphs = [
            "%s's input, without its None values: for ``start``, or a qubesync.kit Operation's "
            "``input``." % workflow.key
        ]
        lines = self.signature("input", self.param_list(params, run=False), name)
        lines.extend(self.method_doc(paragraphs, self.input_args(params), ["The input (``%s``)." % name]))
        lines.extend(self.build(name, [(p.input.name, p.name) for p in params]))
        return lines

    def workflow_paragraph(self, workflow):
        # type: (Workflow) -> List[str]
        description = one_line(workflow.description)
        return ["%s: %s" % (self.title(workflow), description)] if description else []

    def signature(self, name, params, returns):
        # type: (str, List[str], str) -> List[str]
        lines = ["    @staticmethod"]
        if not params:
            return lines + ["    def %s() -> %s:" % (name, returns)]
        lines.append("    def %s(" % name)
        lines.extend("        %s," % param if param != "*" else "        *," for param in params)
        lines.append("    ) -> %s:" % returns)
        return lines

    def param_list(self, params, run):
        # type: (List[Param], bool) -> List[str]
        out = []
        keywords = False
        for param in params:
            rendered = self.type_of(param.input.schema, param.input.name)
            if not param.positional and not keywords:
                out.append("*")
                keywords = True
            if param.input.required:
                out.append("%s: %s" % (param.name, rendered))
            else:
                out.append("%s: %s = None" % (param.name, self.optional(rendered)))
        if run:
            if not keywords:
                out.append("*")
            out.extend(self.run_params())
        return out

    def run_params(self):
        # type: () -> List[str]
        return [
            "reference: str",
            "webhook_url: str",
            "version: Optional[int] = None",
            "client: Optional[Client] = None",
        ]

    def call_args(self, params):
        # type: (List[Param]) -> str
        return ", ".join(p.name if p.positional else "%s=%s" % (p.name, p.name) for p in params)

    def start_call(self, workflow, input_expr):
        # type: (Workflow, str) -> List[str]
        args = ["connection", json.dumps(workflow.key), input_expr, "reference", "webhook_url", "version", "client"]
        line = "        return _start(%s)" % ", ".join(args)
        if len(line) <= WIDTH:
            return [line]
        return ["        return _start("] + ["            %s," % arg for arg in args] + ["        )"]

    def build(self, name, pairs):
        # type: (str, List[Tuple[str, str]]) -> List[str]
        if not pairs:
            return ["        return _cast(%s, {})" % name]
        lines = ["        return _cast(%s, _compact({" % name]
        lines.extend("            %s: %s," % (json.dumps(key), value) for key, value in pairs)
        lines.append("        }))")
        return lines

    # -- Docstrings -------------------------------------------------------------------------

    def docstring(self, paragraphs, indent):
        # type: (List[str], int) -> List[str]
        pad = " " * indent
        lines = []  # type: List[str]
        for i, paragraph in enumerate(paragraphs):
            if i:
                lines.append("")
            lines.extend(wrap(docstring_text(paragraph), pad, pad))
        lines[0] = pad + '"""' + lines[0][indent:]
        if len(paragraphs) == 1 and len(lines) == 1 and len(lines[0]) + 3 <= WIDTH:
            lines[0] += '"""'
        else:
            lines.append(pad + '"""')
        return lines

    def method_doc(self, paragraphs, args, returns):
        # type: (List[str], List[Tuple[str, str]], List[str]) -> List[str]
        pad = " " * 8
        lines = []  # type: List[str]
        for i, paragraph in enumerate(paragraphs):
            if i:
                lines.append("")
            lines.extend(wrap(docstring_text(paragraph), pad, pad))
        if args:
            lines.extend(["", pad + "Args:"])
            for name, text in args:
                lines.extend(wrap(docstring_text(("%s: %s" % (name, text)).rstrip()), pad + "    ", pad + "        "))
        lines.extend(["", pad + "Returns:"])
        for text in returns:
            lines.extend(wrap(docstring_text(text), pad + "    ", pad + "    "))
        lines[0] = pad + '"""' + lines[0][len(pad):]
        lines.append(pad + '"""')
        return lines

    def connection_arg(self):
        # type: () -> Tuple[str, str]
        return ("connection", "the connection's QuBe Sync id, or anything with a ``qube_id`` (a qubesync.kit Connection).")

    def run_args(self):
        # type: () -> List[Tuple[str, str]]
        return [
            ("reference", "your reference for the run, also its Idempotency-Key, so a retry never starts a second run."),
            ("webhook_url", "where QuBe Sync sends the run's webhooks."),
            ("version", "the version to run; None runs the published one."),
            ("client", "the qubesync.Client to start it with; this module's ``client`` by default."),
        ]

    def input_args(self, params):
        # type: (List[Param]) -> List[Tuple[str, str]]
        args = []
        for param in params:
            text = self.input_text(param.input.schema)
            if param.name != param.input.name:
                text = ("the ``%s`` input. %s" % (param.input.name, text)).rstrip()
            args.append((param.name, text))
        return args

    def input_text(self, schema):
        # type: (Dict[str, Any]) -> str
        """What an input's docs say: what it's the body of, its description, what the workflow
        sets in it, and the values it takes."""
        parts = []
        id = operation(schema)
        if id:
            parts.append(self.operation_phrase(id))
        description = one_line(schema.get("description"))
        fields = set_by_workflow(schema) if id else []
        if id and (description or fields):
            parts[-1] += ":" if description else "."
        if description:
            parts.append(description)
        if fields:
            parts.append(
                "The workflow sets %s itself: a value given for %s is overwritten."
                % (", ".join("``%s``" % field for field in fields), "it" if len(fields) == 1 else "them")
            )
        if isinstance(schema.get("enum"), list):
            parts.append("One of %s." % ", ".join(literal_text(value) for value in schema["enum"]))
        if "const" in schema:
            parts.append("Always %s." % literal_text(schema["const"]))
        extra = schema.get("additionalProperties")
        if isinstance(extra, dict) and isinstance(extra.get("enum"), list):
            parts.append("Each value is one of %s." % ", ".join(literal_text(value) for value in extra["enum"]))
        nested = schema["items"] if isinstance(schema.get("items"), dict) else schema
        if not id and discriminated(nested):
            parts.append(self.branches_phrase(nested, "It's" if nested is schema else "Each is"))
        return " ".join(parts)

    def operation_phrase(self, id):
        # type: (str) -> str
        known = known_operation(id)
        if known:
            return "the %s body (see ``client.%s.%s``)" % (id, known[0], id.split(".", 1)[1])
        return "the %s body (an operation this version of qubesync doesn't know)" % id

    def branches_phrase(self, schema, subject):
        # type: (Dict[str, Any], str) -> str
        """A nested discriminated object's branches, by their values: each branch's TypedDict
        says what its bodies are (an ``adds`` entry's ``add``, the customer.create body)."""
        discriminator = schema["discriminator"]["propertyName"]
        values = [literal_text(fixed_value(properties, discriminator)) for _, properties, _ in branch_schemas(schema)]
        return "%s one of these, by ``%s``: %s." % (subject, discriminator, ", ".join(values))

    # -- Types ------------------------------------------------------------------------------

    def type_of(self, schema, path):
        # type: (Dict[str, Any], str) -> str
        return self.union(self.members(schema, path))

    def members(self, schema, path):
        # type: (Dict[str, Any], str) -> List[str]
        id = operation(schema)
        if id:
            return [self.body_type(id, schema, path)]
        if discriminated(schema):
            return [self.named(schema, path)]
        if "const" in schema:
            return [self.literal_type([schema["const"]])]
        if isinstance(schema.get("enum"), list):
            return self.literal_members(schema["enum"])
        kinds = as_list(schema.get("type"))
        if not kinds:
            if "properties" in schema:
                kinds.append("object")
            if "items" in schema:
                kinds.append("array")
        if not kinds:
            return ["Any"]
        out = []
        for kind in kinds:
            if kind in SCALARS:
                out.append(SCALARS[kind])
            elif kind == "null":
                out.append("None")
            elif kind == "array":
                items = schema.get("items") if isinstance(schema.get("items"), dict) else {}
                self.use("List")
                out.append("List[%s]" % self.type_of(items, path + "_item"))
            elif kind == "object":
                out.append(self.object_type(schema, path))
            else:
                out.append("Any")
        return out

    def union(self, members):
        # type: (List[str]) -> str
        seen = []  # type: List[str]
        for member in members:
            if member not in seen:
                seen.append(member)
        if "Any" in seen:
            return "Any"
        others = [member for member in seen if member != "None"]
        inner = others[0] if len(others) == 1 else "Union[%s]" % ", ".join(others)
        if len(others) == len(seen):
            return inner
        if not others:
            return "None"
        return "Optional[%s]" % inner

    def optional(self, rendered):
        # type: (str) -> str
        if rendered in ("Any", "None") or rendered.startswith("Optional["):
            return rendered
        return "Optional[%s]" % rendered

    def literal_members(self, values):
        # type: (List[Any]) -> List[str]
        """An enum's values as types: the strings, integers and booleans as one Literal, None,
        and float or Any for what a Literal can't hold."""
        plain = [v for v in values if isinstance(v, (str, int)) and not isinstance(v, float)]
        out = []
        if plain:
            self.use("Literal")
            out.append("Literal[%s]" % ", ".join(literal_text(v) for v in plain))
        if any(v is None for v in values):
            out.append("None")
        if any(isinstance(v, float) for v in values):
            out.append("float")
        if any(not isinstance(v, (str, int, float)) and v is not None for v in values):
            out.append("Any")
        return out

    def literal_type(self, values):
        # type: (List[Any]) -> str
        return self.union(self.literal_members(values))

    def object_type(self, schema, path):
        # type: (Dict[str, Any], str) -> str
        properties = schema.get("properties") if isinstance(schema.get("properties"), dict) else {}
        extra = schema.get("additionalProperties")
        if not properties:
            if isinstance(extra, dict):
                return "Dict[str, %s]" % self.type_of(extra, path + "_value")
            return "Dict[str, Any]"
        key = ("object", path, json.dumps(schema, sort_keys=True))
        if key in self.memo:
            return self.memo[key]
        required = as_list(schema.get("required"))
        rows = []
        for field, sub in sorted(properties.items()):
            sub = sub if isinstance(sub, dict) else {}
            rows.append((field, self.type_of(sub, path + "_" + field), field in required, self.input_text(sub)))
        name = self.claim(self.workflow.pascal + pascal(path))
        self.memo[key] = name
        self.typeddict(name, rows, None)
        return name

    def named(self, schema, path):
        # type: (Dict[str, Any], str) -> str
        """A nested discriminated object (an ``adds`` entry): a TypedDict per branch, named
        <alias><Title>, and their Union. The same schema at the same place shares one."""
        key = ("union", path, json.dumps(schema, sort_keys=True))
        if key in self.memo:
            return self.memo[key]
        name = self.claim(self.workflow.pascal + pascal(path))
        self.memo[key] = name
        # Shared by every branch of the workflow, so not named for one.
        prefix = self.prefix
        self.prefix = None
        discriminator = schema["discriminator"]["propertyName"]
        members = []
        for title, properties, required in branch_schemas(schema):
            fields = sorted(properties.items(), key=lambda item: (item[0] != discriminator, item[0]))
            rows = []
            for field, sub in fields:
                sub = sub if isinstance(sub, dict) else {}
                is_required = field == discriminator or field in required
                rows.append((field, self.type_of(sub, path + "_" + field), is_required, self.input_text(sub)))
            member = self.claim(name + pascal(title))
            value = literal_text(fixed_value(properties, discriminator))
            self.typeddict(member, rows, "%s's %s with ``%s`` %s." % (self.workflow.key, path, discriminator, value))
            members.append(member)
        self.alias(name, members)
        self.prefix = prefix
        return name

    def body_type(self, id, schema, path):
        # type: (str, Dict[str, Any], str) -> str
        """An operation body: the operation's params TypedDict, or, when the workflow sets some
        of its required fields itself (set_by_workflow), a TypedDict of its own with those made
        optional, named <Workflow><Branch><Input>Body (<Workflow><Input>Body without branches).
        A field or an operation this version doesn't know is ignored."""
        fields = operation_fields(id)
        if fields is None:
            return self.operation_type(id)
        relaxed = [field for field in set_by_workflow(schema) if field in fields and fields[field][1]]
        if not relaxed:
            return self.operation_type(id)
        base = "_".join(part for part in (self.prefix, path) if part)
        key = ("body", base, id, tuple(relaxed))
        if key in self.memo:
            return self.memo[key]
        name = self.claim(self.workflow.pascal + pascal(base) + "Body")
        self.memo[key] = name
        accessor, params = known_operation(id) or ("", "")
        rows = [
            (field, self.library_type(rendered), required and field not in relaxed, "")
            for field, (rendered, required) in sorted(fields.items())
        ]
        doc = (
            "The %s body (``%s``, documented on ``client.%s.%s``), except that the workflow sets %s "
            "itself: optional here, and a value given for %s is overwritten."
            % (
                id,
                params,
                accessor,
                id.split(".", 1)[1],
                ", ".join("``%s``" % field for field in relaxed),
                "it" if len(relaxed) == 1 else "them",
            )
        )
        self.typeddict(name, rows, doc)
        return name

    def operation_type(self, id):
        # type: (str) -> str
        known = known_operation(id)
        if not known:
            return "Dict[str, Any]"
        return self.library_type(known[1])

    # -- Definitions ------------------------------------------------------------------------

    def alias(self, name, members):
        # type: (str, List[str]) -> None
        if not members:
            target = "Dict[str, Any]"
        elif len(members) == 1:
            target = members[0]
        else:
            target = "Union[%s]" % ", ".join(members)
        line = "%s = %s" % (name, target)
        if len(line) > WIDTH and len(members) > 1:
            self.defs.extend(["%s = Union[" % name] + ["    %s," % member for member in members] + ["]"])
        else:
            self.defs.append(line)
        self.defs.extend(["", ""])

    def typeddict(self, name, rows, doc):
        # type: (str, List[Tuple[str, str, bool, str]], Optional[str]) -> None
        """Python 3.8 TypedDicts, as scripts/generate_operations.py writes them: required keys in
        a total=True base, the rest in a total=False class. A key that isn't an identifier
        (``class``) goes in a functional-syntax base."""
        self.use("TypedDict")
        groups = {(r, kw): [] for r in (True, False) for kw in (True, False)}  # type: Dict[Tuple[bool, bool], List[Any]]
        for row in rows:
            groups[(row[2], not row[0].isidentifier() or keyword.iskeyword(row[0]))].append(row)
        out = self.defs
        bases = []

        def body(items, indent):
            # type: (List[Any], int) -> List[str]
            lines = []
            for field, rendered, _, text in items:
                lines.extend(comment(text, indent))
                lines.append(" " * indent + "%s: %s" % (field, rendered))
            return lines

        def functional(base_name, items, total):
            # type: (str, List[Any], bool) -> List[str]
            lines = ["%s = TypedDict(" % base_name, '    "%s",' % base_name, "    {"]
            for field, rendered, _, text in items:
                lines.extend(comment(text, 8))
                lines.append("        %s: %s," % (json.dumps(field), rendered))
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
        lines = self.docstring([doc], 4) if doc else []
        lines.extend(body(groups[(False, False)], 4))
        out.extend(lines or ["    pass"])
        out.extend(["", ""])
