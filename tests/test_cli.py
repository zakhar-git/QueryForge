from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent


def run_cli(user_input: str, home: Path) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["QUERYFORGE_HOME"] = str(home)
    environment["QUERYFORGE_NO_CLEAR"] = "1"
    environment["QUERYFORGE_OUTPUT"] = str(home / "output")
    return subprocess.run(
        [sys.executable, "main.py"],
        cwd=ROOT,
        input=user_input,
        text=True,
        capture_output=True,
        timeout=20,
        env=environment,
        check=False,
    )


def test_cli_exits_with_number_zero(tmp_path):
    result = run_cli("0\n", tmp_path)
    assert result.returncode == 0
    assert "ГЛАВНОЕ МЕНЮ" in result.stdout
    assert "0. Выход" in result.stdout
    assert "interactive mode" not in result.stdout
    assert "SEARCH STRATEGY ENGINE" not in result.stdout


def test_language_setting_persists(tmp_path):
    result = run_cli("4\n1\n2\n0\n0\n", tmp_path)
    assert result.returncode == 0
    settings = json.loads((tmp_path / "settings.json").read_text(encoding="utf-8"))
    assert settings["language"] == "en"
    assert "MAIN MENU" in result.stdout


def test_cli_exports_html_report(tmp_path):
    user_input = "1\n1\nshadow_fox\n1\n1\n3\n2\n\n5\n0\n"
    result = run_cli(user_input, tmp_path)
    assert result.returncode == 0
    reports = list((tmp_path / "output").glob("*.html"))
    assert len(reports) == 1
    text = reports[0].read_text(encoding="utf-8")
    assert "QueryForge" in text
    assert "shadow_fox" in text
    assert not list((tmp_path / "output").glob("*.txt"))


def test_header_does_not_print_version(monkeypatch):
    from io import StringIO
    from rich.console import Console
    from queryforge.models import Settings
    from queryforge.ui import UI

    stream = StringIO()
    ui = UI(Settings(clear_screen=False))
    ui.console = Console(file=stream, force_terminal=False, color_system=None, width=160)
    ui.header()
    output = stream.getvalue()
    assert "v0." not in output
    assert "QueryForge" not in output or "____" in output
