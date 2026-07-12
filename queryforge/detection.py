from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlparse


EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
DOMAIN_RE = re.compile(r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,63}$")
ASN_RE = re.compile(r"^(?:AS)?\d{1,10}$", re.IGNORECASE)
HEX_RE = re.compile(r"^[0-9a-fA-F]+$")
PHONE_RE = re.compile(r"^[+()\-\s.\d]{7,30}$")
USERNAME_RE = re.compile(r"^@?[A-Za-z0-9_.-]{2,64}$")
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
CRYPTO_PATTERNS = [
    re.compile(r"^0x[a-fA-F0-9]{40}$"),
    re.compile(r"^(?:bc1|[13])[a-zA-HJ-NP-Z0-9]{25,62}$"),
    re.compile(r"^T[1-9A-HJ-NP-Za-km-z]{33}$"),
    re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$"),
    re.compile(r"^(?:EQ|UQ)[A-Za-z0-9_-]{46}$"),
]


def detect_candidates(value: str) -> list[str]:
    text = value.strip()
    candidates = []
    if EMAIL_RE.fullmatch(text):
        candidates.append("email")
    try:
        ipaddress.ip_address(text)
        candidates.append("ip")
    except ValueError:
        pass
    parsed = urlparse(text if "://" in text else "")
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        if "github.com" in parsed.netloc and len(parsed.path.strip("/").split("/")) >= 2:
            candidates.append("github_repo")
        if "t.me" in parsed.netloc:
            candidates.append("telegram")
        candidates.extend(["url", "social_profile"])
    if DOMAIN_RE.fullmatch(text.lower().rstrip(".")):
        candidates.append("domain")
    if ASN_RE.fullmatch(text) and text.upper().startswith("AS"):
        candidates.append("asn")
    if len(text) in {32, 40, 64, 128} and HEX_RE.fullmatch(text):
        candidates.append("hash")
    if PHONE_RE.fullmatch(text) and len(re.sub(r"\D", "", text)) >= 7:
        candidates.append("phone")
    if any(pattern.fullmatch(text) for pattern in CRYPTO_PATTERNS):
        candidates.append("crypto_address")
    if text.startswith("@") or text.startswith("t.me/"):
        candidates.append("telegram")
    if REPO_RE.fullmatch(text):
        candidates.append("github_repo")
    if USERNAME_RE.fullmatch(text):
        candidates.append("username")
    if len(text.split()) >= 2:
        candidates.extend(["person", "company", "phrase"])
    elif not candidates:
        candidates.extend(["phrase", "brand"])
    return list(dict.fromkeys(candidates))


def validate_value(entity_id: str, value: str) -> bool:
    text = value.strip()
    if not text:
        return False
    if entity_id == "email":
        return bool(EMAIL_RE.fullmatch(text))
    if entity_id == "domain":
        return bool(DOMAIN_RE.fullmatch(text.lower().rstrip(".")))
    if entity_id == "ip":
        try:
            ipaddress.ip_address(text)
            return True
        except ValueError:
            return False
    if entity_id == "asn":
        return bool(ASN_RE.fullmatch(text))
    if entity_id == "hash":
        return len(text) in {32, 40, 64, 128} and bool(HEX_RE.fullmatch(text))
    if entity_id == "phone":
        return bool(PHONE_RE.fullmatch(text)) and len(re.sub(r"\D", "", text)) >= 7
    if entity_id == "github_repo":
        if "github.com" in text:
            parsed = urlparse(text if "://" in text else f"https://{text}")
            return len(parsed.path.strip("/").split("/")) >= 2
        return bool(REPO_RE.fullmatch(text))
    if entity_id == "crypto_address":
        return any(pattern.fullmatch(text) for pattern in CRYPTO_PATTERNS)
    return True
