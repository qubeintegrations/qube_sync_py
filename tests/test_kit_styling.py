"""The screens: the view-models (the override contract), choices by kind, class hooks, the
wording, the assets, an app's own pieces winning, and the storyboard through Django, Flask and
FastAPI. They mirror qube_rails' view_models, choice_kinds, styling, wording and storyboard specs."""
import json
import os
import re

import pytest

import qubesync.kit as kit
from html_tree import parse
from kit_support import kit_reset, vector_prompt  # noqa: F401
from kit_worlds import make_driver, make_world
from qubesync.kit import _storyboard as storyboard

HERE = os.path.dirname(os.path.abspath(__file__))
PIECES = os.path.join(HERE, "kit_templates", "pieces")
JINJA = os.path.join(os.path.dirname(os.path.abspath(kit.__file__)), "templates", "qubesync")
DJANGO = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(kit.__file__))), "django", "templates", "qubesync")
JARGON = re.compile(r"QuBe Sync|qube sync|webhook|revision|ListID|your app|\bthe run\b", re.I)


def sample(key):
    return storyboard.find(key).sample["prompt"]


def question(prompt):
    return kit.QuestionView(prompt, action_url="/q/1", search_url="/q/1/search")


def arranged(view):
    return [(c.id, c.kind, c.style) for c in view.choices]


@pytest.fixture(autouse=True)
def fresh(kit_reset):
    """No settings of the last test's, and FastAPI's storyboard back on the packaged templates."""
    try:
        import qubesync.fastapi as qube_fastapi

        qube_fastapi._templates[:] = []
    except ImportError:
        pass
    yield


# -- The view-models -------------------------------------------------------------------------


class TestQuestionView:
    def test_is_built_from_a_prompt_as_qube_sync_sends_it(self):
        prompt = vector_prompt()
        view = question(prompt)

        assert view.message == prompt["message"]
        assert view.token == "Vq3kT9xRb2LmW8sZ"
        assert [(d.label, d.value) for d in view.details] == [("Customer", "Riverbend")]
        assert [c.id for c in view.choices] == ["use:1", "use", "none", "cancel"]
        assert view.choices[0].detail == "similar name"
        assert view.choices[0].action_url == "/q/1"
        assert view.choices[-1].secondary
        field = view.choices[1].fields[0]
        assert (field.type, field.name, field.input_name, field.dom_id, field.label, field.required) == (
            "search", "list_id", "data[list_id]", "qube-Vq3kT9xRb2LmW8sZ-1-list_id", "The one to use", True,
        )
        assert (field.search_url, field.search_field, field.kind, field.template) == (
            "/q/1/search", "list_id", "customer", "qubesync/question/fields/search.html",
        )
        assert field.labelled

    def test_shows_an_enum_as_a_select_and_number_and_boolean_fields_as_themselves(self):
        select = question(sample("enum_select")).choices[0].fields[0]
        assert select.type == "select"
        assert (select.options[0].value, select.options[0].label) == ("sales_order", "Sales order")

        fields = question(sample("number_boolean")).choices[0].fields
        assert [f.type for f in fields] == ["number", "boolean"]
        assert [f.input_name for f in fields] == ["data[quantity]", "data[allow_negative]"]


