# Concise DDD renames: dissolve domain/llm, rename generic modules

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-10-30-18-15

## End State

`dandy/domain/` contains exactly `intel, prompt, message, tokens, tool, decoder, request` (no `llm`), `dandy/shared/` contains `settings/` (no `conf/`), the modules `domain/tokens/estimate.py`, `domain/intel/annotation.py`, `shared/typing/signature.py`, `infrastructure/http/intel.py`, `infrastructure/cache/key.py`, `infrastructure/future/process.py`, `interfaces/cli/tui/text.py` exist while `domain/prompt/tools.py`, `dandy/domain/llm/`, `dandy/shared/conf/` no longer do, the classes `ToolService` / `ToolServiceMixin` / `ToolCallIntel` / `ToolCallsIntel` replace `LlmToolService` / `LlmToolServiceMixin` / `LlmToolCallIntel` / `LlmToolCallsIntel`, test dirs are `tests/infrastructure/file/`, `tests/infrastructure/http/`, `tests/shared/settings/`, every in-repo importer + import-linter seam + docs reference points at the new paths, the public API names in `dandy/__init__.py` are unchanged, and the full 476-test suite passes under both pytest and unittest discover with the 90% coverage gate, all 6 import-linter contracts, and the strict mkdocs build green.

## Observable Concern

The `shared/conf` -> `shared/settings` rename is the riskiest single move: `conf/__init__.py` re-exports the `settings` singleton and the `default_settings` submodule, `conf/settings.py` carries the sanctioned function-level `from dandy.shared.conf import default_settings` cycle-breaker (`# noqa: PLC0415`), and `interfaces/cli/utils.py:32` locates `shared/conf/default_settings.py` by **string path** — so ~35 import sites must re-point identically or the failure surfaces at import time, not test time. Secondary: the three import-linter seam edges naming `dandy.infrastructure.future.tools`, and unittest-discover count (476) across five test-directory moves (discovery requires the packages to import as `tests....`).

## Current State

