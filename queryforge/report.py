from __future__ import annotations

from collections import Counter
from datetime import datetime
from html import escape
from pathlib import Path

from .models import QueryResult
from .paths import DATA_DIR


REPORT_TEXT = {
    "ru": {
        "document_title": "Поисковый отчёт",
        "report": "Поисковый отчёт",
        "entity": "Тип данных",
        "target": "Значение",
        "depth": "Глубина",
        "created": "Создан",
        "queries": "Запросы",
        "sources": "Источники",
        "source_list": "ИСТОЧНИКИ",
        "all_sources": "Все источники",
        "search": "Фильтр по запросам и названиям",
        "all_levels": "Все уровни",
        "all_categories": "Все категории",
        "print": "Печать",
        "theme": "Тема",
        "expand": "Развернуть",
        "collapse": "Свернуть",
        "open": "Открыть",
        "copy_query": "Копировать запрос",
        "copy_link": "Копировать ссылку",
        "copied": "Скопировано",
        "no_results": "По выбранным фильтрам ничего не найдено.",
        "visible": "Показано",
        "basic": "Базовая",
        "extended": "Расширенная",
        "full": "Полная",
        "general": "Общее",
        "identity": "Идентификация",
        "social": "Соцсети",
        "code": "Код",
        "images": "Изображения",
        "documents": "Документы",
        "archives": "Архивы",
        "organization": "Организации",
        "records": "Реестры",
        "references": "Упоминания",
        "technical": "Технические данные",
        "maps": "Карты",
        "blockchain": "Блокчейн",
        "content": "Публикации",
        "career": "Карьера",
        "location": "География",
        "contacts": "Контакты",
        "registries": "Реестры и публикации",
        "research": "Исследования",
        "web": "Веб",
    },
    "en": {
        "document_title": "Search report",
        "report": "Search report",
        "entity": "Data type",
        "target": "Value",
        "depth": "Depth",
        "created": "Created",
        "queries": "Queries",
        "sources": "Sources",
        "source_list": "SOURCES",
        "all_sources": "All sources",
        "search": "Filter queries and titles",
        "all_levels": "All levels",
        "all_categories": "All categories",
        "print": "Print",
        "theme": "Theme",
        "expand": "Expand",
        "collapse": "Collapse",
        "open": "Open",
        "copy_query": "Copy query",
        "copy_link": "Copy link",
        "copied": "Copied",
        "no_results": "Nothing matches the selected filters.",
        "visible": "Visible",
        "basic": "Basic",
        "extended": "Extended",
        "full": "Full",
        "general": "General",
        "identity": "Identity",
        "social": "Social",
        "code": "Code",
        "images": "Images",
        "documents": "Documents",
        "archives": "Archives",
        "organization": "Organizations",
        "records": "Registries",
        "references": "References",
        "technical": "Technical data",
        "maps": "Maps",
        "blockchain": "Blockchain",
        "content": "Content",
        "career": "Career",
        "location": "Location",
        "contacts": "Contacts",
        "registries": "Registries and publications",
        "research": "Research",
        "web": "Web",
    },
}


