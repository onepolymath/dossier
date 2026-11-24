from __future__ import annotations

import re

from dossier.schemas import Signal

PATTERNS: list[tuple[str, str, str, re.Pattern[str]]] = [
    ("text.urgency", "Urgent or threatening deadline", "medium",
     re.compile(r"(?i)\b(immediately|urgent|within \d+ hours?|act now|final (notice|warning)|account will be (closed|suspended|terminated)|limited time)\b")),
    ("text.secrecy", "Asks the reader to keep the request secret", "high",
     re.compile(r"(?i)\b(do not tell|don't tell|keep this (confidential|secret)|between us|do not mention|don't mention (this|it) to)\b")),
    ("text.gift_card", "Asks for payment by gift card", "high",
     re.compile(r"(?i)\b(gift ?card|google play card|apple itunes|steam card|vanilla visa)\b")),
    ("text.crypto_payment", "Asks for cryptocurrency payment or a wallet transfer", "high",
     re.compile(r"(?i)\b(bitcoin|btc|usdt|usdc|ethereum|wallet address|send (the )?crypto|connect your wallet|gas fee)\b")),
    ("text.seed_harvest", "Asks for a recovery phrase, seed, or private key", "high",
     re.compile(r"(?i)\b(seed phrase|recovery phrase|secret recovery|mnemonic|private key|12[- ]word|24[- ]word)\b")),
    ("text.credential_harvest", "Asks the reader to submit a password, OTP, or login", "high",
     re.compile(r"(?i)\b(confirm your (password|credentials|login)|enter your (password|one[- ]time|otp|verification code)|verify (your )?account|update your (payment|billing) (details|method))\b")),
    ("text.wire", "Asks for a wire or unexpected payment change", "high",
     re.compile(r"(?i)\b(wire (the|this)? money|new (bank )?account|change(?:d)? (the )?bank details|routing number)\b")),
    ("text.authority", "Impersonates a senior colleague or official", "medium",
     re.compile(r"(?i)\b(i am (the )?(ceo|cfo|director|manager)|this is your (ceo|boss|manager)|as (the )?commissioner|tax (authority|office|refund))\b")),
    ("text.ai_voice", "Claims an AI-cloned or recorded voice / likeness", "high",
     re.compile(r"(?i)\b(ai[- ]?(cloned|generated|voice)|voice clone|this is a recording of|deepfake|cloned (my|the) voice|looks like me on video)\b")),
    ("text.llm_leak", "Text leaks a generative-model assistant persona", "medium",
     re.compile(r"(?i)\b(as an ai (language )?model|i(?: am|'m) (chatgpt|a large language model)|i cannot (access|browse) the internet)\b")),
    ("text.qr_wallet", "Pushes a QR code or 'scan to connect wallet' step", "medium",
     re.compile(r"(?i)\b(scan (the|this)? qr|qr code|walletconnect|connect wallet to (claim|verify|receive))\b")),
    ("text.remote_access", "Asks the reader to install remote-access software", "high",
     re.compile(r"(?i)\b(anydesk|teamviewer|allow (me|us) (remote )?access|install (this )?(tool|software) so i can)\b")),
]


def inspect_text(source_text: str) -> list[Signal]:
    signals: list[Signal] = []
    text = source_text or ""
    for id_, title, severity, pattern in PATTERNS:
        match = pattern.search(text)
        if match:
            span = _snippet(text, match.start(), match.end())
            signals.append(Signal(id=id_, title=title, severity=severity, detail=match.group(0), evidence=span, source="text"))
    if _looks_like_generated_padding(text):
        signals.append(Signal(
            id="text.generic_padding",
            title="Unusually generic, padded phrasing often seen in generated lures",
            severity="low",
            detail="Repeated polite filler with little concrete context",
            evidence=_snippet(text, 0, 180),
            source="text",
        ))
    return signals


def _looks_like_generated_padding(text: str) -> bool:
    lower = text.lower()
    markers = [
        "i hope this message finds you well",
        "please do not hesitate to reach out",
        "kindly proceed at your earliest convenience",
        "thank you for your prompt attention to this matter",
        "we value you as a member of our community",
    ]
    hits = sum(1 for m in markers if m in lower)
    return hits >= 2


def _snippet(text: str, start: int, end: int, pad: int = 60) -> str:
    a = max(0, start - pad)
    b = min(len(text), end + pad)
    snippet = text[a:b].replace("\n", " ").strip()
    if a > 0:
        snippet = "…" + snippet
    if b < len(text):
        snippet = snippet + "…"
    return snippet