class TestChoiceKinds:
    def test_a_choose_lists_items_are_picks_a_choice_with_fields_a_form_and_the_rest_exits(self):
        view = question(sample("near_match"))

        assert arranged(view) == [("use:1", "pick", None), ("use", "form", "primary"), ("none", "exit", "secondary"), ("cancel", "exit", "ghost")]
        assert [[c.id for c in group] for group in (view.picks, view.forms, view.exits)] == [["use:1"], ["use"], ["none", "cancel"]]
        assert not view.plain

    def test_fills_no_button_for_a_pick_from_a_list(self):
        assert arranged(question(sample("choose"))) == [
            ("use:1", "pick", None), ("use:2", "pick", None), ("none", "exit", "secondary"), ("cancel", "exit", "ghost"),
        ]

    def test_shows_the_records_there_are_as_picks_then_the_search_with_the_one_filled_submit(self):
        assert arranged(question(sample("record_search"))) == [
            ("use:1", "pick", None), ("use:2", "pick", None), ("use:3", "pick", None), ("use", "form", "primary"), ("cancel", "exit", "ghost"),
        ]

    def test_fills_only_the_first_forms_submit(self):
        def field(name):
            return [{"name": name, "type": "string", "label": name, "required": True}]

        prompt = {"token": "t", "message": "?", "choices": [
            {"id": "narrow", "label": "Narrow it down", "fields": field("city")},
            {"id": "rename", "label": "Rename it", "fields": field("name")},
            {"id": "cancel", "label": "Cancel", "fields": []},
        ]}
        assert arranged(question(prompt)) == [("narrow", "form", "primary"), ("rename", "form", "secondary"), ("cancel", "exit", "ghost")]

    def test_a_plain_choice_before_the_first_form_is_a_pick_when_there_are_none(self):
        assert arranged(question(sample("name_clash"))) == [("use_existing", "pick", None), ("rename", "form", "primary"), ("cancel", "exit", "ghost")]

    def test_keeps_a_question_of_plain_choices_in_one_row_the_first_primary(self):
        prompt = {"token": "t", "message": "?", "choices": [
            {"id": "approve", "label": "Approve", "fields": []},
            {"id": "skip", "label": "Skip", "fields": []},
            {"id": "cancel", "label": "Cancel", "fields": []},
        ]}
        view = question(prompt)

        assert view.plain
        assert arranged(view) == [("approve", "exit", "primary"), ("skip", "exit", "secondary"), ("cancel", "exit", "ghost")]

    def test_has_at_most_one_primary_on_every_storyboard_question(self):
        for key in storyboard.QUESTIONS:
            assert sum(1 for c in question(sample(key)).choices if c.style == "primary") <= 1, key


class TestRowsView:
    @pytest.fixture
    def rows(self):
        return question(sample("rows")).choices[0].fields[0].rows

    def test_has_the_columns_a_row_per_record_and_a_cell_per_column_it_asks_or_has(self, rows):
        assert [c.name for c in rows.columns] == ["action", "list_id", "item_type", "entity_type", "income_account", "asset_account", "cogs_account"]
        assert [r.key for r in rows.rows] == ["customer_ref", "invoice_line_add.0.item_ref", "invoice_line_add.1.item_ref"]
        customer = rows.rows[0]
        action = customer.cells[0].field
        assert (action.type, action.input_name, action.context, action.cell) == ("select", "data[records][customer_ref][action]", "cell", True)
        list_id = customer.cells[1].field
        assert (list_id.type, list_id.search_field, list_id.row_key) == ("search", "records.list_id", "customer_ref")
        assert [c.column for c in customer.cells] == ["action", "list_id"]
        assert action.segmented
        assert list_id.dom_id == "qube-data-records-0-list_id"

    def test_shows_a_value_a_record_has_by_its_label_and_hides_a_cell_whose_when_doesnt_hold(self, rows):
        kit_row = rows.rows[-1]
        item_type = next(c for c in kit_row.cells if c.column == "item_type")

        assert item_type.preset == "Inventory part"
        assert item_type.hidden
        assert not kit_row.cells[0].hidden
        asset = next(c for c in kit_row.cells if c.column == "asset_account")
        assert (asset.field.disabled, json.loads(asset.when_json)) == (True, {"action": ["create"], "item_type": ["item_inventory"]})

    def test_sets_all_by_the_first_short_enum_two_records_ask_and_isnt_required_while_hidden(self, rows):
        assert rows.set_all.name == "action"
        assert [o.label for o in rows.set_all.options] == ["Create it", "Use an existing one"]
        vinyl = rows.rows[1]
        income = next(c for c in vinyl.cells if c.column == "income_account")
        assert (income.hidden, income.required, income.field.required, income.field.disabled) == (True, True, False, True)
        item_type = next(c for c in vinyl.cells if c.column == "item_type")
        assert not item_type.field.segmented  # four options: a select