Verified on branch `v3/base` (working tree carries the user's uncommitted cleanup + the executed flatten-llm-modules plan; nothing committed by this plan):

- **Baselines (this session)**: hermetic pytest `447 passed, 29 skipped in 3.93s`; clean-env unittest `Ran 476 tests` / `OK (skipped=29)`; `lint-imports` → `Contracts: 6 kept, 0 broken.`; `ruff check .` → 648 pre-existing errors; `ruff format --check .` → 155 files would be reformatted (repo-wide drift; style gate is "no new findings/failures", snapshots at `/tmp/ruff_baseline.txt` and per-file comparison).
- **`dandy/domain/llm/` contents** (all `__init__.py` empty): `request.py` (`LlmRequestBody`), `options.py` (`LlmOptions`, imports `domain.llm.exceptions`), `exceptions.py` (`LlmCriticalError`, `LlmValidationCriticalError`, `LlmRecoverableError`), `intelligence/prompts.py` (`service_system_prompt`, `service_system_validation_error_prompt`), `tool/intel.py` (`LlmToolCallIntel`, `LlmToolCallsIntel`), `decoder/{intel,exceptions,intelligence/prompts}.py`.
- **`dandy/shared/conf/`**: `__init__.py` RE-EXPORTS (`from dandy.shared.conf.settings import DandySettings, settings` — not empty), `settings.py` (`DandySettings`; module-level import of three `conf.utils` helpers + function-level `from dandy.shared.conf import default_settings  # noqa: PLC0415`), `utils.py` (`get_settings_module_name`, `get_cli_llm_config`, `get_settings_json_candidates`, `find_settings_json_file`, `load_settings_from_json_file`), `default_settings.py`. ~35 importers across dandy + tests (`from dandy.shared.conf import settings` is the dominant form). `interfaces/cli/utils.py:32` copies `Path(__file__).parent.parent.parent / 'shared' / 'conf' / 'default_settings.py'` by string.
- **Single-file subpackages**: `domain/intel/field/` (only `annotation.py`; importer: `domain/intel/intel.py`), `infrastructure/http/intelligence/` (only `intel.py`), `domain/prompt/tools.py` (only `list_to_str`; sole importer `domain/prompt/snippet.py:17`), `domain/llm/intelligence/` + `domain/llm/decoder/intelligence/` (one `prompts.py` each).
- **Generic util modules**: `domain/tokens/utils.py` (importers: `application/agent/coding_agent.py`, `domain/prompt/prompt.py`, `domain/llm/request.py`, `domain/message/message.py`, `infrastructure/recorder/llm_events.py`, `tests/domain/tokens/test_utils.py`, `tests/domain/message/test_message_content.py`); `shared/typing/tools.py` (importers: `domain/intel/factory.py`, `tests/shared/typing/test_tools.py`); `infrastructure/cache/tools.py` (importers: `dandy/__init__.py`, `infrastructure/cache/decorators.py`, `tests/infrastructure/cache/test_cache_hashing.py`); `infrastructure/future/tools.py` (importers: `dandy/__init__.py`, `application/decoder/service.py`, `application/bot/bot.py`, `application/llm/service.py`, `tests/infrastructure/future/test_tools.py`, plus **3 pyproject seam edges**: `application.bot.bot`, `application.llm.service`, `application.decoder.service` -> `infrastructure.future.tools`); `interfaces/cli/tui/tools.py` (`wrap_text_with_indentation` — used ONLY by `tests/interfaces/cli/test_tui_tools.py`, no library importer: pre-existing dead helper, kept, renamed).
- **`Llm*` class sites**: `application/tool/{service,mixin}.py` (class + `BaseService['dandy.application.tool.mixin.LlmToolServiceMixin']` string annotation), `application/llm/service.py` (import + MRO), `domain/llm/tool/intel.py` (+ importers `application/tool/service.py`, `infrastructure/llm/connector.py`, `infrastructure/recorder/tool_events.py`, `tests/application/tool/test_service.py` incl. `TestLlmToolService` class, `tests/infrastructure/llm/test_connector.py`).
- **Test dirs**: `tests/infrastructure/file_/` (1 file), `tests/infrastructure/http_/` (4 files) — no `import file`/`import http` stdlib usage inside, no `tests.infrastructure.file_`-style absolute self-imports (grep-verified); `tests/shared/conf/test_settings.py`; `tests/infrastructure/llm/config/test_conf.py` (imports `DandySettings`).
- **Docs**: `docs/reference/{domain,application,infrastructure,shared}.md` mkdocstrings directives name 15 moving modules/classes; `docs/architecture/layering.md` (2x `LlmToolService` + package bullets), `docs/domain_model/tactical.md` (`LlmToolCallIntel` + path), `docs/user_guide/{tool_calling,bots}.md`, `docs/migration/v2_to_v3.md` (v3-column paths + sed one-liners), `AGENTS.md` (package map rows, seams, env bullet 1/2/5/6/7, LLM flow, `LlmOptions`/tool-calling bullets, test-dir quirks row, `generate_cache_key` gotcha); `docs/changelog/v3.md` gets an entry. `archived_docs/` is read-only — untouched.
- **House conventions**: package-per-concept with same-basename module (`request/request.py`, `settings/settings.py`), empty `__init__.py` except documented re-exports (conf's is one — keep its shape), tests mirror packages, Sphinx docstrings, single quotes, line length 100, `ruff check` + `ruff format` no-new-findings gate.

## Plan

1. **Baseline re-check**
   - Re-run hermetic pytest, clean-env unittest discover, `lint-imports`; snapshot `ruff check .` count (648) and `ruff format --check` failing-file list (155) to compare after.
   - Done when pytest `447 passed, 29 skipped`, unittest `Ran 476 ... OK (skipped=29)`, `Contracts: 6 kept, 0 broken.`
2. **Extract `dandy/domain/tokens/utils.py` -> `estimate.py`**
   - Move module + `tests/domain/tokens/test_utils.py` -> `test_estimate.py`; re-point the 7 importers.
   - Done when suite green (both runners), `grep -rn 'dandy.domain.tokens.utils' dandy tests` -> zero hits.
3. **Fold `dandy/domain/prompt/tools.py` into `snippet.py`**
   - Move `list_to_str` verbatim into `domain/prompt/snippet.py` (before first use), delete `tools.py` + its import line; no other importers exist.
   - Done when suite green, `dandy/domain/prompt/tools.py` gone, `grep -rn 'prompt.tools' dandy tests` -> zero hits.
4. **Flatten `domain/intel/field/annotation.py` -> `domain/intel/annotation.py`**
   - Move + delete `field/`; re-point `domain/intel/intel.py`.
   - Done when suite green, `dandy/domain/intel/field/` gone, `grep -rn 'intel.field' dandy tests` -> zero hits.
5. **Move `domain/llm/` core to `domain/request/`**
   - New `dandy/domain/request/` (empty `__init__.py`); move `request.py`, `options.py`, `exceptions.py`, `intelligence/prompts.py` -> `request/prompts.py`; delete `intelligence/`. Fix internal `options.py` import to `dandy.domain.request.exceptions`. Move `tests/domain/llm/test_request.py` -> `tests/domain/request/test_request.py` (+`__init__.py`). Re-point all importers via exact sed: `dandy.domain.llm.intelligence.prompts` -> `dandy.domain.request.prompts`, `dandy.domain.llm.exceptions` -> `dandy.domain.request.exceptions`, `dandy.domain.llm.options` -> `dandy.domain.request.options`, `dandy.domain.llm.request` -> `dandy.domain.request.request` (library + tests, incl. `application/llm/service.py`, `application/decoder/decoder.py`, `infrastructure/llm/{connector,config}.py`, `infrastructure/recorder/llm_events.py`).
   - Done when suite green, `lint-imports` KEPT, `grep -rn 'dandy.domain.llm.request\|dandy.domain.llm.options\|dandy.domain.llm.exceptions\|dandy.domain.llm.intelligence' dandy tests` -> zero hits.
6. **Move `domain/llm/tool/intel.py` -> `domain/tool/intel.py` + class renames**
   - `LlmToolCallIntel` -> `ToolCallIntel`, `LlmToolCallsIntel` -> `ToolCallsIntel` (definition + 5 importer files incl. both tests); delete `domain/llm/tool/`.
   - Done when suite green, `grep -rn 'LlmToolCall\|dandy.domain.llm.tool' dandy tests` -> zero hits.
7. **Move `domain/llm/decoder/` -> `domain/decoder/`, delete `domain/llm/`**
   - New `dandy/domain/decoder/` (empty `__init__.py`); move `intel.py`, `exceptions.py`, `intelligence/prompts.py` -> `prompts.py`; re-point sed: `dandy.domain.llm.decoder.intelligence.prompts` -> `dandy.domain.decoder.prompts` first, then `dandy.domain.llm.decoder.` -> `dandy.domain.decoder.` (`application/decoder/{decoder,service}.py`); move `tests/domain/llm/decoder/` (incl. `intelligence/`) -> `tests/domain/decoder/`; delete `dandy/domain/llm/` and empty `tests/domain/llm/` entirely.
   - Done when suite green (both runners, 476 count), `ls dandy/domain/llm` and `ls tests/domain/llm` fail, `grep -rn 'dandy.domain.llm' dandy tests` -> zero hits.
8. **Rename `shared/conf/` -> `shared/settings/` (`utils.py` -> `load.py`)**
   - Move package + `tests/shared/conf/` -> `tests/shared/settings/` + `tests/infrastructure/llm/config/test_conf.py` -> `test_settings.py`; fix `settings/__init__.py` re-export to `dandy.shared.settings.settings`; re-point sed (specific first): `dandy.shared.conf.utils` -> `dandy.shared.settings.load`, `dandy.shared.conf.settings` -> `dandy.shared.settings.settings`, `from dandy.shared.conf import` -> `from dandy.shared.settings import` (~35 files incl. the PLC0415 line in `settings/settings.py`); fix the string path `'shared' / 'conf'` -> `'shared' / 'settings'` in `interfaces/cli/utils.py`.
   - Done when suite green (both runners, 476 count), `grep -rn 'dandy.shared.conf\|shared' / 'conf' dandy tests` -> zero hits, `python -c 'import dandy'`-level settings load still resolves (`just test` covers it).
9. **Rename `shared/typing/tools.py` -> `signature.py`**
   - Move + `tests/shared/typing/test_tools.py` -> `test_signature.py`; re-point `domain/intel/factory.py`.
   - Done when suite green, `grep -rn 'shared.typing.tools' dandy tests` -> zero hits.
10. **Flatten `infrastructure/http/intelligence/intel.py` -> `infrastructure/http/intel.py`**
    - Move + delete `intelligence/`; re-point ~12 importers (http connector/service, `infrastructure/llm/config.py`, 9 test files incl. the already-moved `tests/domain/decoder/test_decoder.py`).
    - Done when suite green, `grep -rn 'http.intelligence' dandy tests` -> zero hits.
11. **Rename `infrastructure/cache/tools.py` -> `key.py`**
    - Move; re-point `dandy/__init__.py`, `infrastructure/cache/decorators.py`, `tests/infrastructure/cache/test_cache_hashing.py`.
    - Done when suite green, `grep -rn 'infrastructure.cache.tools' dandy tests` -> zero hits.
12. **Rename `infrastructure/future/tools.py` -> `process.py` + seam rewrite**
    - Move + `tests/infrastructure/future/test_tools.py` -> `test_process.py`; re-point 4 importers + `dandy/__init__.py`; rewrite the 3 pyproject seam edges `-> dandy.infrastructure.future.tools` to `-> dandy.infrastructure.future.process`.
    - Done when suite green, `lint-imports` KEPT (6), `grep -rn 'infrastructure.future.tools' dandy tests pyproject.toml` -> zero hits.
13. **Rename `interfaces/cli/tui/tools.py` -> `text.py`**
    - Move + `tests/interfaces/cli/test_tui_tools.py` -> `test_text.py` (the only importer).
    - Done when suite green, `grep -rn 'tui.tools' dandy tests` -> zero hits.
14. **Rename `LlmToolService`/`LlmToolServiceMixin` -> `ToolService`/`ToolServiceMixin`**
    - `application/tool/{service,mixin}.py` (class defs + the `BaseService['...mixin.LlmToolServiceMixin']` string annotation + property return type), `application/llm/service.py` (import + MRO), `tests/application/tool/test_service.py` (`TestLlmToolService` class). Replace `LlmToolServiceMixin` before `LlmToolService`.
    - Done when suite green (reset-chain tests pass), `grep -rn 'LlmToolService' dandy tests` -> zero hits.
15. **Rename test dirs `file_` -> `file`, `http_` -> `http`**
    - Move both dirs (git mv-free plain mv); re-point any `tests.infrastructure.file_`/`http_` absolute imports (verified none exist, re-verify at step anchor).
    - Done when unittest discover still reports 476 tests and pytest green.
16. **Docs, AGENTS.md, changelog**
    - `docs/reference/domain.md`: `domain.llm.request.LlmRequestBody` -> `domain.request.request.LlmRequestBody`, `domain.llm.options.LlmOptions` -> `domain.request.options.LlmOptions`, `domain.tokens.utils` -> `domain.tokens.estimate`, `domain.llm.tool.intel` -> `domain.tool.intel` (member names `ToolCallIntel`/`ToolCallsIntel`), `domain.llm.decoder.{intel,exceptions}` -> `domain.decoder.{intel,exceptions}`, `domain.llm.exceptions` -> `domain.request.exceptions` (plus any `intel.field.annotation` / `prompt.tools` members).
    - `docs/reference/application.md`: `LlmToolService`/`LlmToolServiceMixin` -> `ToolService`/`ToolServiceMixin`.
    - `docs/reference/infrastructure.md`: `http.intelligence.intel` -> `http.intel`, `cache.tools` -> `cache.key`, `future.tools.process_to_future` -> `future.process.process_to_future`.
    - `docs/reference/shared.md`: `conf.settings.DandySettings` -> `settings.settings.DandySettings`, `conf.utils` -> `settings.load`, `conf.default_settings` -> `settings.default_settings`, `typing.tools` -> `typing.signature`.
    - `docs/architecture/layering.md`, `docs/domain_model/{tactical,glossary,contexts}.md`, `docs/user_guide/{tool_calling,bots}.md`: class + path mentions; `docs/migration/v2_to_v3.md`: v3-column targets + sed one-liners; `AGENTS.md`: package-map rows (domain/shared rows), seams (future.process edges), env bullets 1/2/5/6/7 (`shared/settings/...` paths, `domain/tokens/estimate.py`), LLM flow + `LlmOptions`/tool-calling/Decoder bullets, test-dir quirks row (drop `file_`/`http_` mention), `generate_cache_key` gotcha (`cache/key.py`); `docs/changelog/v3.md`: entry with old -> new path table.
    - Done when `just docs-tests` strict build clean and the old-path grep gate over `docs/` + `AGENTS.md` returns zero hits.
17. **Final verification**
    - Run the completion test, quote real output, set `Status: Executed`.
    - Done when every check passes with unchanged test counts (476 / 29 skipped).

## Completion Test

All run from `/home/nathanj/PycharmProjects/dandy`, all must pass:

1. Hermetic pytest: `AI_API_KEY=test-key PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings .venv/bin/python -m pytest . -q` -> 447 passed, 29 skipped, 0 failed.
2. CI-parity unittest (clean env): `env -i PATH="$PATH" HOME="$HOME" .venv/bin/python -m unittest discover -t . ./tests` -> 476 tests, 0 failures, 29 skipped.
3. Coverage gate: `PYTHONPATH=. AI_API_KEY=placeholder DANDY_SETTINGS_MODULE=tests.dandy_settings .venv/bin/python -m coverage run -m unittest discover -t . ./tests && .venv/bin/python -m coverage report --fail-under=90` -> TOTAL >= 90%, exit 0.
4. Architecture: `lint-imports` -> all 6 contracts KEPT.
5. Docs: `just docs-tests` -> strict mkdocs build clean.
6. Style: `ruff check .` error count <= 648 and `ruff format --check .` reformat list a subset of the pre-run 155-file snapshot (no new findings/failures vs baseline).
7. Old-path grep gates (zero hits each over `dandy tests docs AGENTS.md pyproject.toml`): `dandy\.domain\.llm`, `dandy\.shared\.conf`, `dandy\.domain\.tokens\.utils`, `dandy\.domain\.prompt\.tools`, `dandy\.domain\.intel\.field`, `dandy\.shared\.typing\.tools`, `dandy\.infrastructure\.http\.intelligence`, `dandy\.infrastructure\.cache\.tools`, `dandy\.infrastructure\.future\.tools`, `dandy\.interfaces\.cli\.tui\.tools`, `LlmToolService|LlmToolCallIntel|LlmToolCallsIntel`, `tests/infrastructure/file_|tests/infrastructure/http_`.
8. Structure: `ls dandy/domain` -> exactly `decoder intel message prompt request tool tokens`; `ls dandy/domain/request` -> `__init__.py exceptions.py options.py prompts.py request.py`; `ls dandy/shared` has `settings/` no `conf/`; `ls dandy/shared/settings` -> `__init__.py default_settings.py load.py settings.py`; `ls tests/infrastructure` has `file/` `http/` (no underscores); `dandy/domain/llm/` and `dandy/shared/conf/` do not exist.
9. Public API smoke: `PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings .venv/bin/python -c 'import dandy; print(dandy.Bot, dandy.Prompt, dandy.BaseTool, dandy.BaseIntel, dandy.generate_cache_key, dandy.process_to_future)'` -> prints classes, exit 0.

## Deviations

1. Step 4's atomic command broke its own `&&` chain.
   - What: `rmdir dandy/domain/intel/field` failed (the directory still held `__init__.py` + `__pycache__`), so the re-pointing sed and its gate never ran and the first re-anchor showed 61 import errors; re-ran the sed on `dandy/domain/intel/intel.py` after removing the leftover `__init__.py` and the suite returned to 447/476 green.
   - Why: `mv` moved only `annotation.py`, leaving the package `__init__.py` behind; the `&&` chain silently skipped the fix-up steps, and the printed `gate:1` was the rmdir exit code, not a clean grep.
2. Step 7 hit a test-to-test absolute fixture import.
   - What: `tests/domain/decoder/test_decoder.py:12` imported fixtures as `from tests.domain.llm.decoder.intelligence.decoders import ...`; re-pointed to `tests.domain.decoder.intelligence.decoders` (unittest discover had dropped the module: 472 vs 476 tests).
   - Why: `tests.*` absolute fixture imports are a move-sensitive reference class the per-file `dandy.*` sed does not cover (same class as flatten-plan deviation 6).
3. Changelog folded into the existing v3.1.0 section instead of a new entry.
   - What: the rename table was merged into the v3.1.0 "Restructured (breaking)" bullet list (which already carried the flatten's old -> new map) rather than added as a separate dated sub-entry, and the stale "now holds only" paragraph was rewritten to the final state.
   - Why: v3.1.0 is the in-progress release; flatten and this rename ship together, so the release entry describes the cumulative v3.0 -> current move in one table.

## Execution Report

Executed 2026-10-30. Steps 2-17 ran in order; the suite was re-anchored green (pytest + unittest discover + `lint-imports`) after every code step, and the completion test ran last. Completion test output (all real, quoted):

1. Hermetic pytest: `447 passed, 29 skipped in 3.89s`
2. CI-parity unittest (clean env): `Ran 476 tests in 3.467s` / `OK (skipped=29)`
3. Coverage gate: `TOTAL 3959 247 94%` with `--fail-under=90` exiting 0
4. Architecture: `Contracts: 6 kept, 0 broken.` (incl. the three rewritten `-> dandy.infrastructure.future.process` seam edges)
5. Docs: `just docs-tests` -> `Documentation built in 0.86 seconds` (strict, clean)
6. Style: `ruff check .` -> `Found 648 errors.` (identical to the pre-run baseline of 648); `ruff format --check .` -> `155 files would be reformatted` (identical count to baseline; the per-file list shifts only by the renamed paths)
7. Old-path grep gates over `dandy tests docs AGENTS.md pyproject.toml`: zero hits on all 12 patterns (the only remaining old-path text is the changelog's old -> new table and the migration guide's v2 left column, both intentional)
8. Structure: `ls dandy/domain` -> `decoder intel message prompt request tokens tool`; `dandy/domain/request` -> `__init__.py exceptions.py options.py prompts.py request.py`; `dandy/shared/settings` -> `__init__.py default_settings.py load.py settings.py`; `tests/infrastructure` -> `cache file future http llm recorder`; `dandy/domain/llm/` and `dandy/shared/conf/` do not exist
9. Public API smoke: `import dandy` prints `Bot`, `Prompt`, `BaseTool`, `BaseIntel`, `generate_cache_key`, `process_to_future` — exit 0

Result: end state holds. Nothing committed (no instruction to). One finding, not acted on: `dandy/interfaces/cli/tui/text.py::wrap_text_with_indentation` has no library importer (only its test) — a dead-code candidate for a later cleanup.
