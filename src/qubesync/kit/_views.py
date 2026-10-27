"""The view-models the screens' templates render: the override contract, kept stable across
versions (README, "Styling"). The same fields as qube_rails' QuestionView, ChoiceView,
FieldView, RowsView, RowView, CellView and RunStatusView, in snake_case, with no "?" on the
booleans (plain, secondary, labelled, cell, segmented, hidden, visible).
"""
import json
import re
from typing import Any, Callable, Dict, List, Optional

from ._messages import t
from ._settings import UI_PIECES, settings

__all__ = [
    "QuestionView",
    "ChoiceView",
    "FieldView",
    "RowsView",
    "RowView",
    "CellView",
    "DetailView",
    "OptionView",
    "RunStatusView",
    "STALL_REASONS",
    "qube_classes",
]


def qube_classes(piece, *base):
    # type: (str, *Any) -> str
    """The classes for a piece of the screens: its qube- classes (base), then the ui_classes
    setting's for that piece. A piece not in UI_PIECES raises."""
    if piece not in UI_PIECES:
        raise ValueError("QuBe Sync: no ui_classes piece %r" % (piece,))
    extra = settings().ui_classes.get(piece)
    names = []  # type: List[str]
    for item in list(base) + [extra]:
        if isinstance(item, (list, tuple)):
            names.extend(str(i) for i in item if i)
        elif item:
            names.append(str(item))
    return " ".join(names)


def _presence(value):
    # type: (Any) -> Optional[str]
    text = "" if value is None else str(value)
    return text if text.strip() else None


class DetailView(object):
    """One label and value row of what the question is about."""

    def __init__(self, label, value):
        # type: (Any, Any) -> None
        self.label = label
        self.value = value


class OptionView(object):
    """One of a select's options."""

    def __init__(self, value, label):
        # type: (Any, str) -> None
        self.value = value
        self.label = label


class QuestionView(object):
    """The open question of a run, built from the prompt QuBe Sync sent: message, details,
    choices (picks, forms and exits), token, action_url, search_url, error and prompt."""

    def __init__(self, prompt, action_url, search_url, error=None):
        # type: (Dict[str, Any], str, str, Optional[str]) -> None
        self.prompt = prompt
        self.message = str(prompt.get("message") or "")
        self.token = str(prompt.get("token") or "")
        self.details = [
            DetailView(row.get("label"), row.get("value")) for row in prompt.get("details") or [] if isinstance(row, dict)
        ]
        self.action_url = action_url
        self.search_url = search_url
        self.error = error
        choices = [c for c in prompt.get("choices") or [] if isinstance(c, dict)]
        self.choices = [ChoiceView(choice, n, self) for n, choice in enumerate(choices)]
        self._arrange()

    @classmethod
    def from_run(cls, run, action_for, error=None):
        # type: (Any, Callable[[Any], str], Optional[str]) -> Optional[QuestionView]
        """The question run is asking, or None when it isn't. action_for(run) is its question
        route."""
        prompt = run.open_question if run is not None else None
        if prompt is None:
            return None
        action = action_for(run)
        return cls(prompt, action_url=action, search_url="%s/search" % action, error=error)

    @property
    def picks(self):
        # type: () -> List[ChoiceView]
        return [c for c in self.choices if c.kind == "pick"]

    @property
    def forms(self):
        # type: () -> List[ChoiceView]
        return [c for c in self.choices if c.kind == "form"]

    @property
    def exits(self):
        # type: () -> List[ChoiceView]
        return [c for c in self.choices if c.kind == "exit"]

    @property
    def plain(self):
        # type: () -> bool
        """Neither a pick nor a form: the choices show in one row, the first primary."""
        return not self.picks and not self.forms

    # With no picks but a form, a plain choice before the first form (a name clash's "Use the
    # existing record") is a pick too. One filled button at most.
    def _arrange(self):
        # type: () -> None
        kinds = [c.kind for c in self.choices]
        if "pick" not in kinds and "form" in kinds:
            for choice in self.choices[: kinds.index("form")]:
                if not choice.secondary:
                    choice.kind = "pick"
        if self.plain:
            primary = next((c for c in self.choices if not c.secondary), None)
        else:
            primary = self.forms[0] if self.forms else None
        for choice in self.choices:
            if choice.kind == "pick":
                choice.style = None
            elif choice is primary:
                choice.style = "primary"
            elif choice.secondary:
                choice.style = "ghost"
            else:
                choice.style = "secondary"


