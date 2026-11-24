from __future__ import annotations

import json

from openminion import tool

from dossier.extract import extract_artifacts
from dossier.inspect_headers import inspect_headers
from dossier.inspect_text import inspect_text
from dossier.inspect_url import inspect_url
from dossier.memory import bundle_cases, file_case, search_cases
from dossier.pipeline import inspect_body
from dossier.schemas import DossierReport


def _dump(value) -> str:
    if hasattr(value, "model_dump"):
        value = value.model_dump()
    elif isinstance(value, list) and value and hasattr(value[0], "model_dump"):
        value = [item.model_dump() for item in value]
    return json.dumps(value, indent=2)


@tool(name="extract_artifacts", min_scope="READ_ONLY", idempotent=True,
      description="Extract URLs, email addresses, domains, phones, and crypto addresses from a message. Does not fetch anything.")
def extract_artifacts_tool(source_text: str, headers: str = "") -> str:
    return _dump(extract_artifacts(source_text, headers))


@tool(name="inspect_url", min_scope="READ_ONLY", idempotent=True,
      description="Analyse one URL string for lookalikes, punycode, sensitive paths, and other lure signs. Never fetches the destination.")
def inspect_url_tool(url: str) -> str:
    return _dump(inspect_url(url))


@tool(name="inspect_text", min_scope="READ_ONLY", idempotent=True,
      description="Look for urgency, secrecy, payment, seed-phrase, authority, and AI-voice language in message text.")
def inspect_text_tool(source_text: str) -> str:
    return _dump(inspect_text(source_text))


@tool(name="inspect_headers", min_scope="READ_ONLY", idempotent=True,
      description="Check From, Reply-To, Return-Path, and display-name mismatches in raw email headers.")
def inspect_headers_tool(raw_headers: str) -> str:
    return _dump(inspect_headers(raw_headers))


@tool(name="compile_dossier", min_scope="READ_ONLY", idempotent=True,
      description="Run the full deterministic inspection of a message body and optional headers and return a scored evidence dossier.")
def compile_dossier_tool(source_text: str, headers: str = "") -> str:
    return _dump(inspect_body(source_text, headers))


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
      description="Write a local case note for a human reviewer. This is the only write tool and should be approved first.")
def file_case_tool(source_text: str, headers: str = "", summary: str = "") -> str:
    report: DossierReport = inspect_body(source_text, headers)
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
