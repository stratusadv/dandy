# AGENTS.md

Guidance for working in the **Dandy** repository (v2.2.0) — a Python AI framework for building LLM-powered software (bots, prompts, structured intel, recording, caching, decoding).

> This document is the **single source of truth** for agent rules in this repo. The previous `.github/copilot-instructions.md` was removed on 2026-09-06; all of its still-accurate content has been absorbed and updated here. When the two disagree, this file wins.

## Quick orientation

- **Runtime**: Python >= 3.11 (classifiers cover 3.11–3.14); `.python-version` pins 3.11 for local tooling. No `.venv` is committed — create one with `just venv` (uses `uv`).
- **Dependencies** (runtime, deliberate and small): `pydantic`, `requests`, `blessed` (CLI TUI), `python-dotenv`. Dev/config tooling: `ruff`, `uv`, `just`, `ty`, `codespell`, `mkdocs`, `pytest`, `build`/`twine` (packaging).
- **Entry point**: `dandy.cli.main:main` exposes the `dandy` console script and the interactive CLI (`dandy/cli/`).
- This is a single-package repo (`dandy/` is the library; `tests/` mirrors it).

## Essential commands

Environment (all `just` recipes assume a `sh` shell and load `development.env` via dotenv):

```bash
just venv            # uv venv + uv sync --all-extras --upgrade  (do this first)
just venv-upgrade    # re-sync dependencies
```

Tests:

```bash
just test                 # pytest .  (PYTHONPATH includes repo root; auto-sets DANDY_SETTINGS_MODULE=tests.dandy_settings)
just test-failed          # pytest --ff --lf  (run only previously failing tests)
just test-app <path>      # pytest <path>
just test-coverage        # pytest . --cov=dandy --cov-report=term-missing
```

