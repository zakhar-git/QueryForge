from __future__ import annotations

from pathlib import Path
import yaml

from .models import Entity, QueryTemplate, Source
from .paths import DATA_DIR, ENTITY_DIR


class CatalogError(RuntimeError):
    pass


class Catalog:
    def __init__(self, data_dir: Path = DATA_DIR, entity_dir: Path = ENTITY_DIR) -> None:
        self.data_dir = data_dir
        self.entity_dir = entity_dir
        self.sources = self._load_sources()
        self.entities = self._load_entities()
        self._validate()

    def _load_sources(self) -> dict[str, Source]:
        path = self.data_dir / "sources.yaml"
        try:
            payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except (OSError, yaml.YAMLError) as exc:
            raise CatalogError(f"Could not load {path}: {exc}") from exc
        sources = {}
        for item in payload.get("sources", []):
            source = Source(**item)
            sources[source.id] = source
        return sources

    def _load_entities(self) -> dict[str, Entity]:
        entities = {}
        for path in sorted(self.entity_dir.glob("*.yaml")):
            try:
                payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            except (OSError, yaml.YAMLError) as exc:
                raise CatalogError(f"Could not load {path}: {exc}") from exc
            queries = tuple(QueryTemplate(**item) for item in payload.get("queries", []))
            entity = Entity(
                id=payload["id"],
                label_en=payload["label_en"],
                label_ru=payload["label_ru"],
                example_en=payload["example_en"],
                example_ru=payload["example_ru"],
                category=payload["category"],
                recommended_sources=tuple(payload.get("recommended_sources", [])),
                queries=queries,
            )
            entities[entity.id] = entity
        return entities

    def _validate(self) -> None:
        if not self.sources:
            raise CatalogError("No sources were loaded")
        if not self.entities:
            raise CatalogError("No entities were loaded")
        levels = {"basic", "extended", "full"}
        for entity in self.entities.values():
            if not entity.queries:
                raise CatalogError(f"Entity {entity.id} has no templates")
            for source_id in entity.recommended_sources:
                if source_id not in self.sources:
                    raise CatalogError(f"Unknown source {source_id} in {entity.id}")
            for template in entity.queries:
                if template.source not in self.sources:
                    raise CatalogError(f"Unknown source {template.source} in {entity.id}")
                if template.level not in levels:
                    raise CatalogError(f"Unknown level {template.level} in {entity.id}")

    def entity_sources(self, entity_id: str) -> list[Source]:
        entity = self.entities[entity_id]
        used = {template.source for template in entity.queries}
        return [source for source in self.sources.values() if source.id in used]

    def groups_for_entity(self, entity_id: str) -> list[str]:
        return sorted({source.group for source in self.entity_sources(entity_id)})

    def template_count(self) -> int:
        return sum(len(entity.queries) for entity in self.entities.values())
