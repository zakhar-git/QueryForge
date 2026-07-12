from __future__ import annotations

import json
from pathlib import Path

from .models import SearchRecord
from .paths import HISTORY_FILE


class HistoryStore:
    def __init__(self, path: Path = HISTORY_FILE, limit: int = 100) -> None:
        self.path = path
        self.limit = limit

    def load(self) -> list[SearchRecord]:
        if not self.path.exists():
            return []
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            return [SearchRecord(**item) for item in payload if isinstance(item, dict)]
        except (OSError, json.JSONDecodeError, TypeError):
            return []

    def add(self, record: SearchRecord) -> None:
        records = self.load()
        records.insert(0, record)
        self._write(records[: self.limit])

    def clear(self) -> None:
        self._write([])

    def _write(self, records: list[SearchRecord]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps([item.to_dict() for item in records], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary.replace(self.path)
