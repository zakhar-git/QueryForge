from __future__ import annotations

from collections.abc import Sequence

from rich.console import Console


class Menu:
    def __init__(self, console: Console, accent: str) -> None:
        self.console = console
        self.accent = accent

    def choose(self, title: str, options: Sequence[tuple[str, str]], prompt: str) -> str:
        self.console.print(f"\n[{self.accent} bold]{title}[/{self.accent} bold]")
        for index, (_, label) in enumerate(options, start=1):
            self.console.print(f"[{self.accent}]{index:>2}.[/{self.accent}] {label}")
        while True:
            raw = self.console.input(f"\n[{self.accent}]> [/{self.accent}]{prompt}: ").strip()
            if raw.isdigit():
                selected = int(raw)
                if 1 <= selected <= len(options):
                    return options[selected - 1][0]
            self.console.print("[red]×[/red]")

    def choose_with_zero(
        self,
        title: str,
        options: Sequence[tuple[str, str]],
        prompt: str,
        zero_label: str,
        default_key: str | None = None,
    ) -> str | None:
        self.console.print(f"\n[{self.accent} bold]{title}[/{self.accent} bold]")
        for index, (key, label) in enumerate(options, start=1):
            marker = " ↵" if key == default_key else ""
            self.console.print(f"[{self.accent}]{index:>2}.[/{self.accent}] {label}{marker}")
        self.console.print(f"[{self.accent}] 0.[/{self.accent}] {zero_label}")
        while True:
            raw = self.console.input(f"\n[{self.accent}]> [/{self.accent}]{prompt}: ").strip()
            if not raw and default_key is not None:
                return default_key
            if raw == "0":
                return None
            if raw.isdigit():
                selected = int(raw)
                if 1 <= selected <= len(options):
                    return options[selected - 1][0]
            self.console.print("[red]×[/red]")

    def choose_many(
        self,
        title: str,
        options: Sequence[tuple[str, str]],
        prompt: str,
        hint: str,
        all_words: set[str],
        zero_label: str,
    ) -> list[str] | None:
        self.console.print(f"\n[{self.accent} bold]{title}[/{self.accent} bold]")
        for index, (_, label) in enumerate(options, start=1):
            self.console.print(f"[{self.accent}]{index:>2}.[/{self.accent}] {label}")
        self.console.print(f"[{self.accent}] 0.[/{self.accent}] {zero_label}")
        self.console.print(f"[dim]{hint}[/dim]")
        while True:
            raw = self.console.input(f"\n[{self.accent}]> [/{self.accent}]{prompt}: ").strip().lower()
            if raw == "0":
                return None
            if raw in all_words:
                return [key for key, _ in options]
            try:
                indices = self.parse_indices(raw, len(options))
            except ValueError:
                self.console.print("[red]×[/red]")
                continue
            if indices:
                return [options[index - 1][0] for index in indices]
            self.console.print("[red]×[/red]")

    @staticmethod
    def parse_indices(raw: str, maximum: int) -> list[int]:
        selected = set()
        for part in raw.replace(" ", "").split(","):
            if not part:
                continue
            if "-" in part:
                start_text, end_text = part.split("-", 1)
                start = int(start_text)
                end = int(end_text)
                if start > end:
                    start, end = end, start
                selected.update(range(start, end + 1))
            else:
                selected.add(int(part))
        if any(index < 1 or index > maximum for index in selected):
            raise ValueError(raw)
        return sorted(selected)
