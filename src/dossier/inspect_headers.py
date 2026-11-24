from __future__ import annotations

import re
from email.utils import parseaddr

from dossier.schemas import HeaderFindings, Signal


def inspect_headers(raw_headers: str) -> HeaderFindings:
    fields: dict[str, str] = {}
    current = None
    for line in (raw_headers or "").splitlines():
        if not line.strip():
            continue
        if line[0] in " \t" and current:
            fields[current] += " " + line.strip()
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            current = key.strip().lower()
            fields[current] = value.strip()

    from_display, from_address = parseaddr(fields.get("from", ""))
    _, reply_to = parseaddr(fields.get("reply-to", ""))
    _, return_path = parseaddr(fields.get("return-path", "") or fields.get("return_path", ""))
    subject = fields.get("subject", "")

    signals: list[Signal] = []
    if from_address and reply_to and _domain(from_address) != _domain(reply_to):
        signals.append(Signal(
            id="header.reply_to_mismatch",
            title="Reply-To domain does not match the From address",
            severity="high",
            detail=f"From {from_address} replies to {reply_to}",
            evidence=f"From: {fields.get('from','')}; Reply-To: {fields.get('reply-to','')}",
            source="header",
        ))
    if from_address and return_path and _domain(return_path) and _domain(from_address) != _domain(return_path):
        signals.append(Signal(
            id="header.return_path_mismatch",
            title="Return-Path domain does not match the From address",
            severity="medium",
            detail=f"From {from_address}; Return-Path {return_path}",
            evidence=fields.get("return-path", ""),
            source="header",
        ))
    if from_display and from_address:
        display_l = from_display.lower()
        if _looks_like_org(display_l) and _looks_free_mail(from_address):
            signals.append(Signal(
                id="header.display_name_spoof",
                title="Display name looks official but the mailbox is a consumer address",
                severity="high",
                detail=f"{from_display} <{from_address}>",
                evidence=fields.get("from", ""),
                source="header",
            ))
    return HeaderFindings(
        from_display=from_display,
        from_address=from_address,
        reply_to=reply_to,
        subject=subject,
        return_path=return_path,
        signals=signals,
    )


def _domain(addr: str) -> str:
    return addr.split("@", 1)[-1].lower() if "@" in addr else ""


def _looks_like_org(display: str) -> bool:
    return bool(re.search(
        r"(?i)\b(payroll|hr|human resources|it support|helpdesk|billing|invoice|accounts payable|ceo|cfo|director|security team|tax)\b",
        display,
    ))


def _looks_free_mail(addr: str) -> bool:
    domain = _domain(addr)
    return domain in {
        "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com",
        "aol.com", "proton.me", "mail.com",
    }
