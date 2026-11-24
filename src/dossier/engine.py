from __future__ import annotations

import json
import os
from collections.abc import Callable
from typing import Any

from openminion import (
    APIRuntime,
    Agent,
    AgentOutputValidationError,
    Handoff,
    ProviderError,
    TurnTimeoutError,
    subagent,
)

from dossier.paths import config_path, ensure_local_home
from dossier.pipeline import inspect_item
from dossier.prompts import INSTRUCTIONS, URL_SPECIALIST
from dossier.schemas import DossierReport
from dossier.tools import ALL_TOOLS, READ_TOOLS, inspect_url_tool

ApprovalFn = Callable[[str, dict[str, Any], str], bool]


def inspect_with_optional_agent(
    *,
    path: str | None = None,
    text: str | None = None,
    use_agent: bool = False,
    session_id: str = "dossier-demo",
    file_case: bool = False,
    approval_callback: ApprovalFn | None = None,
    timeout_seconds: float = 180,
) -> DossierReport:
    """Always run the deterministic inspectors; optionally wrap them in OpenMinion."""
    report = inspect_item(path=path, text=text)
    if not use_agent:
        return report
    ensure_local_home()
    cfg = config_path()
    if not cfg.exists():
        report.summary += " OpenMinion agent mode was requested but no local config was found; ran deterministically."
        report.mode = "deterministic-fallback"
        return report

    agent_id = os.environ.get("DOSSIER_AGENT_ID") or None
    model = os.environ.get("DOSSIER_MODEL") or None
    auto = os.environ.get("DOSSIER_AUTO_APPROVE", "").strip().lower() in {"1", "true", "yes"}
    callback = approval_callback or (_auto_approve if auto else _prompt_approval)
    tools = ALL_TOOLS if file_case else READ_TOOLS
    force_compile = os.environ.get("DOSSIER_FORCE_TOOLS", "1").strip() not in {"0", "false", "no"}
    forced = ["compile_dossier"] if force_compile else None

    runtime = APIRuntime.from_config_path(str(cfg))
    try:
        with Agent(
            name="url-specialist",
            instructions=URL_SPECIALIST,
            runtime=runtime,
            agent_id=agent_id,
            model=model,
            tools=[inspect_url_tool],
            session_id=f"{session_id}-urls",
        ) as specialist:
            with Agent(
                name="dossier",
                instructions=INSTRUCTIONS,
                output_type=DossierReport,
                runtime=runtime,
                agent_id=agent_id,
                model=model,
                tools=tools,
                forced_tools=forced,
                handoffs=[Handoff(target=specialist, name="transfer_to_url_specialist",
                                  description="Hand a URL-inspection question to the URL specialist.")],
                session_id=session_id,
            ) as coordinator:
                url_notes = ""
                if report.artifacts.urls:
                    child = subagent(
                        coordinator,
                        name="url-reviewer",
                        instructions=URL_SPECIALIST,
                        tools=[inspect_url_tool],
                        timeout_seconds=int(timeout_seconds),
                    )
                    child_result = child.run(
                        "Inspect these URL strings. Do not fetch them:\n"
                        + "\n".join(report.artifacts.urls),
                        timeout_seconds=timeout_seconds,
                    )
                    url_notes = child_result.text or ""
                message = _build_prompt(report, path=path, text=text, file_case=file_case, url_notes=url_notes)
                result = coordinator.run(
                    message,
                    timeout_seconds=timeout_seconds,
                    approval_callback=callback,
                )
                return _merge_result(report, result)
    except AgentOutputValidationError as exc:
        raw = getattr(exc, "raw_text", "") or ""
        if _looks_like_prompt_echo(raw):
            report.summary += " The provider echoed the prompt instead of returning a dossier; keeping the deterministic brief."
            report.mode = "agent-echo-fallback"
            return report
        report.summary += f" The model reply failed schema validation ({exc}). Keeping the deterministic brief."
        report.mode = "agent-validation-fallback"
        return report
    except TurnTimeoutError as exc:
        report.summary += f" The OpenMinion turn timed out ({exc}). Keeping the deterministic brief."
        report.mode = "agent-timeout-fallback"
        return report
    except ProviderError as exc:
        report.summary += f" The model provider failed ({exc.code}: {exc.message}). Keeping the deterministic brief."
        report.mode = "agent-provider-fallback"
        return report
    finally:
        runtime.close()


def _looks_like_prompt_echo(text: str) -> bool:
    """Echo (and some stub providers) replay the prompt; that is not a model answer."""
    t = (text or "").lstrip().lower()
    return t.startswith("openminion:") or t.startswith("inspect this message")


def _merge_result(report: DossierReport, result) -> DossierReport:
    raw_text = getattr(result, "text", "") or ""
    if _looks_like_prompt_echo(raw_text):
        report.summary += " The provider echoed the prompt instead of returning a dossier; keeping the deterministic brief."
        report.mode = "agent-echo-fallback"
        report.session_id = getattr(result, "session_id", None)
        report.run_id = getattr(result, "run_id", None)
        return report
    output = result.output if isinstance(getattr(result, "output", None), DossierReport) else None
    if output is None and getattr(result, "text", ""):
        try:
            output = DossierReport.model_validate_json(result.text)
        except Exception:
            output = None
    if output is None:
        report.summary += " The model ran but did not return a valid DossierReport; keeping the deterministic brief."
        report.mode = "agent-untyped"
        report.session_id = getattr(result, "session_id", None)
        report.run_id = getattr(result, "run_id", None)
        return report
    output.mode = "openminion-agent"
    output.session_id = result.session_id
    output.run_id = result.run_id
    if not output.signals:
        output.signals = report.signals
    if not output.artifacts.urls and report.artifacts.urls:
        output.artifacts = report.artifacts
    if not output.recommendation:
        output.recommendation = report.recommendation
    return output


def _build_prompt(
    report: DossierReport,
    *,
    path: str | None,
    text: str | None,
    file_case: bool,
    url_notes: str,
) -> str:
    source = f"file {path}" if path else "pasted text"
    body = text if text is not None and path is None else ""
    if path and not body:
        from pathlib import Path as P
        try:
            body = P(path).read_text(encoding="utf-8", errors="replace")[:4000]
        except OSError:
            body = ""
    action = (
        " File a local case note with file_case after you finish if the severity is medium or high."
        if file_case
        else ""
    )
    extra = f"\n\nURL specialist notes:\n{url_notes[:3000]}" if url_notes else ""
    return (
        f"Inspect this message ({source}) and return a DossierReport.\n\n"
        f"Deterministic preview (you may confirm or refine with tools):\n"
        f"{report.model_dump_json(indent=2)}\n\n"
        f"Source excerpt:\n{body[:4000]}{extra}\n\n"
        f"Use compile_dossier or the inspectors. Do not visit URLs.{action}"
    )


def _auto_approve(tool_name: str, args: dict[str, Any], approval_id: str) -> bool:
    return "file_case" in tool_name


def _prompt_approval(tool_name: str, args: dict[str, Any], approval_id: str) -> bool:
    print(f"\nOpenMinion is asking to run {tool_name} (approval {approval_id}).")
    print(json.dumps(args, indent=2)[:2000])
    try:
        answer = input("Allow this exact action? [yes/no] ").strip().lower()
    except EOFError:
        return False
    return answer in {"y", "yes"}
