#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FRAMES = ROOT / "frames"
W, H = 1920, 1080
PAPER = (244, 239, 230)
INK = (28, 25, 21)
MUTED = (107, 98, 88)
RULE = (216, 207, 192)
ACCENT = (122, 62, 29)
CREAM = (232, 224, 210)
HIGH = (122, 62, 29)
INFO = (70, 92, 70)

SERIF_SB = "/usr/share/fonts/truetype/sand-box/custom/Source Serif Pro/SourceSerifPro-Semibold.ttf"
SERIF_RG = "/usr/share/fonts/truetype/sand-box/custom/Source Serif Pro/SourceSerifPro-Regular.ttf"
INTER = "/usr/share/fonts/truetype/sand-box/google/Inter/Inter-VariableFont_opsz,wght.ttf"
MONO = "/usr/share/fonts/truetype/sand-box/google/IBM Plex Mono/IBMPlexMono-Regular.ttf"


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    if name == "serif":
        return ImageFont.truetype(SERIF_SB, size)
    if name == "serif-reg":
        return ImageFont.truetype(SERIF_RG, size)
    if name == "mono":
        return ImageFont.truetype(MONO, size)
    f = ImageFont.truetype(INTER, size)
    try:
        f.set_variation_by_name("Medium" if name == "sans-med" else "Regular")
    except OSError:
        pass
    return f


def canvas():
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((120, 80, W - 120, H - 80), 8, fill=PAPER, outline=RULE, width=2)
    return img, draw


def footer(draw, page: str) -> None:
    draw.line((180, H - 160, W - 180, H - 160), fill=RULE, width=1)
    draw.text((180, H - 140), "Dossier  ·  an OpenMinion evidence clerk", font=font("sans", 22), fill=MUTED)
    draw.text((W - 180, H - 140), page, font=font("sans", 22), fill=MUTED, anchor="ra")


def save(img, name: str) -> None:
    FRAMES.mkdir(parents=True, exist_ok=True)
    path = FRAMES / name
    img.save(path, "PNG")
    print(path)


def frame_title():
    img, draw = canvas()
    draw.text((180, 200), "Dossier", font=font("serif", 96), fill=INK)
    draw.text((180, 330), "An evidence clerk for AI-enabled phishing lures.", font=font("serif-reg", 36), fill=INK)
    for i, line in enumerate([
        "Inspect a message. Collect evidence. Leave the verdict to a human reviewer.",
        "Never fetches a destination URL. Built on the OpenMinion 0.1.22 Python SDK.",
        "Deterministic inspectors in CI; live Ollama llama3.2:3b agent demo on this box.",
    ]):
        draw.text((180, 460 + i * 56), line, font=font("sans", 30), fill=MUTED)
    footer(draw, "01  /  07")
    save(img, "01-title.png")


def signal_block(draw, y, items, color=HIGH):
    for title, detail in items:
        draw.text((180, y), "HIGH" if color == HIGH else "NOTE", font=font("sans-med", 22), fill=color)
        draw.text((280, y), title, font=font("serif", 30), fill=INK)
        draw.text((280, y + 40), detail, font=font("sans", 24), fill=MUTED)
        y += 100
    return y


def frame_payroll():
    img, draw = canvas()
    draw.text((180, 140), "Payroll lure", font=font("serif", 60), fill=INK)
    draw.text((180, 220), "severity  high   ·   mode  agent-validation-fallback   ·   llama3.2:3b", font=font("sans-med", 22), fill=ACCENT)
    signal_block(draw, 300, [
        ("Display-name spoof", "“Acme Payroll” is sending from a gmail.com mailbox"),
        ("Reply-To mismatch", "Replies would go to mail-acme-secure.xyz"),
        ("Credential harvest", "Asks the reader to enter a password on a lookalike login URL"),
        ("Secrecy", "“Please do not tell HR about this request”"),
    ])
    draw.text((180, 740), "URL specialist called inspect_url. Coordinator answered in markdown, not JSON.", font=font("sans", 24), fill=MUTED)
    draw.text((180, 784), "session  dossier-ollama-payroll-3    346s on CPU    brief kept, not invented", font=font("mono", 22), fill=MUTED)
    footer(draw, "02  /  07")
    save(img, "02-payroll.png")


def frame_wallet():
    img, draw = canvas()
    draw.text((180, 140), "Wallet lure", font=font("serif", 60), fill=INK)
    draw.text((180, 220), "severity  high   ·   mode  deterministic", font=font("sans-med", 24), fill=ACCENT)
    signal_block(draw, 300, [
        ("AI-cloned voice claim", "“This is a recording of your account manager”"),
        ("Seed-phrase harvest", "Asks for a 12-word phrase on metamask-secure.top"),
        ("Lookalike host", "Resembles MetaMask, but it is not metamask.io"),
        ("Crypto payment", "A bitcoin address is included as a “gas fee”"),
    ])
    footer(draw, "03  /  07")
    save(img, "03-wallet.png")


