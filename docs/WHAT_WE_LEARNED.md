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

## Bugs

No original, security-sensitive OpenMinion defect was confirmed well enough to file against the security policy. The items above are product-feedback notes, not exploit reports. If a later live Portal or Ollama run produces a reproducible runtime bug, it should be reported as an issue with version, environment, steps, expected versus actual behaviour, and logs with secrets removed — and only then, after acknowledgement, considered for a fix PR (the bonus path).

## Environment used

- OpenMinion `0.1.22` from PyPI
- Python 3.13 (also intended to run on 3.11+)
- Deterministic inspectors and tests: no network, no provider key
- Echo: used only for local config / doctor wiring
- Cortensor Portal and Ollama: scripts ready; not run in this build because Portal needs access and Ollama was not installed on the machine
