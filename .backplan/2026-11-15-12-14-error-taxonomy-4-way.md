# Error taxonomy: replace Critical/Recoverable with a 4-way split

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-15-12-14

## End State
Every Dandy exception names the *category* of the failure — Configuration / Usage / External / Flow — instead of Critical/Recoverable: `dandy/shared/exceptions.py` defines `DandyError` with exactly four branches (`DandyConfigurationError`, `DandyUsageError`, `DandyExternalError`, `DandyFlowError`), every per-subsystem `exceptions.py` is renamed to match, all `raise`/`except` sites, tests, and docs (including `AGENTS.md`) use the new names, no old `*CriticalError`/`*RecoverableError` name remains anywhere in the repo, and the hermetic suite, `ruff`, `just lint-imports`, and `mkdocs build --strict` all pass.

## Observable Concern
The old names carry inconsistent semantics (e.g. `IntelRecoverableError` wrongly subclasses `DandyCriticalError`, dead classes like `BotRecoverableError` and `LlmValidationCriticalError` exist, `FileRecoverableError` is raised for non-transient bad-input cases in `media.py`); a blind rename would preserve those bugs — every raise site must be re-classified against the table below, not just renamed.

## Current State
- Verified by inspection:
  - `dandy/shared/exceptions.py`: `DandyError` → `DandyCriticalError` + `DandyRecoverableError`; also hosts `FileCriticalError`, `FileRecoverableError`, `RunStoppedError`, `RUN_STOPPED_MESSAGE`.
  - 14 per-subsystem `exceptions.py` files; 15 including `dandy/shared/connector/exceptions.py` (only ever a base for the http module).
  - ~108 `raise`/`except`/`assertRaises` sites in `dandy/`; ~33 test files reference old names (~170 hits); no references in `evals/`.
  - Dead classes (defined, never raised): `BotCriticalError`, `BotRecoverableError`, `HttpConnectorCriticalError`, `ServiceRecoverableError`, `CacheRecoverableError`, `RecorderRecoverableError`, `IntelRecoverableError`, `LlmValidationCriticalError`.
  - Bug: `IntelRecoverableError(DandyCriticalError)` — "Recoverable" name on the Critical branch (and dead).
  - Mislabels: `dandy/shared/media.py` raises `FileRecoverableError` for undecodable base64 (bad input, not transient); `dandy/shared/files.py` "path does not exist" raises `FileCriticalError` (arguably bad input, not config).
  - Public API: `dandy/__init__.py` exports `DandyError`, `DandyCriticalError`, `DandyRecoverableError` (flat + `Dandy` namespace). Decision: hard cut, no aliases (v3 alpha, migration doc covers it).
  - Docs referencing old names: `docs/user_guide/error_handling.md` (whole page), ~12 other doc pages, `docs/reference/{shared,domain,application}.md` mkdocstrings member lists, `docs/introduction/why_dandy.md`, `docs/roadmap/2026.md`, and many mentions in `AGENTS.md`.
- House conventions: per-subsystem `exceptions.py` extending the shared base; names are `<Subsystem><Category>Error`; tests are `unittest.TestCase` discoverable by pytest and `unittest discover`.

## Classification table (the contract for the rename)
Base branches (in `dandy/shared/exceptions.py`):
| New base | Meaning |
|---|---|
| `DandyConfigurationError` | settings/config invalid or missing; fix the config, not the call |
| `DandyUsageError` | bad arguments / API misuse in user code; fix the call site |
| `DandyExternalError` | outside Dandy failed: network, LLM response, file I/O, disk, timeout |
| `DandyFlowError` | flow control, not a fault (user stop) |

Subsystem mapping (old → new):
| Module | New classes |
|---|---|
| `shared/exceptions.py` | `FileUsageError` (was FileCriticalError), `FileExternalError` (was FileRecoverableError), `RunStoppedError(DandyFlowError)` |
| `shared/connector/` | module deleted |
| `shared/service/` | `ServiceConfigurationError` (was ServiceCriticalError; recoverable variant deleted) |
| `shared/typing/` | single `TypingUsageError` (both old classes were bad-input; collapsed) |
| `domain/intel/` | `IntelUsageError` (was IntelCriticalError; dead IntelRecoverableError deleted) |
| `domain/request/` (llm) | `LlmUsageError` (was LlmCriticalError — config setters, option range checks, message-shape rules), `LlmExternalError` (was LlmRecoverableError — response validation exhaustion, tool-cap exhaustion); `LlmValidationCriticalError` deleted |
| `domain/decision/` | `DecisionUsageError` (was DecisionCriticalError), `DecisionExternalError` (was DecisionRecoverableError, base for the retry loop), `DecisionNoChoicesExternalError`, `DecisionTooManyChoicesExternalError` |
| `domain/tool/` | `ToolUsageError` (was ToolCriticalError) |
| `domain/skill/` | `SkillUsageError` (was SkillCriticalError) |
| `application/bot/` | single `BotError(DandyUsageError)` (both dead classes collapsed to one for the future) |
| `application/agent/` | `AgentUsageError` (was AgentCriticalError — missing done field, invalid session name), `AgentExternalError` (was AgentRecoverableError — max turns, session load, oversized history) |
| `infrastructure/http/` | single `HttpConnectorError(DandyExternalError)` (was the Critical/Recoverable pair; only the recoverable was ever raised) |
| `infrastructure/future/` | `FutureUsageError` (non-positive timeout), `FutureExternalError` (timeout exceeded) |
| `infrastructure/recorder/` | `RecorderUsageError` (was RecorderCriticalError; recoverable variant deleted) |
| `infrastructure/cache/` | `CacheUsageError` (was CacheCriticalError; recoverable variant deleted) |
| `shared/settings/` + `shared/typed_kwargs.py` | raise `DandyConfigurationError` / `DandyUsageError` directly (as today, but re-pointed) |
| `dandy/__init__.py` | export `DandyError`, `DandyConfigurationError`, `DandyUsageError`, `DandyExternalError`, `DandyFlowError` (hard cut of the old two) |

