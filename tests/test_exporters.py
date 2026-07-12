from html.parser import HTMLParser
from pathlib import Path
import re

from queryforge.catalog import Catalog
from queryforge.engine import QueryEngine
from queryforge.exporters import Exporter
from queryforge.paths import OUTPUT_DIR


class ReportInspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.article_count = 0
        self.group_count = 0
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        classes = values.get("class", "").split()
        if tag == "article" and "query-row" in classes:
            self.article_count += 1
        if tag == "section" and "source-group" in classes:
            self.group_count += 1
        element_id = values.get("id")
        if element_id:
            assert element_id not in self.ids
            self.ids.add(element_id)


def make_results(language: str = "ru"):
    catalog = Catalog()
    engine = QueryEngine(catalog)
    entity = catalog.entities["company"]
    sources = {template.source for template in entity.queries}
    results = engine.generate("company", "ООО Пример", "full", sources, language)
    return catalog, results


def test_html_report_is_generated_in_selected_output(tmp_path: Path):
    catalog, results = make_results()
    exporter = Exporter(tmp_path)
    paths = exporter.export(
        "company",
        "ООО Пример",
        "full",
        results,
        {"html"},
        "ru",
        catalog.entities["company"].label_ru,
    )
    assert len(paths) == 1
    report = paths[0]
    assert report.parent == tmp_path
    assert report.suffix == ".html"
    text = report.read_text(encoding="utf-8")
    assert "<!doctype html>" in text
    assert "Поисковый отчёт" in text
    assert "ООО Пример" in text
    assert str(len(results)) in text
    assert "<script src=" not in text
    assert "<link rel=" not in text
    assert not re.search(r"\{\{[A-Z_]+\}\}", text)


def test_html_report_escapes_user_content(tmp_path: Path):
    catalog = Catalog()
    engine = QueryEngine(catalog)
    value = '<script>alert("x")</script>'
    results = engine.generate("phrase", value, "basic", {"google", "yandex", "tgstat"}, "en")
    path = Exporter(tmp_path).export(
        "phrase",
        value,
        "basic",
        results,
        {"html"},
        "en",
        catalog.entities["phrase"].label_en,
    )[0]
    text = path.read_text(encoding="utf-8")
    assert value not in text
    assert "&lt;script&gt;" in text


def test_all_export_formats_replace_txt_with_html(tmp_path: Path):
    catalog, results = make_results("en")
    paths = Exporter(tmp_path).export(
        "company",
        "Example Labs",
        "extended",
        results,
        {"html", "json", "csv", "md"},
        "en",
        catalog.entities["company"].label_en,
    )
    assert {path.suffix for path in paths} == {".html", ".json", ".csv", ".md"}
    assert not list(tmp_path.glob("*.txt"))


def test_default_output_folder_is_named_output():
    assert OUTPUT_DIR.name == "output"


def test_html_report_structure_matches_results(tmp_path: Path):
    catalog, results = make_results()
    report = Exporter(tmp_path).export(
        "company",
        "ООО Пример",
        "full",
        results,
        {"html"},
        "ru",
        catalog.entities["company"].label_ru,
    )[0]
    inspector = ReportInspector()
    inspector.feed(report.read_text(encoding="utf-8"))
    assert inspector.article_count == len(results)
    assert inspector.group_count == len({item.source.id for item in results})
    assert {"searchInput", "levelSelect", "categorySelect", "resultGroups"}.issubset(inspector.ids)
