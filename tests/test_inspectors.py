from pathlib import Path

from dossier.extract import extract_artifacts, load_source
from dossier.inspect_headers import inspect_headers
from dossier.inspect_text import inspect_text
from dossier.inspect_url import WATCHED_BRANDS, inspect_url
from dossier.pipeline import inspect_item

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "samples"


def test_extracts_urls_and_emails_from_payroll_lure():
    body, headers = load_source(FIXTURES / "payroll_lure.eml")
    arts = extract_artifacts(body, headers)
    assert any("acme-payroll-secure.xyz" in u for u in arts.urls)
    assert "payroll.helpdesk@gmail.com" in arts.emails
    assert "mail-acme-secure.xyz" in arts.domains


def test_header_mismatch_and_display_spoof():
    _, headers = load_source(FIXTURES / "payroll_lure.eml")
    findings = inspect_headers(headers)
    ids = {s.id for s in findings.signals}
    assert "header.reply_to_mismatch" in ids
    assert "header.display_name_spoof" in ids
    assert findings.from_address.endswith("@gmail.com")


def test_text_patterns_on_wallet_lure():
    text = (FIXTURES / "wallet_seed_lure.txt").read_text()
    ids = {s.id for s in inspect_text(text)}
    assert "text.seed_harvest" in ids
    assert "text.crypto_payment" in ids
    assert "text.ai_voice" in ids
    assert "text.qr_wallet" in ids


def test_ai_persona_leak_and_secrecy():
    text = (FIXTURES / "ai_persona_leak.txt").read_text()
    ids = {s.id for s in inspect_text(text)}
    assert "text.llm_leak" in ids
    assert "text.gift_card" in ids
    assert "text.secrecy" in ids


def test_url_lookalike_punycode_and_sensitive_query():
    sigs = inspect_url("https://paypa1.com/login?token=abc")
    ids = {s.id for s in sigs}
    assert "url.brand_lookalike" in ids
    assert "url.sensitive_path" in ids
    assert "url.sensitive_query" in ids

    puny = inspect_url("https://xn--pypal-4ve.com/signin")
    assert any(s.id == "url.punycode" for s in puny)

    ip = inspect_url("http://192.0.2.18/wallet")
    ids = {s.id for s in ip}
    assert "url.ip_host" in ids
    assert "url.cleartext" in ids

    official = inspect_url("https://www.paypal.com/signin")
    assert not any(s.id == "url.brand_lookalike" for s in official)


def test_official_watched_brands_are_not_flagged():
    for _brand, domains in WATCHED_BRANDS.items():
        for domain in domains:
            sigs = inspect_url(f"https://{domain}/")
            assert not any(s.id == "url.brand_lookalike" for s in sigs), domain


def test_pipeline_scores_payroll_high():
    report = inspect_item(path=FIXTURES / "payroll_lure.eml")
    assert report.severity == "high"
    assert report.mode == "deterministic"
    assert "evidence" in report.disclaimer.lower()
    assert any(s.id == "header.reply_to_mismatch" for s in report.signals)
    assert any(s.id.startswith("url.") for s in report.signals)


def test_benign_meeting_is_not_high():
    report = inspect_item(path=FIXTURES / "benign_meeting.txt")
    assert report.severity in {"info", "low"}
    assert report.signals == [] or all(s.severity in {"info", "low"} for s in report.signals)