class TestRunStatusView:
    @pytest.fixture(params=["django", "sqlalchemy"])
    def world(self, request):
        return make_world(request.param)

    @pytest.fixture
    def account(self, world):
        return world.account()

    @pytest.fixture
    def invoice(self, world, account):
        return world.invoice(account)

    @pytest.fixture
    def connection(self, world, account):
        return world.connection(account)

    def view(self, world, invoice, connection=None):
        sync = kit.SyncStatus.latest(invoice, "create_invoice")
        return kit.RunStatusView.from_sync(
            sync, lambda run: "/qube/runs/%s/retry_start" % run.id, lambda run: "/qube/runs/%s/redeliver" % run.id, connection=connection
        )

    def test_says_a_failure_with_why_and_what_to_do(self, world, invoice, connection):
        world.run(invoice, connection, state="failed", ended_at=world.Run._kit_store.now(), error={"message": "No customer", "detail": "Add it first."})
        view = self.view(world, invoice)

        assert (view.status, view.state, view.summary, view.reason, view.detail) == ("failed", "failed", "Couldn't sync", "No customer.", "Add it first.")
        assert view.css_class == "qube-run-status qube-sync-failed qube-run-failed"
        assert (view.retry_url, view.redeliver_url) == (None, None)

    def test_has_the_retry_url_for_an_unconfirmed_start_and_the_redeliver_url_for_a_quiet_run(self, world, invoice, connection):
        run = world.ago(world.run(invoice, connection, state="starting"), 120)
        assert self.view(world, invoice).retry_url == "/qube/runs/%s/retry_start" % run.id

        world.quiet(world.update(run, state="running", qube_run_id="run-q"), 11 * 60)
        view = self.view(world, invoice)
        assert (view.redeliver_url, view.quiet_text) == ("/qube/runs/%s/redeliver" % run.id, "No update from QuickBooks for a while.")

    def test_says_why_a_run_waits_on_a_stalled_connection_and_offers_no_redelivery(self, world, invoice, connection):
        run = world.quiet(world.run(invoice, connection, state="running", qube_run_id="run-q"), 11 * 60)
        world.update(connection, status="stalled", stall_reason="not_checking_in")

        view = self.view(world, invoice)
        assert (view.stall, view.summary, view.redeliver_url, view.quiet_text) == ("not_checking_in", "Waiting for QuickBooks", None, None)
        assert view.stall_text.startswith("QuickBooks hasn't checked in for a while")
        assert "qube-connection-stalled" in view.css_class
        world.update(connection, stall_reason="quickbooks_unavailable")
        assert self.view(world, invoice).stall_text.startswith("The Web Connector is checking in but can't open QuickBooks")
        world.update(connection, stall_reason="something_new")
        view = self.view(world, invoice)
        assert (view.stall, view.stall_text) == ("something_new", kit.t("status.stalled.other"))

        world.update(connection, status="connected", stall_reason=None)
        view = self.view(world, invoice)
        assert (view.stall, view.stall_text, view.summary) == (None, None, "Syncing with QuickBooks")
        assert view.redeliver_url == "/qube/runs/%s/redeliver" % run.id

    def test_leaves_a_question_waiting_on_the_person_as_it_is(self, world, invoice, connection):
        world.run(invoice, connection, state="awaiting_input", question={"message": "?"})
        world.update(connection, status="stalled", stall_reason="not_checking_in")

        view = self.view(world, invoice)
        assert (view.status, view.stall, view.summary) == ("needs_answer", None, "Needs your answer")

    def test_takes_the_connection_the_page_is_about(self, world, account, invoice, connection):
        world.run(invoice, connection, state="running")
        other = world.update(world.connection(account, qube_id="conn-q-other", status="stalled"), stall_reason="quickbooks_unavailable")
        sync = kit.SyncStatus.latest(invoice, "create_invoice")

        assert kit.RunStatusView.from_sync(sync, connection=other).stall == "quickbooks_unavailable"
        assert kit.RunStatusView.from_sync(sync).stall is None

    def test_isnt_visible_before_the_record_is_sent(self, world, invoice):
        view = self.view(world, invoice)

        assert (view.visible, view.status) == (False, "not_sent")


