from __future__ import annotations

import json
from contextvars import ContextVar

from openminion import tool

from dossier.extract import extract_artifacts
from dossier.inspect_headers import inspect_headers
from dossier.inspect_text import inspect_text
from dossier.inspect_url import inspect_url
from dossier.memory import bundle_cases, file_case, search_cases
from dossier.pipeline import inspect_body
from dossier.schemas import DossierReport

# Set by the inspect engine so forced/empty tool calls still see the message.
# Small local models often invoke compile_dossier with no arguments, or with
# aliases such as input_text / text instead of source_text.
_CURRENT_SOURCE: ContextVar[tuple[str, str]] = ContextVar(
    "dossier_current_source", default=("", "")
)


def set_current_source(source_text: str = "", headers: str = "") -> None:
    _CURRENT_SOURCE.set((source_text or "", headers or ""))


def clear_current_source() -> None:
    _CURRENT_SOURCE.set(("", ""))


def _resolve_source(*candidates: str, headers: str = "") -> tuple[str, str]:
    for item in candidates:
        if item and item.strip():
            current_headers = headers or _CURRENT_SOURCE.get()[1]
            return item, current_headers
    return _CURRENT_SOURCE.get()


def _dump(value) -> str:
    if hasattr(value, "model_dump"):
        value = value.model_dump()
    elif isinstance(value, list) and value and hasattr(value[0], "model_dump"):
        value = [item.model_dump() for item in value]
    return json.dumps(value, indent=2)


@tool(name="extract_artifacts", min_scope="READ_ONLY", idempotent=True,
      description="Extract URLs, email addresses, domains, phones, and crypto addresses from a message. Does not fetch anything. source_text may be omitted to reuse the current inspect message.")
def extract_artifacts_tool(source_text: str = "", headers: str = "", text: str = "", input_text: str = "") -> str:
    body, hdrs = _resolve_source(source_text, text, input_text, headers=headers)
    return _dump(extract_artifacts(body, hdrs))


@tool(name="inspect_url", min_scope="READ_ONLY", idempotent=True,
      description="Analyse one URL string for lookalikes, punycode, sensitive paths, and other lure signs. Never fetches the destination.")
def inspect_url_tool(url: str) -> str:
    return _dump(inspect_url(url))


@tool(name="inspect_text", min_scope="READ_ONLY", idempotent=True,
      description="Look for urgency, secrecy, payment, seed-phrase, authority, and AI-voice language in message text. source_text may be omitted to reuse the current inspect message.")
def inspect_text_tool(source_text: str = "", text: str = "", input_text: str = "") -> str:
    body, _ = _resolve_source(source_text, text, input_text)
    return _dump(inspect_text(body))


@tool(name="inspect_headers", min_scope="READ_ONLY", idempotent=True,
      description="Check From, Reply-To, Return-Path, and display-name mismatches in raw email headers.")
def inspect_headers_tool(raw_headers: str = "", headers: str = "") -> str:
    blob = raw_headers or headers or _CURRENT_SOURCE.get()[1]
    return _dump(inspect_headers(blob))


@tool(name="compile_dossier", min_scope="READ_ONLY", idempotent=True,
      description="Run the full deterministic inspection of a message body and optional headers and return a scored evidence dossier. source_text may be omitted to reuse the current inspect message.")
def compile_dossier_tool(source_text: str = "", headers: str = "", text: str = "", input_text: str = "") -> str:
    body, hdrs = _resolve_source(source_text, text, input_text, headers=headers)
    return _dump(inspect_body(body, hdrs))


@tool(name="recall_cases", min_scope="READ_ONLY", idempotent=True,
      description="Search previously filed local case notes by a short query.")
def recall_cases_tool(query: str) -> str:
    records = search_cases(query)
    return _dump([r.model_dump() for r in records])


@tool(name="export_memory_bundle", min_scope="READ_ONLY", idempotent=True,
      description="Export filed case notes as an OpenMinion MemoryBundle JSON snapshot.")
def export_memory_bundle_tool() -> str:
    return bundle_cases().to_json()


@tool(name="file_case", min_scope="WRITE_SAFE", idempotent=False,
      description="Write a local case note for a human reviewer. This is the only write tool and should be approved first. source_text may be omitted to reuse the current inspect message.")
def file_case_tool(source_text: str = "", headers: str = "", summary: str = "", text: str = "", input_text: str = "") -> str:
    body, hdrs = _resolve_source(source_text, text, input_text, headers=headers)
    report: DossierReport = inspect_body(body, hdrs)
    record = file_case(report, summary=summary or None)
    return _dump(record)


READ_TOOLS = [
    extract_artifacts_tool,
    inspect_url_tool,
    inspect_text_tool,
    inspect_headers_tool,
    compile_dossier_tool,
    recall_cases_tool,
    export_memory_bundle_tool,
]

WRITE_TOOLS = [file_case_tool]
ALL_TOOLS = READ_TOOLS + WRITE_TOOLS