class HtmlReport:
    def __init__(self, template_path: Path = DATA_DIR / "report_template.html") -> None:
        self.template_path = template_path

    def render(
        self,
        entity_label: str,
        value: str,
        depth: str,
        results: list[QueryResult],
        language: str,
    ) -> str:
        selected = language if language in REPORT_TEXT else "en"
        text = REPORT_TEXT[selected]
        created = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
        source_counts = Counter(item.source.id for item in results)
        categories = sorted({item.category for item in results})
        groups = self._groups(results, text)
        sources = self._sources(results, source_counts, text)
        level_options = self._level_options(results, text)
        category_options = self._category_options(categories, text)
        replacements = {
            "{{LANG}}": escape(selected, quote=True),
            "{{DOCUMENT_TITLE}}": escape(f"QueryForge — {text['document_title']}", quote=True),
            "{{REPORT_LABEL}}": escape(text["report"]),
            "{{ENTITY_LABEL_KEY}}": escape(text["entity"]),
            "{{ENTITY_LABEL}}": escape(entity_label),
            "{{TARGET_KEY}}": escape(text["target"]),
            "{{TARGET}}": escape(value),
            "{{DEPTH_KEY}}": escape(text["depth"]),
            "{{DEPTH}}": escape(text.get(depth, depth)),
            "{{CREATED_KEY}}": escape(text["created"]),
            "{{CREATED}}": escape(created),
            "{{QUERIES_KEY}}": escape(text["queries"]),
            "{{QUERY_COUNT}}": str(len(results)),
            "{{SOURCES_KEY}}": escape(text["sources"]),
            "{{SOURCE_COUNT}}": str(len(source_counts)),
            "{{SOURCE_LIST_LABEL}}": escape(text["source_list"]),
            "{{ALL_SOURCES_LABEL}}": escape(text["all_sources"]),
            "{{SEARCH_PLACEHOLDER}}": escape(text["search"], quote=True),
            "{{ALL_LEVELS_LABEL}}": escape(text["all_levels"]),
            "{{ALL_CATEGORIES_LABEL}}": escape(text["all_categories"]),
            "{{PRINT_LABEL}}": escape(text["print"]),
            "{{THEME_LABEL}}": escape(text["theme"]),
            "{{EXPAND_LABEL}}": escape(text["expand"]),
            "{{COLLAPSE_LABEL}}": escape(text["collapse"]),
            "{{VISIBLE_LABEL}}": escape(text["visible"]),
            "{{NO_RESULTS_LABEL}}": escape(text["no_results"]),
            "{{COPIED_LABEL}}": escape(text["copied"], quote=True),
            "{{SOURCE_NAV}}": sources,
            "{{LEVEL_OPTIONS}}": level_options,
            "{{CATEGORY_OPTIONS}}": category_options,
            "{{RESULT_GROUPS}}": groups,
        }
        template = self.template_path.read_text(encoding="utf-8")
        for key, rendered in replacements.items():
            template = template.replace(key, rendered)
        return template

    def _sources(self, results: list[QueryResult], counts: Counter[str], text: dict[str, str]) -> str:
        names = {}
        for item in results:
            names[item.source.id] = item.source.name
        rows = []
        for source_id, count in sorted(counts.items(), key=lambda item: names[item[0]].lower()):
            rows.append(
                '<button class="source-nav" type="button" data-source-filter="{}">'
                '<span>{}</span><b>{}</b></button>'.format(
                    escape(source_id, quote=True),
                    escape(names[source_id]),
                    count,
                )
            )
        return "\n".join(rows)

    def _level_options(self, results: list[QueryResult], text: dict[str, str]) -> str:
        present = {item.level for item in results}
        order = ["basic", "extended", "full"]
        return "\n".join(
            f'<option value="{escape(level, quote=True)}">{escape(text.get(level, level))}</option>'
            for level in order
            if level in present
        )

    def _category_options(self, categories: list[str], text: dict[str, str]) -> str:
        return "\n".join(
            f'<option value="{escape(category, quote=True)}">{escape(text.get(category, category.replace("_", " ").title()))}</option>'
            for category in categories
        )

    def _groups(self, results: list[QueryResult], text: dict[str, str]) -> str:
        grouped: dict[str, list[QueryResult]] = {}
        for item in results:
            grouped.setdefault(item.source.id, []).append(item)
        blocks = []
        for source_id, items in grouped.items():
            source = items[0].source
            initials = "".join(part[:1] for part in source.name.replace(".", " ").split())[:2].upper() or source.name[:2].upper()
            rows = "\n".join(self._result(item, text) for item in items)
            blocks.append(
                '<section class="source-group" data-source="{}">'
                '<button class="group-head" type="button" aria-expanded="true">'
                '<span class="source-mark">{}</span>'
                '<span class="group-name">{}</span>'
                '<span class="group-count">{}</span>'
                '<span class="group-arrow">⌄</span>'
                '</button>'
                '<div class="group-results">{}</div>'
                '</section>'.format(
                    escape(source_id, quote=True),
                    escape(initials),
                    escape(source.name),
                    len(items),
                    rows,
                )
            )
        return "\n".join(blocks)

    def _result(self, item: QueryResult, text: dict[str, str]) -> str:
        category_label = text.get(item.category, item.category.replace("_", " ").title())
        level_label = text.get(item.level, item.level.title())
        searchable = " ".join([item.source.name, item.title, item.query, item.url, category_label, level_label]).lower()
        return (
            '<article class="query-row" data-source="{}" data-level="{}" data-category="{}" data-search="{}">'
            '<div class="query-index">{}</div>'
            '<div class="query-main">'
            '<div class="query-title"><span>{}</span><span class="tag">{}</span><span class="tag muted">{}</span></div>'
            '<code>{}</code>'
            '<a class="query-url" href="{}" target="_blank" rel="noopener noreferrer">{}</a>'
            '</div>'
            '<div class="query-actions">'
            '<button type="button" class="icon-button copy-button" data-copy="{}" title="{}" aria-label="{}">Q</button>'
            '<button type="button" class="icon-button copy-button" data-copy="{}" title="{}" aria-label="{}">L</button>'
            '<a class="open-button" href="{}" target="_blank" rel="noopener noreferrer">{}</a>'
            '</div>'
            '</article>'
        ).format(
            escape(item.source.id, quote=True),
            escape(item.level, quote=True),
            escape(item.category, quote=True),
            escape(searchable, quote=True),
            item.index,
            escape(item.title),
            escape(level_label),
            escape(category_label),
            escape(item.query),
            escape(item.url, quote=True),
            escape(item.url),
            escape(item.query, quote=True),
            escape(text["copy_query"], quote=True),
            escape(text["copy_query"], quote=True),
            escape(item.url, quote=True),
            escape(text["copy_link"], quote=True),
            escape(text["copy_link"], quote=True),
            escape(item.url, quote=True),
            escape(text["open"]),
        )
