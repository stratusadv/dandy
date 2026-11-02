# Fix multi-line story beats duplicating every animation tick

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-02-12-25

## End State

The animating story frame of a multi-line beat (e.g. a multi-line
`run_command` command) is a single line, so the 0.12 s tick loop no longer
appends a line pair to the terminal scrollback on every tick; the settled
frame still prints the full multi-line text exactly once, and new tests
prove both.

## Observable Concern

The wall of ~50 repeated `> Executing … python -c " / from blessed import
Terminal` pairs in the user's paste is a **rendering artifact, not a model
loop**: each 0.12 s tick writes an animating frame that itself contains
raw newlines, and the frame's leading `\r` only redraws the current line, so
every tick leaves a fresh line pair in scrollback (reproduced below). The
repeated-call guard is not involved — the model issued each multi-line
command once (the full text appears exactly once per block, as the settled
frame). Second concern: the user is live-editing `test_printer.py` and the
CLI files; re-View before each edit.

## Current State

- Reproduced (observed): stub `term` with `width=143`, an 8-line
  `run_command` beat → `frame(beat, '...')` contains **2 newlines** (a 3-line
  frame, width-truncated); `settled_frame(beat)` contains 7 (the full
  command). Each tick of the loop prints that 3-line string prefixed by `\r`.
- `dandy/interfaces/cli/tui/printer.py:95-108` — `frame()`:
  `plain_beat = self._plain_beat(beat.label, beat.description)` keeps raw
  newlines; width truncation cuts by character count; return value
  `f'\r{prefix}{beat_text} {dots}{self.term.clear_eol()}'` therefore embeds
  `\n` whenever the description is multi-line (truncated or not — the
  else-branch uses `beat.description` raw).
- `printer.py:227-244` — the render loop writes `frame(beats[-1], dots)` +
  flush every 0.12 s while the task runs; a multi-line frame thus appends
  line pairs to scrollback each tick (~50 pairs ≈ 6 s of animation, matching
  the paste).
- `printer.py:90-93` — `settled_frame()` prints the untruncated multi-line
  text; written only when the beat settles (lines 230-233) or the task ends
  (246-247) — once per beat.
- `RunCommandTool.action_output` returns the raw command, so a multi-line
  model command becomes a multi-line beat description (the user's live edit
  also dropped the quotes, so the full command text is what shows).
- The paste shows two such walls (one per multi-line `python -c` smoke
  command), each ending in the full 8-line command = the settled frame.

## Plan

1. Single-line animating frame
   - In `frame()`: `plain_beat = ' '.join(self._plain_beat(beat.label,
     beat.description).split())` (folds newlines and whitespace runs); in the
     non-truncated branch use the same folded description instead of raw
     `beat.description`, so no raw `\n` can reach the frame string.
   - Done when the stub repro shows 0 newlines in the animating frame of an
     8-line beat, and width truncation still applies.

2. Tests (tests/interfaces/cli/test_printer.py)
   - New test: multi-line beat (label + 3-line description, `ascii_char='>'`)
     → `frame(beat, '...')` contains no `'\n'`; `settled_frame(beat)` still
     contains the newlines (full text preserved).
   - Done when `pytest tests/interfaces/cli -q` is green.

3. Docs
   - AGENTS.md `_StoryProgress` sentence and `docs/user_guide/tool_calling.md`
     render description: note the animating frame collapses a multi-line beat
     onto one line; the settled frame shows the full text.
   - Done when `just docs-tests` exits 0.

4. Gate
   - Full suite, ruff check/format on touched files, `just lint-imports`.
   - Done when every command in the Completion Test passes with output
     quoted.

## Completion Test

- Stub repro (python -c): animating frame of an 8-line beat → `newlines: 0`;
  settled frame unchanged (7 newlines).
- `DANDY_SETTINGS_MODULE=tests.dandy_settings PYTHONPATH=. .venv/bin/python -m
  pytest tests -q` → whole suite passes.
- `.venv/bin/ruff check <touched files>` + `grep -E 'E501|F[0-9]{3}|W[0-9]{3}'`
  empty; `.venv/bin/ruff format --check <touched files>` clean.
- `just lint-imports` → all 6 contracts kept.
- `just docs-tests` → mkdocs strict build exits 0.

### Observed

- Stub repro after the fix: animating frame of the 8-line beat →
  `animating frame newlines: 0` (single line, width-truncated); settled frame
  unchanged → `settled frame newlines: 7`.
- `pytest tests/interfaces/cli -q` → `107 passed` (incl. the new
  `test_multiline_beat_animates_on_a_single_line`).
- `pytest tests -q` (full) → `1 failed, 650 passed, 49 subtests passed in
  129.59s`; the single failure is `test_example_project.py::test_book_generation`,
  the `@live_llm_test` hitting a real endpoint (documented live flake — passed
  in the previous two full runs and in earlier standalone re-runs; untouched by
  this change, which only affects the CLI printer's animating frame).
  Standalone re-runs flapped: fail (`1 failed in 41.00s`), pass, fail
  (`1 failed in 52.13s`), fail — the last captured failure is the live
  chapter-generation LLM call returning an empty chapter list
  (`AssertionError: 0 != 2` on `len(dandy_book.chapters)`) — model-side
  endpoint flakiness; the test's multi-bot Intel flow does not touch the CLI
  printer layer at all.
- `ruff check` on the two touched .py files + `grep -E 'E501|F[0-9]{3}|W[0-9]{3}'`
  → empty; `ruff format --check` → `2 files already formatted`.
- `just lint-imports` → `Contracts: 6 kept, 0 broken.`
- `just docs-tests` → `Documentation built in 0.99 seconds` (exit 0).

## Deviations

none yet