class ChoiceView(object):
    """One thing the user can pick: a form of its own posting choice=<id> and data[...] to
    action_url. kind is "pick" (an option row), "form" (a choice with fields) or "exit" (none of
    these, cancel); style is its button's: "primary", "secondary", "ghost" (cancel), or None for
    a pick."""

    def __init__(self, choice, index, question):
        # type: (Dict[str, Any], int, QuestionView) -> None
        self.id = str(choice.get("id") or "")
        self.label = str(choice.get("label") or "")
        self.detail = _presence(choice.get("detail"))
        self.description = _presence(choice.get("description"))
        self.index = index
        self.action_url = question.action_url
        self.fields = [
            FieldView.from_prompt(field, question, index) for field in choice.get("fields") or [] if isinstance(field, dict)
        ]
        if self.fields:
            self.kind = "form"
        elif re.search(r":\d+\Z", self.id):
            self.kind = "pick"
        else:
            self.kind = "exit"
        self.style = None  # type: Optional[str]

    @property
    def secondary(self):
        # type: () -> bool
        """A choice that stops (cancel)."""
        return self.id == "cancel"

    @property
    def button_piece(self):
        # type: () -> str
        """The ui_classes piece for its button."""
        if self.style == "primary":
            return "button"
        if self.style == "ghost" and "button_ghost" in settings().ui_classes:
            return "button_ghost"
        return "button_secondary"


class FieldView(object):
    """One input: a choice's field, or a field of a rows field's record. type is "text",
    "number", "boolean", "select", "search" or "rows"; template is the piece that renders it
    (qubesync/question/fields/<type>.html). Post its value as input_name."""

    TYPES = ("text", "number", "boolean", "select", "search", "rows")

    def __init__(
        self,
        name,
        type,
        label,
        input_name=None,
        dom_id=None,
        required=False,
        options=None,
        kind=None,
        search_url=None,
        search_field=None,
        row_key=None,
        when=None,
        rows=None,
        context="choice",
        disabled=False,
    ):
        # type: (str, str, Any, Optional[str], Optional[str], bool, Optional[List[OptionView]], Any, Optional[str], Optional[str], Optional[str], Optional[Dict[str, Any]], Optional[RowsView], str, bool) -> None
        if type not in self.TYPES:
            raise ValueError("QuBe Sync: no field type %r" % (type,))
        self.name = name
        self.type = type
        self.label = "" if label is None else str(label)
        self.input_name = input_name
        self.dom_id = dom_id
        self.required = required
        self.options = options or []
        self.kind = kind
        self.search_url = search_url
        self.search_field = search_field
        self.row_key = row_key
        self.when = when or {}
        self.rows = rows
        self.context = context
        self.disabled = disabled

    @classmethod
    def from_prompt(cls, field, question, choice_index):
        # type: (Dict[str, Any], QuestionView, int) -> FieldView
        name = str(field.get("name") or "")
        input_name = "data[%s]" % name
        type = cls.type_of(field)
        rows = RowsView(field, input_name=input_name, search_url=question.search_url) if type == "rows" else None
        return cls(
            name=name,
            type=type,
            label=field.get("label") or name,
            input_name=input_name,
            dom_id="qube-%s-%s-%s" % (question.token, choice_index, name),
            required=field.get("required") is True,
            options=cls.options_of(field),
            kind=field.get("kind"),
            search_url=question.search_url,
            search_field=name,
            rows=rows,
        )

    @staticmethod
    def type_of(field):
        # type: (Dict[str, Any]) -> str
        """What a prompt field shows as: a record a search, an enum a select, else its type."""
        if field.get("type") == "rows":
            return "rows"
        if field.get("type") == "record":
            return "search"
        if isinstance(field.get("enum"), list) and field.get("enum"):
            return "select"
        if field.get("type") in ("boolean", "number"):
            return str(field["type"])
        return "text"

    @staticmethod
    def options_of(field):
        # type: (Dict[str, Any]) -> List[OptionView]
        return [
            OptionView(e.get("value"), str(e.get("label") or e.get("value")))
            for e in field.get("enum") or []
            if isinstance(e, dict)
        ]

    @property
    def template(self):
        # type: () -> str
        return "qubesync/question/fields/%s.html" % self.type

    @property
    def cell(self):
        # type: () -> bool
        """A field of a rows field's record."""
        return self.context == "cell"

    @property
    def labelled(self):
        # type: () -> bool
        """Shown with its own label: always, now that a record's fields stack."""
        return True

    @property
    def segmented(self):
        # type: () -> bool
        """A record's select of at most three options: a segmented control."""
        return self.cell and self.type == "select" and 1 <= len(self.options) <= 3