# -- Settings: class hooks and wording -------------------------------------------------------


def test_an_unknown_ui_classes_piece_raises_naming_the_pieces():
    with pytest.raises(ValueError, match="no piece 'table'.*button_secondary"):
        kit.configure(ui_classes={"table": "x"})


def test_an_unknown_message_key_raises_naming_the_keys():
    with pytest.raises(ValueError, match="no key 'status.nope'.*status.running"):
        kit.configure(messages={"status": {"nope": "x"}})


def test_qube_classes_puts_the_apps_classes_after_ours():
    kit.configure(ui_classes={"button": ["btn", "btn-primary"], "input": "form-control"})

    assert kit.qube_classes("button", "qube-choice-button") == "qube-choice-button btn btn-primary"
    assert kit.qube_classes("select", "qube-select", None) == "qube-select"
    with pytest.raises(ValueError):
        kit.qube_classes("table")


def test_no_english_string_names_qube_sync_or_its_plumbing():
    assert [text for text in kit.MESSAGES.values() if JARGON.search(text)] == []


def test_the_messages_setting_rewords_a_key_dotted_or_nested():
    kit.configure(messages={"status.running": "Syncing with your accounts", "question": {"or": "ou"}})

    assert kit.t("status.running") == "Syncing with your accounts"
    assert kit.t("question.or") == "ou"
    assert kit.t("question.use_for_all", count=3) == "Use for all 3"


# -- Through each adapter: the page, the classes, the assets ----------------------------------


@pytest.fixture(params=["django", "flask", "fastapi"])
def app(request, kit_reset):
    return make_driver(request.param)


@pytest.fixture
def http(app):
    return app[0]


@pytest.fixture
def world(app):
    return app[1]


@pytest.fixture
def account(world):
    return world.account()


def asking(world, account, prompt=None):
    invoice = world.invoice(account)
    run = world.run(invoice, world.connection(account), state="awaiting_input", question=prompt or vector_prompt(), links={"decisions": "d", "search": "s"})
    return invoice, run


def page(http, invoice, account):
    response = http.get("/invoices/%s" % invoice.id, account=account)
    assert response.status == 200
    return response.text


class TestStyling:
    def test_adds_the_ui_classes_beside_the_qube_classes(self, http, world, account):
        kit.configure(ui_classes={"question": "card", "button": ["btn", "btn-primary"], "button_secondary": "btn btn-link",
                                  "input": "form-control", "status": "alert", "label": "form-label", "search_result": "list-group-item"})
        invoice, _ = asking(world, account)
        doc = parse(page(http, invoice, account))

        assert doc.find("section", class_="card") is not None
        assert len(doc.find_all("button", class_="btn-primary")) == 1  # the form's submit; a pick is never a button piece
        assert doc.find("form", data_qube_choice="use").find("button")["class"] == "qube-choice-button btn btn-primary"
        assert doc.find("form", data_qube_choice="use:1").find("button")["class"] == "qube-pick"
        assert doc.find("form", data_qube_choice="none").find("button")["class"] == "qube-choice-button btn btn-link"
        assert doc.find("form", data_qube_choice="cancel").find("button")["class"] == "qube-choice-button btn btn-link"
        assert "form-control" in doc.find("input", class_="qube-search-input").classes
        assert doc.find("label", class_="form-label") is not None
        assert doc.find(data_qube_search=True)["data-qube-result-class"] == "qube-search-result list-group-item"
        assert {"qube-sync-needs_answer", "alert"} <= set(doc.find(class_="qube-run-status").classes)

    def test_takes_the_choice_pieces_classes(self, http, world, account):
        kit.configure(ui_classes={"button": "btn", "button_secondary": "btn-2", "button_ghost": "btn-link", "picks": "list",
                                  "pick": "list-item", "pick_detail": "muted", "choice_footer": "actions", "choice_divider": "or"})
        invoice, _ = asking(world, account)
        doc = parse(page(http, invoice, account))

        picks = doc.find(class_="list")
        assert "qube-picks" in picks.classes
        pick = picks.find("form", data_qube_choice="use:1").find("button", class_="list-item")
        assert pick.find(class_="muted") is not None
        assert "or" in doc.find(class_="qube-choice-divider").classes
        footer = doc.find(class_="actions")
        assert footer.find("form", data_qube_choice="none").find("button")["class"] == "qube-choice-button btn-2"
        assert footer.find("form", data_qube_choice="cancel").find("button")["class"] == "qube-choice-button btn-link"

    def test_posts_the_same_names_as_before(self, http, world, account):
        invoice, run = asking(world, account)
        doc = parse(page(http, invoice, account))
        form = doc.find("form", data_qube_choice="use")

        names = [i["name"] for i in form.find_all("input") if i.get("name") and "csrf" not in i["name"]]
        assert names == ["choice", "data[list_id]"]
        assert form["action"] == "/qube/questions/runs/%s" % run.id
        assert form["data-qube-choice-kind"] == "form"

    def test_leaves_no_inline_script(self, http, world, account):
        invoice, _ = asking(world, account, sample("rows"))
        shown = page(http, invoice, account)

        assert parse(shown).find(data_qube_rows=True).find(data_qube_row=True, data_qube_values=True) is not None
        assert "<script" not in shown


