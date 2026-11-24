# Draft BUIDL and PR — Dossier (Cortensor Hackathon #5)

Paste or adapt this on DoraHacks and in a pull request to [cortensor/community-projects](https://github.com/cortensor/community-projects) when submitting. Do not submit until the GitHub repository is public, a 1–5 minute demo video of a real model-backed run is attached, and the live command output is current.

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

The inspectors are deterministic Python tools, unit-tested, and always available. `--agent` wraps them in the released OpenMinion `0.1.22` SDK: decorated tools, a forced compile step for a reliable demo, structured `DossierReport` output, a durable session, a bounded URL subagent, a peer handoff, approval-gated case filing, a portable `MemoryBundle`, and runtime diagnostics. If the model, schema, or provider fails, the deterministic brief is kept.

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

Script: `demo/walkthrough.md`. Still frames and a short video are in `demo/`. Locally: `make test` and `python -m dossier inspect fixtures/samples/payroll_lure.eml`. After Ollama or Portal is configured, add `--agent` and record the model-backed run (required for submission).

## GitHub

Private during development: `https://github.com/onepolymath/dossier`  
Make the repository **public** immediately before submitting (the hackathon requires a public source repo; this project is MIT).

Also open a PR to `cortensor/community-projects` linking the public repo, the video, and the two notes above. The official “fork, clone, and star OpenMinion / follow on X” steps are left for the submitter.

## Submitter checklist (Yusuf)

1. Review the private repository, this draft, and the two notes in `docs/`.
2. For the required model-backed demo, either install free local Ollama (`ollama pull llama3.1`, then `./scripts/setup-ollama.sh`) or, if you have Portal access, put `CORTENSOR_API_KEY` in the gitignored `.env` and run `./scripts/setup-portal.sh`. Do not spend money on a paid API if a free path works. Do not commit the key.
3. Run `python -m dossier inspect --agent fixtures/samples/payroll_lure.eml` and record a 1–5 minute video (inspect a lure, show evidence, optionally file a case after approval, show the benign control).
4. If a reproducible OpenMinion bug appears, file it with the team (privately if security-sensitive) and only attempt a fix PR after they acknowledge it.
5. Register on DoraHacks for Cortensor Hackathon #5 if you have not already.
6. Star / follow the official OpenMinion and Cortensor GitHub (and X, if you want to follow the written participate steps). This was not done during the private build.
7. Make `onepolymath/dossier` public.
8. Create the DoraHacks BUIDL with the text above, the public repo, and the video. Open the `cortensor/community-projects` PR with the same links.
9. Submit before **19 December 2026, 07:59 UTC** (07:59 Europe/London, 08:59 Africa/Lagos).
10. Do not use paid APIs, do not deploy anything that costs money, and do not spend on boosts.
