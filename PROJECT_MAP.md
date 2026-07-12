# Project map

## Entry point

- `main.py` starts the interactive application.

## Application modules

- `queryforge/app.py` controls menus and application flow.
- `queryforge/ui.py` renders the terminal interface and ASCII banner.
- `queryforge/menu.py` handles numeric selection and ranges.
- `queryforge/catalog.py` loads and validates YAML data.
- `queryforge/engine.py` normalizes values and builds queries and links.
- `queryforge/detection.py` detects common value types.
- `queryforge/browser.py` opens selected links.
- `queryforge/exporters.py` writes HTML, JSON, CSV and Markdown.
- `queryforge/report.py` renders the self-contained HTML report.
- `queryforge/config.py` stores local settings.
- `queryforge/history.py` stores local search history.
- `queryforge/i18n.py` contains Russian and English interface text.
- `queryforge/models.py` contains data models.
- `queryforge/paths.py` contains package, user-data and output paths.

## Data packs

- `queryforge/data/sources.yaml` defines source names, groups and URL formats.
- `queryforge/data/entities/*.yaml` defines data types, recommended sources and query templates.
- `queryforge/data/report_template.html` contains the offline report layout.

## Tests

- `tests/test_catalog.py` checks source and template integrity.
- `tests/test_engine.py` checks rendering, deduplication and generated URLs.
- `tests/test_detection.py` checks value detection and validation.
- `tests/test_menu.py` checks numeric range parsing.
- `tests/test_cli.py` checks startup, clean banner output, exports and saved language.
- `tests/test_exporters.py` checks HTML and structured exports.
- `tests/test_repository.py` checks repository hygiene.

## User data

QueryForge stores settings and history in `~/.queryforge`. Reports are stored in `output` in the current working directory. The locations can be overridden with `QUERYFORGE_HOME` and `QUERYFORGE_OUTPUT`.
