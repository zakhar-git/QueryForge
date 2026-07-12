from __future__ import annotations

import hashlib
import ipaddress
import re
from urllib.parse import quote, quote_plus, urlparse

from .catalog import Catalog
from .models import QueryResult


LEVEL_ORDER = {"basic": 1, "extended": 2, "full": 3}


class RenderContext(dict[str, str]):
    def __missing__(self, key: str) -> str:
        raise KeyError(key)


class QueryEngine:
    def __init__(self, catalog: Catalog) -> None:
        self.catalog = catalog

    def generate(
        self,
        entity_id: str,
        value: str,
        depth: str,
        source_ids: set[str],
        language: str,
    ) -> list[QueryResult]:
        entity = self.catalog.entities[entity_id]
        context = self.build_context(entity_id, value)
        maximum = LEVEL_ORDER[depth]
        results = []
        seen = set()
        for template in entity.queries:
            if template.source not in source_ids:
                continue
            if LEVEL_ORDER[template.level] > maximum:
                continue
            source = self.catalog.sources[template.source]
            query = template.query.format_map(context).strip()
            url = self._render_url(source.url_template, source.encoding, query)
            if template.url:
                url = template.url.format_map(context)
            key = (source.id, query, url)
            if key in seen:
                continue
            seen.add(key)
            title = template.title_ru if language == "ru" else template.title_en
            results.append(
                QueryResult(
                    index=len(results) + 1,
                    source=source,
                    title=title,
                    query=query,
                    url=url,
                    level=template.level,
                    category=template.category,
                )
            )
        return results

    def build_context(self, entity_id: str, raw_value: str) -> RenderContext:
        value = raw_value.strip()
        context = RenderContext()
        context.update({
            "value": value,
            "value_q": quote_plus(value),
            "value_path": quote(value, safe=""),
            "username": value.lstrip("@"),
            "email": value.lower(),
            "local": value.split("@", 1)[0] if "@" in value else value,
            "domain": value.lower().strip().rstrip("."),
            "name": value,
            "company": value,
            "brand": value,
            "phrase": value,
            "location": value,
            "document": value,
            "image": value,
            "hash": value.lower(),
            "hash_type": self._hash_type(value),
            "crypto": value,
            "telegram": value.lstrip("@").replace("https://t.me/", "").replace("http://t.me/", "").strip("/"),
            "phone": value,
            "phone_digits": re.sub(r"\D", "", value),
            "phone_plus": "+" + re.sub(r"\D", "", value),
            "asn": value.upper() if value.upper().startswith("AS") else f"AS{value}",
            "asn_number": re.sub(r"\D", "", value),
            "url": value,
            "url_q": quote_plus(value),
            "url_path_encoded": quote(value, safe=""),
            "repo": value,
            "repo_owner": "",
            "repo_name": "",
            "first": "",
            "last": "",
            "initials": "",
            "email_md5": hashlib.md5(value.strip().lower().encode("utf-8"), usedforsecurity=False).hexdigest(),
            "ip": value,
            "ip_version": "",
        })
        if entity_id == "email" and "@" in value:
            local, domain = value.rsplit("@", 1)
            context["local"] = local
            context["domain"] = self._normalize_domain(domain)
            context["email"] = f"{local}@{context['domain']}"
        if entity_id == "domain":
            context["domain"] = self._normalize_domain(value)
            context["value"] = context["domain"]
        if entity_id in {"url", "social_profile", "image"}:
            candidate = value if "://" in value else f"https://{value}"
            parsed = urlparse(candidate)
            if parsed.hostname:
                context["domain"] = self._normalize_domain(parsed.hostname)
                context["url"] = candidate
                context["url_q"] = quote_plus(candidate)
                context["url_path_encoded"] = quote(candidate, safe="")
                path_parts = [part for part in parsed.path.split("/") if part]
                if path_parts:
                    context["username"] = path_parts[-1].lstrip("@")
        if entity_id == "person":
            parts = [part for part in re.split(r"\s+", value) if part]
            if parts:
                context["first"] = parts[0]
                context["last"] = parts[-1]
                context["initials"] = "".join(part[0] for part in parts if part)
        if entity_id == "github_repo":
            repo = self._normalize_repo(value)
            context["repo"] = repo
            if "/" in repo:
                owner, name = repo.split("/", 1)
                context["repo_owner"] = owner
                context["repo_name"] = name
        if entity_id == "ip":
            try:
                address = ipaddress.ip_address(value)
                context["ip"] = str(address)
                context["ip_version"] = str(address.version)
            except ValueError:
                pass
        context["username_q"] = quote_plus(context["username"])
        context["domain_q"] = quote_plus(context["domain"])
        context["repo_q"] = quote_plus(context["repo"])
        context["telegram_q"] = quote_plus(context["telegram"])
        return context

    @staticmethod
    def _hash_type(value: str) -> str:
        length_map = {32: "md5", 40: "sha1", 64: "sha256", 128: "sha512"}
        return length_map.get(len(value.strip()), "hash")

    @staticmethod
    def _normalize_domain(value: str) -> str:
        candidate = value.strip().lower()
        if "://" in candidate:
            candidate = urlparse(candidate).hostname or candidate
        candidate = candidate.split("/", 1)[0].strip(".")
        if candidate.startswith("www."):
            candidate = candidate[4:]
        try:
            return candidate.encode("idna").decode("ascii")
        except UnicodeError:
            return candidate

    @staticmethod
    def _normalize_repo(value: str) -> str:
        text = value.strip().removesuffix(".git")
        if "github.com" in text:
            parsed = urlparse(text if "://" in text else f"https://{text}")
            parts = parsed.path.strip("/").split("/")
            if len(parts) >= 2:
                return f"{parts[0]}/{parts[1]}"
        return text.strip("/")

    @staticmethod
    def _render_url(template: str, encoding: str, query: str) -> str:
        if encoding == "path":
            encoded = quote(query, safe="")
        elif encoding == "fragment":
            encoded = quote(query, safe=':.*"')
        elif encoding == "raw":
            encoded = query
        else:
            encoded = quote_plus(query)
        return template.format(query=encoded)