def _when_of(column):
    # type: (Dict[str, Any]) -> Dict[str, Any]
    when = column.get("when")
    return when if isinstance(when, dict) else {}


class RowsView(object):
    """A rows field (add_transaction's question about missing records): the same columns asked
    of each record, posted as data[<field>][<row key>][<column>]. columns are FieldViews, rows
    RowViews; set_all is the column "Set all to:" sets on every record, or None."""

    def __init__(self, field, input_name, search_url):
        # type: (Dict[str, Any], str, str) -> None
        self.name = str(field.get("name") or "")
        self.label = str(field.get("label") or self.name)
        self.input_name = input_name
        self.search_url = search_url
        declared = [c for c in field.get("columns") or [] if isinstance(c, dict)]
        self.columns = [self._column_field(column) for column in declared]
        rows = [r for r in field.get("rows") or [] if isinstance(r, dict)]
        self.rows = [RowView(row, declared, self, n) for n, row in enumerate(rows)]

    def cell_field(self, column, row_key, row_index, shown):
        # type: (Dict[str, Any], str, int, bool) -> FieldView
        """A column's control for one record; not required in the markup while hidden."""
        col = str(column.get("name") or "")
        prefix = re.sub(r"-+", "-", "qube-%s%s-%s" % (re.sub(r"[^A-Za-z0-9]+", "-", self.input_name), row_index, col))
        return FieldView(
            name=col,
            type=FieldView.type_of(column),
            label=column.get("label") or col,
            input_name="%s[%s][%s]" % (self.input_name, row_key, col),
            dom_id=prefix,
            required=column.get("required") is True and shown,
            options=FieldView.options_of(column),
            kind=column.get("kind"),
            search_url=self.search_url,
            search_field="%s.%s" % (self.name, col),
            row_key=row_key,
            when=_when_of(column),
            context="cell",
            disabled=not shown,
        )

    @property
    def set_all(self):
        # type: () -> Optional[FieldView]
        """The first segmented column two records or more ask."""
        if len(self.rows) < 2:
            return None
        for column in self.columns:
            if column.type != "select" or not 1 <= len(column.options) <= 3:
                continue
            asking = [r for r in self.rows if any(c.column == column.name and c.field is not None for c in r.cells)]
            if len(asking) >= 2:
                return column
        return None

    def _column_field(self, column):
        # type: (Dict[str, Any]) -> FieldView
        col = str(column.get("name") or "")
        return FieldView(
            name=col,
            type=FieldView.type_of(column),
            label=column.get("label") or col,
            required=column.get("required") is True,
            options=FieldView.options_of(column),
            kind=column.get("kind"),
            search_url=self.search_url,
            search_field="%s.%s" % (self.name, col),
            when=_when_of(column),
            context="cell",
        )


class RowView(object):
    """One record: its cells (the columns it asks, and a value it already has) and its values
    (values_json for data-qube-values, which a column's "when" reads)."""

    def __init__(self, row, declared, rows, index=0):
        # type: (Dict[str, Any], List[Dict[str, Any]], RowsView, int) -> None
        self.key = str(row.get("key") or "")
        self.label = str(row.get("label") or self.key)
        self.detail = _presence(row.get("detail"))
        values = row.get("values")
        self.values = values if isinstance(values, dict) else {}  # type: Dict[str, Any]
        self.index = index
        self.header_id = re.sub(r"-+", "-", "qube-row-%s%s" % (re.sub(r"[^A-Za-z0-9]+", "-", rows.input_name), index))
        asks = [str(c) for c in row.get("columns") or []]
        self.cells = []  # type: List[CellView]
        for column in declared:
            col = str(column.get("name") or "")
            when = _when_of(column)
            shown = self._applies(when)
            label = str(column.get("label") or col)
            if col in asks:
                self.cells.append(
                    CellView(
                        column=col,
                        label=label,
                        field=rows.cell_field(column, self.key, index, shown),
                        when=when,
                        shown=shown,
                        required=column.get("required") is True,
                    )
                )
            elif self.values.get(col) not in (None, ""):
                self.cells.append(
                    CellView(column=col, label=label, preset=self._preset(column, self.values[col]), when=when, shown=shown)
                )

    @property
    def values_json(self):
        # type: () -> str
        return json.dumps(self.values)

    @property
    def segmented_cells(self):
        # type: () -> List[CellView]
        return [c for c in self.cells if c.segmented]

    @property
    def field_cells(self):
        # type: () -> List[CellView]
        return [c for c in self.cells if not c.segmented]

    def _applies(self, when):
        # type: (Dict[str, Any]) -> bool
        for col, allowed in when.items():
            allowed = allowed if isinstance(allowed, list) else [allowed]
            if self.values.get(col) not in allowed:
                return False
        return True

    @staticmethod
    def _preset(column, value):
        # type: (Dict[str, Any], Any) -> str
        for entry in column.get("enum") or []:
            if isinstance(entry, dict) and entry.get("value") == value:
                return str(entry.get("label") or "")
        return str(value)