class TestAssets:
    def test_serves_the_behaviour_script_and_the_stylesheet(self, app, http, account):
        if app[0].__class__.__name__ == "DjangoDriver":
            pytest.skip("Django serves them as static files (qubesync/question.js, qubesync/qubesync.css)")
        script = http.get("/qube/assets/question.js")
        assert script.status == 200
        assert 'document.addEventListener("input"' in script.text
        assert http.get("/qube/assets/qubesync.css").status == 200
        assert http.get("/qube/assets/nope.js").status == 404
        assert http.get("/qube/assets/..%2Fstoryboard%2Frows.json").status == 404

    def test_the_script_keys_on_data_attributes_and_the_stylesheet_has_no_specificity(self):
        with open(os.path.join(kit.STATIC_DIR, "question.js")) as handle:
            script = handle.read()
        with open(os.path.join(kit.STATIC_DIR, "qubesync.css")) as handle:
            css = handle.read()

        assert all(part in script for part in ("[data-qube-search-input]", "[data-qube-set-all]", "[data-qube-use-for-all]"))
        assert not re.search(r"\.qube-[a-z-]+[\"']", script)
        bare = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
        selectors = [s.strip() for s in re.findall(r"^([^{}\n][^{}]*)\{", bare, flags=re.M)]
        rules = [s for s in selectors if not s.startswith("@") and s not in ("from", "to")]
        assert rules and [s for s in rules if not s.startswith(":where(")] == []
        assert not re.search(r"transition:\s*all|scale\(0\)", css)
        for name in ("--qube-accent", "--qube-border", "--qube-radius", "--qube-gap", "--qube-font", "--qube-muted", "--qube-error", "--qube-surface"):
            assert "var(%s" % name in css

    def test_flask_writes_the_tags_for_the_layout(self, kit_reset):
        pytest.importorskip("flask")
        driver, _ = make_driver("flask")
        import qubesync.flask as qube_flask

        with driver.app.test_request_context("/"):
            tags = str(qube_flask.assets_html(stylesheet=True, csp_nonce="n0"))
        assert tags == ('<link rel="stylesheet" href="/qube/assets/qubesync.css" media="all">\n'
                        '<script src="/qube/assets/question.js" defer nonce="n0"></script>')

    def test_django_writes_the_tags_for_the_base_template(self, kit_reset):
        pytest.importorskip("django")
        make_driver("django")
        from django.template import engines

        shown = engines["django"].from_string("{% load qubesync %}{% qube_assets stylesheet=True %}").render({})
        assert shown == ('<link rel="stylesheet" href="/static/qubesync/qubesync.css" media="all">\n'
                         '<script src="/static/qubesync/question.js" defer></script>')


