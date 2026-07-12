from __future__ import annotations

import csv
from datetime import datetime
import json
from pathlib import Path
import re

from .models import QueryResult
from .paths import OUTPUT_DIR
from .report import HtmlReport


class Exporter:
    def __init__(self, output_dir: Path = OUTPUT_DIR, report: HtmlReport | None = None) -> None:
        self.output_dir = output_dir
        self.report = report or HtmlReport()

    def export(
        self,
        entity_id: str,
        value: str,
        depth: str,
        results: list[QueryResult],
        formats: set[str],
        language: str = "en",
        entity_label: str | None = None,
    ) -> list[Path]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_value = re.sub(r"[^\w._-]+", "_", value, flags=re.UNICODE).strip("_")[:48] or "search"
        stem = f"{entity_id}_{safe_value}_{timestamp}"
        paths = []
        if "html" in formats:
            path = self.output_dir / f"{stem}.html"
            self._write_html(path, entity_label or entity_id, value, depth, results, language)
            paths.append(path)
        if "json" in formats:
            path = self.output_dir / f"{stem}.json"
            self._write_json(path, entity_id, value, depth, results)
            paths.append(path)
        if "csv" in formats:
            path = self.output_dir / f"{stem}.csv"
            self._write_csv(path, results)
            paths.append(path)
        if "md" in formats:
            path = self.output_dir / f"{stem}.md"
            self._write_markdown(path, entity_id, value, depth, results)
            paths.append(path)
        return paths

    def _write_html(
        self,
        path: Path,
        entity_label: str,
        value: str,
        depth: str,
        results: list[QueryResult],
        language: str,
    ) -> None:
        rendered = self.report.render(entity_label, value, depth, results, language)
        path.write_text(rendered, encoding="utf-8")

    @staticmethod
    def _write_json(path: Path, entity_id: str, value: str, depth: str, results: list[QueryResult]) -> None:
        payload = {
            "entity": entity_id,
            "value": value,
            "depth": depth,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "count": len(results),
            "results": [item.to_dict() for item in results],
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def _write_csv(path: Path, results: list[QueryResult]) -> None:
        with path.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(
                stream,
                fieldnames=["index", "source", "source_name", "title", "query", "url", "level", "category"],
            )
            writer.writeheader()
            for result in results:
                writer.writerow(result.to_dict())

    @staticmethod
    def _write_markdown(path: Path, entity_id: str, value: str, depth: str, results: list[QueryResult]) -> None:
        lines = [
            "# QueryForge",
            "",
            f"- Entity: `{entity_id}`",
            f"- Value: `{value}`",
            f"- Depth: `{depth}`",
            f"- Count: `{len(results)}`",
            "",
        ]
        current = ""
        for result in results:
            if result.source.name != current:
                current = result.source.name
                lines.extend([f"## {current}", ""])
            lines.extend([
                f"### {result.index}. {result.title}",
                "",
                f"`{result.query}`",
                "",
                f"[Open]({result.url})",
                "",
            ])
        path.write_text("\n".join(lines), encoding="utf-8")
