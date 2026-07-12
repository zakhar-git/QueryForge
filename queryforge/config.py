from __future__ import annotations

import json
from pathlib import Path

from .models import Settings
from .paths import SETTINGS_FILE


class SettingsStore:
    def __init__(self, path: Path = SETTINGS_FILE) -> None:
        self.path = path

    def load(self) -> Settings:
        if not self.path.exists():
            return Settings()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return Settings()
        defaults = Settings().to_dict()
        defaults.update({key: value for key, value in data.items() if key in defaults})
        settings = Settings(**defaults)
        if settings.language not in {"ru", "en"}:
            settings.language = "ru"
        if settings.accent not in {"cyan", "green", "blue", "magenta", "white"}:
            settings.accent = "cyan"
        if settings.page_size not in {10, 20, 50, 0}:
            settings.page_size = 20
        if settings.default_depth not in {"basic", "extended", "full"}:
            settings.default_depth = "extended"
        if settings.default_source_mode not in {"recommended", "all"}:
            settings.default_source_mode = "recommended"
        return settings

    def save(self, settings: Settings) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(settings.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary.replace(self.path)
