from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Severity = Literal["info", "low", "medium", "high"]


class Signal(BaseModel):
    """One piece of evidence, not a verdict."""

    id: str
    title: str
    severity: Severity
    detail: str
    evidence: str = ""
    source: str = "text"


class ArtifactSet(BaseModel):
    urls: list[str] = Field(default_factory=list)
    emails: list[str] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    phones: list[str] = Field(default_factory=list)
    crypto_addresses: list[str] = Field(default_factory=list)
    attachments: list[str] = Field(default_factory=list)


class HeaderFindings(BaseModel):
    from_display: str = ""
    from_address: str = ""
    reply_to: str = ""
    subject: str = ""
    return_path: str = ""
    signals: list[Signal] = Field(default_factory=list)


class DossierReport(BaseModel):
    """Typed result for a single inspection."""

    severity: Severity
    summary: str
    recommendation: str
    signals: list[Signal] = Field(default_factory=list)
    artifacts: ArtifactSet = Field(default_factory=ArtifactSet)
    disclaimer: str = (
        "This is an evidence brief for a human reviewer. It is not a finding of "
        "fraud, a legal conclusion, or a substitute for reporting channels your "
        "organisation already uses."
    )
    mode: str = "deterministic"
    session_id: str | None = None
    run_id: str | None = None
    cases_filed: list[str] = Field(default_factory=list)


class CaseRecord(BaseModel):
    id: str
    created_at: str
    severity: Severity
    summary: str
    path: str
