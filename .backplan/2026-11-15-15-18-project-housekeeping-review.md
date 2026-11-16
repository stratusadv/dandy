# Project housekeeping review and plan

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-15-15-18

> Headless session: goal derived from the request (full project review + housekeeping
> backplan, safe/simple changes only, deliverable is this doc for review). Assumed,
> flagged here per procedure; the approval step still covers it.

## End State

This doc contains a feature-by-feature review of the whole project (strengths and
findings) plus a forward plan of safe, behavior-preserving housekeeping changes, and
the user has reviewed it.

## Observable Concern

The working tree's test suite is RED right now (9 failures, all from today's two
commits `8b92e70` + `d802b24`), so the first housekeeping item is repairing the
baseline — everything else in the plan hangs on a green `just test`.

## Current State

Verified facts from this session (2026-11-15, branch `v3/base`, clean tree):

- **Test suite is red.** `just test` → `9 failed, 964 passed` in ~203s. All 9 are
  label/unicode drift between today's commits and their tests:
  - `ReadFileTool.action_label` is `'Viewing'` (changed in `8b92e70`); the test
    asserts `'Reading'`.
  - `RunCommandTool.action_label` is `'Running'`; the test asserts `'Executing'`
    (which the label has *never* been per `git log -S` — the test codified a
    docstring, not the code).
  - `dandy/interfaces/cli/tui/printer.py:270` prints the bullet as `◈ ` (space inside
    the colored span); `test_printer.py` expects `◈{term.normal} ` (7 failures, 5 of
    them in `TestPrinterFileChangeSections`, 4 in `TestPrinterStory`).
  - The 4 story failures are a second, older drift: `StoryProgress.frame()` renders
    the evaluating phrase in `bold_grey` (line 242), but the tests (written when it
    was `bold_blue`) assert `bold_grey not in frame`. The tests were last touched
    today only for the ◈ bullet, so they predate the grey change.
  - Note: `just test` runs `pytest .`, which also collects `evals/` (conftest.py only
    excludes `evals/runs`); CI runs `-t . ./tests` and excludes `evals/`.
- **`ruff check .` is failing (1006 errors)** even though AGENTS.md implies it is
  clean:
  - `archived_docs/` (explicitly read-only) contributes ~500 — it was never
    excluded from ruff.
  - `evals/` (self-contained eval harness, hidden tests) contributes ~400 — never
    excluded either; its 167 PT errors are in `evals/task/hidden_tests/`, which the
    repo convention keeps outside normal tooling.
  - `dandy/` + `tests/` contribute 486. The substantive remainder after ignoring
    docstring-style noise: 76 in `dandy/` (36 E501 lines, 8 S608 SQL f-strings —
    safe but flagged, 6 W291 trailing whitespace in `tui/ascii.py`, 4 DTZ005
    `datetime.now()` in `recording.py`, B010 in `bot.py`, etc.) and ~410 in
    `tests/` (182 ANN201 missing return annotations, 50 E501, 46 ANN001, 40 RUF001
    ambiguous unicode — mostly intentional `•`/`↳`/`◈` glyphs in assertions, plus
    unused imports/variables: 8 F401, 4 F841, 2 F811).
  - No ruff CI gate exists (only tests/lint-imports/codespell/docs), which is why
    this accumulated.
  - `ruff format --check .` wants to reformat 9 files (4 in tests, 5 others).
  - `ty` is warn-only and not a gate (525 diagnostics) — out of scope.