- Local `just` recipes run **pytest**; CI (`ci: .github/workflows/run_tests.yml`) runs **`python -m unittest discover -v ./tests`** and then **`PYTHONPATH=. mkdocs build --strict`**. Both test runners must pass — keep tests compatible with both (they are `unittest.TestCase`, which pytest also discovers).
- **The suite is hermetic by default**: `tests/dandy_settings.py` fills LLM configs with placeholder values, and live-LLM tests skip unless a real `AI_API_KEY` is exported (see [Testing approach](#testing-approach)). A plain `just test` passes on any dev machine with no secrets.
- The `dandy-testing` CI job needs these secrets/env: `AI_API_HOST`, `AI_API_KEY`, `DANDY_SETTINGS_MODULE`, `LLM_AUDIO_MODEL`, `LLM_DEFAULT_MODEL`, `LLM_THINKING_MODEL`, `LLM_VISION_MODEL`, `OPENAI_API_KEY`, `OPENAI_HOST` (with a real `AI_API_KEY`, CI exercises the live-LLM tests that skip locally).

Lint / format / type / spelling:

```bash
ruff check .            # lint (ruff.toml: ALL rules selected, explicit ignore list)
ruff format .           # format (single quotes, indent 4, line length 100)
ty                      # type checking (config: ty.toml; warn-only rules — advisory, not a CI gate)
codespell .             # spelling (config in pyproject.toml; ignore-words-list: doesnt; separately enforced by .github/workflows/codespell.yml)
```

Docs:

```bash
just docs               # mkdocs serve (hot reload; changes to example code re-execute via markdown-exec)
just docs-tests         # mkdocs build --strict  (CI requirement — broken docs fail CI)
```

CLI / packaging:

```bash
just cli                # PYTHONPATH=:. python ./dandy/cli/main.py
python -m build         # build sdist+wheel (setuptools dynamic version from dandy.constants.__VERSION__)
twine upload dist/*     # publish (see publish_pypi_package.yml; triggered on GitHub release)
```

## Environment & settings (least obvious part)

Dandy resolves runtime config through a settings module, not constructor args:

1. Importing `dandy` instantiates a `DandySettings` singleton (`dandy/conf/settings.py`) that imports a user settings module named by `DANDY_SETTINGS_MODULE` env var, defaulting to `dandy_settings` (`dandy/conf/utils.py`, `dandy/constants.py`).
2. The settings module must define `BASE_PATH` (project root). Everything else falls back to `dandy/default_settings.py`.
3. `LLM_CONFIGS` is a dict; a `DEFAULT` entry is **required** (`dandy/llm/config.py`). Other configs inherit missing `HOST`/`PORT`/`API_KEY` from `DEFAULT`. LLM errors quote the settings module name, so cite that file when users see "is not set" messages.
4. In this repo `tests/dandy_settings.py` is the settings module (configs: `DEFAULT`, `THINKING`, `AUDIO`, `VISION`). It defaults `AI_API_HOST`/`AI_API_KEY`/`LLM_*_MODEL` to hermetic placeholders so `LlmConfig` validates without a live endpoint; real env vars override them. CI injects `DANDY_SETTINGS_MODULE` (+ `AI_API_*`, `LLM_*_MODEL`) as secrets.
5. The CLI auto-creates a `dandy_settings.py` if missing (`dandy/cli/utils.py::check_or_create_settings`) and loads env from `dandy.env` / `development.env` / `dev.env` / `.env`.
6. **JSON fallback**: when neither the settings module nor a JSON file imports, `DandySettings.load_user_settings` (`dandy/conf/settings.py`) falls back to loading settings from a JSON file before the CLI creates a `.py`: first `Path.cwd() / DANDY_LOCAL_DIRECTORY_NAME / 'dandy.json'` (i.e. `.dandy/dandy.json`), then `Path.home() / '.config' / 'dandy' / 'dandy.json'`. The loader (`dandy/conf/utils.py::load_settings_from_json_file`) returns a `SimpleNamespace`: top-level keys are upper-cased (`llm_configs` -> `LLM_CONFIGS`), `LLM_CONFIGS` config-name keys and each config's own keys are upper-cased (but `OPTIONS` sub-keys stay lowercase — they are `LlmOptions` field names), `CLI_CONFIG` keys and values are upper-cased (values reference `LLM_CONFIGS` names), and `BASE_PATH`/`CACHE_SQLITE_DATABASE_PATH` strings become absolute `Path`s. A missing `BASE_PATH` defaults to `Path.cwd()`. `check_or_create_settings` probes the same two JSON locations before writing `dandy_settings.py` and prints `Loaded settings from "<path>"` when one is found. Tests live in `tests/cli/test_json_settings.py`.
7. **Token estimation & agent compaction**: token counts come from `dandy/llm/tokens/utils.py` — a dependency-free character-class heuristic (fitted to BPE tokenizer output; letters ~4.65 chars/token, digits ~2, symbols ~1.5, whitespace near-free) plus per-message/per-content costs: chat-template role overhead, tool-call framing ids/names/arguments, image tokens by `detail` (low = 85, high/auto = 765), and audio base64. `Message.estimated_token_count` (`dandy/llm/request/message.py`) branches per content type on the wire form — it does **not** count pydantic reprs anymore. **Context management comes from `CONTEXT_SIZE` in `LLM_CONFIGS`** (e.g. `'CONTEXT_SIZE': 65536` on `DEFAULT`; non-`DEFAULT` configs inherit it from `DEFAULT`, and it also works through the `dandy.json` fallback). `max_completion_tokens` is **not an option** anymore: `LlmConfig` (`dandy/llm/config.py`) derives it as `CONTEXT_SIZE * LLM_OUTPUT_TOKEN_RATIO` (constant `0.20`) and puts it on the request body. The CLI coding agent reads the coding config's `CONTEXT_SIZE` (`CodingAgent._resolve_context_size`) and `_compaction_target_token_count` compacts to `CONTEXT_SIZE * AGENT_COMPACTION_TARGET_RATIO` (constant `0.70`), leaving a 0.10 margin for error so input + output always fit under `CONTEXT_SIZE`. `CodingAgent.chat` compacts `self.history` before every LLM call via `compact_message_history` — it always keeps the system message and the newest message, drops oldest tool-use rounds first then oldest plain exchanges, never leaves a dangling `assistant` tool-calls message without its `tool` results, and reports progress via the `progress_callback` (`Compacting conversation history (...) tokens...`). Without any `CONTEXT_SIZE` the config still works (no `max_completion_tokens` is sent) and compaction falls back to a 65536 window constant. Tests: `tests/llm/tokens/test_utils.py`, `tests/llm/config/test_config.py`, `tests/cli/intelligence/test_coding_agent.py`.
8. **`DEBUG` mode**: if `DEBUG = True` in settings, `tests/dandy_settings.py` (and `dandy_settings.py` templates) do `from dandy.core.debug import *`, which replaces `warnings.showwarning` with a stack-trace-printing handler used to debug LLM retry/validation issues.

## Architecture & data flow

### Package layout (`dandy/`)

| Module | Role |
|---|---|
| `bot/` | `Bot` base class + recorder wrapper |
| `llm/` | LLM service/connector, config, options, prompt builder (snippets), decoder, **tool calling**, diligence, request/messages, tokens |
| `intel/` | `BaseIntel` (pydantic), `IntelFactory`, field/typing helpers, `IntelService` |
| `recorder/` | Singleton `Recorder`, event store, html/json/markdown renderers |
| `cache/` | `MemoryCache`, `SqliteCache`, decorators, hashing tools |
| `http/` | `HttpConnector`, `HttpRequestIntel`/`HttpResponseIntel`, `HttpServiceMixin` |
| `file/` | File read/write + image/audio utils, `FileServiceMixin` |
| `core/` | Service/mixin/connector ABCs, exceptions, singleton, typing registry, `future` (thread pool) |
| `cli/` | TUI (`blessed`), `session`, the agentic loop (`agent/` coding agent), its `tools/`, and `main.py` entry point |
| `tool/` | `BaseTool` (tool descriptors, base-level) + `BaseSubprocessTool`/`GitTool` (subprocess wrapper) |
| `conf/` | `settings.py` (`DandySettings` singleton + `settings` instance) + `utils.py` (settings-module name + JSON settings loading helpers) |
| `constants.py`, `default_settings.py` | Version/constants, defaults |

Convention: every subsystem keeps its supporting pydantic models, bots, and user-facing prompts under a nested **`intelligence/`** directory (e.g. `dandy/llm/decoder/intelligence/`, `dandy/cli/intelligence/`, `tests/bot/intelligence/`). Follow this when adding fakes or fixtures.

### The mixin/service pattern (used everywhere)

Three layers, consistently named:

- **`BaseServiceMixin`** (`core/service/mixin.py`): `_get_service_instance(ServiceClass)` lazily builds and caches a service on `self` (`_{ServiceName}_instance` attr). Mixins expose it via a property (`self.llm`, `self.file`, `self.http`, `self.intel`). `_required_attrs` + `__init_subclass__` raise `ServiceCriticalError` if a required class attr is `None` — define class-level defaults before subclassing.
- **`BaseService`** (`core/service/service.py`): generic service wrapping the owner (`self.obj`), carries a `recorder_event_id`, calls `__post_init__` hook. `reset()` is abstract; subclasses implement it (the chain relies on call `super().reset()`).
- **`Bot`** (`bot/bot.py`) composes `FileServiceMixin, LlmServiceMixin, HttpServiceMixin, IntelServiceMixin` (MRO order matters — reset chains up through them).

**Reset chain** (verified by `tests/bot/test_reset_chain.py`): `Bot.reset()` propagates to `llm`, `http`, `intel`, `file` services. The **decoder service is deliberately not reset** (`DecoderService.reset()` is a no-op).

### Public API surface

`dandy/__init__.py` re-exports the curated API: `Bot`, `Prompt`, `BaseIntel`, `BaseListIntel`, `Recorder`, `MemoryCache`, `SqliteCache`, `cache_to_memory`, `cache_to_sqlite`, `generate_cache_key`, `process_to_future`, `recorder_to_html_file`/`recorder_to_json_file`/`recorder_to_markdown_file`, and exceptions `DandyError` / `DandyCriticalError` / `DandyRecoverableError`.

### LLM flow

```
Bot.process(prompt, intel_class=..., include/exclude=..., intel_object=...)
  → LlmService.prompt_to_intel  (dandy/llm/service.py)
    → LlmConnector.prompt_to_intel (dandy/llm/connector.py)
        builds LlmRequestBody + JSON schema from IntelType (IntelFactory.intel_to_json_inc_ex_schema)
        always prepends a system message; asserts >= 1 system + 1 user message (LlmCriticalError)
        pre/post-diligence handlers run around the HTTP call
        → HttpConnector.request_to_response (retries HTTP_CONNECTION_RETRY_COUNT + 1 times)
        → IntelFactory.json_str_to_intel_object parses response into Intel
        on pydantic ValidationError → retry (option prompt_retry_count, default 2) re-prompting with validation errors
```

- Message history persists on the connector between calls; `Bot.reset()` / `LlmService.reset()` clears messages and re-applies options from settings.
- `include_fields`/`exclude_fields` trim the generated JSON schema so the model only needs to produce those fields (see Intel below).
- Multimodal: `prompt_to_intel` accepts `audio_urls/file_paths/base64_strings` and `image_urls/file_paths/base64_strings` (see `tests/assets/{audio,images}` and `tests/bot/test_bot_vision.py`).
- **`LlmOptions`** (`dandy/llm/options.py`, a pydantic model with `extra='allow'`): `frequency_penalty`, `presence_penalty`, `top_p`, `temperature`, `prompt_retry_count` (default `2`). Non-None values are range-checked (e.g. temperature 0–2); violations raise `LlmCriticalError`. `max_completion_tokens` is **not** an option — it is derived from the config's `CONTEXT_SIZE` (see [Environment & settings](#environment--settings-least-obvious-part) bullet 7).
- `LlmConfig` (`dandy/llm/config.py`) hard-codes `url.path_parameters = ['v1','chat','completions']` — providers must be OpenAI-compatible chat completions. Non-`DEFAULT` configs inherit `HOST`/`PORT`/`API_KEY` from `DEFAULT`.

### Prompt building

`Prompt` (`dandy/llm/prompt/prompt.py`) is a dataclass (`input: Self | str | None`, `tag: str | None`) that appends **snippets** (`dandy/llm/prompt/snippet.py`) and joins them in `to_str()`. When `tag` is set, output is wrapped in `<tag>...</tag>`. All builder methods return `self` for chaining:

`text`, `heading`, `sub_heading`, `title`, `list`/`unordered_list`, `ordered_list`, `array`, `array_random_order`, `unordered_random_list`, `dict`, `divider`, `line_break` (alias `lb`), `file`, `directory_list`, `intel`, `intel_schema`, `module_source`, `object_source`, `prompt`, `random_choice`. Most accept `triple_backtick`/label kwargs. `estimated_token_count` uses the character-class heuristic in `dandy/llm/tokens/utils.py` (see [Environment & settings](#environment--settings-least-obvious-part) bullet 7).

### Tool calling

- **`BaseTool`** (`dandy/tool/tool.py`, exported from `dandy`) is an **abstract** base-level tool descriptor (`ABC`), written **inheritance-style like `Bot`**: subclasses set `name` and `description` as class attributes and **must** override the abstract `handle(self, ...) -> str | BaseIntel` with **typed, annotated** keyword parameters (`BaseTool` cannot be instantiated without an override — the abstract `handle` body raises `NotImplementedError`). The handle signature becomes the tool's OpenAI `function` parameters (`to_function_dict()`, validated at call time — a missing `name` raises `ToolCriticalError`): `BaseTool.get_parameters_intel_class()` derives the parameter schema via `IntelFactory.callable_signature_to_intel_class(self.handle)` (the bound method, so `self` is stripped; it is cached per instance). Required-vs-optional follows the signature (no default = required; pydantic omits the `required` key entirely when nothing is required). A handle with no parameters yields a schema with empty `properties` (a no-argument tool). There are **no** `intel_class` or `include_fields`/`exclude_fields` attributes — parameters always come from the handle signature alone. It is LLM-agnostic (the `dandy/llm/tool/` subsystem is one consumer, others are free to use descriptors + `handle()` standalone); the old subprocess base in `dandy/tool/` was renamed `BaseSubprocessTool` (behind `GitTool`).
- **Premade tools**: tools are reusable because each carries its schema **and optionally its execution**:
  ```python
  class GetWeatherTool(BaseTool):
      name = 'get_weather'
      description = 'Get the current weather for a location.'

      def handle(self, location: str = '', units: str = 'celsius') -> str:
          return weather_service.get(location, units)
  ```
  Every tool is self-contained because `handle()` is mandatory and carries the execution; an external `tool_functions` handler can still take over at call time (see below). `tools=[...]` accepts a mix of classes and instances (`to_tool_instances()` normalizes everything to instances before the wire call).
- **Handle dispatch**: at `LlmToolService._process_tool_call`, arguments are validated against the derived schema and the validated keyword dict is passed straight through (`tool.handle(**arguments_intel.model_dump())`), so defaults are applied and values are Python-typed (a `bool`/`int`/nested annotation is parsed, not left as JSON text). An external `tool_functions` entry still wins and receives the parsed argument Intel object (its `ToolHandler = Callable[[BaseIntel | str], str | BaseIntel]` contract is unchanged). Empty/whitespace arguments are treated as `{}` so no-argument tools handle `arguments: ""` from providers. Because `handle` is abstract, a tool class without an override cannot even be instantiated (it must always declare the schema); no-argument tools declare `handle(self)` and receive no kwargs. Every CLI tool (`dandy/cli/intelligence/tools/`) follows this pattern; the shared `tools/intel.py` (and its Intel classes) was deleted with the migration.
- **Execute-and-loop**: `bot.llm.tools.prompt_to_intel(prompt, intel_class, tools=[...], tool_functions={'name': handler}, max_tool_iterations=5, progress_callback=...)` (`LlmToolService`, `dandy/llm/tool/service.py`) keeps calling the model, executing any requested tools (an explicit `tool_functions` entry wins over the tool's own `handle()`), feeding results back as `role='tool'` messages, until the model returns the final Intel. The original prompt is only sent on the first iteration (history carries it after that). An optional `progress_callback: Callable[[str], None]` gets one beat per tool round for a running narrative: if the model wrote a narration sentence alongside its tool calls, the connector captures it on the returned `LlmToolCallsIntel.summary` (`dandy/llm/tool/intel.py`, from the assistant `content`) and that sentence is emitted; and one beat is emitted as each tool actually executes — the tool's optional `action_sentence(**validated_args)` override (`dandy/tool/tool.py`, receiving the validated keyword arguments so it can name the exact files or commands), falling back to the tool name via `pascal_to_title_case` (`dandy/core/utils.py`, e.g. `'get_weather'` → `'Get Weather'`). A tool returns `None` from `action_sentence` to opt out; the agent's own tools all implement it (e.g. `read_file` → 'Reading src/foo.py lines 1-10', `run_command` → 'Running "pytest -q"'), so the CLI story shows exactly what each tool is doing. The service strips the trailing period from each action beat before it reaches `progress_callback` (`removesuffix('.')`), so story beats read 'Reading src/foo.py lines 1-10' without colliding with the model's narration sentence, which keeps its natural period. The CLI bots are prompted to narrate each step ("Begin every message that calls a tool with one short, natural sentence...") so the CLI can render a story. `max_tool_iterations` caps how many tool rounds run before a final answer (default `5`; exceeding it raises `LlmRecoverableError`). Passing `max_tool_iterations=None` disables the cap so the loop never gives up — the CLI's coding and planning agents opt into this. The loop also **compacts its own accumulated conversation before every round** (`LlmToolService._compact_history_before_next_round`, using the shared `compact_message_history` in `dandy/llm/request/message.py`): it targets `0.70` of the resolved config's `CONTEXT_SIZE` (falling back to a `65536` window when unset; `LlmService.config` exposes the resolved `LlmConfig`), so an unbounded tool-calling session can never overflow the provider's context window — for the coding agent this compacts the same persistent history its pre-chat compaction trims. An optional `verbose_callback: Callable[[str], None]` gets one line per event for debugging: the round number and tool-call count, each tool's arguments and result (truncated previews, newlines escaped), arguments that fail validation (fed back to the model), and a `GAVE UP` line when a finite cap is hit.
- **Handlers** are plain callables `Callable[[BaseIntel | str], str | BaseIntel]` — they receive the **parsed arguments Intel** (validated against the tool's handle-derived schema) and return a string or Intel (dumped to JSON) fed back to the model. An unknown tool name raises `LlmCriticalError`; invalid arguments (pydantic `ValidationError`) are fed back to the model as a tool message so it can self-correct; exhausting a finite `max_tool_iterations` raises `LlmRecoverableError` (when it is `None` the loop never gives up, at the cost of unbounded API spend).
- **Manual path**: calling `bot.llm.prompt_to_intel(..., tools=[...])` directly returns `LlmToolCallsIntel` (a `BaseListIntel` of `LlmToolCallIntel` with `name`/`arguments`/`id`) instead of the requested Intel — inspect it and continue the conversation yourself. Tool classes are accepted here too.
- **Wire**: `tools`/`tool_choice` are explicit fields on `LlmRequestBody`; `Message`/`MessageHistory` support `role='tool'` messages (`add_message(role='tool', tool_call_id=..., text=...)`) and assistant `tool_calls`. `Message.model_dump()` emits the OpenAI wire shape (tool content as string, assistant tool_calls with `content: None`).
- **Gotcha**: when `tools` is passed, `response_format` (strict JSON-schema mode) is **cleared** on the request body — strict response_format + non-strict tools 400-errors on OpenAI. The final answer is still validated locally by Dandy's Intel validation + retry loop.

### Decoder

- `DecoderService` (`dandy/llm/decoder/service.py`) exposes `prompt_to_value` (single, wraps `..._values[...][0]`) and `prompt_to_values`, plus `*_future` variants. Access via `self.llm.decoder` (DecoderServiceMixin) — not a standalone component.
- `decoder.process()` (`dandy/llm/decoder/decoder.py`) requires **all `keys_values` keys to be strings** (raises `DecoderCriticalError` otherwise — values can be any type). Returns `DecoderValuesIntel` (appendable). Keys are auto-numbered 1..n and the LLM returns which it chose.
- Retry loop: on empty result → `DecoderNoKeysRecoverableError`, on too many → `DecoderToManyKeysRecoverableError`, each re-prompts via `LlmConnector.retry_request_to_intel` until `prompt_retry_count` exhausted, then re-raises.
- `.as_enum()` on a `Decoder` builds a runtime `Enum` from the mapping for type-safe handling.

### Intel (`dandy/intel/intel.py`)

- `BaseIntel(BaseModel, ABC)`. Everything an LLM returns is an Intel (pydantic) model.
- `model_inc_ex_class_copy(include=..., exclude=...)` builds a **runtime auto-generated subclass** (via pydantic `create_model`) with only the listed fields; use nested dicts `{field: {...}}` for deep filtering of nested Intel. Include and exclude together → `IntelCriticalError`; unknown field names also raise. `model_to_kwargs()`, `model_json_inc_ex_schema`, `create_from_file`/`save_to_file`, `model_validate_and_copy`/`model_validate_json_and_copy` are the other helpers.
- `IntelFactory` (`dandy/intel/factory.py`) maps Python types ↔ JSON schema and validates LLM responses; `IntelService` (`dandy/intel/service.py`) exposes static wrappers: `intel_class_from_callable_signature`, `intel_class_from_simple_json_schema`, `json_str_to_intel_object`.

### Recorder

- `Recorder` is a `Singleton` (`core/singleton.py`). `Recorder.start_recording(name)` … `stop_recording(name)`, then `to_html_file` / `to_json_file` / `to_markdown_file` (renderers under `recorder/renderer/`, HTML templates under `html_templates/`). Recordings write to `{BASE_PATH}/{DANDY_LOCAL_DIRECTORY_NAME}/recordings/`; requires `ALLOW_RECORDING_TO_FILE = True`.
- `Bot.__init_subclass__` installs a **custom `__getattribute__`** that lazily wraps `process` with `record_process_wrapper` (`bot/recorder.py`), so every `process()` call auto-record events. See Gotchas about not overriding it.

### Caching

- `MemoryCache` / `SqliteCache` (pydantic `BaseCache` subclasses, `cache_name`/`limit`) + decorators `cache_to_memory` / `cache_to_sqlite` and `generate_cache_key` hashing. `CACHE_KEY_HASH_LAYER_LIMIT = 3` in `constants.py` intentionally caps how deep cache keys hash (higher pulls in unwanted attrs).

### Futures

- `dandy/core/future`: `AsyncFuture` runs callables on a module-level `ThreadPoolExecutor` (max workers = `FUTURES_MAX_WORKERS`). `Bot.process_to_future`, `LlmService.prompt_to_intel_future`. Timeout → `FutureRecoverableError`; non-positive timeout → `FutureCriticalError`.

## Conventions & style

- **Ruff** (`ruff.toml`): single quotes (format-enforced), indent-width 4, line-length **100**, target py311, `select = ["ALL"]` with an explicit ignore list (includes docstring rules D1xx, `ANN001/002/003/401`, `PLR0913/0915`, `SLF001`, `T201`, etc.). New code must pass `ruff check .` **and** `ruff format .`.
- **Naming**: Classes PascalCase, functions/methods snake_case, constants UPPER_SNAKE_CASE, modules/dirs snake_case. Verbose names preferred (`include_fields` not `include`), no single-letter names.
- **Imports**: stdlib → third-party → `dandy.*`, absolute paths only (note `ruff.toml` `known-first-party = ["system", "app"]` — isort otherwise treats `dandy` as first-party automatically). **Inside the framework (`dandy/` and tests), never import from the `dandy` package root** (`from dandy import X`): the root `__init__` eagerly imports nearly every subsystem, so a root import from within a framework module hits a partially-initialized `dandy` and is the #1 circular-import trap. Always import the defining module's full path instead — `from dandy.bot.bot import Bot`, `from dandy.llm.prompt.prompt import Prompt`, `from dandy.recorder.recorder import Recorder`, `from dandy.tool.tool import BaseTool` — which pulls in only that module's dependency subtree. The one sanctioned root import is `dandy/conf/settings.py`'s function-level `from dandy import default_settings  # noqa: PLC0415` (deliberately lazy to break the settings load cycle; keep it). **Framework consumers / user code** import the core API from the root (`from dandy import Bot, Prompt, BaseIntel, BaseTool, Recorder, MemoryCache, ...`) — that's exactly what `dandy/__init__.py` re-exports, and that file must stay a thin re-export layer with no logic.
- **Type hints**: always annotate signatures; `X | Y` union syntax (Python 3.11+). Generic class names are typed in-string (e.g. `BaseService['dandy.llm.mixin.LlmServiceMixin']`) because of deferred annotations.
- **Exceptions**: `DandyError` (base) → `DandyCriticalError` (fail fast / programming error) and `DandyRecoverableError` (retry or fallback), each subsystem extends these in `<module>/exceptions.py` (e.g. `DecoderNoKeysRecoverableError`, `DecoderToManyKeysRecoverableError`, `IntelCriticalError`, `LlmRecoverableError`, `LlmCriticalError`, `HttpConnectorRecoverableError`, `FutureCriticalError`, `ServiceCriticalError`, `RecorderCriticalError`).
- **No comments in code unless asked**; when present, comments explain *why* (see the LLM-freeze warning in `tests/bot/test_bot.py`).

## Testing approach

- `unittest.TestCase` classes, discoverable by both `pytest` (just) and `unittest` (CI). Mocking is via `unittest.mock` (`mock.patch(...)`).
- **Test intelligence lives beside the tests** under `tests/<module>/intelligence/` (e.g. `tests/bot/intelligence/bots.py`, `intel.py`).
- **Live-LLM tests are skipped by default** via `@live_llm_test` (`tests/consts.py`): they run only when `AI_API_KEY` is set and is **not** one of the placeholder values in `_PLACEHOLDER_API_KEYS` (`test-key`, `changeme`, `your-api-key`, `placeholder`). `@run_llm_configs()` (`tests/llm/decorators.py`) does the same at runtime via `self.skipTest(...)` and only loops over `TESTING_LLM_CONFIGS` (`tests/consts.py`, currently `['DEFAULT']`). `tests/dandy_settings.py` supplies placeholder config values so hermetic tests can build `LlmConfig`s. For hermetic LLM tests, patch at the connector boundary: `mock.patch('dandy.http.connector.HttpConnector.request_to_response', ...)` returning `HttpResponseIntel(status_code=200, json_data={'choices': [{'message': {'content': '<json>'}}]})`.
- **Tool calling is tested hermetically** (`tests/llm/tool/`): `test_tool.py` covers the abstract base (cannot instantiate without `handle`, the abstract `handle` raising `NotImplementedError`), schema generation from handle signatures (defaults, required params, no-parameter tools, missing-name `ToolCriticalError`, derived-class caching, `to_tool_instances` normalization); `test_service.py` mocks `HttpConnector.request_to_response` with a `side_effect` list of `HttpResponseIntel`s — first a `tool_calls` message, then the final-content message — and asserts on the request bodies (`request_intel.json_data['messages']`, `['tools']`, absence of `response_format`) to verify the loop/history/wire behavior, plus the `handle()` dispatch path. Tool fakes live in `tests/llm/tool/intelligence/`.
- **The CLI is an agentic loop with no action system**: `dandy/cli/cli.py` (`DandyCli`) is a pure agent REPL — every message typed goes to `CodingAgent` (`dandy/cli/intelligence/coding_agent.py`), which wraps `CodingBot`, a `PlanningBot` (`dandy/cli/intelligence/bots/planning_bot.py`, THINKING config), and a persistent `MessageHistory`. `CodingAgent.chat` optionally runs the planning bot first (`run_planning`, default on) and feeds the plan into the coding turn as an 'Implementation Plan' section of the user prompt, then calls `bot.llm.tools.prompt_to_intel(..., tools=AGENT_TOOLS, message_history=..., replace_message_history=True, max_tool_iterations=None)` so each turn keeps the prior conversation and the tool loop runs as many rounds as needed (no give-up cap, see [Tool calling](#tool-calling)). Before each call `CodingAgent.chat` compacts the history when it approaches the coding config's `CONTEXT_SIZE` (compaction targets 70% of it via `AGENT_COMPACTION_TARGET_RATIO`, the derived `max_completion_tokens` reserves 20% for output, and 10% is left as a margin for error; see [Environment & settings](#environment--settings-least-obvious-part) bullet 7), keeping the system message and the newest exchange. The only `/` commands are `/clear` (resets history) and `/quit`/`/exit` (stops the loop); anything else reports "Unknown command". Pressing **escape twice** in `Tui.get_user_input` (`dandy/cli/tui/tui.py`) returns `None`, which breaks the loop. The old `ActionManager`/`/code`/`/explain`/`/help`/`/bot` action system and `dandy/cli/actions/` are gone; the agent lives in `dandy/cli/intelligence/`, with bots in `dandy/cli/intelligence/bots/` and tools in `dandy/cli/intelligence/tools/`. **One-shot mode**: `dandy "<request>"` (entry point `dandy.cli.main:main` in `pyproject.toml`) joins `sys.argv[1:]` and runs `process_user_input` for a single turn, then exits; `dandy -h`/`--help` prints usage, `dandy -v`/`--version` prints the version, both before any settings load (`dandy/cli/main.py`). The final answer (`result_intel.text` in `DandyCli.process_agent_input`) is printed through `Printer.output` (`dandy/cli/tui/printer.py`), which renders it with `MarkdownRenderer` (`dandy/cli/tui/markdown.py`) — a dependency-free markdown-to-terminal renderer (headings with dividers, inline bold/italic/code/links, fenced code blocks, lists, blockquotes, horizontal rules, and pipe tables) built only on blessed's `Terminal` styling and `wrap`. **`CLI_CONFIG` in settings** maps CLI task names to `LLM_CONFIGS` entries — `CodingBot.__post_init__` sets `self.llm_config = get_cli_llm_config('CODING')` (`dandy/cli/utils.py`), and the welcome banner shows that config's model; unknown/missing entries fall back to `'DEFAULT'`. A `DEBUG: bool = True` setting (see [Environment & settings](#environment--settings-least-obvious-part), `dandy/default_settings.py`) turns on verbose tracing: `DandyCli.__init__` reads it and, when true, passes a `verbose_callback` (prints each tool-round event from [Tool calling](#tool-calling) to stdout) into `CodingAgent.chat` → `prompt_to_intel`. When no `dandy_settings.py` exists, `CLI_CONFIG`/`LLM_CONFIGS` are resolved from a `dandy.json` fallback instead (see [JSON fallback](#environment--settings-least-obvious-part)). The toolset is `AGENT_TOOLS = CODE_EDITING_TOOLS + [search_files, run_command, git_status, git_diff]` (`dandy/cli/intelligence/tools/`): the six file tools plus `SearchFilesTool` (grep-style, excludes `.git`/`.dandy`/`node_modules`/`.venv`/`__pycache__`, capped output), `RunCommandTool` (runs commands with no user confirmation), and `GitStatusTool`/`GitDiffTool` (via `run_subprocess`, `cwd=session.project_base_path`). Every path resolves against `session.project_base_path` and refuses paths that escape it; every `handle()` returns a string, never raises, so the model can self-correct. `run_subprocess` (`dandy/cli/intelligence/tools/subprocess_utils.py`) uses `use_shell=True` only for `run_command`. Covered hermetically in `tests/cli/intelligence/` (tool unit tests, a mocked `request_to_response` `CodingAgent` multi-turn test asserting the second turn's request contains the first turn's user/assistant messages and that `clear()` resets the history, plus `DandyCli` loop tests for escape-exit/quit).
- **`tests/nines/`** is a self-contained (non-package) flakiness harness: `@nines_testing(n)` re-runs a function 1000× to shake out nondeterminism. Not part of the library; gated by `TEST_NINES` (see commented-out CI job in `run_tests.yml`).
- **`tests/example_project/book/`** demonstrates full multi-bot orchestration (theme → title → characters → world → plot → chapters) with Intel flowing between bots (`create_book` in `book/workflow.py`). Best reference for "how to compose many bots".
- Test directory quirks: `tests/file_/`, `tests/http_/` (trailing underscore), `tests/recorder/`, `tests/nines/`.
- **Strict OpenAI-compatible endpoints (vLLM via litellm) reject conversations with more than one leading system message or system messages elsewhere** (400 `System message must be at the beginning.`). The connector only prepends its own system prompt when the merged `message_history` does not already lead with a system message, and diligence instructions merge into that leading system message instead of adding another (`BaseDiligence._prepend_system_instruction`). Preserve both behaviors when refactoring the request-building flow.
- **`MessageHistory` is falsy when empty** (it defines `__len__` and pydantic does not define `__bool__`), so the connector's history merge guard must be `if message_history is not None:` — never `if message_history:`. An empty history is a legitimate value when `replace_message_history=True`: it means "attach this (currently empty) history object so the conversation accumulates into it". `connector.py:_update_request_body_options` uses this to make multi-turn `CodingAgent.chat` calls persist into the caller's history.
- **Live models (e.g. `stratus.turbo`) often wrap the final JSON answer in markdown code fences**, which fails strict JSON validation; the connector's validation retry prompt and the `CodingBot` guidelines both now explicitly demand raw JSON (no fences, no extra text). On top of that, `LlmConnector._validate_fenced_json_response` (`dandy/llm/connector.py`) recovers when the model does it anyway: if the response contains exactly one fenced code block (` ``` ` or ` ~~~ `, language tag optional, a narration line before it is fine) and that block's body parses and validates against the target intel, it is used as the answer so the CLI renders text instead of a raw javascript block. When the fenced body does not validate (e.g. it is a legit code sample, or multiple fences exist), behavior is unchanged (raw-text fallback for `DefaultIntel`, retry loop otherwise). Keep those instructions when adjusting prompts.
- **`DefaultIntel` is prose-tolerant**: its whole purpose is "whatever text the model said", so `LlmConnector._request_to_intel` has a fallback — when the response is plain text (validation error type is exactly `json_invalid`) and the target Intel is `DefaultIntel`, it stores the raw text in `DefaultIntel.text` instead of failing. Wrong-key but valid JSON (e.g. `{"message": ...}`) still goes through the retry loop; only unparseable prose takes the fallback. This is what lets the agent REPL answer "how do I..." questions without crashing.
- Reset behavior is explicitly tested (`tests/bot/test_reset_chain.py`) — preserve the exact reset call graph if refactoring.

## Gotchas & non-obvious patterns

1. **Do not override `__getattribute__` in `Bot` subclasses** — the base already injects the recorder wrapper through it; overriding breaks recording (and typing). No `__getattribute__` in new bot code.
2. **The `Agent`/processor-pipeline module was removed in v2.0.0.** Compose multiple `Bot` instances (see `tests/example_project`) — there is no orchestrator class anymore.
3. **Bot subclasses must call `super().__post_init__()` first** when they define `__post_init__`; `ServiceCriticalError` guards rely on class attrs being set (`llm_config`, `role`, `task`, `intel_class` — see `LlmServiceMixin._required_attrs`).
4. **`Bot.process` requires a `prompt`**: it forwards `args[0]` as `prompt` or raises `ValueError`. Subclass `process()` to accept your own signature (see `tests/bot/intelligence/bots.py`) and call `self.llm.prompt_to_intel(...)`.
5. **Decoder keys must be strings** — non-string keys raise `DecoderCriticalError` (a runtime check in `Decoder.process()`).
6. **LLM configuration is OpenAI-compatible chat completions only** — `LlmConfig` forces path `v1/chat/completions`; the response parser reads `choices[0].message.content` (and `choices[0].message.tool_calls` when tools are used).
7. **Calling `request_body.json_schema`/`estimated_token_count` is only valid when `response_format` is set** — the tool path sets `response_format` to `None`; guards exist in the recorder and token estimator for that case, keep them.
8. There is a documented **"LLM freeze" trigger**: the prompt `'Please give me 22 coins and 17 gems.'` was observed to lock a model in indefinite inference and is deliberately commented out in `tests/bot/test_bot.py` — don't reintroduce it.
8. **Settings are a singleton imported once**; the CLI calls `settings.reload_from_os()` to pick up env changes. After editing `tests/dandy_settings.py` or env vars in a dev loop, restart the process.
9. Live-LLM tests skip locally (hermetic-by-default, see [Testing approach](#testing-approach)), so a missing key never fails `just test`; to run them, export a real `AI_API_KEY` first. They can be slow/flaky against real endpoints — `just test-failed` (`--lf`) is the targeted rerun.
10. `DEBUG=True` settings swap in `dandy.core.debug`'s warning handler (prints stack traces for warnings) — useful when debugging LLM retry/validation flow.
11. Recorder output only persists to disk when `ALLOW_RECORDING_TO_FILE = True`; the `.dandy` artifact directory (and `recordings/`) is gitignored noise — don't commit it.

## Documentation

- `mkdocs.yml` (Material theme + `watch: [dandy, tests]`) is the source of truth. `docs/tutorials/` map 1:1 to package concepts (intel, prompts, bots, recorder, decoders, futures, caching, agents, errors, project structure).
- API reference pages are **generated** via `mkdocs-gen-files` running `docs/scripts/generate_api_reference.py`; don't hand-edit `reference/` output.
- Docstrings are Sphinx-style (see `mkdocstrings` handler config). Code examples in docs re-execute via `markdown-exec` — their output must stay correct.
- `mkdocs build --strict` (or `just docs-tests`) is a CI gate — broken links/warnings fail the build.
- Keep tutorials and `docs/changelog/v2_changelog.md` in sync when changing public API.
