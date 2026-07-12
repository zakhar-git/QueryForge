from __future__ import annotations

from datetime import datetime
from .browser import Browser
from .catalog import Catalog
from .config import SettingsStore
from .detection import detect_candidates, validate_value
from .engine import QueryEngine
from .exporters import Exporter
from .history import HistoryStore
from .i18n import tr
from .menu import Menu
from .models import QueryResult, SearchRecord
from .ui import UI


ENTITY_ORDER = [
    "username",
    "email",
    "person",
    "phone",
    "telegram",
    "social_profile",
    "company",
    "brand",
    "domain",
    "url",
    "ip",
    "asn",
    "github_repo",
    "hash",
    "crypto_address",
    "document",
    "image",
    "location",
    "phrase",
]


class Application:
    def __init__(self) -> None:
        self.settings_store = SettingsStore()
        self.settings = self.settings_store.load()
        self.ui = UI(self.settings)
        self.menu = Menu(self.ui.console, self.settings.accent)
        self.catalog = Catalog()
        self.engine = QueryEngine(self.catalog)
        self.history = HistoryStore()
        self.exporter = Exporter()
        self.browser = Browser()

    def refresh_ui(self) -> None:
        self.ui = UI(self.settings)
        self.menu = Menu(self.ui.console, self.settings.accent)

    def t(self, key: str) -> str:
        return tr(self.settings.language, key)

    def run(self) -> None:
        while True:
            self.ui.clear()
            self.ui.header()
            choice = self.menu.choose_with_zero(
                self.t("main_menu"),
                [
                    ("new", self.t("new_search")),
                    ("detect", self.t("auto_detect")),
                    ("history", self.t("history")),
                    ("settings", self.t("settings")),
                    ("sources", self.t("sources")),
                    ("about", self.t("about")),
                ],
                self.t("choose"),
                self.t("exit"),
            )
            if choice == "new":
                self.new_search()
            elif choice == "detect":
                self.auto_detect()
            elif choice == "history":
                self.history_menu()
            elif choice == "settings":
                self.settings_menu()
            elif choice == "sources":
                self.sources_view()
            elif choice == "about":
                self.about_view()
            elif choice is None:
                return

    def new_search(self, preselected: str | None = None, value: str | None = None) -> None:
        entity_id = preselected or self.choose_entity()
        if not entity_id:
            return
        entity = self.catalog.entities[entity_id]
        if value is None:
            value = self.ui.value_prompt(entity)
        if not value:
            self.ui.error(self.t("empty_value"))
            self.ui.wait()
            return
        if not validate_value(entity_id, value):
            self.ui.error(self.t("warning"))
            decision = self.menu.choose_with_zero(
                self.t("continue_anyway"),
                [("yes", self.t("yes")), ("no", self.t("no"))],
                self.t("choose"),
                self.t("back"),
            )
            if decision != "yes":
                return
        depth = self.choose_depth()
        if not depth:
            return
        source_ids = self.choose_sources(entity_id)
        if not source_ids:
            return
        results = self.engine.generate(entity_id, value, depth, set(source_ids), self.settings.language)
        if not results:
            self.ui.error(self.t("no_templates"))
            self.ui.wait()
            return
        if self.settings.save_history:
            self.history.add(
                SearchRecord(
                    entity=entity_id,
                    value=value,
                    depth=depth,
                    sources=source_ids,
                    count=len(results),
                    created_at=datetime.now().isoformat(timespec="seconds"),
                    results=[item.to_dict() for item in results],
                )
            )
        self.results_loop(entity_id, value, depth, results)

    def choose_entity(self) -> str | None:
        options = []
        for entity_id in ENTITY_ORDER:
            entity = self.catalog.entities[entity_id]
            label = entity.label_ru if self.settings.language == "ru" else entity.label_en
            options.append((entity.id, label))
        return self.menu.choose_with_zero(
            self.t("entity"),
            options,
            self.t("choose"),
            self.t("back"),
        )

    def choose_depth(self) -> str | None:
        order = ["basic", "extended", "full"]
        options = []
        for depth in order:
            label = self.t(depth)
            if depth == self.settings.default_depth:
                label = f"{label} ({self.t('current')})"
            options.append((depth, label))
        return self.menu.choose_with_zero(
            self.t("depth"),
            options,
            self.t("choose"),
            self.t("back"),
            self.settings.default_depth,
        )

    def choose_sources(self, entity_id: str) -> list[str] | None:
        mode = self.menu.choose_with_zero(
            self.t("source_mode"),
            [
                ("recommended", self.t("recommended")),
                ("all", self.t("all_sources")),
                ("group", self.t("source_group")),
                ("manual", self.t("manual")),
            ],
            self.t("choose"),
            self.t("back"),
            self.settings.default_source_mode,
        )
        if not mode:
            return None
        entity = self.catalog.entities[entity_id]
        available = self.catalog.entity_sources(entity_id)
        if mode == "recommended":
            return [source.id for source in available if source.id in entity.recommended_sources]
        if mode == "all":
            return [source.id for source in available]
        if mode == "group":
            groups = self.catalog.groups_for_entity(entity_id)
            group = self.menu.choose_with_zero(
                self.t("select_group"),
                [(item, self.t(f"group_{item}")) for item in groups],
                self.t("choose"),
                self.t("back"),
            )
            if not group:
                return None
            return [source.id for source in available if source.group == group]
        options = [(source.id, f"{source.name} · {self.t(f'group_{source.group}')}") for source in available]
        return self.menu.choose_many(
            self.t("select_sources"),
            options,
            self.t("enter_numbers"),
            self.t("range_hint"),
            {"all", "все", "a"},
            self.t("back"),
        )

    def auto_detect(self) -> None:
        self.ui.section(self.t("auto_detect"))
        value = self.ui.console.input(f"\n[{self.settings.accent}]> [/{self.settings.accent}]{self.t('enter_value')}: ").strip()
        if not value:
            return
        candidates = [item for item in detect_candidates(value) if item in self.catalog.entities]
        if not candidates:
            self.ui.error(self.t("not_detected"))
            self.ui.wait()
            return
        options = []
        for entity_id in candidates:
            entity = self.catalog.entities[entity_id]
            label = entity.label_ru if self.settings.language == "ru" else entity.label_en
            options.append((entity_id, label))
        selected = self.menu.choose_with_zero(
            self.t("detected"),
            options,
            self.t("choose"),
            self.t("back"),
        )
        if selected:
            self.new_search(selected, value)

    def results_loop(self, entity_id: str, value: str, depth: str, results: list[QueryResult]) -> None:
        page = 1
        while True:
            self.ui.clear()
            self.ui.header()
            page, pages = self.ui.show_results(results, page, self.settings.page_size)
            actions = [
                ("open_one", self.t("open_one")),
                ("open_many", self.t("open_many")),
                ("export", self.t("export")),
            ]
            if pages > 1 and page < pages:
                actions.append(("next", self.t("next_page")))
            if pages > 1 and page > 1:
                actions.append(("prev", self.t("prev_page")))
            actions.extend([
                ("new", self.t("new_again")),
                ("main", self.t("main_return")),
            ])
            action = self.menu.choose(self.t("results"), actions, self.t("choose"))
            if action == "open_one":
                self.open_one(results)
            elif action == "open_many":
                self.open_many(results)
            elif action == "export":
                self.export_results(entity_id, value, depth, results)
            elif action == "next":
                page += 1
            elif action == "prev":
                page -= 1
            elif action == "new":
                self.new_search()
                return
            elif action == "main":
                return

    def open_one(self, results: list[QueryResult]) -> None:
        raw = self.ui.console.input(f"\n[{self.settings.accent}]> [/{self.settings.accent}]{self.t('enter_number')}: ").strip()
        if not raw.isdigit() or not 1 <= int(raw) <= len(results):
            self.ui.error(self.t("invalid_choice"))
            self.ui.wait()
            return
        success = self.browser.open(results[int(raw) - 1].url)
        if success:
            self.ui.status(f"{self.t('opened')}: 1")
        else:
            self.ui.error(self.t("browser_error"))
        self.ui.wait()

    def open_many(self, results: list[QueryResult]) -> None:
        raw = self.ui.console.input(f"\n[{self.settings.accent}]> [/{self.settings.accent}]{self.t('enter_numbers')}: ").strip()
        try:
            indices = Menu.parse_indices(raw, len(results))
        except ValueError:
            self.ui.error(self.t("invalid_list"))
            self.ui.wait()
            return
        if len(indices) > 10:
            self.ui.error(self.t("too_many_links"))
            self.ui.wait()
            return
        opened = self.browser.open_many([results[index - 1].url for index in indices])
        self.ui.status(f"{self.t('opened')}: {opened}")
        self.ui.wait()

    def export_results(self, entity_id: str, value: str, depth: str, results: list[QueryResult]) -> None:
        selected = self.menu.choose_with_zero(
            self.t("export_format"),
            [
                ("all", self.t("all_formats")),
                ("html", "HTML"),
                ("json", "JSON"),
                ("csv", "CSV"),
                ("md", "Markdown"),
            ],
            self.t("choose"),
            self.t("back"),
        )
        if not selected:
            return
        formats = {"html", "json", "csv", "md"} if selected == "all" else {selected}
        entity = self.catalog.entities[entity_id]
        entity_label = entity.label_ru if self.settings.language == "ru" else entity.label_en
        paths = self.exporter.export(
            entity_id,
            value,
            depth,
            results,
            formats,
            self.settings.language,
            entity_label,
        )
        self.ui.status(self.t("saved"))
        for path in paths:
            self.ui.console.print(str(path), markup=False)
        self.ui.wait()

    def history_menu(self) -> None:
        records = self.history.load()
        if not records:
            self.ui.error(self.t("history_empty"))
            self.ui.wait()
            return
        self.ui.clear()
        self.ui.header()
        visible = records[:30]
        self.ui.show_history(visible, self.catalog.entities)
        self.ui.console.print(f"[{self.settings.accent}] 0.[/{self.settings.accent}] {self.t('back')}")
        raw = self.ui.console.input(f"\n[{self.settings.accent}]> [/{self.settings.accent}]{self.t('history_pick')}: ").strip()
        if raw == "0":
            return
        if not raw.isdigit() or not 1 <= int(raw) <= len(visible):
            self.ui.error(self.t("invalid_choice"))
            self.ui.wait()
            return
        record = visible[int(raw) - 1]
        results = self.engine.generate(record.entity, record.value, record.depth, set(record.sources), self.settings.language)
        self.results_loop(record.entity, record.value, record.depth, results)

    def settings_menu(self) -> None:
        while True:
            self.ui.clear()
            self.ui.header()
            current_history = self.t("enabled") if self.settings.save_history else self.t("disabled")
            current_clear = self.t("enabled") if self.settings.clear_screen else self.t("disabled")
            selected = self.menu.choose_with_zero(
                self.t("settings"),
                [
                    ("language", f"{self.t('settings_language')}: {self.settings.language.upper()}"),
                    ("accent", f"{self.t('settings_accent')}: {self.settings.accent}"),
                    ("page", f"{self.t('settings_page')}: {self.settings.page_size or 'ALL'}"),
                    ("depth", f"{self.t('settings_depth')}: {self.t(self.settings.default_depth)}"),
                    ("sources", f"{self.t('settings_sources')}: {self.t(self.settings.default_source_mode)}"),
                    ("history", f"{self.t('settings_history')}: {current_history}"),
                    ("clear", f"{self.t('settings_clear')}: {current_clear}"),
                    ("clear_history", self.t("history_clear")),
                ],
                self.t("choose"),
                self.t("back"),
            )
            if not selected:
                return
            if selected == "language":
                value = self.menu.choose_with_zero(
                    self.t("settings_language"),
                    [("ru", self.t("language_ru")), ("en", self.t("language_en"))],
                    self.t("choose"),
                    self.t("back"),
                )
                if value:
                    self.settings.language = value
            elif selected == "accent":
                value = self.menu.choose_with_zero(
                    self.t("settings_accent"),
                    [(item, item) for item in ["cyan", "green", "blue", "magenta", "white"]],
                    self.t("choose"),
                    self.t("back"),
                )
                if value:
                    self.settings.accent = value
            elif selected == "page":
                value = self.menu.choose_with_zero(
                    self.t("settings_page"),
                    [("10", "10"), ("20", "20"), ("50", "50"), ("0", "ALL")],
                    self.t("choose"),
                    self.t("back"),
                )
                if value is not None:
                    self.settings.page_size = int(value)
            elif selected == "depth":
                value = self.menu.choose_with_zero(
                    self.t("settings_depth"),
                    [(item, self.t(item)) for item in ["basic", "extended", "full"]],
                    self.t("choose"),
                    self.t("back"),
                )
                if value:
                    self.settings.default_depth = value
            elif selected == "sources":
                value = self.menu.choose_with_zero(
                    self.t("settings_sources"),
                    [("recommended", self.t("recommended")), ("all", self.t("all_sources"))],
                    self.t("choose"),
                    self.t("back"),
                )
                if value:
                    self.settings.default_source_mode = value
            elif selected == "history":
                self.settings.save_history = not self.settings.save_history
            elif selected == "clear":
                self.settings.clear_screen = not self.settings.clear_screen
            elif selected == "clear_history":
                self.history.clear()
                self.ui.status(self.t("history_cleared"))
                self.ui.wait()
            self.settings_store.save(self.settings)
            self.refresh_ui()

    def sources_view(self) -> None:
        self.ui.clear()
        self.ui.header()
        self.ui.show_sources(list(self.catalog.sources.values()))
        self.ui.wait()

    def about_view(self) -> None:
        self.ui.clear()
        self.ui.header()
        self.ui.section(self.t("about"))
        self.ui.console.print(self.t("about_text"))
        self.ui.console.print()
        self.ui.console.print(f"{self.t('source_total')}: {len(self.catalog.sources)}")
        self.ui.console.print(f"{self.t('entity_total')}: {len(self.catalog.entities)}")
        self.ui.console.print(f"{self.t('template_total')}: {self.catalog.template_count()}")
        self.ui.wait()