- **Doc rot vs. `3.0.0a5` code** (code moved on, docs did not):
  - `AGENTS.md` says `v3.0.0a3` in the header; docs/getting_started/cli.md and
    docs/roadmap/2026.md still cite `3.0.0a1`; `pyproject.toml` says
    `Development Status :: 5 - Production/Stable` while shipping `3.0.0a5`.
  - AGENTS.md (3×) and docs (2×) say the CLI agent runs
    `max_tool_iterations=None` (uncapped), but `Agent` has capped turns at
    `AGENT_MAX_TOOL_ROUNDS_DEFAULT = 200` since `4701db8`+ and `CliAgent` passes it
    through unchanged — AGENTS.md's "the CLI agent opts into this" is false.
  - AGENTS.md says `read_file` → label `'Reading'` and file-change bullets are
    "green/blue/red" — code now has `'Viewing'` and purple for modified.
  - AGENTS.md's StoryProgress description (bold blue thinking phrase, `↳` arrow
    detail) predates the phrase/arrow styling and the `◈` bullet.
  - `README.md` still documents `/clear`, which no longer exists (changelog v3
    itself says `/new` superseded it); README also predates the one-shot flag set
    and the `dandy -r`/`-s` resume forms.
  - `docs/user_guide/agent.md` documents `max_tool_rounds=None` as "no cap" with
    default "200" — consistent, but the cli_agent.md architecture diagram (line 42)
    still says `max_tool_iterations=None  # uncapped`.
  - `docs/changelog/v3.md` has an `## Unreleased` section (tool risk flags, error
    taxonomy) that matches shipped behavior but has never been versioned.
  - `tests/example_project_book.md` — a ~committed generated artifact (gitignored
    pattern `example_book.md` exists but this name slipped through); no test
    reference found, content is a generated book title page.
- **Dead / low-value code** (verified no references outside tests or self):
  - `dandy/interfaces/cli/main.py` calls `sys.path.append(str(CWD_PATH))` twice
    (module import-time line 28 and again in `main()` line 89) — redundant.
  - `dandy/interfaces/cli/main.py:25` a commented-out `print(...)` line (dead).
  - `dandy/application/agent/session.py:22` `project_dandy_cli_path` — no callers.
  - `dandy/application/agent/session.py:14` `post_init()` — a custom,
    non-pydantic-lifecycle name; the only caller is `main.py`. `model_post_init`
    or plain attribute reassignment is the idiom used elsewhere.
  - `dandy/infrastructure/llm/connector.py:195` `_reset_prompt_retry_attempt()` —
    defined, never called.
  - `dandy/shared/utils.py:24` `generate_forwardable_kwargs_if_not_none` — no
    callers anywhere.
  - `dandy/application/bot/bot.py:51` `get_description()` — classmethod returning
    nothing, no callers; `bot.py:21` `self._recorder_called = None` is re-assigned
    by `bot_events.py` and only read there — fine, but `get_description` is noise.
  - `dandy/application/decision/decision.py` `Decision.process` re-raises
    `DecisionTooManyChoicesExternalError` caught and immediately re-raised; and
    `Decision` keeps a `self._llm_connector` it never exposes. Minor.
  - `dandy/application/diligence/*`: the `trigger_level` / `trigger_operator`
    attributes on all three diligence classes and `BaseDiligence` are **never
    consulted by any activation logic** — `activate()` just sets a bool. They are a
    vestigial API (tests only exercise `activate()`).
  - `dandy/shared/typing/constants.py` `STRING_TO_TYPE_MAP` has JS-isms (`'null'`,
    `'undefined'`) feeding tool-schema derivation — harmless but confusing.
