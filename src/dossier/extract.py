from __future__ import annotations

import re
from email import policy
from email.parser import BytesParser, Parser
from pathlib import Path

from dossier.schemas import ArtifactSet

URL_RE = re.compile(r"""(?i)\b((?:https?://|www\.)[^\s<>"'\)\]]+)""")
EMAIL_RE = re.compile(r"(?i)\b[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}\b")
PHONE_RE = re.compile(r"\b(?:\+?\d[\d\-().\s]{8,}\d)\b")
ETH_RE = re.compile(r"\b0x[a-fA-F0-9]{40}\b")
BTC_RE = re.compile(r"\b(?:bc1|[13])[a-zA-HJ-NP-Z0-9]{25,62}\b")


def load_source(path: str | Path | None = None, text: str | None = None) -> tuple[str, str]:
    """Return (body, raw_headers). Headers are empty for plain text."""
    if text is not None and path is None:
        return text, ""
    if path is None:
        raise ValueError("provide a path or text")
    p = Path(path)
    raw = p.read_bytes()
    if p.suffix.lower() in {".eml", ".msg"} or b"\nFrom:" in raw[:4000] or raw.lower().startswith(b"from:"):
        message = BytesParser(policy=policy.default).parsebytes(raw)
        body = _message_body(message)
        headers = "\n".join(f"{k}: {v}" for k, v in message.items())
        return body, headers
    return raw.decode("utf-8", errors="replace"), ""


def load_headers_and_body_from_text(raw: str) -> tuple[str, str]:
    if "\n\n" in raw and re.match(r"(?i)(from|to|subject|return-path):", raw):
        message = Parser(policy=policy.default).parsestr(raw)
        return _message_body(message), "\n".join(f"{k}: {v}" for k, v in message.items())
    return raw, ""


def _message_body(message) -> str:
    parts: list[str] = []
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/plain":
                parts.append(part.get_content())
            elif part.get_content_type() == "text/html" and not parts:
                parts.append(part.get_content())
    else:
        parts.append(message.get_content())
    return "\n".join(p.strip() for p in parts if p and str(p).strip())


def extract_artifacts(source_text: str, headers: str = "") -> ArtifactSet:
    blob = f"{headers}\n{source_text}"
    urls = _clean_urls(URL_RE.findall(blob))
    emails = sorted(set(m.group(0).lower() for m in EMAIL_RE.finditer(blob)))
    domains: set[str] = set()
    for url in urls:
        host = _host(url)
        if host:
            domains.add(host.lower())
    for mail in emails:
        domains.add(mail.split("@", 1)[1].lower())
    phones = sorted({re.sub(r"[^\d+]", "", m.group(0)) for m in PHONE_RE.finditer(blob) if len(re.sub(r"\D", "", m.group(0))) >= 10})
    crypto = ETH_RE.findall(blob) + BTC_RE.findall(blob)
    attachments: list[str] = []
    for line in headers.splitlines():
        if line.lower().startswith("content-disposition:") and "filename=" in line.lower():
            attachments.append(line.split("filename=", 1)[-1].strip().strip('";'))
    return ArtifactSet(
        urls=urls,
        emails=emails,
        domains=sorted(domains),
        phones=phones,
        crypto_addresses=sorted(set(crypto)),
        attachments=attachments,
    )


def _clean_urls(urls: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for url in urls:
        url = url.rstrip(".,;:!?")
        if url.lower().startswith("www."):
            url = "https://" + url
        key = url.lower()
        if key not in seen:
            seen.add(key)
            out.append(url)
    return out


def _host(url: str) -> str:
    from urllib.parse import urlparse

    parsed = urlparse(url if "://" in url else "https://" + url)
    return parsed.hostname or ""
