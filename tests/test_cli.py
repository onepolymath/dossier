from pathlib import Path

from dossier.cli import main

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "samples"


def test_cli_inspect_pretty(capsys):
    code = main(["inspect", str(FIXTURES / "payroll_lure.eml")])
    assert code == 0
    out = capsys.readouterr().out
    assert "severity high" in out
    assert "Evidence" in out
    assert "human reviewer" in out.lower() or "evidence brief" in out.lower()


def test_cli_inspect_json(capsys):
    code = main(["inspect", "--format", "json", str(FIXTURES / "benign_meeting.txt")])
    assert code == 0
    out = capsys.readouterr().out
    assert '"severity"' in out
    assert '"mode": "deterministic"' in out


def test_cli_requires_input(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    code = main(["inspect"])
    assert code == 2
    assert "Provide a file path" in capsys.readouterr().err