def frame_benign():
    img, draw = canvas()
    draw.text((180, 140), "Benign control", font=font("serif", 60), fill=INK)
    draw.text((180, 220), "severity  info   ·   mode  agent-validation-fallback   ·   llama3.2:3b", font=font("sans-med", 22), fill=INFO)
    draw.text((180, 330), "No lure-shaped evidence signals were found in this item.", font=font("serif-reg", 34), fill=INK)
    draw.text((180, 420), "The model called compile_dossier, extract_artifacts,", font=font("sans", 28), fill=MUTED)
    draw.text((180, 466), "inspect_headers, and inspect_text, then said:", font=font("sans", 28), fill=MUTED)
    draw.text((180, 530), "“No strong lure signals were found. This is not a clean bill of health.”", font=font("serif-reg", 28), fill=INK)
    draw.text((180, 620), "That prose is not a valid DossierReport, so the deterministic brief is kept.", font=font("sans", 24), fill=MUTED)
    draw.text((180, 700), "session  dossier-ollama-benign-2    ~244s on CPU", font=font("mono", 22), fill=MUTED)
    draw.text((180, 760), "Dossier is a clerk, not a judge.", font=font("serif", 32), fill=ACCENT)
    footer(draw, "04  /  07")
    save(img, "04-benign.png")


def frame_blocks():
    img, draw = canvas()
    draw.text((180, 140), "OpenMinion building blocks", font=font("serif", 56), fill=INK)
    items = [
        "Agent + shared APIRuntime",
        "@tool inspectors (READ_ONLY) and file_case (WRITE_SAFE)",
        "forced_tools, typed DossierReport, durable session_id",
        "subagent URL reviewer and peer Handoff",
        "approval_callback, MemoryBundle, dossier doctor",
    ]
    y = 280
    for item in items:
        draw.text((180, y), "•", font=font("serif", 36), fill=ACCENT)
        draw.text((230, y), item, font=font("sans", 32), fill=INK)
        y += 80
    footer(draw, "05  /  07")
    save(img, "05-blocks.png")


def frame_tests():
    img, draw = canvas()
    draw.text((180, 140), "Twenty tests, all passing", font=font("serif", 56), fill=INK)
    tests = [
        "test_extracts_urls_and_emails",
        "test_header_mismatch_and_spoof",
        "test_text_patterns_on_wallet",
        "test_ai_persona_leak_and_secrecy",
        "test_url_lookalike_and_punycode",
        "test_official_brands_not_flagged",
        "test_pipeline_scores_payroll_high",
        "test_benign_meeting_is_not_high",
        "test_compile_and_url_tools",
        "test_file_recall_and_memory_bundle",
        "test_cli_inspect_pretty_and_json",
        "test_freshness_and_tool_defaults",
    ]
    col1, col2 = tests[:6], tests[6:]
    y0 = 280
    for i, name in enumerate(col1):
        draw.text((180, y0 + i * 70), "PASS", font=font("sans-med", 22), fill=ACCENT)
        draw.text((280, y0 + i * 70), name, font=font("mono", 24), fill=INK)
    for i, name in enumerate(col2):
        draw.text((980, y0 + i * 70), "PASS", font=font("sans-med", 22), fill=ACCENT)
        draw.text((1080, y0 + i * 70), name, font=font("mono", 24), fill=INK)
    footer(draw, "06  /  07")
    save(img, "06-tests.png")


def frame_model():
    img, draw = canvas()
    draw.text((180, 140), "Live Ollama run, honestly reported", font=font("serif", 52), fill=INK)
    lines = [
        "Provider: Ollama 0.40.18    Model: llama3.2:3b (Q4_K_M) on CPU",
        "Both fixture inspects used --agent and a real local model. No paid API.",
        "The URL specialist and the benign coordinator called real @tool inspectors.",
        "OpenMinion’s freshness classifier labelled a payroll lure as “sports”, and",
        "llama3.2:3b answered in prose, not typed JSON. Dossier kept the brief.",
        "That fallback is the intended behaviour — never invent a structured result.",
        "Outputs: demo/output/*.agent.json  +  .txt  +  .meta.json  +  slim logs.",
    ]
    y = 260
    for line in lines:
        draw.text((180, y), line, font=font("sans", 28), fill=INK)
        y += 56
    footer(draw, "07  /  07")
    save(img, "07-model-step.png")


def main():
    frame_title()
    frame_payroll()
    frame_wallet()
    frame_benign()
    frame_blocks()
    frame_tests()
    frame_model()


if __name__ == "__main__":
    main()
