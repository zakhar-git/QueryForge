from urllib.parse import urlparse

from queryforge.catalog import Catalog
from queryforge.engine import QueryEngine


SAMPLES = {
    "username": "shadow_fox",
    "email": "analyst@example.com",
    "person": "Jane Alexandra Doe",
    "phone": "+1 202 555 0174",
    "domain": "example.com",
    "url": "https://example.com/about?q=1",
    "ip": "8.8.8.8",
    "asn": "AS15169",
    "company": "Example Labs",
    "brand": "Example",
    "location": "Berlin Alexanderplatz",
    "phrase": "distinct public phrase",
    "document": "annual-report-2025.pdf",
    "image": "https://example.com/avatar.jpg",
    "github_repo": "octocat/Hello-World",
    "hash": "a" * 64,
    "crypto_address": "0x0000000000000000000000000000000000000000",
    "telegram": "example_channel",
    "social_profile": "https://example.social/@example",
}


def test_every_template_renders_valid_url():
    catalog = Catalog()
    engine = QueryEngine(catalog)
    for entity_id, entity in catalog.entities.items():
        value = SAMPLES[entity_id]
        sources = {template.source for template in entity.queries}
        results = engine.generate(entity_id, value, "full", sources, "en")
        assert results
        for result in results:
            parsed = urlparse(result.url)
            assert parsed.scheme in {"http", "https"}
            assert parsed.netloc
            assert "{" not in result.query
            assert "}" not in result.query
            assert "{" not in result.url
            assert "}" not in result.url


def test_results_are_deduplicated():
    catalog = Catalog()
    engine = QueryEngine(catalog)
    entity = catalog.entities["username"]
    sources = {template.source for template in entity.queries}
    results = engine.generate("username", "sample", "full", sources, "ru")
    keys = {(item.source.id, item.query, item.url) for item in results}
    assert len(keys) == len(results)


def test_recommended_basic_is_never_empty():
    catalog = Catalog()
    engine = QueryEngine(catalog)
    for entity_id, entity in catalog.entities.items():
        results = engine.generate(entity_id, SAMPLES[entity_id], "basic", set(entity.recommended_sources), "en")
        assert results, entity_id
