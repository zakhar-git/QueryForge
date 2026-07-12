from queryforge.catalog import Catalog


def test_catalog_loads_all_data():
    catalog = Catalog()
    assert len(catalog.sources) >= 120
    assert len(catalog.entities) >= 18
    assert catalog.template_count() >= 700


def test_every_entity_has_recommended_queries():
    catalog = Catalog()
    for entity in catalog.entities.values():
        used = {template.source for template in entity.queries}
        assert set(entity.recommended_sources).issubset(used)


def test_all_sources_are_used_and_titles_are_complete():
    catalog = Catalog()
    used = {template.source for entity in catalog.entities.values() for template in entity.queries}
    assert used == set(catalog.sources)
    for entity in catalog.entities.values():
        for template in entity.queries:
            assert template.title_en.strip()
            assert template.title_ru.strip()
            assert template.query.strip()


def test_catalog_has_unique_sources_and_templates():
    catalog = Catalog()
    assert len(catalog.sources) == len(set(catalog.sources))
    for entity in catalog.entities.values():
        keys = [
            (template.source, template.level, template.query, template.url)
            for template in entity.queries
        ]
        assert len(keys) == len(set(keys)), entity.id


def test_cis_source_pack_is_present():
    catalog = Catalog()
    expected = {
        "vk",
        "ok",
        "rutube",
        "tgstat",
        "habr",
        "pikabu",
        "yandex_maps",
        "two_gis",
        "rusprofile",
        "checko",
        "egrul_nalog",
        "zakupki_ru",
        "youcontrol",
        "opendatabot",
        "adata_kz",
        "kgd_kz",
        "orginfo_uz",
        "egr_by",
    }
    assert expected.issubset(catalog.sources)


def test_yandex_pack_is_present():
    catalog = Catalog()
    expected = {"yandex", "yandex_images", "yandex_maps", "yandex_news"}
    assert expected.issubset(catalog.sources)
    entities = {"username", "email", "person", "phone", "company", "brand", "domain", "url", "document", "location", "phrase"}
    for entity_id in entities:
        entity = catalog.entities[entity_id]
        assert "yandex" in entity.recommended_sources
        assert any(template.source == "yandex" for template in entity.queries)


def test_extended_source_pack_is_present():
    catalog = Catalog()
    expected = {
        "qwant", "mojeek", "ecosia", "yahoo", "google_news", "bing_news", "yandex_news", "gdelt",
        "codeberg", "gitflic", "bitbucket", "bluesky", "tiktok", "linkedin", "arquivo_pt",
        "companies_house", "sec_edgar", "e_register_am", "minjust_kg", "georgia_registry", "srl_md",
        "pubmed", "arxiv", "semantic_scholar", "worldcat", "viaf", "rdap", "ipinfo", "bgp_he",
        "urlhaus", "threatfox", "pulsedive", "blockchain_com", "bscscan", "polygonscan", "arbiscan", "basescan",
    }
    assert expected.issubset(catalog.sources)


def test_yandex_templates_use_yandex_syntax():
    catalog = Catalog()
    templates = [template for entity in catalog.entities.values() for template in entity.queries if template.source == "yandex"]
    assert templates
    for template in templates:
        assert " OR " not in template.query
        assert "filetype:" not in template.query
