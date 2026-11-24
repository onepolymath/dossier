from __future__ import annotations

from pathlib import Path

from dossier.extract import extract_artifacts, load_headers_and_body_from_text, load_source
from dossier.inspect_headers import inspect_headers
from dossier.inspect_text import inspect_text
from dossier.inspect_url import inspect_url
from dossier.schemas import DossierReport, Signal
from dossier.score import score_report


def inspect_item(*, path: str | Path | None = None, text: str | None = None) -> DossierReport:
    """Deterministic inspection used by both the CLI and the OpenMinion tools."""
    if path is not None:
        body, headers = load_source(path=path)
    else:
        body, headers = load_headers_and_body_from_text(text or "")
    return inspect_body(body, headers)


def inspect_body(body: str, headers: str = "") -> DossierReport:
    artifacts = extract_artifacts(body, headers)
    signals: list[Signal] = []
    signals.extend(inspect_headers(headers).signals)
    signals.extend(inspect_text(body))
    for url in artifacts.urls:
        signals.extend(inspect_url(url))
    return score_report(signals, artifacts, mode="deterministic")
