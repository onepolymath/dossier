from pathlib import Path

from dossier.engine import inspect_with_optional_agent

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "samples"


def test_agent_mode_without_config_falls_back(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENMINION_HOME", str(tmp_path / "home"))
    monkeypatch.setenv("OPENMINION_DATA_ROOT", str(tmp_path / "home" / ".openminion"))
    report = inspect_with_optional_agent(
        path=str(FIXTURES / "payroll_lure.eml"),
        use_agent=True,
    )
    assert report.severity == "high"
    assert report.mode == "deterministic-fallback"
    assert "no local config" in report.summary.lower()


def test_deterministic_mode_ignores_missing_provider():
    report = inspect_with_optional_agent(
        path=str(FIXTURES / "wallet_seed_lure.txt"),
        use_agent=False,
    )
    assert report.mode == "deterministic"
    assert report.severity == "high"
    assert any(s.id == "text.seed_harvest" for s in report.signals)


def test_prompt_echo_is_detected():
    from dossier.engine import _looks_like_prompt_echo

    assert _looks_like_prompt_echo("openminion: Inspect this message (file x)")
    assert _looks_like_prompt_echo("Inspect this message (pasted text) and return a DossierReport.")
    assert not _looks_like_prompt_echo('{"severity": "high", "summary": "ok"}')


from dossier.engine import _looks_like_freshness_refusal, _fallback_from_model_text
from dossier.pipeline import inspect_item


def test_freshness_refusal_is_detected():
    raw = (
        "I couldn't provide a grounded current sports answer because "
        "Missing exact-date evidence for an exact-date freshness answer. "
        "Please retry with live data available so I can answer with sources and an exact date."
    )
    assert _looks_like_freshness_refusal(raw)
    report = inspect_item(text="hello, see you at 3pm for the standup.")
    out = _fallback_from_model_text(report, raw=raw, session_id="dossier-ollama-test")
    assert out.mode == "agent-freshness-fallback"
    assert out.session_id == "dossier-ollama-test"
    assert "freshness classifier" in out.summary
