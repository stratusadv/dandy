# Distinguishable edit_file results

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-02-16-40

## End State

`EditFileTool.handle`'s success result names where the edit landed (matched line
number or range) plus a short snippet of the matched text, so two distinct
`edit_file` calls on the same file yield distinct result strings while a
genuinely repeated identical call still yields an identical result string.

## Observable Concern

Distinguishability must come from file state and arguments, never a random
nonce: the repeated-call guard in `dandy/application/tool/service.py` counts
`(name, result)` pairs, so identical repeats (the true loop case, e.g. an
`old_string == new_string` no-op on an unchanged file) must keep producing the
same result string or the guard silently loses its only catch for edit loops.

## Current State

- `dandy/application/agent/tools/file/edit_file_tool.py:53-55` — after
  `write_to_file`, returns the single generic success string
  `Applied {occurrence_count} replacement(s) to "{file_path}".`. No position,
  no snippet. The three error results (file missing, not found, ambiguous) are
  already detailed and state-dependent.
- The replacement is computed in memory: `occurrence_count =
  content.count(old_string)`, then `content.replace(old_string, new_string)` —
  the match position is freely computable from `content` with no extra I/O.
- Guard (`dandy/application/tool/service.py`):
  - `_process_tool_call` (223-299) caps the result at 8000 chars (280-281),
    then `_guard_repeated_call` (301-378) returns the possibly-annotated text,
    which is added as the `role='tool'` message (299).
  - Signature counter key: `(name, _canonical_arguments(args), result)`;
    result counter key: `(name, result)`. Both are per-loop dicts created in
    `prompt_to_intel` (111-112).
  - At `REPEATED_CALL_WARNING_THRESHOLD` (3) a steering note is appended to the
    tool result fed back to the model; at `REPEATED_CALL_STOP_THRESHOLD` (10)
    the loop raises `LlmRecoverableError`.
  - The 16:25 failed session: four parallel `edit_file` calls on
    `tests/interfaces/cli/test_cli.py` in one round, all returning the
    identical generic success string, so the result counter hit 3 and 4 and
    appended false-positive steering notes.
- Tests:
  - `tests/application/agent/test_file_tools.py:99-137` —
    `test_edit_file_single_replacement` asserts `'1 replacement'` in the
    result; `test_edit_file_replace_all` asserts `'3 replacement'`. Both are
    substring checks that survive the new format. `setUp` points
    `session.project_base_path` at a temp dir.
  - `tests/application/tool/test_service.py:720+` (`TestRepeatedCallGuard`) —
    all guard tests use the weather/echo fakes; none touch `edit_file`.
    `tool_call_response` (70-91) emits exactly one `tool_calls` entry per
    assistant message, so a parallel-calls regression test must build its
    `HttpResponseIntel` inline with three entries.
- Docs: no page in `docs/` quotes the success string (grep for
  `replacement` finds nothing in `docs/`), so the only doc update is the
  changelog.
- Scope note: `write_file_tool.py:29` returns the similarly generic
  `Successfully wrote {line_count} line(s) to "{file_path}".` (two writes of
  equal line count would share a result). Out of scope — user approved
  `edit_file` only.
- House style: tool results are plain single-line strings; agent tools cap
  long output near 8000 chars; tests assert on substrings, not exact strings.

## Plan

1. Distinguish the success result
   - In `EditFileTool.handle`, after the count checks pass, compute the first
     match: `match_start = content.find(old_string)`, `start_line =
     content.count('\n', 0, match_start) + 1`; for multi-line matches,
     `end_line = content.count('\n', 0, match_start + len(old_string)) + 1`,
     minus 1 when the match ends on a newline boundary. Snippet = first
     non-empty stripped line of `old_string`, capped at 40 chars.
   - Return `Applied {n} replacement(s) to "{file_path}" (line {L}:
     "{snippet}").`, using `lines {L1}-{L2}` when the match spans lines.
     `replace_all` (n > 1) reports the first match's line — the count and
     snippet still distinguish calls.
   - Done when the new/updated `test_file_tools.py` assertions pass.