class TestOverrides:
    def test_django_renders_an_apps_own_piece_from_the_view_model_alone(self, kit_reset):
        pytest.importorskip("django")
        _, world = make_driver("django")
        from django.template import Context, Engine

        account = world.account()
        invoice, _ = asking(world, account, sample("number_boolean"))
        engine = Engine(dirs=[PIECES], app_dirs=True, libraries={"qubesync": "qubesync.django.templatetags.qubesync"})
        shown = engine.from_string("{% load qubesync %}{% qube_question invoice 'create_invoice' %}").render(Context({"invoice": invoice}))
        self.assert_own_piece(shown)

    def test_jinja_renders_an_apps_own_piece_from_the_view_model_alone(self, kit_reset):
        pytest.importorskip("flask")
        from flask import Flask

        import qubesync.flask as qube_flask

        _, world = make_driver("flask")
        app = Flask("pieces", template_folder=PIECES)
        qube_flask.init_app(app)
        account = world.account()
        invoice, _ = asking(world, account, sample("number_boolean"))
        with app.test_request_context("/"):
            shown = str(qube_flask.question_html(invoice, "create_invoice"))
        self.assert_own_piece(shown)

    def assert_own_piece(self, shown):
        doc = parse(shown)
        assert doc.find(class_="app-toggle", data_app_field="allow_negative").find("input", name="data[allow_negative]") is not None
        assert doc.find(class_="qube-checkbox") is None
        assert doc.find("input", class_="qube-input", name="data[quantity]") is not None  # the rest stay ours

    def test_a_plain_jinja_environment_still_escapes(self, kit_reset):
        pytest.importorskip("fastapi")
        import jinja2

        import qubesync.fastapi as qube_fastapi

        env = qube_fastapi.add_templates(jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(HERE, "kit_templates", "empty"))))
        view = kit.QuestionView(dict(vector_prompt(), message="<script>alert(1)</script>"), action_url="/q", search_url="/q/search")
        shown = qube_fastapi._render(env, "qubesync/question.html", {"question": view})

        assert "&lt;script&gt;alert(1)" in shown and "<script>alert(1)" not in shown


def test_django_and_jinja_ship_the_same_pieces():
    def listed(root):
        return sorted(os.path.relpath(os.path.join(d, f), root) for d, _, files in os.walk(root) for f in files if f.endswith(".html"))

    jinja = [p for p in listed(JINJA) if p != "_error.html"]
    assert jinja == listed(DJANGO)


# -- The storyboard ----------------------------------------------------------------------------


