from __future__ import annotations

import re
from urllib.parse import parse_qs, unquote, urlparse

from dossier.schemas import Signal

# Common brands that lures impersonate. This is a heuristic list, not an
# affiliation, partnership, or official watchlist.
WATCHED_BRANDS = {
    "paypal": ["paypal.com"],
    "microsoft": ["microsoft.com", "office.com", "live.com", "outlook.com"],
    "apple": ["apple.com", "icloud.com"],
    "google": ["google.com", "gmail.com", "withgoogle.com"],
    "amazon": ["amazon.com", "amazonaws.com"],
    "metamask": ["metamask.io"],
    "binance": ["binance.com"],
    "coinbase": ["coinbase.com"],
    "wellsfargo": ["wellsfargo.com"],
    "irs": ["irs.gov"],
    "hmrc": ["gov.uk"],
    "dhl": ["dhl.com"],
    "fedex": ["fedex.com"],
}

SUSPICIOUS_TLDS = {
    "xyz", "top", "click", "zip", "mov", "gq", "tk", "ml", "cf", "ga",
    "cfd", "sbs", "rest", "country", "icu", "cyou", "buzz", "work",
}

SHORTENERS = {
    "bit.ly", "t.co", "tinyurl.com", "goo.gl", "ow.ly", "is.gd", "cutt.ly",
    "rebrand.ly", "lnkd.in",
}

SENSITIVE_PATH = re.compile(
    r"(?i)(login|signin|sign-in|verify|wallet|seed|mnemonic|recover|password|passwd|otp|2fa|billing|invoice|walletconnect|connect-wallet|reset|unlock)"
)
SENSITIVE_QUERY = re.compile(
    r"(?i)(token|password|passwd|seed|mnemonic|secret|otp|session|auth|key|redirect|next|url|continue)"
)

# A few Cyrillic/Greek lookalikes frequently used in homograph lures.
HOMOGLYPHS = str.maketrans(
    {
        "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "у": "y", "х": "x",
        "і": "i", "ѕ": "s", "ԁ": "d",
        "Α": "A", "ο": "o", "ρ": "p",
    }
)


def inspect_url(url: str) -> list[Signal]:
    """Analyse a URL string without fetching it."""
    signals: list[Signal] = []
    raw = url.strip()
    parsed = urlparse(raw if "://" in raw else "https://" + raw)
    host = (parsed.hostname or "").lower()
    userinfo = parsed.netloc.split("@", 1)[0] if "@" in parsed.netloc else ""

    if not host:
        signals.append(_sig("url.invalid", "URL could not be parsed", "medium", raw, raw))
        return signals

    if re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", host):
        signals.append(_sig("url.ip_host", "Host is a raw IP address", "high", host, raw))

    if userinfo and userinfo.lower() not in {host, ""}:
        signals.append(_sig("url.userinfo", "URL embeds a userinfo (credential) prefix", "high", parsed.netloc, raw))

    if parsed.scheme.lower() not in {"http", "https", ""}:
        signals.append(_sig("url.odd_scheme", "Unusual URL scheme", "medium", parsed.scheme, raw))

    if parsed.scheme.lower() == "http":
        signals.append(_sig("url.cleartext", "Link uses unencrypted http", "low", parsed.scheme, raw))

    labels = host.split(".")
    tld = labels[-1] if labels else ""
    if tld in SUSPICIOUS_TLDS:
        signals.append(_sig("url.odd_tld", f"Unusual TLD .{tld} on a lure-shaped link", "low", host, raw))

    if host in SHORTENERS or any(host.endswith("." + s) for s in SHORTENERS):
        signals.append(_sig("url.shortener", "URL shortener hides the eventual destination", "medium", host, raw))

    if "xn--" in host:
        signals.append(_sig("url.punycode", "Internationalised (punycode) host can hide lookalike characters", "high", host, raw))

    folded = host.translate(HOMOGLYPHS)
    if folded != host:
        signals.append(_sig("url.homoglyph", "Host uses lookalike Unicode characters", "high", host, raw))

    path = unquote(parsed.path or "")
    if SENSITIVE_PATH.search(path) or SENSITIVE_PATH.search(parsed.netloc):
        signals.append(_sig("url.sensitive_path", "Path or host suggests a login, wallet, or recovery flow", "medium", path or host, raw))

    query = parse_qs(parsed.query, keep_blank_values=True)
    sensitive_keys = [k for k in query if SENSITIVE_QUERY.search(k)]
    if sensitive_keys:
        signals.append(_sig("url.sensitive_query", "Query string asks for a secret or a redirect", "medium", ", ".join(sensitive_keys), raw))

    for brand, official in WATCHED_BRANDS.items():
        if _impersonates(host, folded, brand, official):
            official_list = ", ".join(official)
            signals.append(_sig(
                "url.brand_lookalike",
                f"Host resembles '{brand}' but is not one of {official_list}",
                "high",
                host,
                raw,
            ))
            break

    return signals


def _impersonates(host: str, folded: str, brand: str, official: list[str]) -> bool:
    if any(host == d or host.endswith("." + d) for d in official):
        return False
    candidates = {brand, folded.split(".")[0], host.split(".")[0]}
    for label in {host, folded, *host.split("."), *folded.split(".")}:
        compact = re.sub(r"[^a-z0-9]", "", label.lower())
        if not compact:
            continue
        if brand in compact and not any(compact == re.sub(r"[^a-z0-9]", "", d) or compact.endswith(re.sub(r"[^a-z0-9]", "", d)) for d in official):
            # paypal-secure.example.com, paypa1.com, paypaI.com
            return True
        if _levenshtein(compact, brand) == 1 and len(brand) >= 5:
            return True
    return False


def _levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if abs(len(a) - len(b)) > 1:
        return 2
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            ins, delete, sub = cur[j - 1] + 1, prev[j] + 1, prev[j - 1] + (ca != cb)
            cur.append(min(ins, delete, sub))
        prev = cur
    return prev[-1]


def _sig(id_: str, title: str, severity: str, detail: str, evidence: str) -> Signal:
    return Signal(id=id_, title=title, severity=severity, detail=detail, evidence=evidence, source="url")
