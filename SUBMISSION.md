# Draft BUIDL and PR — Dossier (Cortensor Hackathon #5)

Paste or adapt this on DoraHacks and in a pull request to [cortensor/community-projects](https://github.com/cortensor/community-projects) when submitting. Do not submit until the GitHub repository is public. A short demo video and the live Ollama `llama3.2:3b` command outputs are already in `demo/` — record a slightly longer 1–5 minute screen capture of the same commands if the organiser wants a talking walkthrough, but do not present echo as the model run.

**Deadline (DoraHacks cutoff):** 19 December 2026, 07:59 UTC — 07:59 Europe/London, 08:59 Africa/Lagos.

The organiser’s written build window ends 18 December 2026, Pacific Time, which is the same cutoff (end of 18 Dec PT is 07:59 UTC on 19 Dec). Use the DoraHacks timestamp as the exact close.

**Track:** Default Track (the hackathon does not use multiple tracks).

**Prize note:** Awards are discretionary, paid in $COR equivalent, 50% liquid and 50% in a one-month Cortensor staking lock. Cortensor may require identity checks before payout.

---

## Title

Dossier — an OpenMinion evidence clerk for AI-enabled phishing lures

## Tagline

Inspect a message, collect evidence, and leave the verdict to a human reviewer.

## Description

Dossier is a small OpenMinion 0.1 agent that inspects a pasted message or `.eml` file and returns a typed evidence brief. It flags lookalike and punycode URLs, seed-phrase and gift-card language, From / Reply-To mismatches, and claims of an AI-cloned voice or a leaked model persona. It never fetches the destination URL and never claims that a crime occurred.

The inspectors are deterministic Python tools, unit-tested, and always available. `--agent` wraps them in the released OpenMinion `0.1.22` SDK: decorated tools, a forced compile step for a reliable demo, structured `DossierReport` output, a durable session, a bounded URL subagent, a peer handoff, approval-gated case filing, a portable `MemoryBundle`, and runtime diagnostics. If the model, schema, freshness gate, or provider fails, the deterministic brief is kept.

A live Ollama `llama3.2:3b` `--agent` run of the payroll lure and the benign control is recorded under `demo/output/`. Both reports are `agent-validation-fallback`: the model and tools ran, and the brief was kept because the final model text was not valid `DossierReport` JSON. That is intentional and documented.

This is new work, written for Cortensor Hackathon #5.

## OpenMinion SDK workflow

1. Deterministic inspectors extract artifacts and score signals.
2. `Agent` is constructed on a shared `APIRuntime` with `@tool` inspectors.
3. A `subagent` reviews URL strings; a `Handoff` exposes the same specialist to the coordinator.
4. The coordinator returns a Pydantic `DossierReport`.
5. `file_case` is the only write and goes through `approval_callback`.
6. Case notes export as `MemoryBundle`. `dossier doctor` records runtime diagnostics.

Details: `docs/BUILDING_BLOCKS_TESTED.md` and `docs/WHAT_WE_LEARNED.md`.

## Demo

Script: `demo/walkthrough.md`. Still frames and a short video (`demo/walkthrough.mp4`, ~21s) show the live Ollama run. Command outputs:

- `demo/output/payroll-lure.agent.json` / `.txt` / `.meta.json` — session `dossier-ollama-payroll-3`, severity high, 10 signals, 346s. URL specialist called `inspect_url`. Coordinator wrote markdown, not JSON.
- `demo/output/benign-meeting.agent.json` / `.txt` / `.meta.json` — session `dossier-ollama-benign-2`, severity info, ~244s. The model called `compile_dossier`, `extract_artifacts`, `inspect_headers`, and `inspect_text`.

Reproduce: `./scripts/setup-ollama.sh llama3.2:3b`, then `python -m dossier inspect --agent --timeout 600 --session <fresh-id> fixtures/samples/payroll_lure.eml`.

Locally: `make test` also remains green without a model (20 tests).

## GitHub

Private during development: `https://github.com/onepolymath/dossier`  
Make the repository **public** immediately before submitting (the hackathon requires a public source repo; this project is MIT).

Also open a PR to `cortensor/community-projects` linking the public repo, the video, and the two notes above. The official “fork, clone, and star OpenMinion / follow on X” steps are left for the submitter.

## Submitter checklist (Yusuf)

1. Review the private repository, this draft, the two notes in `docs/`, and the recorded outputs in `demo/output/`.
2. The free local Ollama run is already done (`llama3.2:3b`, CPU). You can re-run it, or optionally add a Portal run if you have a `CORTENSOR_API_KEY` (gitignored `.env`, `./scripts/setup-portal.sh`). Do not spend money on a paid API. Do not commit a key. If you record a longer 1–5 minute screen-capture, show the payroll lure, the evidence, the honest `agent-validation-fallback` line, and the benign control — not an echo run.
3. Consider filing the freshness-classifier and forced-tool default notes in `docs/WHAT_WE_LEARNED.md` with the OpenMinion team as product feedback (not a security report). Only attempt a fix PR after they acknowledge it.
4. Register on DoraHacks for Cortensor Hackathon #5 if you have not already.
5. Star / follow the official OpenMinion and Cortensor GitHub (and X, if you want to follow the written participate steps). This was not done during the private build.
6. Make `onepolymath/dossier` public.
7. Create the DoraHacks BUIDL with the text above, the public repo, and the video. Open the `cortensor/community-projects` PR with the same links.
8. Submit before **19 December 2026, 07:59 UTC** (07:59 Europe/London, 08:59 Africa/Lagos).
9. Do not use paid APIs, do not deploy anything that costs money, and do not spend on boosts.
