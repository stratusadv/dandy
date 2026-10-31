# Dandy entry-point namespace

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed (user sign-off: "yes")
- Date: 2026-10-30-22-52

## End State

`from dandy import Dandy` works and `Dandy.<name>` reaches the full public API — the 20
current exported names plus 4 new public names (`Decision`, `DefaultIntel`,
`LlmOptions`, `MessageHistory`) — with each `Dandy.X` the identical object as
`dandy.X`, proven by hermetic tests, documented in the docs and AGENTS.md, with every
existing gate (pytest, unittest, coverage, import-linter, docs, ruff) still green.

## Observable Concern

AGENTS.md mandates that `dandy/__init__.py` "must stay a thin re-export layer with no
logic" and is the one module allowed to touch every layer. The `Dandy` namespace must
therefore be pure re-binding — a docstring plus class attributes referencing already
imported names, with no methods, no `__init__`, no factory behavior. Any drift toward
helper methods makes it a second composition root with logic and breaks that rule.

## Current State

Verified 2026-10-30 (working tree at the skill-feature close-out):

- `dandy/__init__.py` — composition root; imports 20 curated names across all layers and
  lists them in `__all__` (alphabetical): `Agent`, `BaseIntel`, `BaseListIntel`,
  `BaseSkill`, `BaseTool`, `Bot`, `DandyCriticalError`, `DandyError`,
  `DandyRecoverableError`, `MemoryCache`, `Prompt`, `Recorder`, `SqliteCache`,
  `cache_to_memory`, `cache_to_sqlite`, `generate_cache_key`, `process_to_future`,
  `recorder_to_html_file`, `recorder_to_json_file`, `recorder_to_markdown_file`.
- Import contracts — 6 forbidden contracts in `pyproject.toml`, all keyed to the layer
  packages (`dandy.domain`, `dandy.shared`, `dandy.application`,
  `dandy.infrastructure`, `dandy.interfaces`). The root `dandy/__init__` module is the
  source of no contract, so a class defined there that only re-binds already-imported
  names adds zero import edges; `.venv/bin/lint-imports` currently reports
  `Contracts: 6 kept, 0 broken.`
- No existing `Dandy` symbol — only `DandyCli`, `DandyError`, `DandyCriticalError`,
  `DandyRecoverableError`, `DandySettings`, `DandyCliSession`; the name is free.
- Expansion candidates (all stable, already rendered in the API reference, so no new
  reference entries are needed):
  - `LlmOptions` — `dandy/domain/request/options.py:22` (reference:
    `docs/reference/domain.md`); whole user-guide page
    (`docs/user_guide/options_and_context.md`) is about it.
  - `DefaultIntel` — `dandy/domain/intel/intel.py:271` (the prose-tolerant target).
  - `MessageHistory` — `dandy/domain/message/message.py:154` (agent conversations,
    `Agent.history`).
  - `Decision` — `dandy/application/decision/decision.py` (user guide page
    `docs/user_guide/decision.md`; value object with `as_enum()`).
- Docs style — `docs/introduction/what_is_dandy.md` and
  `docs/getting_started/quick_start.md` show flat imports (`from dandy import Bot,
  Prompt`); the entry point gets a short section/note there.
- Tests — no top-level test file in `tests/` today (layer dirs + `consts.py` /
  `dandy_settings.py`); a root-mirroring `tests/test_dandy.py` is discoverable by both
  runners (`pytest .` and `python -m unittest discover -t . ./tests`).
- Gate baselines (skill-feature close-out): pytest `502 passed, 29 skipped`; unittest
  `Ran 531 tests` / `OK (skipped=29)`; coverage TOTAL 94% (4226 stmts), exit 0 at
  `--fail-under=90`; lint-imports `Contracts: 6 kept, 0 broken.`; `just docs-tests`
  exit 0; `ruff check .` 648 findings; `ruff format --check .` 155 files.

## Assumptions (flagged for approval)

1. `Dandy` is a **class** defined in `dandy/__init__.py` (not a separate module):
   pure namespace of class attributes, no methods — this keeps the composition root as
   the only all-layers module and honors the "thin re-export layer" rule.
2. The 4 expansion names are added to the flat `__all__` too, so
   `from dandy import LlmOptions` and `Dandy.LlmOptions` are consistent. Trim the set at
   approval if unwanted.
3. **No behavior change** (user chose pure namespace): `Dandy.Agent` is the plain
   `Agent` class — it still requires a `bot`, so the `Dandy.Agent().run()` pseudo-code
   is *not* enabled; `Dandy.Agent(bot).run(...)` is the real shape.
4. `'Dandy'` joins `__all__` so `from dandy import *` picks it up.
5. No default-bot sugar, no factory methods, no file discovery — none of it.

## Plan

1. **Entry-point namespace in the composition root**
   - In `dandy/__init__.py`: add the 4 new imports
     (`Decision`, `DefaultIntel`, `LlmOptions`, `MessageHistory`); add
     `class Dandy` (Sphinx docstring explaining the namespace; class attributes
     binding all 24 public names); extend `__all__` to the 25 entries
     (24 public names + `'Dandy'`), keeping alphabetical order.
   - Done when a clean interpreter proves identity and usability:
     `PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings .venv/bin/python -c
     "from dandy import Dandy, Bot, Prompt, LlmOptions; assert Dandy.Bot is Bot and
     Dandy.Prompt is Prompt and Dandy.LlmOptions is LlmOptions;
     print(Dandy.Prompt().text('hi').to_str())"` prints `hi`, and
     `.venv/bin/lint-imports` still reports `Contracts: 6 kept, 0 broken.`
