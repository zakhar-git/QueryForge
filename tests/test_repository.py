from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_python_files_have_no_comment_lines() -> None:
    for path in ROOT.rglob("*.py"):
        if any(part in {".venv", "build", "dist"} or part.endswith(".egg-info") for part in path.parts):
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            assert not line.lstrip().startswith("#"), f"{path}:{line_number}"


def test_markdown_has_no_control_characters() -> None:
    for path in ROOT.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        invalid = [character for character in text if ord(character) < 32 and character not in "\n\r\t"]
        assert not invalid, str(path)
