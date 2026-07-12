from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .models import GeneratedQuery


def export_results(
    entity: str,
    value: str,
    level: str,
    queries: list[GeneratedQuery],
    output_dir: Path,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_entity = "".join(ch for ch in value if ch.isalnum() or ch in "-_.")[:40]
    base = f"{entity}_{safe_entity or 'query'}_{timestamp}"

    txt_path = output_dir / f"{base}.txt"
    json_path = output_dir / f"{base}.json"

    txt_lines = [
        "QueryForge OSINT Search Plan",
        f"Entity: {entity}",
        f"Value: {value}",
        f"Depth: {level}",
        f"Queries: {len(queries)}",
        "",
    ]

    current_source = None
    for item in queries:
        if item.source != current_source:
            current_source = item.source
            txt_lines.extend([f"[{current_source.upper()}]", ""])
        txt_lines.append(f"- {item.title}")
        txt_lines.append(f"  {item.query}")
        if item.note:
            txt_lines.append(f"  Note: {item.note}")
        txt_lines.append("")

    txt_path.write_text("\n".join(txt_lines), encoding="utf-8")

    payload = {
        "entity": entity,
        "value": value,
        "level": level,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "queries": [query.to_dict() for query in queries],
    }
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return txt_path, json_path
