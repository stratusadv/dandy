# Per-instance mid-flight LLM config change

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-11-19-08

## End State

Any `Bot` (LlmServiceMixin child) instance can change its full LLM configuration mid-conversation through one consistent path — `bot.llm.set_config('THINKING', model='x', temperature=0.2)` (named entry switch + field overrides) or `bot.llm.config = LlmConfig('THINKING')` (direct assignment) — covering every setting (HOST, PORT, API_KEY, MODEL, CONTEXT_SIZE, PROMPT_RETRY_COUNT, and all OPTIONS) without touching the in-flight conversation; from the next request on, all LLM traffic from that instance (direct prompts, tool-loop rounds, the Agent's compaction window, and Decision calls) uses the new config. Proven by new hermetic tests plus a green suite, lint, import contracts, and the strict docs build.

## Observable Concern

The mid-flight swap must regenerate the connector's request body from the new config while preserving the live `MessageHistory` object, and a `host` override must keep `Url.parsed_url` fresh (it is derived from `host` at construction and drives the wire URL via `Url.to_str()`) — otherwise the conversation is silently truncated on the next request, or the request silently goes to the old/wrong endpoint. The completion test asserts actual wire bytes (host, port, model, bearer token) captured from a mocked `HttpConnector.request_to_response` after a switch.

## Current State

Verified by reading the code (no `set_config`/`change_config`/`switch_config` API exists anywhere in `dandy/` or `tests/`):

- **Config resolution is once at construction.** `LlmServiceMixin.llm_config` is a required class-attr string (default `'DEFAULT'`), settable in `Bot(llm_config=...)`; `LlmService.__post_init__` resolves it once via `self.obj.get_llm_config()` into a `LlmConfig` and hands it to `LlmConnector` (dandy/application/llm/service.py:40). Assigning `bot.llm_config = 'X'` afterwards is a silent no-op — nothing re-resolves.
- **Partial mid-flight mutability already exists, un-integrated.** `bot.llm.options.temperature = 0.5` works today (the `options` property exposes the live `LlmOptions`, and `LlmConnector._update_request_body` copies options into the request body on every `prompt_to_intel`), but `bot.reset()` → `LlmConfig.reset()` re-applies options from the config's `_settings_values` snapshot, discarding the mutation. `LlmService.config`/`.options` are read-only properties.
- **`LlmConfig` internals** (dandy/infrastructure/llm/config.py): `name`, `model`, `context_size`, `prompt_retry_count`, `options` (live `LlmOptions`), `http_request_intel` (Url host/port + bearer token), private `_settings_values`. HOST/PORT/API_KEY are **not** first-class attributes — they live inside `http_request_intel`, so there is no supported override path for them. `LlmConfig.__init__` mutates the shared `settings.LLM_CONFIGS` dict (fills HOST/PORT/API_KEY/CONTEXT_SIZE from `DEFAULT`); re-resolution is idempotent.
- **Stale `Url.parsed_url` trap.** `Url` (pydantic, dandy/infrastructure/http/url.py:15-16) computes `parsed_url = urlparse(host)` in `model_post_init`; `to_str()` and `is_https` read `parsed_url`, so setting `url.host` after construction silently keeps the old scheme/netloc on the wire.
- **`LlmOptions` validates only at construction.** Range checks (temperature 0-2, penalties -2..2, `top_p` 0-1, positive minimums) run in `model_post_init`; setting fields on a live instance bypasses them. Option overrides must therefore be routed through `LlmOptions(**merged)` construction.
- **Consumers snapshot the config.** `Decision.__init__` snapshots `self.llm_config = self._llm_service_mixin.get_llm_config()` (dandy/application/decision/decision.py:39); `DecisionService` is built once per bot and deliberately never reset, so a snapshot stays stale after a switch. `Agent.max_context_tokens` is resolved once at construction (dandy/application/agent/agent.py:65). In contrast, `ToolService._compact_history_before_next_round` reads `self.obj.config` live every round (dandy/application/tool/service.py:159) and the connector reads `self.llm_config` live per request — so the tool loop already tracks a swap; only Decision and Agent need fixing.
- **History lives on the request body.** `LlmRequestBody.messages` is the `MessageHistory`; `LlmConfig.generate_request_body()` builds a fresh body (new model + options, empty messages); `reset_messages()` clears it. A swap must carry the messages object across.
- **Reset semantics to preserve.** `LlmService.reset()` → `connector.reset()` (`llm_config.reset()` re-applies options from the config's snapshot + regenerate request body) + `reset_messages()` + `skills.reset()`. `DecisionService.reset()` is a no-op by design (tests/application/bot/test_reset_chain.py asserts the call graph).
- **Seam already documented.** `dandy.application.llm.service -> dandy.infrastructure.llm.config` is already in `pyproject.toml` `ignore_imports`, so a runtime (non-TYPE_CHECKING) `LlmConfig` import in `LlmService` adds no new contract edge.
- **`LlmConfig` is not in the public API.** `dandy/__init__.py` exports `LlmOptions` but not `LlmConfig`; direct assignment needs `LlmConfig` importable from the root.
- **Test conventions.** `unittest.TestCase`, hermetic; mock `dandy.infrastructure.http.connector.HttpConnector.request_to_response` returning `HttpResponseIntel(status_code=200, json_data={'choices': [{'message': {'content': '<json>'}}]})`; assert on `request_intel.json_data`. Test settings (tests/dandy_settings.py): DEFAULT (CONTEXT_SIZE 65536, OPTIONS temperature 0.7 / frequency_penalty 1.0), THINKING (CONTEXT_SIZE 262144, OPTIONS max_completion_tokens 13107 / reasoning_effort medium / temperature 1.0), AUDIO, VISION — all models are `gpt-test`, so wire-level model assertions need an override. LlmConfig tests live in tests/infrastructure/llm/config/test_config.py.
- **Docs gates.** `docs/reference/application.md` lists `LlmService` members explicitly (needs `set_config`); `docs/reference/infrastructure.md` lists `LlmConfig` members (needs `host`/`port`/`api_key`); `docs/user_guide/options_and_context.md` is the user-facing options/CONTEXT_SIZE page; `docs/changelog/v3.md` has a v3.0.0a3 Added section; `mkdocs build --strict` is a CI gate; AGENTS.md documents the LLM flow and settings behavior and must stay accurate.

## Plan

1. First-class identity fields on `LlmConfig`
   - Add `host`, `port`, `api_key` properties to `LlmConfig` (get/set through `http_request_intel`; the `host` setter also refreshes `url.parsed_url = urlparse(value)` so `Url.to_str()` stays correct).
   - Done when `config.host` / `config.port` / `config.api_key` can be read and set, a changed host changes `url.parsed_url`, and the existing config tests stay green.
2. History-preserving swap on `LlmConnector`
   - Add `LlmConnector.set_llm_config(llm_config)`: replace `self.llm_config`, regenerate `self.request_body` from the new config, and carry the existing `request_body.messages` object over so the conversation survives.
   - Done when a service-level test shows the messages object is unchanged after a swap while model/options come from the new config.
3. The change API on `LlmService`
   - `set_config(name, **overrides)`: build `LlmConfig(name)` (unknown name → the existing `DandyError`), then apply overrides: identity fields (`model`, `host`, `port`, `api_key`, `context_size`, `prompt_retry_count`) with type checks, option fields (any declared `LlmOptions` field) built via `LlmOptions(**merged)` so range checks run; unknown keys and out-of-range/wrong-type values raise `LlmCriticalError`; option overrides are also merged into the config's `_settings_values['options']` so `reset()` preserves them. Swap through step 2 and sync `self.obj.llm_config` to the entry name.
   - Make `LlmService.config` settable: accepts an `LlmConfig` (anything else → `LlmCriticalError`), swaps through step 2, syncs `self.obj.llm_config` to the config's `name`.
   - Done when all three entry points (named switch, named switch + overrides, direct assignment) change the full config mid-conversation with history preserved, and invalid input fails fast with a clear error.
4. Consumers track the live config (parallel with each other)
   - `Decision.llm_config` becomes a property reading `self._llm_service_mixin.llm.config` instead of the constructor snapshot.
   - `Agent.turn` re-resolves `self.max_context_tokens = self._resolve_context_size()` at the top of each turn so a CONTEXT_SIZE change moves the compaction window and overflow guard immediately.
   - `Agent` gains a thin `llm` property delegating to `self.bot.llm`, so the interface is exactly `agent.llm.set_config(...)` / `agent.llm.config = ...`.
   - Done when after `set_config` (via `agent.llm` or `bot.llm`), a `Decision` call and an Agent turn use the new config, `agent.llm` is the bot's cached LlmService, and the reset-chain test still passes unchanged.
5. Public export of `LlmConfig`
   - Re-export `LlmConfig` from `dandy/__init__.py` (import + `Dandy` namespace class + `__all__`, keeping the file a thin re-export layer) so the direct-assignment path is first-class.
   - Done when `from dandy import LlmConfig` works and the root imports no new layer.
6. Hermetic tests
   - New `tests/application/llm/test_config_change.py`: named switch (model/context/options change, `bot.llm_config` synced), history preserved across a swap, wire assertions (host, port, bearer token, model) from a mocked `HttpConnector.request_to_response`, override validation (unknown key, out-of-range temperature, wrong type all raise), direct assignment (works; non-`LlmConfig` raises), reset semantics (per-instance option override survives `bot.reset()`, messages cleared), instance independence (bot A's switch does not affect bot B), live tracking by Decision and Agent, and `agent.llm` being the bot's cached LlmService.
   - Extend `tests/infrastructure/llm/config/test_config.py` for the `host`/`port`/`api_key` properties (including `parsed_url` freshness).
   - Done when `just test` is green including the new tests and the hermetic suite stays fast (~4s).
7. Docs
   - `docs/reference/application.md`: add `set_config` to the `LlmService` member list. `docs/reference/infrastructure.md`: add `host`/`port`/`api_key` to the `LlmConfig` member list. `docs/user_guide/options_and_context.md`: new section on changing the config mid-conversation (the two entry points, what each field override does, history preserved, reset behavior). `docs/changelog/v3.md`: Added entry under v3.0.0a3. `AGENTS.md`: keep the LLM-flow / settings description accurate (config is per-instance mutable mid-flight; `Decision` and `Agent` track the live config).
   - Done when `just docs-tests` (`mkdocs build --strict`) passes.
8. Full verification
   - Run `just test`, `ruff check .`, `ruff format .`, `just lint-imports`, `just docs-tests`; capture real output.
   - Done when every one is green and the evidence is quoted in the final report.

## Completion Test

```bash
just test                 # hermetic suite green, including tests/application/llm/test_config_change.py
ruff check .              # no findings
ruff format --check .     # no reformatting needed
just lint-imports         # contracts hold (no new cross-layer edges)
just docs-tests           # mkdocs build --strict passes
```

Smoke (inside the new hermetic tests, mocked `HttpConnector.request_to_response`): build a `Bot`, add a user message, run `bot.llm.set_config('DEFAULT', host='https://alt.example', port=8443, api_key='sk-test', model='gpt-override', context_size=120000, temperature=0.2)`, run one `prompt_to_intel`, and assert the captured request's `json_data['model'] == 'gpt-override'`, URL host/port/bearer match the overrides, the history still contains the pre-swap message, and `agent.max_context_tokens` / `decision.llm_config` follow the switch.

## Deviations

1. In-place identity changes needed per-request live sync
   - What: `LlmConnector._update_request_body` now also copies `llm_config.model` into the request body on every call, and the `LlmConfig.api_key` setter re-runs `HttpRequestIntel.generate_headers()`.
   - Why: in-place `config.model` / `config.api_key` changes (part of the approved direct-assignment / field-mutation path) would not have reached the next request's wire — the model was only read at request-body generation, and the Authorization header only derived at `HttpRequestIntel` construction.
2. New documented seam edge in pyproject.toml
   - What: added `dandy.application.decision.decision -> dandy.infrastructure.llm.config` to the "Application layer imports infrastructure only at documented seams" contract's `ignore_imports` (the `Decision.llm_config` property's `-> LlmConfig` annotation is a TYPE_CHECKING-only import).
   - Why: the plan's Current State only noted the already-documented `dandy.application.llm.service -> dandy.infrastructure.llm.config` seam; the `Decision` class needed its own exact edge for the live-tracking annotation. It joins the three edges `decision.decision` already has in that list (llm.connector, recorder builders) and matches the AGENTS.md seam text ("LlmService/Decision/ToolService → LlmConnector, LlmConfig, ...").
3. Verification bar for ruff
   - What: `ruff check .` was verified as "zero findings above the pristine-HEAD baseline" (975 pre-existing findings under the un-pinned venv ruff 0.17.3, measured with a `git worktree` at HEAD and diffed), and `ruff format --check .` as "no files beyond the 14 pre-existing ones" (my one new test file was formatted).
   - Why: the repo carries 975 pre-existing ruff findings and 14 unformatted files at HEAD (CI has no ruff job); mass-fixing unrelated debt was out of scope, so the practical standard was no new findings, diffed against the worktree baseline.
4. Live-LLM flake observed once (not caused by this change)
   - What: `tests/application/bot/test_bot.py::TestBot::test_bot_intel_class_exclude` failed in one full-suite run, passed in every other run (including isolation and the final verification run).
   - Why: it is a live-LLM test (`@run_llm_configs()`, runs only with a real non-placeholder `AI_API_KEY`) whose `assertGreater(gems_value, 0)` / `assertGreater(money_bag.coins, 0)` assertions depend on the model's non-deterministic output. Pre-existing flake, unrelated to this change.