Re-classification fixes folded in (not pure renames):
- `dandy/shared/media.py` undecodable-base64 raises → `FileUsageError`.
- `dandy/shared/files.py` missing-path raises stay `FileUsageError`; failed mkdir/rmdir/unlink stays `FileExternalError`.

## Plan
1. Rewrite the shared base taxonomy
   - `dandy/shared/exceptions.py`: four new base branches, `FileUsageError`, `FileExternalError`, `RunStoppedError(DandyFlowError)`, keep `RUN_STOPPED_MESSAGE`.
   - Delete `dandy/shared/connector/exceptions.py`.
   - Done when: `python -c "import dandy.shared.exceptions"` works and old names are gone.
2. Rewrite all 13 remaining per-subsystem `exceptions.py` files per the table
   - Delete dead classes; collapse single-use subsystems to one class.
   - Done when: `ruff check .` finds no imports of deleted names (expected failures at this point are only in modules not yet re-pointed).
3. Re-point every `raise`/`except` site in `dandy/` (~108 sites) using the table, including the two re-classification fixes in `media.py`
   - Update `dandy/__init__.py` exports + `Dandy` namespace (hard cut) and `__all__`.
   - Done when: `grep -rn "CriticalError\|RecoverableError" dandy/` returns nothing.
4. Update the test suite (~33 files) to the new names
   - Rewrite `tests/application/bot/test_bot_exceptions.py` for `BotError`.
   - Done when: `PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings python -m unittest discover -t . ./tests` passes and `just test` passes.
5. Update documentation to the new taxonomy
   - Rewrite `docs/user_guide/error_handling.md` (4-way story + subsystem table); fix mentions in the other ~12 doc pages; update `docs/reference/{shared,domain,application,infrastructure}.md` mkdocstrings member lists; `docs/introduction/why_dandy.md`; `docs/roadmap/2026.md`; add the taxonomy change to `docs/changelog/v3.md` and note it in `docs/migration/v2_to_v3.md`.
   - Done when: `just docs-tests` (mkdocs build --strict) passes.
6. Update `AGENTS.md` exception names to the new taxonomy (mechanical + the two re-classification notes)
   - Done when: `grep -n "CriticalError\|RecoverableError" AGENTS.md` returns nothing.

Steps 3–4 are one logical change but split so the framework is provably clean before tests are re-pointed. Steps 5–6 can run in parallel once 4 is green.

## Completion Test
```bash
just test                # full hermetic pytest suite green
PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings python -m unittest discover -t . ./tests   # CI parity runner green
ruff check . && ruff format --check .
just lint-imports
just docs-tests
grep -rn "CriticalError\|RecoverableError" dandy tests docs AGENTS.md   # only allowed hits: docs/migration + docs/changelog (history)
```

## Deviations
1. Pre-existing test failures left in place (not caused by, nor fixed by, this change)
    - What: 6 tests fail both before and after the rename, verified by `git stash` + rerun on the clean branch: 2 action-label assertions (`'Running' != 'Executing'`, `'Viewing' != 'Reading'` in the agent file-tools tests) and 4 `TestPrinterStory` frame-rendering assertions. Left untouched as out of scope.
    - Why: they fail identically on the untouched `v3/base` tree, so they are unrelated to the error taxonomy.
2. The CI-parity `unittest discover` run additionally reported `test_book_generation` (a `@live_llm_test`) failing with 1 chapter instead of 2
    - What: no code change; the live-LLM book workflow ran against a real endpoint during the run (the shell environment carried a real key) and came back short.
    - Why: live tests are excluded from the hermetic completion test (CI's hermetic job sets `AI_API_KEY=placeholder` so they skip); the pytest hermetic run skips it and is green apart from the 6 pre-existing failures above.
