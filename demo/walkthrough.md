# Dossier walkthrough

A two-minute path used for the still frames and the demo video. The recorded `--agent` outputs live under `demo/output/`.

1. **Title.** Dossier is an OpenMinion evidence clerk for AI-enabled phishing lures. It does not visit links and it does not declare a verdict.
2. **A payroll lure.** `python -m dossier inspect --agent --session dossier-ollama-payroll-3 --timeout 600 fixtures/samples/payroll_lure.eml` — severity high, mode `agent-validation-fallback`, Ollama `llama3.2:3b`. Display-name spoof, Reply-To mismatch, password harvest, secrecy, a lookalike login URL. The URL specialist called `inspect_url`. The coordinator answered in markdown, not JSON; the deterministic brief was kept (346s on CPU).
3. **A wallet lure.** `python -m dossier inspect fixtures/samples/wallet_seed_lure.txt` — seed-phrase harvest, a MetaMask lookalike, an AI-cloned voice claim. Shown on the deterministic path.
4. **A benign control.** `python -m dossier inspect --agent --session dossier-ollama-benign-2 --timeout 600 fixtures/samples/benign_meeting.txt` — severity info, mode `agent-validation-fallback`. The model called `compile_dossier`, `extract_artifacts`, `inspect_headers`, and `inspect_text`, then said “No strong lure signals were found. This is not a clean bill of health.” That prose is not a valid `DossierReport`, so the brief is kept.
5. **How OpenMinion is used.** Tools, session, subagent, handoff, approval-gated `file_case`, MemoryBundle, diagnostics.
6. **Tests.** `make test` — inspectors, tools (including empty/aliased `compile_dossier` arguments), CLI, echo guard, and freshness-fallback detection. Twenty tests, all passing.
7. **The live model run.** Ollama `0.40.18`, `llama3.2:3b` Q4_K_M on CPU, no paid API. Findings about the freshness classifier and forced-tool defaults are in `docs/WHAT_WE_LEARNED.md`.

The samples are fictional and written for this demo.
