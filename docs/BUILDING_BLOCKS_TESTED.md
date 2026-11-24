# Building Blocks Tested

What Dossier used from OpenMinion `0.1.22`, what worked, and what did not.

| Building block | How it is used | Result |
| --- | --- | --- |
| Agent execution | `Agent` / `APIRuntime` in `src/dossier/engine.py` | Worked. One shared `APIRuntime` is passed to both agents so a handoff does not open a second runtime. `runtime=` and `config_path=` are mutually exclusive, as documented. |
| Decorated tools | `@tool` inspectors in `src/dossier/tools.py` | Worked. Callables stay directly invokable in tests. `min_scope="READ_ONLY"` and `idempotent=True` are set on inspectors; `file_case` is `WRITE_SAFE` and not idempotent. A bare `@tool` would be classified as a write, so metadata was declared from the real effects. |
| Forced tools | `forced_tools=["compile_dossier"]` by default | Worked as a demo guard so a weak model still exercises the inspector. Set `DOSSIER_FORCE_TOOLS=0` to leave the choice to the model. |
| Typed output | `output_type=DossierReport` | Worked when the model returns schema-shaped JSON. On `AgentOutputValidationError`, Dossier keeps the deterministic brief and records `agent-validation-fallback` rather than inventing fields. |
| Sessions | Stable `session_id` (default `dossier-demo`) | Worked as an API. History is isolated per id. |
| Permissions / approval | `approval_callback(tool_name, args, approval_id)` on `file_case` | Wired. Interactive prompt in the CLI; `DOSSIER_AUTO_APPROVE=1` only for tests. |
| Delegation | `subagent(...)` for URL review, plus `Handoff(target=specialist)` | Implemented against the public API. Requires a real tool-capable model to show the model choosing the transfer tool. |
| Memory | Local case notes exported as `MemoryBundle` | Worked in tests: `to_json` / `from_json` round-trip. |
| Diagnostics | `dossier doctor` calls `runtime_posture`, `capability_report`, `tool_inventory_report`, `scheduler_readiness` | Available once a local config exists. Echo config is enough to exercise the surfaces; it is not a model-backed run. |
| Models / Portal | Ollama (free, local) and optional Cortensor Portal | Ollama `0.40.18` was installed on the build machine; `llama3.2:3b` ran `--agent` inspects of `payroll_lure.eml` and `benign_meeting.txt` (see `demo/output/`). Portal was not called: it needs a `CORTENSOR_API_KEY`. Participants without Portal access are not penalized. |
| Skills, tasks, scheduling | Not used | Left out on purpose. The workflow is one useful inspection, not a feature tour. |

See also [What We Learned](WHAT_WE_LEARNED.md).
