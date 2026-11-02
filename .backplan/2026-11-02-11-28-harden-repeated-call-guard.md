# Harden repeated-call guard against re-typed calls

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-02-11-28

## End State

`ToolService`'s repeated-call guard can no longer be evaded by re-typed calls:
the existing signature counter keys on **canonicalized** arguments (whitespace
runs folded in every string value, sorted-key compact JSON of the validated
kwargs), and a second counter keyed on **(tool name, exact result)** counts
repeats across any argument wording. Both counters steer at 3 and hard-stop at
10 (existing thresholds, kept per user decision), and the existing 4 guard tests
plus new tests for both evasions pass.

## Observable Concern

`tool_call.arguments` is the model's raw JSON text: newlines inside a command
value are literal `\n` escape sequences in that text, so whitespace-folding the
raw string would do nothing for heredoc line-wrap drift. Normalization must run
on the **parsed** kwargs (`arguments_intel.model_dump()`, already computed at
service.py:235) — implementing it on the raw JSON text would silently not fix
the reported case. Second: the result counter's count is always >= the
signature counter's for the same call, so note/exception emission must be
unified (signature-first) or the signature note becomes dead code.

## Current State

- `dandy/application/tool/service.py:39-50` — comment block +
  `REPEATED_CALL_WARNING_THRESHOLD = 3`, `REPEATED_CALL_STOP_THRESHOLD = 10`.
- `prompt_to_intel` (line 85) creates one tracker
  `repeated_call_tracker: dict[tuple[str, str, str], int] = {}` and passes it
  through the single `_process_tool_call` call (line 141-148; parameter at 203).
- `_process_tool_call`: validates args → `arguments_kwargs =
  arguments_intel.model_dump()` (line 235) → executes → `result_text` capped at
  `_TOOL_RESULT_CHARACTER_LIMIT` (8000, lines 249-250) →
  `_guard_repeated_call(tool_call, result_text, tracker, verbose)` (line 261) →
  `add_message(role='tool', text=feedback_text)` (line 268).
- `_guard_repeated_call` (lines 270-313): signature =
  `(tool_call.name, tool_call.arguments.strip(), result_text)`; at >= 10 raises
  `LlmRecoverableError('LLM Tool Service stopped the loop: the model repeated
  the identical tool call "{name}" {n} times in this conversation and the
  result never changed.')`; at >= 3 appends the
  `'[Note: you have now run this exact same call {n} times ...]'` steering note;
  returns the (annotated) result text.
- The reported failure (user CLI run, `.backplan`-adjacent paste): the same
  multi-line `python3 - <<'EOF'` heredoc command executed 80+ times. The guard
  was live (committed in f32e790; the run's `>` beat prefix proves today's
  tree) but each re-typed heredoc drifted internally (invisible past the beat's
  one-line preview), so every call was a fresh signature and the counter never
  accumulated; the loop ran to the 200-round cap.
- Tests: `TestRepeatedCallGuard` (tests/application/tool/test_service.py:704-817)
  — 4 tests: steering note at 3 identical, fail-fast at 10 identical, different
  args count separately, oscillating repeats accumulate. Pattern:
  `tool_call_response(name, args_json, tool_call_id)` side_effect lists,
  `max_tool_iterations` caps, assertions on final-request tool contents,
  exception text, and `mock_post_request.call_count`.
- Docs describing the guard: `AGENTS.md` (Execute-and-loop paragraph),
  `docs/user_guide/tool_calling.md` (repeated-call guard bullet),
  `docs/changelog/v3.md` (v3.1.0 Added entry, lines 64-74), and the constant
  comment block in service.py.

## Plan

1. Canonicalize arguments for the existing signature
   - Add a module-level `_canonical_arguments(kwargs: dict) -> str` in
     service.py: recursively fold whitespace runs in every string value to a
     single space, then `json.dumps(..., sort_keys=True, separators=(',', ':'))`.
   - `_process_tool_call` computes the canonical form from `arguments_kwargs`
     and passes it to `_guard_repeated_call`, which builds the signature as
     `(tool_call.name, canonical_args, result_text)`.
   - Update the constant comment block to describe both counters.
   - Done when a new test shows calls differing only in JSON key order /
     spacing / line-wrap of a string value accumulate toward one signature.