2. **Hermetic tests**
   - New `tests/test_dandy.py` (root mirror, `unittest.TestCase`): (a) every one of the
     24 public names on `Dandy` is `is` the same object as the flat root attribute
     (no shadowing, no re-wrapping); (b) construction smokes through the namespace
     (`Dandy.Prompt().text(...).to_str()`, a `Dandy.BaseSkill` subclass instance,
     `Dandy.LlmOptions()`); (c) `__all__` contains `'Dandy'` and every listed name
     resolves on the module.
   - Done when the file is green under both
     `AI_API_KEY=test-key PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings
     .venv/bin/python -m pytest tests/test_dandy.py -q` and
     `env -i PATH="$PATH" HOME="$HOME" .venv/bin/python -m unittest discover -t .
     ./tests` (no failures).
3. **Docs**
   - `docs/introduction/what_is_dandy.md`: short "One import" note after "One example"
     showing `from dandy import Dandy` and `Dandy.Bot` / `Dandy.Prompt`.
   - `docs/getting_started/quick_start.md`: one-line note that the same API is also
     reachable via the `Dandy` namespace.
   - `docs/changelog/v3.md`: v3.1.0 Added bullet (the `Dandy` namespace + the 4 new
     public names).
   - `AGENTS.md`: Public API surface section updated with the `Dandy` namespace and the
     4 new exports (and a note that the class must stay logic-free re-binding).
   - Done when `just docs-tests` exits 0.
4. **Completion test + close**
   - Run the full battery below, quote real output, append any deviations, set
     `Status: Executed`, `ruff format` the plan doc.
   - Done when every completion-test line passes.

## Completion Test

All run from `/home/nathanj/PycharmProjects/dandy`, all must pass (N = new hermetic
test count; baselines in Current State):

1. Namespace smoke (identity + usability), exit 0, prints `hi`:
   `PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings .venv/bin/python -c "from dandy import Dandy, Bot, Prompt, LlmOptions; assert Dandy.Bot is Bot and Dandy.Prompt is Prompt and Dandy.LlmOptions is LlmOptions; print(Dandy.Prompt().text('hi').to_str())"`
2. Namespace breadth: the same interpreter prints exactly `24` for
   `len([n for n in dir(Dandy) if not n.startswith('_')])`.
3. Hermetic pytest:
   `AI_API_KEY=test-key PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings .venv/bin/python -m pytest . -q`
   -> 502+N passed, 29 skipped, 0 failed.
4. CI-parity unittest (clean env):
   `env -i PATH="$PATH" HOME="$HOME" .venv/bin/python -m unittest discover -t . ./tests`
   -> 531+N tests, 0 failures, 29 skipped.
5. Coverage gate:
   `PYTHONPATH=. AI_API_KEY=placeholder DANDY_SETTINGS_MODULE=tests.dandy_settings .venv/bin/python -m coverage run -m unittest discover -t . ./tests && .venv/bin/python -m coverage report --fail-under=90`
   -> TOTAL >= 90%, exit 0.
6. Architecture: `.venv/bin/lint-imports` -> `Contracts: 6 kept, 0 broken.` (the
   namespace adds no import edges).
7. Docs: `just docs-tests` -> exit 0.
8. Style: `.venv/bin/ruff check .` <= 648 findings; `.venv/bin/ruff format --check .`
   reformat count <= 155 (format the new files/doc pages first).

## Deviations

1. **Prompt smoke assertion detail (step 2)** — What: the construction smoke in
   `tests/test_dandy.py` initially asserted `Dandy.Prompt().text('hello').to_str()
   == 'hello'` and failed, because `Prompt.to_str()` renders snippets with a trailing
   newline (`'hello\n'`). The test now asserts on the stripped rendering
   (`rendered.strip() == 'hello'`). Why: keeps the smoke robust to snippet-formatting
   details while still proving the namespace object behaves as `Prompt`. No product
   change; the plan's own completion-test smoke prints `hi` as specified (the printed
   line carries Prompt's trailing newline).

## Execution Report

N = 6 new hermetic tests (`tests/test_dandy.py`: namespace identity for all 24 public
names, exact breadth, Prompt/BaseSkill/LlmOptions construction smokes, `__all__`
completeness).

1. Namespace smoke: printed `hi` and `24`, exit 0 (identity asserts
   `Dandy.Bot is Bot`, `Dandy.Prompt is Prompt`, `Dandy.LlmOptions is LlmOptions`).
2. Namespace breadth: exactly `24` public attributes on `Dandy`.
3. Hermetic pytest:
   `508 passed, 29 skipped, 49 subtests passed in 4.15s` (502 + 6).
4. CI-parity unittest (clean env):
   `Ran 537 tests in 3.599s` / `OK (skipped=29)` (531 + 6).
5. Coverage gate: `TOTAL  4254  253  94%`, `--fail-under=90` exit 0.
6. Architecture: `Contracts: 6 kept, 0 broken.` (no new edges).
7. Docs: `Documentation built in 0.99 seconds`, exit 0.
8. Style: `Found 648 errors.` (baseline 648);
   `155 files would be reformatted, 268 files already formatted` (baseline 155).
