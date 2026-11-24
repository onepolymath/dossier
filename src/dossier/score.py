from __future__ import annotations

from dossier.schemas import DossierReport, Severity, Signal

_RANK = {"info": 0, "low": 1, "medium": 2, "high": 3}

_RECOMMENDATIONS = {
    "high": "Do not follow the links, install software, or send funds. Preserve the original message and ask a human reviewer or your usual reporting channel to take a look.",
    "medium": "Treat the message as untrusted until a human reviewer confirms the sender and the request through a second, known channel.",
    "low": "Worth a second look. Check the sender and any links before acting.",
    "info": "No strong lure signals were found. This is not a clean bill of health.",
}


def score_report(signals: list[Signal], artifacts, *, mode: str = "deterministic") -> DossierReport:
    unique: list[Signal] = []
    seen: set[str] = set()
    for sig in signals:
        key = f"{sig.id}:{sig.detail}:{sig.evidence}"
        if key in seen:
            continue
        seen.add(key)
        unique.append(sig)
    unique.sort(key=lambda s: (-_RANK[s.severity], s.id))
    severity: Severity = "info"
    for sig in unique:
        if _RANK[sig.severity] > _RANK[severity]:
            severity = sig.severity
    if unique:
        titles = "; ".join(s.title for s in unique[:3])
        summary = f"{len(unique)} evidence signal(s), highest severity {severity}: {titles}."
    else:
        summary = "No lure-shaped evidence signals were found in this item."
    return DossierReport(
        severity=severity,
        summary=summary,
        recommendation=_RECOMMENDATIONS[severity],
        signals=unique,
        artifacts=artifacts,
        mode=mode,
    )
