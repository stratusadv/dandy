# Fuzz-test compaction with hypothesis

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-10-30-23-41

## End State

`tests/domain/message/test_compaction_fuzz.py` exists: a hypothesis
property battery (six invariants over generated wire-well-formed
conversations, written as `unittest.TestCase` methods with `@given` so both
pytest and CI's `python -m unittest discover` run it) against
`compact_message_history`, passing alongside the full gate, with `hypothesis`
added to the `development` extra.

## Observable Concern

A new third-party dev dependency (`hypothesis`) lands in the `development`
extra and the lockfile, and the battery runs inside the hermetic CI suite,
adding roughly 10-40s of runtime and a gitignored `.hypothesis/` example
database. Second: if a property fails, that is a real bug in
`compact_message_history` — the fix goes in the code, never by weakening the
property.

## Current State

Verified by code read:

- `compact_message_history` (`dandy/domain/message/message.py:231`) mutates a
  `MessageHistory` in place in a `while total > budget` loop;
  `_oldest_droppable_range` (`:259`) returns the first `assistant`
  tool-call declaration at index >= 1 (range extends through the consecutive
  `tool` results that follow it), else the first single `user` or plain
  `assistant` message at index >= 1, else `(None, None)`; the loop stops when
  the history fits, has fewer than 2 messages, or nothing is droppable, and
  never raises.
- Invariants that follow from the implementation and the docstring (the fuzz
  oracles): position 0 is never touched; the result is an order-preserving
  subsequence (the implementation `del`s slices, so survivors are the same
  objects); tool rounds are atomic (a declaration is only ever dropped in the
  same slice as its consecutive results, and a result is only ever dropped
  with its declaration); compaction is a fixed point (a second pass at the
  same budget is a no-op); input that already fits is unchanged; on a
  system-led well-formed history the result either fits the budget or is
  stuck at 2 messages or fewer (indices 1..last-1 of such a history are
  always droppable when the length is >= 3); non-empty input never compacts
  to empty.
- `hypothesis` is not in `pyproject.toml` and not installed in `.venv`;
  `.gitignore` has no `.hypothesis/` entry.
- `tests/domain/message/` contains `test_message_content.py` and
  `test_messages.py` and no `intelligence/` dir yet; the repo convention
  (`tests/application/bot/intelligence/`) uses an `intelligence/` package
  with an `__init__.py` for test fixtures.
- All tests are `unittest.TestCase` and must stay discoverable by both
  pytest and `python -m unittest discover`; hypothesis' `@given` works on
  `unittest.TestCase` methods (it runs all examples when the method is
  called), so one test file serves both runners.
- The token estimator (`dandy/domain/tokens/estimate.py:38`) is a pure-Python
  per-character loop (~0.2-0.5us/char), so generated text sizes must be
  bounded to keep the battery fast; `get_estimated_token_count_for_tool_calls`
  (`:81`) reads `id` / `function.name` / `function.arguments` leniently.
- The `development` extra (`pyproject.toml:37`) is an unversioned,
  alphabetical list; CI's `just venv` runs `uv sync --all-extras`, so a new
  entry is picked up with no workflow change.
- Existing deterministic compaction tests: `tests/domain/message/
  test_message_content.py` and `TestCompactMessageHistory` in
  `tests/application/agent/test_coding_agent.py` (system slot, newest-tool-
  result round drop, oversized-newest no-raise, fixed scenarios). Fuzzing
  adds invariant coverage over the shapes those do not enumerate; the
  agent-level pre-chat compaction is thin glue (target math + one call) and
  stays covered by its existing tests.

## Plan

1. Add `hypothesis` to the `development` extra
   - Insert `"hypothesis"` in alphabetical position (unversioned, like its
     siblings), run `just venv-upgrade`.
   - Done when `.venv/bin/python -c "import hypothesis; print(hypothesis.__version__)"`
     prints a version.

2. Write the conversation-generation strategy
   - New package `tests/domain/message/intelligence/` (`__init__.py` +
     `compaction_fuzz_strategies.py`) exposing a `@composite`
     `conversation_history_strategy()` that draws a `MessageHistory` led by a
     system message, then 0-5 rounds, each either a plain exchange (user,
     optionally followed by a plain assistant) or a tool round (optional
     user lead-in, one assistant declaration with 1-3 tool-call dicts, one
     `tool` result per call id - wire-well-formed: every result matches a
     preceding declaration, no orphans); with low probability the final
     message is an unfinished declaration (no results yet). Text sizes span
     empty to a few thousand characters, with an occasional 10-30k-character
     message to force overflow. Plus a `budget_strategy()` drawing
     `max_context_tokens` across 0-100k so examples span fits, overflows,
     and budgets smaller than the system message alone.
   - Done when a throwaway generation run produces several hundred
     well-formed histories without error.

3. Write the property battery
   - `tests/domain/message/test_compaction_fuzz.py`: one
     `unittest.TestCase` class; each test is `@given(history=...,
     budget=...)` + `@settings(deadline=None)` (estimation on generated
     histories is slower than hypothesis' default per-example deadline):
     1. the system slot survives (position 0 is the same object);
     2. the result is an order-preserving subsequence of the input
        (identity-based two-pointer check);
     3. tool rounds are atomic in both directions (a surviving declaration's
        results all survive; a surviving result's declaration survives and
        precedes it, and the result's `tool_call_id` is among that
        declaration's call ids);
     4. compaction is a fixed point (a second pass at the same budget leaves
        the message list unchanged);
     5. input that already fits the budget is byte-for-byte unchanged;
     6. the result either fits the budget or has 2 messages or fewer, and
        non-empty input never compacts to empty.
   - Done when all six properties pass under both
     `pytest tests/domain/message -q` and `python -m unittest discover`.

4. Housekeeping + performance budget
   - Add `.hypothesis/` to `.gitignore`.
   - Tune generated size / `max_examples` so the whole fuzz file runs in
     under ~30s locally (default 100 examples per property first; drop the
     count or text sizes before touching the properties).
   - Done when `time ... pytest tests/domain/message/test_compaction_fuzz.py -q`
     is green inside the budget.

5. Docs
   - `AGENTS.md`: add `hypothesis` to the dev-tooling list and one line in
     the testing-approach section naming the fuzz battery and the invariants
     it guards; `docs/changelog/v3.md`: one v3.1.0 line (new dev dependency +
     property tests for compaction).
   - Done when `just docs-tests` passes and the bullets match the code.

6. Full gates + close-out
   - Full pytest, `unittest discover`, coverage >= 90%, `lint-imports`,
     `ruff check` (zero per-file delta on the new files), `ruff format
     --check`, `just docs-tests`; close this doc with the real outputs and
     set Status: Executed.
   - Done when every gate meets the current baseline (517 passed / 29 skipped
     / 49 subtests; `Ran 546 tests`; 94% coverage; 6 kept / 0 broken).

## Completion Test

```bash
cd /home/nathanj/PycharmProjects/dandy
.venv/bin/python -c "import hypothesis; print(hypothesis.__version__)"
AI_API_KEY=test-key PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings \
  .venv/bin/python -m pytest tests/domain/message -q
env -i PATH="$PATH" HOME="$HOME" .venv/bin/python -m unittest discover -t . ./tests
AI_API_KEY=test-key PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings \
  .venv/bin/python -m pytest . -q
PYTHONPATH=. AI_API_KEY=placeholder DANDY_SETTINGS_MODULE=tests.dandy_settings \
  .venv/bin/python -m coverage run -m unittest discover -t . ./tests \
  && .venv/bin/python -m coverage report --fail-under=90
.venv/bin/lint-imports
.venv/bin/ruff check .
.venv/bin/ruff format --check .
just docs-tests
```

pytest/unittest counts at or above the baseline (the six new property tests
are the delta); ruff/format clean on the new files; coverage still >= 90%.

## Deviations

1. `just venv-upgrade` upgraded the whole lockfile, not just the hypothesis addition
    - What: the recipe is `uv sync --all-extras --upgrade`, so adding `hypothesis` (6.170.14, plus its dep `sortedcontainers` 2.4.0; `tomli` dropped) also bumped 29 dev/docs packages and their transitives (ruff 0.16.9 -> 0.17.3, pytest 9.1.1 -> 9.2.0, ty 0.0.84 -> 0.0.95, faker, the mkdocs stack, coverage, certifi, markupsafe, ...). The four direct runtime dependencies (pydantic 2.13.4, requests 2.34.2, blessed 1.44.0, python-dotenv 1.2.2) are unchanged in the lockfile.
    - Why: the plan named this recipe as the sync step (it is the repo's documented re-sync command, and CI uses the same `--all-extras` flow); the consequence is that the repo-wide ruff baseline shifted 668 -> 648 (ruff 0.17.3 reports 20 fewer on pre-existing code). The gate that holds is the one in step 6: zero ruff errors on the new files, verified with the new ruff.

## Execution Report

All outputs observed at close-out:

| Gate | Observed output |
|---|---|
| hypothesis import | `6.170.14` |
| strategy generation check | `300 well-formed histories + budgets generated OK` (system slot, matched call ids, budget range all verified) |
| fuzz file, pytest | `6 passed in 1.60s` (well under the 30s budget - no tuning needed) |
| targeted pytest (`tests/domain/message -q`) | `34 passed, 1 skipped in 1.60s` |
| full pytest | `523 passed, 29 skipped, 49 subtests passed in 5.18s` (517 + 6 new) |
| unittest discover | `Ran 552 tests in 4.827s` / `OK (skipped=29)` (546 + 6 new) |
| coverage (`--fail-under=90`) | `TOTAL 4286 253 94%` (unchanged - the battery adds test code only) |
| lint-imports | `Contracts: 6 kept, 0 broken.` |
| ruff check, new files | `All checks passed!` (zero errors on the three new files; repo-wide `Found 648 errors.` under the upgraded ruff 0.17.3, see deviation 1) |
| ruff format --check, new files | `3 files already formatted` |
| just docs-tests | `Documentation built in 1.02 seconds`, exit 0 |

First fuzz run also validated the machinery: it caught a bug in the test draft
itself (`compact_message_history` called with a `budget=` keyword that does not
exist - the parameter is `max_context_tokens`), which was fixed and re-run
green; no property of `compact_message_history` itself was falsified.

`.hypothesis/` example DB is gitignored. Nothing committed.
