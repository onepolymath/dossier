import json
from pathlib import Path

import pytest
from openminion import MemoryBundle

from dossier import memory as memory_mod
from dossier.pipeline import inspect_item
from dossier.tools import (
    compile_dossier_tool,
    export_memory_bundle_tool,
    extract_artifacts_tool,
    file_case_tool,
    inspect_url_tool,
    recall_cases_tool,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "samples"


@pytest.fixture()
def isolated_cases(tmp_path, monkeypatch):
    monkeypatch.setattr(memory_mod, "CASES_DIR", tmp_path / "cases")
    return tmp_path


def test_compile_and_url_tools_return_json():
    text = (FIXTURES / "wallet_seed_lure.txt").read_text()
    payload = json.loads(compile_dossier_tool(text))
    assert payload["severity"] == "high"
    assert payload["signals"]
    url_payload = json.loads(inspect_url_tool("https://metamask-secure.top/wallet?seed=confirm"))
    ids = {row["id"] for row in url_payload}
    assert "url.brand_lookalike" in ids
    arts = json.loads(extract_artifacts_tool(text))
    assert arts["urls"]


def test_file_recall_and_memory_bundle(isolated_cases):
    text = (FIXTURES / "ai_persona_leak.txt").read_text()
    record = json.loads(file_case_tool(text, summary="gift-card lure"))
    assert record["id"]
    hits = json.loads(recall_cases_tool("gift-card"))
    assert any(row["id"] == record["id"] for row in hits)
    bundle = MemoryBundle.from_json(export_memory_bundle_tool())
    assert bundle.metadata["count"] == 1
    assert bundle.items[0]["id"] == record["id"]


def test_case_roundtrip_matches_report(isolated_cases):
    report = inspect_item(path=FIXTURES / "payroll_lure.eml")
    saved = memory_mod.file_case(report, summary="payroll")
    listed = memory_mod.list_cases()
    assert listed[0].id == saved.id
    assert listed[0].severity == "high"