- **Correctness nits** (safe to fix, behavior-visible only on failure paths):
  - `dandy/shared/settings/default_settings.py:24` reads
    `os.getenv('AI_API_POST', 443)` — typo for `AI_API_PORT` (every settings module
    and the committed `development.env` use `AI_API_PORT`); also
    `int(None)` if the var is set-but-empty. `tests/dandy_settings.py` uses
    `AI_API_PORT` correctly.
  - `dandy/domain/intel/factory.py:69` f-string typo: `'...one of f{required_attributes}.'`
    renders a stray `f` in the error message.
  - `dandy/infrastructure/recorder/recorder.py:38-39`: the "choices" help message is
    built only when `len(cls.recordings) == 0` — i.e. it is empty exactly when it
    would say "choices are []", and silent exactly when choices exist. Inverted
    condition.
  - `dandy/infrastructure/cache/decorators.py:17` `if cached_value:` — falsy cached
    values (`''`, `0`, `False`, empty Intel) are never served from cache.
  - `dandy/infrastructure/cache/sqlite/cache.py` stores pickled bytes in a `TEXT`
    column (works via sqlite's dynamic typing; `BLOB` is correct); `clean()` only
    deletes once overage reaches 10% of limit, so the table can grow well past it.
  - `dandy/infrastructure/future/future.py:23` mutates the shared executor's
    `_max_workers` on every `AsyncFuture` — no-op after first submit (executor
    started lazily); harmless but wrong; should be set once at creation.
  - `dandy/shared/settings/settings.py:24-25` `self._settings_module_name = ...`
    uses the literal `Ellipsis` as a sentinel in two places (`_user_settings` too),
    and `_import_settings_module` checks `is not ...` — works but obscure.
  - `dandy/shared/connector/exceptions.py` is an empty stub (no symbols) — the
    module exists only to carry a `DiligenceType` TypeVar; could fold into
    `connector.py`, or leave.
  - `dandy/interfaces/cli/tui/ascii.py` — trailing whitespace on 6 lines of the
    ASCII banner (W291).
- **Repo hygiene**:
  - `.gitignore` has a malformed line `!dandy/cli/actions/build/` — a negation of a
    path that never existed (the v2 actions system is gone); it is inert and
    confusing.
  - `cats.md` (a pet bio) is tracked at repo root; `.profile/` exists on disk empty
    and untracked.
  - `tests/application/example_project/` + `docs/user_guide/example_project.md`
    reference the book example; `tests/example_project_book.md` at tests/ root is
    the stray output of that example's cache run.
  - `docs/reference/` and `docs/architecture/` were checked and are current with the
    guard/agent API (member lists include `Guard*`, `StoryBeat`) — good.
  - `.backplan/` docs are committed (45 files) even though the backplan skill says
    plan docs are never committed unless directly instructed — housekeeping
    candidate for `.gitignore` (keep in place, stop tracking is a user decision).
  - `development.env` is present on disk but untracked (correct — `.gitignore`
    `*.env`); CI supplies equivalents via secrets. Fine.
- **Architecture is sound** (re-verified against code): import-linter 6 contracts
  all KEPT; `BaseService`/mixin composition, Intel factory, LlmConnector
  request/retry/fenced-JSON recovery, ToolService loop + guard chain,
  `Agent`/`CliAgent` turn/compaction/session store, CLI one-shot/REPL dispatch,
  skill loader, and the hermetic test strategy all match the documented design.
  No structural rework is proposed — this plan is hygiene, not redesign.
- **Strengths worth keeping** (do not "fix"): the `intelligence/` test fixture
  convention, `evals/` isolation, `tests/dandy_settings.py` placeholder
  hermeticity, the `SessionStore` slug/validation design, `truncate_output`'s
  line-aware capping, and the explicit per-module import style.

## Plan

All steps are behavior-preserving unless noted; each ends with the stated check.
Order matters only in that step 1 (green baseline) precedes everything else.

1. **Repair the red test baseline (9 failures)**
   - Decide per-item which side of each drift is intended (recommend: keep the
     *code* — `'Viewing'`, `'Running'`, the `◈ ` bullet, and the grey
     evaluating-phrase — and fix the 11 stale assertions to match; the phrase
     color needs the author's intent confirmed since both code and test were
     changed by different commits) and update `tests/application/agent/intelligence/tools/
     test_file_tools.py`, `test_agent_tools.py`, and
     `tests/interfaces/cli/test_printer.py`.
   - Done when `just test` reports 0 failed (and ~973 passed).

2. **Bring `ruff` to a usable, clean state**
   - Add `archived_docs` and `evals` to `ruff.toml` `exclude` (both are
     deliberately outside the repo's normal tooling; `archived_docs` is
     read-only-by-convention, `evals` is a self-contained harness whose hidden
     tests must not be linted or "fixed" by the repo).
   - Run `ruff format .` on the 9 files it wants to reformat.
   - Fix the real findings in `dandy/` (36 long lines, W291 in `tui/ascii.py`,
     B010 `setattr` in `bot.py`, DTZ005 `datetime.now()` → `datetime.now(UTC)` in
     `recording.py`, the 2 fixable ones) and the test findings that are real
     (F401/F841/F811 unused imports and variables, UP006 `List`/`Type`, C416).
   - For the bulk style rules that would be churn to fix now (ANN201/ANN001
     annotations in tests, E501, RUF001 intentional glyphs, PT009 in evals),
     extend the `ignore`/`per-file-ignores` list in `ruff.toml` deliberately,
     rule by rule, with a one-line comment — so `ruff check .` reaches zero
     without a 500-line annotation rewrite.
   - Optionally add a `Lint (ruff check .)` step to the `hermetic` CI job so it
     cannot silently drift again (the justfile already has `lint-imports`; add a
     `lint` recipe).
   - Done when `ruff check .` and `ruff format --check .` both exit 0 locally, and
     (if the CI step was added) the hermetic job passes.

3. **Fix the small correctness nits in `dandy/`** (each with the existing test
   suite as guard; add a one-line test where coverage is missing):
   - `default_settings.py`: `AI_API_POST` → `AI_API_PORT`; guard `int(...)`.
   - `intel/factory.py:69`: remove the stray `f` in the error message.
   - `recorder.py`: fix the inverted `choices_message` condition.
   - `cache/decorators.py`: use `is not None` for the cache-hit test.
   - `cache/sqlite/cache.py`: `BLOB` column for `value` (data already pickled);
     note the `clean()` 10%-threshold behavior in a comment.
   - `future/future.py`: set `max_workers` on the executor once at creation
     instead of poking `_max_workers` per future.
   - `settings/settings.py`: replace the `Ellipsis` sentinels with `None`
     (the `is ...` checks become `is not None` / `is None`).
   - Done when `just test` still reports 0 failed.

4. **Remove verified dead code**
   - `main.py`: the duplicate `sys.path.append` and the commented-out print.
   - `session.py`: remove `project_dandy_cli_path`; rename `post_init` to
     `model_post_init` (pydantic idiom) or inline the assignment at the single
     call site in `main.py` — pick the simpler; update `main.py` and the test
     that references it (`tests/application/agent/test_session.py`).
   - `connector.py`: remove the never-called `_reset_prompt_retry_attempt`.
   - `shared/utils.py`: remove `generate_forwardable_kwargs_if_not_none`.
   - `bot.py`: remove the empty `get_description` classmethod.
   - `diligence`: remove the never-consulted `trigger_level`/`trigger_operator`
     from `BaseDiligence` and the three subclasses (keep `requires_new_llm_request`
     — it is real).
   - `shared/typing/constants.py`: drop `'null'`/`'undefined'` from
     `STRING_TO_TYPE_MAP` (JS-isms with no Python path).
   - Done when `just test` is green and no removed name is referenced (grep).

5. **Documentation realignment to `3.0.0a5`**
   - Version strings: AGENTS.md header → `3.0.0a5`; `docs/getting_started/cli.md`
     and `docs/roadmap/2026.md` `a1` references → `a5`;
     `pyproject.toml` classifier → `4 - Beta` (alpha release is not
     Production/Stable).
   - Fix the agent cap story everywhere: AGENTS.md (3 spots) and
     `docs/user_guide/cli_agent.md` / `docs/architecture/agents.md` — the CLI
     agent caps at `AGENT_MAX_TOOL_ROUNDS_DEFAULT = 200` per turn; `None`
     disables.
   - Fix the stale rendering descriptions in AGENTS.md (`'Reading'` → `'Viewing'`,
     green/blue/red → green/purple/red, and the thinking-phrase color) and the
     README `/clear` → `/new` + one-shot flag table (`-r`/`-s`/`-n`/`-d`).
   - Move the `## Unreleased` changelog entries under a new `## v3.0.0a5`-contiguous
     heading, or version them, per the release cadence.
   - Run `just docs-tests` (strict build) to catch anchor/member drift.
   - Done when `just docs-tests` passes and the listed strings no longer mismatch
     the code (spot-grep).

6. **Repo hygiene**
   - Delete `tests/example_project_book.md` (stray generated artifact; confirm no
     reference first).
   - Remove the malformed `!dandy/cli/actions/build/` line from `.gitignore`.
   - Add `.backplan/` to `.gitignore` (stop future plans from being committed;
     untracking the 45 existing docs is a separate decision for the author —
     flag it, don't do it unprompted).
   - `cats.md`: ask before touching (it is the author's pet, not code) — default
     to leaving it.
   - Done when `git status` is clean of the listed items and `just test` is green.

## Completion Test

1. `just test` → `0 failed` (quote the summary line).
2. `ruff check .` → exit 0; `ruff format --check .` → exit 0.
3. `just lint-imports` → `Contracts: 6 kept, 0 broken.`
4. `just docs-tests` → strict mkdocs build succeeds.
5. Spot grep: `AI_API_POST`, `max_tool_iterations=None` (outside the
   `max_tool_rounds=None` doc), `/clear` (outside changelog), `project_dandy_cli_path`,
   `_reset_prompt_retry_attempt`, `generate_forwardable_kwargs_if_not_none` → no
   hits in `dandy/` (docs hits only where the changelog intentionally records the
   change).

### Observed results (2026-11-15, after execution)

1. `pytest tests -q` → `974 passed, 57 subtests passed in 155.35s` (0 failed;
   was 9 failed before step 1).
2. `.venv/bin/python -m ruff check .` → `All checks passed!`;
   `.venv/bin/python -m ruff format --check .` → `404 files already formatted`.
3. `lint-imports` → `Contracts: 6 kept, 0 broken.`
4. `python -m mkdocs build --strict` → `Documentation built in 1.35 seconds`
   (no strict errors).
5. Spot greps: `AI_API_POST` → 0 hits; `/clear` → 0 hits outside
   `docs/changelog/v3.md` (historical record); `project_dandy_cli_path`,
   `_reset_prompt_retry_attempt`, `generate_forwardable_kwargs_if_not_none`,
   `trigger_level`, `get_description`, `post_init` (except the pydantic hooks)
   → 0 hits in `dandy/`/`tests/`; the only remaining `max_tool_iterations=None`
   mention in AGENTS.md is the correct "disables the cap" documentation line.
6. CI parity: `python -m unittest discover -t . ./tests` → `Ran 974 tests ... OK`.

## Deviations

1. Ruff version drift between system and venv binaries.
    - What: early in step 2 I ran the system `ruff` (0.15.20); the completion
      gates use the venv ruff (0.17.3, matching the dev extras). The newer
      version flagged two extra rules: PLR0917 (too many positional args) and
      ISC004 (unparenthesized implicit string concatenation in collections).
    - Why: 0.17.3 is what `just lint` and the new CI Lint step actually run, so
      the config must satisfy it. PLR0917 joined the existing PLR0913/PLR0915
      ignores (the wide `prompt_to_intel`-style signatures are intentional);
      the four ISC004 sites got parentheses.
2. Unexpected working-tree change in `printer.py`.
    - What: `dandy/interfaces/cli/tui/printer.py` picked up a change
      (`Executing "{task}"` → `Executing request "{task}"`) while step 2 was
      running; it was not made by any step (verified `ruff format` does not
      produce it). It looks like a live editor edit from the author.
    - Why: the affected string has no test coverage, the suite passes with it,
      and reverting the author's in-flight edit would be worse than keeping it.
      Flagged here so it is reviewed with the diff.
3. Inlined `post_init` instead of renaming it.
    - What: `DandyCliSession.post_init` was removed entirely; `main.py` now
      assigns `session.project_base_path = CWD_PATH` directly (allowed because
      `BaseIntel` is not `model_config` frozen).
    - Why: the plan offered "rename or inline — pick the simpler"; with one
      call site, inlining removes a method whose only purpose was to be called
      once.
4. `docs/changelog/v3.md` Unreleased section left as-is.
    - What: the a5-era "Unreleased" block (tool risk flags, error taxonomy) was
      not re-titled or versioned.
    - Why: the plan left this to the release cadence, and picking a heading is
      an author decision; everything else in step 5 was done.
5. `.backplan/` docs remain tracked.
    - What: `.backplan/` was added to `.gitignore` (with a note), but the 45
      already-tracked plan docs were not `git rm --cached`.
    - Why: the plan flagged untracking as a separate author decision; stopping
      future commits and preserving the choice is the safe default.
6. `cats.md` left untouched (plan default).