class TestStoryboard:
    @pytest.fixture
    def on(self):
        kit.configure(storyboard=True)

    def doc(self, http, account, path="/qube/storyboard", params=None):
        response = http.get(path, params, account=account)
        assert response.status == 200, response.text[:300]
        return parse(response.text)

    def panel(self, doc, key):
        return doc.find(data_qube_storyboard=key)

    def test_shows_every_screen_from_sample_data_with_each_pieces_override_path(self, on, http, world, account):
        rows_before = (world.count(world.Run), world.count(world.Connection))
        doc = self.doc(http, account)
        panels = doc.find_all(data_qube_storyboard=True)

        assert [p["data-qube-storyboard"] for p in panels] == [s.key for s in storyboard.screens()]
        assert len(doc.find_all(class_="qube-run-status")) == 11  # not_sent renders nothing
        assert len(doc.find_all("section", class_="qube-question")) == 10
        assert (world.count(world.Run), world.count(world.Connection)) == rows_before
        assert self.panel(doc, "unconfirmed").find("form", class_="qube-retry-start-form")["action"] == "/qube/storyboard/unconfirmed/answer"
        assert self.panel(doc, "looks_stuck").find("form", class_="qube-redeliver-form") is not None
        stalled = self.panel(doc, "stalled_not_checking_in").find(class_="qube-connection-stalled")
        assert stalled["data-qube-stall"] == "not_checking_in"
        assert stalled.find(class_="qube-run-summary").words() == "Waiting for QuickBooks"
        assert "Web Connector is running" in stalled.find(class_="qube-run-stall").words()
        assert stalled.find(class_="qube-redeliver-form") is None and stalled.find(class_="qube-run-quiet") is None
        assert "can't open QuickBooks" in self.panel(doc, "stalled_quickbooks_unavailable").find(class_="qube-run-stall").words()
        assert "active in QuickBooks" in self.panel(doc, "failed").find(class_="qube-run-error-detail").words()
        assert self.panel(doc, "failed").find(class_="qube-run-reason").words().endswith("is inactive.")
        assert self.panel(doc, "error").find(class_="qube-error") is not None
        assert "couldn't be used" in self.panel(doc, "refusal").find(class_="qube-question").find(class_="qube-error").words()
        assert len(self.panel(doc, "rows").find_all(data_qube_row=True, data_qube_values=True)) == 3
        missing = self.panel(doc, "missing_record")
        assert len(missing.find_all(data_qube_row=True, data_qube_values=True)) == 1
        assert "Create it" in missing.words() and "Use an existing one" in missing.words()
        assert 'None of these: add "Riverbend" as new' in self.panel(doc, "near_match").words()
        assert self.panel(doc, "near_match").find(data_qube_search=True)["data-qube-search"] == "/qube/storyboard/near_match/search"
        files = self.panel(doc, "failed").find(class_="qube-storyboard-files").words()
        assert "templates/qubesync/run_status/status.html" in files and "templates/qubesync/run_status/detail.html" in files

    def test_names_every_piece_shipped_as_an_override_path(self, on, http, account):
        named = {c.words() for c in self.doc(http, account).find_all("code")}
        pieces = [os.path.relpath(os.path.join(d, f), JINJA) for d, _, files in os.walk(JINJA) for f in files]
        pieces = [p for p in pieces if p.split(os.sep)[0] in ("question", "run_status")] + ["error.html"]

        assert sorted(p for p in pieces if "templates/qubesync/%s" % p not in named) == []

    def test_shows_choices_by_kind_and_at_most_one_filled_button(self, on, http, account):
        doc = self.doc(http, account)

        def kinds(key):
            return [(f["data-qube-choice"], f["data-qube-choice-kind"]) for f in self.panel(doc, key).find_all("form", data_qube_choice=True)]

        assert kinds("near_match") == [("use:1", "pick"), ("use", "form"), ("none", "exit"), ("cancel", "exit")]
        assert self.panel(doc, "near_match").find(class_="qube-choice-footer").find("form", data_qube_choice="none") is not None
        assert self.panel(doc, "choose").find_all(data_qube_button="primary") == []
        for key in storyboard.QUESTIONS:
            assert len(self.panel(doc, key).find_all(data_qube_button="primary")) <= 1, key
        assert [b for b in doc.find_all("button") if b.get("disabled") is not None and b.ancestor(class_=True)] == []

    def test_shows_one_screen(self, on, http, account):
        doc = self.doc(http, account, "/qube/storyboard/rows")

        assert [p["data-qube-storyboard"] for p in doc.find_all(data_qube_storyboard=True)] == ["rows"]
        assert doc.find("a", aria_current="page").words() == "Records not in QuickBooks yet"
        assert http.get("/qube/storyboard/nope", account=account).status == 404

    def test_answers_a_search_from_the_samples(self, on, http, account):
        response = http.get("/qube/storyboard/rows/search", {"field": "records.income_account", "q": "sales", "row": "customer_ref"}, account=account)

        assert [m["label"] for m in response.json()] == ["Sales", "Sales:Signs"]

    def test_sends_nothing_for_an_answer_and_says_so(self, on, http, account):
        response = http.post("/qube/storyboard/name_clash/answer", {"choice": "rename", "data[name]": "x"}, account=account)

        assert response.status == 303
        assert response.location.endswith("/qube/storyboard/name_clash?sent=0")
        notice = self.doc(http, account, "/qube/storyboard/name_clash", {"sent": "0"}).find(class_="qube-storyboard-notice")
        assert notice.words() == "Storyboard: nothing was sent."

    def test_is_behind_the_apps_sign_in(self, on, http):
        assert http.get("/qube/storyboard").status in http.signed_out

    def test_is_off_by_default_outside_development(self, http, account):
        assert http.get("/qube/storyboard", account=account).status == 404
        assert http.get("/qube/storyboard/rows/search", {"field": "records.list_id", "q": "lo"}, account=account).status == 404
        assert http.post("/qube/storyboard/rows/answer", account=account).status == 404

    def test_never_names_qube_sync_on_a_screen(self, on, http, account):
        canvases = self.doc(http, account).find_all(data_qube_storyboard_canvas=True)

        assert len(canvases) == len(storyboard.screens())
        for canvas in canvases:
            words = [canvas.words()]
            for node in canvas.walk():
                words.extend(v for k, v in node.attrs.items() if k == "aria-label" or k.startswith("data-qube-text-"))
            text = " ".join(words)
            assert not JARGON.search(text), (canvas.ancestor(data_qube_storyboard=True)["data-qube-storyboard"], JARGON.search(text).group(0))

    def test_takes_an_apps_own_words_on_the_screens_and_in_a_routes_message(self, on, http, world, account):
        kit.configure(messages={"status.check_for_updates": "Look again", "status": {"stalled": {"not_checking_in": "Turn on the office PC."}},
                                "errors.not_starting": "Already on its way."})
        doc = self.doc(http, account)

        assert self.panel(doc, "looks_stuck").find(class_="qube-redeliver-form").find("button").words() == "Look again"
        assert self.panel(doc, "stalled_not_checking_in").find(class_="qube-run-stall").words() == "Turn on the office PC."

        invoice = world.invoice(account)
        run = world.run(invoice, world.connection(account), state="running")
        http.post("/qube/runs/%s/retry_start" % run.id, account=account, headers={"Referer": "/invoices/%s" % invoice.id})
        errors = [e.words() for e in parse(page(http, invoice, account)).find_all(class_="qube-error")]
        assert errors == ["Already on its way."]

    def test_renders_in_the_apps_layout(self, on, app, http, account):
        if app[0].__class__.__name__ == "FastAPIDriver":
            pytest.importorskip("jinja2")
            from fastapi.templating import Jinja2Templates

            import qubesync.fastapi as qube_fastapi

            qube_fastapi.add_templates(Jinja2Templates(directory=os.path.join(HERE, "kit_templates", "layout")))
        kit.configure(storyboard_layout="app_layout.html")
        if app[0].__class__.__name__ == "FlaskDriver":
            app[0].app.jinja_loader.searchpath.append(os.path.join(HERE, "kit_templates", "layout"))

        doc = self.doc(http, account)
        assert doc.find(id="app-nav") is not None
        assert doc.find(id="app-main").find(class_="qube-storyboard") is not None


def test_django_and_jinja_render_every_screen_alike(kit_reset):
    pytest.importorskip("django")
    pytest.importorskip("jinja2")
    make_driver("django")
    import jinja2
    from django.template import engines

    jinja = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(JINJA)), autoescape=True)
    page = storyboard.page(None, lambda name, key: "/%s/%s" % (name, key))

    def shape(markup):
        def walk(node):
            if isinstance(node, str):
                return " ".join(node.split()) or None
            kids = [k for k in (walk(c) for c in node.children) if k]
            return (node.tag, sorted(node.attrs.items()), kids)

        return walk(parse(markup))

    for entry in page["screens"]:
        if entry["kind"] == "run_status":
            name, values = "qubesync/run_status/status.html", {"run_status": entry["run_status"]}
        elif entry["kind"] == "error":
            name, values = "qubesync/error.html", {"message": entry["message"]}
        else:
            name, values = "qubesync/question/question.html", {"question": entry["question"]}
        ours = jinja.get_template(name).render(qube_classes=kit.qube_classes, qube_t=kit.t, **values)
        theirs = engines["django"].get_template(name).render(values)
        assert shape(ours) == shape(theirs), entry["key"]
