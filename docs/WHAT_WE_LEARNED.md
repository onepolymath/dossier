# What We Learned

Actionable feedback from building Dossier on OpenMinion `0.1.22`.

## What worked

- The published programmatic API matches the documentation well: `Agent`, `@tool`, `output_type`, `session_id`, `subagent`, `Handoff`, `ProviderError`, `TurnTimeoutError`, and `AgentOutputValidationError` are all importable from the package root or `openminion.api` as described.
- Decorated tools remain ordinary Python functions, so the inspectors can be unit-tested without a model. That is what makes the project reproducible in CI.
- `APIRuntime.from_config_path` plus a shared `runtime=` is a clean way to run a coordinator and a specialist in one process.
- `--storage-location config` together with `OPENMINION_HOME` keeps state inside the project. That is easy to gitignore and easy to explain.

## Rough edges and suggestions

1. **`config init --provider` and `setup --list-providers` advertise different sets.** Init offers `echo`, `openai`, `anthropic`, `claude`, `openrouter`, `cerebras`, `groq`, `ollama`, and `cortensor`. Setup also offers `cortensor-portal`, `cortensor-router`, and several other hosts. A new builder following only `config init` will not see Portal. Suggestion: list the same preset IDs in both commands, or have `config init --provider` print a pointer to `setup --list-providers`.

2. **The default `config init --storage-location home` path is easy to miss.** It writes to `~/.openminion/state/openminion.db`. For a project meant to be copied, the documented default for application work should be the data-root / config location, with the home location called out as a machine-wide option.

3. **Echo is documented as insufficient for a qualifying demo, which is correct, but the runtime still presents it as a provider.** A one-line warning from `openminion doctor --check-turn` when the selected provider is echo (“this does not call a model and cannot prove tool use”) would save judges and builders a cycle.

4. **`forced_tools` is essential for a first demo and easy to overlook.** Without it, a small local model may answer in prose and never call the inspector. The quickstart mentions this; it would help to show it in the first Cortensor hackathon example as well.

5. **Structured output is brittle on small models.** `output_type=` is the right API, and raising `AgentOutputValidationError` with `raw_text` is helpful. A documented “best-effort parse + fallback” pattern (which Dossier implements) would reduce broken demos.

6. **Portal is optional, but the happy path still assumes a key.** Official docs already say participants without access will not be penalized, and that Portal can be slow, is not retried, and can return `router_v4_correlation_mismatch` under concurrent use of one session. Carrying that warning into `setup --provider cortensor-portal` output would set expectations at the moment of configuration.

7. **Path isolation is good, once you find `OPENMINION_HOME` and `--home-root`.** The CLI help mentions `--home-root` / `--data-root`; a short “application-owned home” paragraph in the Python SDK quickstart would have shortened this project’s setup.


8. **Echo can look like a successful structured run if the prompt already contains a JSON preview.** On a short benign sample, echo replayed the prompt and `output_type` sometimes appeared to succeed because the deterministic `DossierReport` JSON was already in the message. On a longer lure, the echoed prefix (`openminion: Inspect this message...`) failed JSON validation and Dossier correctly fell back. Dossier now treats a reply that starts with `openminion:` or `Inspect this message` as an echo, not a model answer (`agent-echo-fallback`). Suggestion: echo should wrap or tag its output so it cannot be mistaken for a validated structured result.


9. **OpenMinion’s freshness classifier can mis-route an inspect as live sports or finance.** On `llama3.2:3b`, `brain.freshness.classified` labelled the payroll lure `domain=sports` and the benign meeting `domain=finance`. In one earlier run the coordinator then refused with “I couldn’t provide a grounded current sports answer because Missing exact-date evidence…”. On the recorded runs the mode was `local_only`, so the turn continued, but the payroll coordinator still took the `respond` path and never called `compile_dossier`. Dossier now recognises the sports-refusal text as `agent-freshness-fallback`. Suggestion: skip or constrain freshness classification when `output_type` is set, when `forced_tools` is set, or when the user prompt is clearly a local document inspect. A 3B classifier is not reliable enough for this gate.

10. **`forced_tools=["compile_dossier"]` still needs default arguments.** The benign coordinator did call `compile_dossier`, but the first attempt used `{}`. OpenMinion then raised `source_text Field required` and the 3B model looped on aliases (`input_text`, nested `args`). Dossier now treats `source_text` as optional, accepts `text` / `input_text` aliases, and fills the current inspect message from a context variable set by the engine. After that change, `compile_dossier`, `extract_artifacts`, `inspect_headers`, and `inspect_text` all completed on the benign control. Suggestion: document that forced tools must have defaults, or have the runtime bind forced calls to the current user message.

11. **`output_type` is still brittle on a 3B model, even after tools succeed.** The payroll coordinator wrote a markdown “DossierReport” (and correctly counted the 10 signals). The benign coordinator, after a successful `compile_dossier` that returned `severity: info`, finished with the prose “No strong lure signals were found. This is not a clean bill of health.” — the right recommendation, but not valid JSON. Dossier keeps the deterministic brief (`agent-validation-fallback`) and does not treat that prose as a structured model result. Suggestion: when `output_type` is set, a finalisation step should prefer the last successful tool payload that already matches the schema over a prose trailer.

12. **Switching providers can leave a session bound to the previous agent.** After `setup-echo.sh`, the default session `dossier-demo` belonged to agent `openminion`. Configuring Ollama as agent `dossier` and reusing that session raised `TurnRequestError`. Dossier now falls back with `agent-runtime-fallback` and a hint to pass a fresh `--session`. Suggestion: allow a session to be rebound, or auto-open a new session when the agent id changes.

13. **The official `ollama pull` failed on this host because a registry redirect resolved to a non-public address** (`redirect target not allowed: …r2.cloudflarestorage.com resolves to non-public 198.18.0.1`). Downloading the same blob via the signed URL with curl succeeded, hashes matched, and `ollama list` then showed `llama3.2:3b`. Worth knowing for builders behind similar resolvers.

## Bugs

No original, security-sensitive OpenMinion defect was confirmed well enough to file against the security policy. The items above are product-feedback notes, not exploit reports. The freshness mis-route and forced-tool empty-argument failure are reproducible on OpenMinion `0.1.22` with `llama3.2:3b` and are reported here as product feedback, not as a security issue. A later Portal run should still be filed separately if it produces a new defect, with version, environment, steps, expected versus actual behaviour, and logs with secrets removed — and only then, after acknowledgement, considered for a fix PR (the bonus path).

## Environment used

- OpenMinion `0.1.22` from PyPI
- Python 3.13 (also intended to run on 3.11+)
- Deterministic inspectors and tests: no network, no provider key
- Echo: used only for local config / doctor wiring
- Cortensor Portal: still not called; it needs a `CORTENSOR_API_KEY`
- Ollama `0.40.18` on this box, project-local models at `.ollama/models`, model `llama3.2:3b` (Q4_K_M). `dossier inspect --agent` was run for real on `payroll_lure.eml` and `benign_meeting.txt`. Outputs live under `demo/output/`.