2. Tests
   - `tests/application/agent/test_file_tools.py`: extend
     `test_edit_file_single_replacement` to assert the line number and
     snippet; add a multi-line-match case; add a distinguishability case
     (two different edits to one file → different results); add a
     true-repeat case (`old_string == new_string` twice on an unchanged file
     → identical results, so the guard can still accumulate).
   - `tests/application/tool/test_service.py` (`TestRepeatedCallGuard`):
     end-to-end regression mirroring the failed session — one assistant
     message with three parallel `edit_file` tool_calls (different
     old/new, same temp file, `session.project_base_path` pointed at it),
     then a final content response; assert no `'Note:'` in any of the three
     tool results.
   - Done when `pytest tests/application/agent/test_file_tools.py
     tests/application/tool/test_service.py -q` passes.
3. Docs
   - `docs/changelog/v3.md`: one entry under the unreleased section describing
     the distinguishable result and why (guard false positives on parallel
     same-file edits).
   - Done when the entry exists and `just docs-tests` passes.
4. Gate
   - Full suite: `DANDY_SETTINGS_MODULE=tests.dandy_settings PYTHONPATH=.
     .venv/bin/python -m pytest . -q` (baseline 661 passed, 49 subtests).
   - `ruff check` on each touched file with `--config ruff.toml`, rule
     multiset diffed against `git show HEAD:<file>` — no new findings (repo
     baseline is red; we add zero).
   - `just lint-imports` — 6 contracts kept.
   - `just docs-tests` — strict mkdocs build.
   - Done when all four gates are green.

## Completion Test

1. `DANDY_SETTINGS_MODULE=tests.dandy_settings PYTHONPATH=. .venv/bin/python
   -m pytest tests/application/agent/test_file_tools.py
   tests/application/tool/test_service.py -q` → all pass, including the new
   distinguishability, true-repeat, and parallel-edits-no-note tests.
2. Full suite command from step 4 → green.
3. ruff no-new-findings diff for `edit_file_tool.py`,
   `tests/application/agent/test_file_tools.py`,
   `tests/application/tool/test_service.py`, `docs/changelog/v3.md`.
4. `just lint-imports` → "kept" for all 6 contracts.
5. `just docs-tests` → strict build success.
6. Evidence: two real calls — `handle(file_path='example.txt', old_string='a',
   new_string='b')` then `handle(file_path='example.txt', old_string='c',
   new_string='d')` on a file containing both — return different strings, and
   repeating a no-op edit returns the identical string it first returned.

## Deviations

1. Gate step extended beyond the planned four files
    - What: mid-execution the user asked to verify and finish the in-flight AI
      session-naming feature. Completed it: two of its tests were fixed to the
      post-restructure wire shape (`request_intel.json_data` instead of
      `request_intel.model_dump()`, `tools` excluded-by-none assert, part-list
      content extraction), the `capture` stubs gained real annotations, and the
      documented seam edge `dandy.interfaces.cli.cli ->
      dandy.application.agent.bots.session_naming_bot` was added to the
      interfaces → infrastructure contract in `pyproject.toml` plus the AGENTS.md
      seams bullet.
    - Why: the new `cli → session_naming_bot` import broke the "Interface layer
      imports infrastructure only at documented seams" contract, and the two
      tests asserted the pre-restructure `LlmRequestBody`-direct connector
      signature; the rest of the feature (bot, prompt, intel, CLI wiring,
      SIMPLE config) was already complete and passing.

## Observed Output (completion test)

- Targeted: `pytest tests/application/agent/test_file_tools.py
  tests/application/tool/test_service.py -q` → `20 passed`, then `34 passed`
  (includes new distinguishability, true-repeat, multi-line, and
  parallel-edits-no-note regression tests).
- Full suite (evals deselected): `pytest . -q --deselect evals` →
  `672 passed, 15 deselected, 49 subtests passed in 211.66s`. The 15 deselected
  are the stockroom eval-harness tests, which fail environmentally without the
  eval container's generated `evals/task/seed.json` (pre-existing, unrelated).
- Ruff vs HEAD (mirror-tree at matching paths, same config): identical rule
  multisets for `edit_file_tool.py`, `test_file_tools.py`, `test_service.py`;
  `test_session_naming_bot.py` fully clean after annotation cleanup.
- `just lint-imports` → `Contracts: 6 kept, 0 broken.`
- `just docs-tests` → strict mkdocs build success.
