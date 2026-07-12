from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Source:
    id: str
    name: str
    group: str
    url_template: str
    encoding: str = "query"


@dataclass(frozen=True)
class QueryTemplate:
    source: str
    level: str
    title_en: str
    title_ru: str
    query: str
    category: str = "general"
    url: str = ""


@dataclass(frozen=True)
class Entity:
    id: str
    label_en: str
    label_ru: str
    example_en: str
    example_ru: str
    category: str
    recommended_sources: tuple[str, ...]
    queries: tuple[QueryTemplate, ...]


@dataclass(frozen=True)
class QueryResult:
    index: int
    source: Source
    title: str
    query: str
    url: str
    level: str
    category: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "source": self.source.id,
            "source_name": self.source.name,
            "title": self.title,
            "query": self.query,
            "url": self.url,
            "level": self.level,
            "category": self.category,
        }


@dataclass
class Settings:
    language: str = "ru"
    accent: str = "cyan"
    page_size: int = 20
    default_depth: str = "extended"
    default_source_mode: str = "recommended"
    save_history: bool = True
    clear_screen: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "language": self.language,
            "accent": self.accent,
            "page_size": self.page_size,
            "default_depth": self.default_depth,
            "default_source_mode": self.default_source_mode,
            "save_history": self.save_history,
            "clear_screen": self.clear_screen,
        }


@dataclass
class SearchRecord:
    entity: str
    value: str
    depth: str
    sources: list[str]
    count: int
    created_at: str
    results: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity": self.entity,
            "value": self.value,
            "depth": self.depth,
            "sources": self.sources,
            "count": self.count,
            "created_at": self.created_at,
            "results": self.results,
        }
