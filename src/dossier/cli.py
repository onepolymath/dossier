from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dossier import __version__
from dossier.engine import inspect_with_optional_agent
from dossier.memory import bundle_cases, file_case, list_cases
from dossier.paths import ensure_local_home
from dossier.schemas import DossierReport


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="dossier",
        description="Compile an evidence dossier for a suspected phishing or social-engineering lure.",
    )
    parser.add_argument("--version", action="version", version=f"dossier {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    inspect = sub.add_parser("inspect", help="Inspect a message file or stdin")
    inspect.add_argument("path", nargs="?", help="Path to a .eml or text file (stdin if omitted)")
    inspect.add_argument("--text", help="Inspect this text instead of a file")
    inspect.add_argument("--agent", action="store_true", help="Wrap the inspection in an OpenMinion agent turn")
    inspect.add_argument("--session", default="dossier-demo", help="OpenMinion session id")
    inspect.add_argument("--file-case", action="store_true", help="Ask the agent to file a local case note")
    inspect.add_argument("--save-case", action="store_true", help="File a local case note from the deterministic report")
    inspect.add_argument("--format", choices=["pretty", "json"], default="pretty")
    inspect.add_argument("--timeout", type=float, default=180)

    cases = sub.add_parser("cases", help="List filed local case notes")
    cases.add_argument("--bundle", action="store_true", help="Print an OpenMinion MemoryBundle of the cases")

    sub.add_parser("doctor", help="Dump OpenMinion runtime diagnostics")

    args = parser.parse_args(argv)
    ensure_local_home()

    if args.cmd == "inspect":
        return _cmd_inspect(args)
    if args.cmd == "cases":
        return _cmd_cases(args)
    if args.cmd == "doctor":
        from dossier.diagnostics import collect_diagnostics

        print(json.dumps(collect_diagnostics(), indent=2, default=str))
        return 0
    return 1


def _cmd_inspect(args) -> int:
    text = args.text
    path = args.path
    if text is None and path is None:
        if sys.stdin.isatty():
            print("Provide a file path, --text, or pipe a message on stdin.", file=sys.stderr)
            return 2
        text = sys.stdin.read()
    report = inspect_with_optional_agent(
        path=path,
        text=text,
        use_agent=args.agent,
        session_id=args.session,
        file_case=args.file_case,
        timeout_seconds=args.timeout,
    )
    if args.save_case:
        record = file_case(report)
        report.cases_filed.append(record.id)
    if args.format == "json":
        print(report.model_dump_json(indent=2))
    else:
        print(_pretty(report))
    return 0


def _cmd_cases(args) -> int:
    if args.bundle:
        print(bundle_cases().to_json())
        return 0
    records = list_cases()
    if not records:
        print("No case notes yet.")
        return 0
    for record in records:
        print(f"{record.id}\t{record.severity}\t{record.summary}")
    return 0


def _pretty(report: DossierReport) -> str:
    lines = [
        f"Dossier  ·  severity {report.severity}  ·  mode {report.mode}",
        report.summary,
        "",
        "Recommendation: " + report.recommendation,
        "",
    ]
    if report.signals:
        lines.append("Evidence")
        for sig in report.signals:
            lines.append(f"  [{sig.severity}] {sig.title}")
            if sig.detail:
                lines.append(f"          {sig.detail}")
            if sig.evidence and sig.evidence != sig.detail:
                lines.append(f"          quote: {sig.evidence}")
        lines.append("")
    arts = report.artifacts
    if any((arts.urls, arts.emails, arts.domains, arts.crypto_addresses)):
        lines.append("Artifacts")
        if arts.urls:
            lines.append("  urls: " + ", ".join(arts.urls))
        if arts.emails:
            lines.append("  emails: " + ", ".join(arts.emails))
        if arts.domains:
            lines.append("  domains: " + ", ".join(arts.domains))
        if arts.crypto_addresses:
            lines.append("  crypto: " + ", ".join(arts.crypto_addresses))
        lines.append("")
    if report.session_id:
        lines.append(f"session: {report.session_id}")
    if report.run_id:
        lines.append(f"run: {report.run_id}")
    if report.cases_filed:
        lines.append("filed: " + ", ".join(report.cases_filed))
    lines.append("")
    lines.append(report.disclaimer)
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