2. Add the (tool name, result) counter
   - `prompt_to_intel` creates `repeated_result_tracker: dict[tuple[str, str], int]
     = {}`; plumbed through `_process_tool_call` to `_guard_repeated_call`
     alongside the existing tracker.
   - `_guard_repeated_call` increments both counters per call. Stop:
     `signature_count >= STOP` raises the existing "identical tool call"
     message; else `result_count >= STOP` raises a new "received the identical
     result from {name} {n} times" message. Warning: one note per call —
     signature note when `signature_count >= WARN` (preserves existing text),
     else a new result-based note ("{name} has returned this exact same result
     {n} times ... change your approach or give your final answer") when
     `result_count >= WARN`. Verbose lines for both counters.
   - Done when a new test shows re-typed calls (different argument wording,
     identical result) steer at 3 and fail fast at 10, and a second new test
     shows the result counter is per-tool-name (alternating two
     constant-result tools does not combine toward the stop).

3. Tests
   - New tests in `TestRepeatedCallGuard`: whitespace/key-order canonical
     equivalence; re-typed-calls-same-result steering + fail-fast; per-name
     result separation. Existing 4 tests must pass unchanged (verified by
     walkthrough: their different-args cases produce different results, so the
     result counter separates them too).
   - Done when `pytest tests/application/tool -q` is green.

4. Docs
   - service.py comment block; `AGENTS.md` Execute-and-loop guard paragraph;
     `docs/user_guide/tool_calling.md` guard bullet; `docs/changelog/v3.md`
     v3.1.0 Added entry (still unreleased, so the entry is amended).
   - Done when `just docs-tests` exits 0.

5. Gate
   - Full suite, ruff check/format on touched files, `just lint-imports`,
     `just docs-tests`.
   - Done when every command in the Completion Test passes with output quoted.

## Completion Test

- `DANDY_SETTINGS_MODULE=tests.dandy_settings PYTHONPATH=. .venv/bin/python -m pytest tests -q`
  → whole suite passes.
- `DANDY_SETTINGS_MODULE=tests.dandy_settings PYTHONPATH=. .venv/bin/python -m pytest
  tests/application/tool -q` → includes the new guard tests, all pass.
- `.venv/bin/ruff check <touched files>` + `grep -E 'E501|F[0-9]{3}|W[0-9]{3}'`
  empty; `.venv/bin/ruff format --check <touched files>` clean.
- `just lint-imports` → all 6 contracts kept.
- `just docs-tests` → mkdocs strict build exits 0.

### Observed

- `pytest tests/application/tool -q` → `33 passed` (4 new guard tests incl. per-name separation).
- `pytest tests/application/agent -q` (after deviation 2) → `97 passed`.
- `pytest tests -q` (second full run, after deviation 2; the tree had since grown
  ~6 new tests from the user's in-flight agents-md work) → `2 failed, 634 passed,
  49 subtests passed in 91.70s`. Neither failure touches the guard:
  (a) `test_example_project.py::test_book_generation` is `@live_llm_test` hitting a
  real endpoint — a documented live flake (passed in the first full run and in a
  standalone re-run, `1 passed in 103.91s`); (b)
  `test_coding_agent.py::test_reload_agents_md_syncs_the_running_conversation`
  belongs to the user's uncommitted in-flight `agents_md.py` / `reload_agents_md`
  feature (`dandy/application/agent/agents_md.py` is untracked; the test asserts the
  first request's system message keeps the pre-reload AGENTS.md text, but the shared
  history is updated in place) — out of scope, left to the user. All guard work
  verified green in its own suites: `pytest tests/application/tool -q` → 33 passed,
  `pytest tests/application/agent -q` → 97 passed.
- `ruff check` on touched files + `grep -E 'E501|F[0-9]{3}|W[0-9]{3}'` → empty;
  `ruff format --check` → clean (one reformat of test_service.py during the run).
- `just lint-imports` → `Contracts: 6 kept, 0 broken.`
- `just docs-tests` → `Documentation built in 1.03 seconds` (exit 0); re-verified
  after the label-test adaptation → `Documentation built in 0.98 seconds` (exit 0).

## Deviations

1. **`action_ascii_char` default `'.'` → `'•'`** — the user live-edited
   `dandy/domain/tool/tool.py` mid-run, changing the default beat character to a
   U+2022 bullet (explicit user choice despite the attribute's name). Adapted
   rather than reverted: 5 expectations in `tests/application/tool/test_service.py`,
   `tests/domain/tool/test_tool.py` (test renamed `test_action_ascii_char_defaults_to_bullet`,
   asserts `'•'`), the `tool.py` docstring ("a bullet is used"), and the three doc
   default mentions (AGENTS.md, docs/user_guide/tool_calling.md,
   docs/changelog/v3.md).
2. **`RunCommandTool` label `'Running'` → `'Executing'`** — the user's live edit
   added `action_label = 'Executing'` + `action_ascii_char = '>'` to
   `command_tool.py` and made `action_output` return the unquoted command, which
   broke `test_run_command_output_names_the_command` (`AssertionError:
   'Executing' != 'Running'`) in the first full-suite run. Applied the same
   live-edit adaptation policy: updated the two assertions at
   `tests/application/agent/test_agent_tools.py:188-189` to `'Executing'` /
   `'pytest -q'` and the AGENTS.md `run_command` example to `'Executing' +
   'pytest -q'`; `command_tool.py` was not reverted.
