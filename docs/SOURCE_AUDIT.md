# Source audit

## Catalog checks

The automated test suite checks that:

- every source has a valid identifier, group and URL template;
- every source is used by at least one entity;
- every entity has working recommended templates;
- every template renders without unresolved placeholders;
- generated links contain an HTTP or HTTPS host;
- duplicate templates are rejected;
- Yandex templates do not use Google-only `OR` or `filetype:` syntax;
- the HTML report is self-contained and escapes user input.

## External service limits

A passing catalog test confirms local structure and link rendering, not permanent availability of an external website. Sources may require authentication, JavaScript, CAPTCHA or regional access. Official registries without stable query parameters open at the search form.
