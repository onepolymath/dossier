from __future__ import annotations

import json
from typing import Any

from openminion import APIRuntime

from dossier.paths import config_path, ensure_local_home


def collect_diagnostics() -> dict[str, Any]:
    """Exercise OpenMinion diagnostic surfaces against the local runtime."""
    ensure_local_home()
    cfg = config_path()
    report: dict[str, Any] = {
        "config_path": str(cfg),
        "config_exists": cfg.exists(),
    }
    if not cfg.exists():
        report["error"] = "No OpenMinion config yet. Run scripts/setup-echo.sh or configure a model provider."
        return report
    runtime = APIRuntime.from_config_path(str(cfg))
    try:
        for name, fn in (
            ("runtime_posture", lambda: runtime.runtime_posture()),
            ("capability_report", lambda: runtime.capability_report()),
            ("tool_inventory_report", lambda: runtime.tool_inventory_report(readiness=False)),
            ("scheduler_readiness", lambda: runtime.scheduler_readiness()),
        ):
            try:
                report[name] = _safe(fn())
            except Exception as exc:
                report[name] = {"error": f"{type(exc).__name__}: {exc}"}
        try:
            report["compile_dossier_schema"] = _safe(runtime.tool_schema_report(tool_name="compile_dossier"))
        except Exception as exc:
            report["compile_dossier_schema"] = {"error": f"{type(exc).__name__}: {exc}"}
    finally:
        runtime.close()
    return report


def _safe(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "__dict__") and not isinstance(value, dict):
        try:
            json.dumps(value.__dict__)
            return value.__dict__
        except TypeError:
            return repr(value)
    try:
        json.dumps(value)
        return value
    except TypeError:
        return repr(value)
