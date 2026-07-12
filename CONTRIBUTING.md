# Contributing

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

On Windows use `.venv\Scripts\activate`.

## Adding a source

Add one entry to `queryforge/data/sources.yaml`, then add matching query templates to one or more files in `queryforge/data/entities`.

## Adding a data type

Create a YAML file in `queryforge/data/entities`, add its identifier to `ENTITY_ORDER` in `queryforge/app.py`, and add detection or validation rules when needed.

Every source and template must have a real purpose, a valid generated URL and clear Russian and English labels. Run the full test suite before opening a pull request.
