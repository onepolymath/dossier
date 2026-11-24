from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from openminion import MemoryBundle

from dossier.schemas import CaseRecord, DossierReport

ROOT = Path(__file__).resolve().parents[2]
CASES_DIR = ROOT / "var" / "cases"


def file_case(report: DossierReport, *, summary: str | None = None) -> CaseRecord:
    CASES_DIR.mkdir(parents=True, exist_ok=True)
    case_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]
    path = CASES_DIR / f"{case_id}.json"
    record = CaseRecord(
        id=case_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        severity=report.severity,
        summary=summary or report.summary,
        path=str(path),
    )
    payload = {
        "case": record.model_dump(),
        "report": report.model_dump(),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return record


def list_cases() -> list[CaseRecord]:
    if not CASES_DIR.exists():
        return []
    records: list[CaseRecord] = []
    for path in sorted(CASES_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        records.append(CaseRecord.model_validate(data["case"]))
    return records


def search_cases(query: str) -> list[CaseRecord]:
    needle = query.lower().strip()
    if not needle:
        return list_cases()
    hits = []
    for record in list_cases():
        blob = (record.summary + " " + record.id + " " + record.severity).lower()
        path = Path(record.path)
        if path.exists():
            blob += " " + path.read_text(encoding="utf-8").lower()
        if needle in blob:
            hits.append(record)
    return hits


def bundle_cases() -> MemoryBundle:
    items = []
    for record in list_cases():
        items.append(
            {
                "id": record.id,
                "kind": "dossier.case",
                "severity": record.severity,
                "summary": record.summary,
                "path": record.path,
                "created_at": record.created_at,
            }
        )
    return MemoryBundle(
        items=items,
        metadata={"source": "dossier", "count": len(items)},
    )
