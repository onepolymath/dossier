# Dossier walkthrough

A two-minute path used for the still frames and the demo video.

1. **Title.** Dossier is an OpenMinion evidence clerk for AI-enabled phishing lures. It does not visit links and it does not declare a verdict.
2. **A payroll lure.** `python -m dossier inspect fixtures/samples/payroll_lure.eml` — display-name spoof, Reply-To mismatch, password harvest, secrecy, a lookalike login URL.
3. **A wallet lure.** `python -m dossier inspect fixtures/samples/wallet_seed_lure.txt` — seed-phrase harvest, a MetaMask lookalike, an AI-cloned voice claim.
4. **A benign control.** `python -m dossier inspect fixtures/samples/benign_meeting.txt` — no lure-shaped signals, still not a clean bill of health.
5. **How OpenMinion is used.** Tools, session, subagent, handoff, approval-gated `file_case`, MemoryBundle, diagnostics.
6. **Tests.** `make test` — inspectors, tools, CLI, and agent-without-config fallback.
7. **Model-backed run.** After Ollama or Portal is configured, repeat step 2 with `--agent` and show the `openminion-agent` mode line.

The samples are fictional and written for this demo.
