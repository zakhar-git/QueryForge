from __future__ import annotations

import os

from rich.align import Align
from rich.console import Console
from rich.text import Text

from .i18n import tr
from .models import Entity, QueryResult, Settings, Source


BANNER = "\n".join(
    [
        "   ____                        ______",
        r"  / __ \__  _____  _______  __/ ____/___  _________ ____",
        r" / / / / / / / _ \/ ___/ / / / /_  / __ \/ ___/ __ `/ _ \ ",
        r"/ /_/ / /_/ /  __/ /  / /_/ / __/ / /_/ / /  / /_/ /  __/",
        r"\___\_\__,_/\___/_/   \__, /_/    \____/_/   \__, /\___/",
        r"                     /____/                  /____/",
    ]
)


class UI:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.console = Console()

    @property
    def language(self) -> str:
        return self.settings.language

    @property
    def accent(self) -> str:
        return self.settings.accent

    def text(self, key: str) -> str:
        return tr(self.language, key)

    def clear(self) -> None:
        if self.settings.clear_screen and not os.environ.get("QUERYFORGE_NO_CLEAR"):
            self.console.clear()

    def header(self) -> None:
        banner = Text(BANNER, style=f"bold {self.accent}")
        self.console.print(Align.center(banner))

    def section(self, title: str) -> None:
        self.console.print(f"\n[{self.accent} bold]{title}[/{self.accent} bold]")

    def value_prompt(self, entity: Entity) -> str:
        example = entity.example_ru if self.language == "ru" else entity.example_en
        label = entity.label_ru if self.language == "ru" else entity.label_en
        self.console.print(f"\n[{self.accent} bold]{label}[/{self.accent} bold]")
        self.console.print(f"[dim]{self.text('example')}: {example}[/dim]")
        return self.console.input(f"\n[{self.accent}]> [/{self.accent}]{self.text('enter_value')}: ").strip()

    def show_results(self, results: list[QueryResult], page: int, page_size: int) -> tuple[int, int]:
        total = len(results)
        if page_size == 0:
            page_size = total or 1
        pages = max(1, (total + page_size - 1) // page_size)
        page = min(max(page, 1), pages)
        start = (page - 1) * page_size
        end = min(start + page_size, total)
        self.section(self.text("results"))
        self.console.print(f"{self.text('query_count')}: [bold]{total}[/bold]    {self.text('page')}: [bold]{page}/{pages}[/bold]\n")
        current_source = ""
        for result in results[start:end]:
            if result.source.name != current_source:
                current_source = result.source.name
                self.console.print(f"[{self.accent} bold]{current_source}[/{self.accent} bold]")
            self.console.print(f"[{self.accent}]{result.index:>3}.[/{self.accent}] [bold]{result.title}[/bold]")
            self.console.print(Text(f"     {result.query}"))
            self.console.print(Text(f"     {result.url}\n", style="dim"))
        return page, pages

    def show_sources(self, sources: list[Source]) -> None:
        grouped = {}
        for source in sources:
            grouped.setdefault(source.group, []).append(source)
        for group, items in grouped.items():
            self.section(self.text(f"group_{group}"))
            for source in items:
                self.console.print(f"[{self.accent}]•[/{self.accent}] {source.name}")

    def show_history(self, records, entities: dict[str, Entity]) -> None:
        self.section(self.text("history"))
        for index, record in enumerate(records, start=1):
            entity = entities.get(record.entity)
            label = record.entity
            if entity:
                label = entity.label_ru if self.language == "ru" else entity.label_en
            line = Text()
            line.append(f"{index:>2}. ", style=self.accent)
            line.append(record.value, style="bold")
            self.console.print(line)
            self.console.print(Text(f"    {label} · {record.depth} · {record.count} · {record.created_at}", style="dim"))

    def status(self, message: str) -> None:
        line = Text("\n✓ ", style=self.accent)
        line.append(message)
        self.console.print(line)

    def error(self, message: str) -> None:
        line = Text("\n× ", style="red")
        line.append(message, style="default")
        self.console.print(line)

    def wait(self) -> None:
        self.console.input(f"\n[dim]{self.text('press_enter')}[/dim]")