class CellView(object):
    """One field of a record: a field to fill, or what it already has (preset, read-only). A
    cell whose "when" doesn't hold yet is hidden, its input disabled and not required; required
    is the column's, which the script restores as it shows it."""

    def __init__(self, column, label=None, field=None, preset=None, when=None, shown=True, required=False):
        # type: (str, Optional[str], Optional[FieldView], Optional[str], Optional[Dict[str, Any]], bool, bool) -> None
        self.column = column
        self.label = label or column
        self.field = field
        self.preset = preset
        self.when = when or {}
        self.shown = shown
        self.required = required

    @property
    def when_json(self):
        # type: () -> str
        return json.dumps(self.when)

    @property
    def hidden(self):
        # type: () -> bool
        return not self.shown

    @property
    def segmented(self):
        # type: () -> bool
        return self.field is not None and self.field.segmented


# The stall reasons with words of their own (status.stalled.<reason>); any other is "other".
STALL_REASONS = ("not_checking_in", "quickbooks_unavailable")


class RunStatusView(object):
    """Where a record stands: status (SyncStatus's), state (the latest run's, or None), summary
    (a few words, for the pill), reason (why it failed or was cancelled, a sentence), detail
    (what to do about a failure), quiet_text, retry_url and redeliver_url (None when the button
    doesn't apply), error, stall (the stalled connection's reason while a sending status waits
    on it) and stall_text."""

    def __init__(
        self,
        status,
        state=None,
        summary=None,
        reason=None,
        detail=None,
        quiet_text=None,
        retry_url=None,
        redeliver_url=None,
        error=None,
        stall=None,
    ):
        # type: (str, Optional[str], Optional[str], Optional[str], Optional[str], Optional[str], Optional[str], Optional[str], Optional[str], Optional[str]) -> None
        self.status = str(status)
        self.state = state
        self.summary = summary
        self.reason = reason
        self.detail = detail
        self.quiet_text = quiet_text
        self.retry_url = retry_url
        self.redeliver_url = redeliver_url
        self.error = error
        self.stall = stall
        if stall:
            self.stall_text = t("status.stalled.%s" % (stall if stall in STALL_REASONS else "other"))  # type: Optional[str]
        else:
            self.stall_text = None

    @classmethod
    def from_sync(cls, sync, retry_url_for=None, redeliver_url_for=None, error=None, connection=None):
        # type: (Any, Optional[Callable[[Any], str]], Optional[Callable[[Any], str]], Optional[str], Any) -> RunStatusView
        """From a SyncStatus. connection is the one the page is about (else the latest run's):
        while it's stalled, a sending status says why and offers no redelivery."""
        run = sync.run
        state = ("cancelled" if run.cancelled() else run.state) if run is not None else None
        failed = sync.status == "failed"
        reason = run.reason_text if run is not None and (failed or run.cancelled()) else None
        detail = run.error_detail if failed and run is not None else None
        if connection is None and run is not None:
            connection = run.connection
        stall = cls.stall_of(connection) if sync.status == "sending" else None
        stuck = run is not None and not stall and run.looks_stuck()
        return cls(
            status=sync.status,
            state=state,
            summary=t("status.waiting_for_quickbooks") if stall else sync.summary_text,
            reason=reason,
            detail=detail,
            quiet_text=t("status.quiet") if stuck else None,
            retry_url=retry_url_for(run) if retry_url_for is not None and sync.unconfirmed else None,
            redeliver_url=redeliver_url_for(run) if redeliver_url_for is not None and stuck else None,
            error=error,
            stall=stall,
        )

    @staticmethod
    def stall_of(connection):
        # type: (Any) -> Optional[str]
        """A stalled connection's reason ("other" when it gives none), or None."""
        if connection is None or getattr(connection, "status", None) != "stalled":
            return None
        return str(connection.stall_reason or "").strip() or "other"

    @property
    def visible(self):
        # type: () -> bool
        """Nothing is shown before the record is sent (the error aside)."""
        return self.status != "not_sent"

    @property
    def css_class(self):
        # type: () -> str
        names = ["qube-run-status", "qube-sync-%s" % self.status]
        if self.state:
            names.append("qube-run-%s" % self.state)
        if self.stall:
            names.append("qube-connection-stalled")
        return " ".join(names)
