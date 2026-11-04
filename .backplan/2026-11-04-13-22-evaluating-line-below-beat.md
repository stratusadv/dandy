# Evaluating phrase on its own blue line, 3s rotation

- Developer: Nathan Johnson (nathanj@stratusadv.com)

- Date: 2026-11-04-13-22

## End State
In the CLI's animating story frame, the thinking phrase (e.g. "Polishing a
Diamond-Encrusted Cufflink ...") renders on the line below the current tool
beat (not appended to the beat's line), in plain blue (`term.blue`, not bold);
a random phrase is picked once and held for 3 seconds, then a new random one
is picked; `tests/interfaces/cli/test_printer.py` is fully green.

## Observable Concern
The animating frame becomes a 2–3 line live region (label / description /
phrase) that is redrawn every 0.12s tick by overwriting; the cursor ends on
the phrase line, so every subsequent write (next tick, the beat's settle, the
final completion line) must move up the exact number of live lines first
(CSI `nA`), or the scrollback gets stale duplicated lines or corrupted text.

## Current State
Verified facts (on the current working tree, which is mid-WIP):
- `_StoryProgress.frame` (`dandy/interfaces/cli/tui/printer.py:179-206`)
  appends `f'{self.term.bold_orange}{random.choice(THINKING_PHRASES)} {dots}'`
  to the end of the beat line; a new random phrase is drawn **every tick**
  (0.12s), which is the "randomly flipping" the user sees.
- The phrase is bold orange in code (docstrings still say 'Evaluating ...');
  the user perceives it as bold blue; the requested end state is plain blue
  either way.
- The truncation budget reserves room for the phrase on the same line:
  `max_beat_length = term.width - len(prefix) - len(f'{phrase} ...')`. Long
  random phrases shrink the description to a few characters.
- The render loop (`run_timed_task`, lines 334-381) writes `frame(...)` every
  tick with no trailing newline (cursor stays on the live line) and
  `settled_frame(...)` (ends with `\n`) when a beat advances; final settle
  after the thread dies, then the green completion line.
- `THINKING_PHRASES` (~400 phrases) in `dandy/interfaces/cli/thinking_phrases.py`;
  `Printer.running_phrase` (line 276) also draws one phrase, once, at turn
  start ("... in preparation of ...") — not affected.
- `test_printer.py` currently has 8 failing tests, all format-related:
  3 fail purely because the long random phrase truncates the description
  (`test_first_labeled_beat_gets_a_heading`,
  `test_frames_link_file_paths_in_tool_beats`,
  `test_frames_style_label_grey_and_description_plain`); 2 assert the old
  literal `bold_orange 'Evaluating ...'` suffix (stale against the WIP code);
  1 asserts the old single-line animating contract
  (`test_multiline_beat_animates_on_a_single_line`); 1 also asserts a
  completion sentence the code no longer prints (`'I have completed your
  request in '` vs the code's `'Request Completed in '` — WIP debt, not
  suffix-related). The earlier `beats[-1]` IndexError race is gone from the
  current tree.

## Plan
1. Rework the animating frame in `_StoryProgress` (`dandy/interfaces/cli/tui/printer.py`)
   - Track `_evaluating_phrase` / `_evaluating_phrase_since` (perf_counter) and
     rotate: pick `random.choice(THINKING_PHRASES)` when none or 3.0s elapsed
     (`EVALUATING_PHRASE_CHANGE_SECONDS = 3.0`).
   - Frame layout: line 1 = label heading (when emitted) + beat description
     (folded, truncated only to `term.width - len(prefix) - 1` — the phrase no
     longer eats the budget); line 2 = plain blue phrase + cycling dots.
   - Live-region bookkeeping: `frame`/`settled_frame` move up
     `n-1` lines (CSI) when the previous live frame was n lines, clear the
     old phrase line(s) on settle, and a `drop_live_frame()` resets the
     region after a question round-trip so resuming never moves the cursor
     into the question's prompt lines.
   - Done when frame strings carry the phrase below the beat, in `term.blue`,
     stable across ticks within 3s.
2. Update `run_timed_task` + docstrings
   - Call `drop_live_frame()` after `question_gate.deliver(answer)`; update
     the `_StoryProgress` and `run_timed_task` docstrings to the new layout.
   - Done when a question pause/resume renders without corrupting lines.
3. Update `tests/interfaces/cli/test_printer.py`
   - Re-point the two stale `bold_orange 'Evaluating ...'` assertions at the
     new contract (phrase line below the beat, plain blue), patch
     `random.choice` for determinism; rename the one test whose name encodes
     the old behavior.
   - Add a rotation test: with a mocked `perf_counter`, the phrase is stable
     at t=0 and t=2.9 and changes at t=3.1 (one new `random.choice` call).
   - Update `test_multiline_beat_animates_on_a_single_line` to the new
     line-count contract; align the stale completion-sentence assertion in
     `test_run_timed_task_prints_story_and_completion_sentence` with the
     current code text (`Request Completed in ...`).
   - Done when the whole `test_printer.py` file passes.
4. Doc touch-ups
   - AGENTS.md sentence describing the animating frame suffix, and
     `docs/user_guide/coding_agent.md` if it describes it.
   - Done when `just docs-tests` still passes.
5. Verification
   - `pytest tests/interfaces/cli/test_printer.py` fully green; then the
     `tests/interfaces/cli` slice + full suite, ruff check/format on touched
     files, `lint-imports`.
   - Done when all green.

## Completion Test
1. `PYTHONPATH=. .venv/bin/python -m pytest tests/interfaces/cli/test_printer.py -q` → 0 failed (currently 8).
2. `PYTHONPATH=. .venv/bin/python -m pytest tests -q` → no new failures vs. the pre-change tree.
3. `ruff check`/`ruff format --check` on `dandy/interfaces/cli/tui/printer.py` and `tests/interfaces/cli/test_printer.py` → clean; `lint-imports` → 6 kept.
4. Smoke: a small script calls `frame()` twice with mocked `perf_counter` 2.9s apart and prints the raw frame — same phrase, phrase on the line after the description, `ESC[34m`-style blue (not bold) styling; at 3.1s a different phrase.

### Observed results
- `test_printer.py`: 46 passed, 0 failed.
- Full suite: 735 passed + 49 subtests passed, 0 failed; `tests/interfaces/cli/`: 159 passed.
- `ruff check`: the only violations in the two files are pre-existing user WIP debt
  (ANN201 in `printer.py`, ARG001/TRY003/EM101 in the tests); `ruff format`
  clean on the changed spots; `lint-imports`: 6 kept, 0 broken.
- Smoke: a terminal-grid simulator (`/tmp/sim_story.py`, cell array, parses
  CSI cursor-up / clear-EOL / CR / LF) rendered 4 scenarios (consecutive
  single-line beats, multi-line beat, narration, narration sandwiched) and
  ended byte-exact: phrase on its own line below the beat, same phrase held
  across ticks within 3s, no tail residue after settle, no blank line between
  beats in a group, blank line before each heading/narration, completion line
  on a fresh line.
- Note: the smoke's "blue (not bold)" expectation was superseded by the
  user's mid-execution color edits (see Deviations 4); the final phrase style
  is bold blue and the tests assert it.
- Docs closed out after the test run: the stale animating-suffix paragraph in
  `docs/user_guide/tool_calling.md` was rewritten to the new contract and a
  `Changed` bullet was added to `docs/changelog/v3.md`; `mkdocs build
  --strict` passes.

## Deviations
1. `action_name` was dropped from `run_timed_task` mid-execution (user request):
   the header now prints just the quoted task, and the two call sites in
   `cli.py` lost their `action_name=` kwargs.
2. The user's live story-style edits (a leading `\n` in `_styled_label` so
   each heading group is preceded by a blank line, plus the pre-existing
   leading `\n` on narration) forced generalized region bookkeeping: the
   live region is 3–4 lines (blank/heading/description/phrase) with
   `_live_desc_index` computed once at region start, and a narration
   variant that redraws and settles from the region's *start* line (its
   text begins with a newline, so redrawing from the description line
   slides the region down one line per tick). The approved plan assumed a
   fixed 2–3 line region.
3. Live-run defect fixes beyond the approved plan:
   - per-line tail clearing on settle (`_clear_line_tails`) — fixes the
     "cutting off action outputs" report (a shorter settled line left the
     longer animating line's tail visible);
   - stable region size across redraws (region geometry is fixed at region
     start) — fixes a latent ghost-phrase bug where the region shrank
     3→2 lines on redraw;
   - carry-line reuse: the leftover phrase line is cleared and consumed as
     the first line of the next region (`_carry_lines`,
     `_fresh_line_prefix`, `carry_prefix`), which eliminates the blank
     space left after each evaluation output (the user's second report);
   - explicit `\r` after every `\n` in frame/settle strings — a bare LF
     keeps the cursor's column, so without it the description, phrase, and
     multi-line settled lines rendered indented instead of flush left;
   - `pause_at_fresh_line()` + a pre-question catch-up settle in
     `run_timed_task`: the question prompt now prints at column zero on a
     fresh line, and the render loop's animation condition
     (`len(beats) > settled_count`) stops re-animating a beat that a
     question pause already settled;
   - `carry_prefix()` returns `''` (not `'\r'`) when there is no carry,
     matching its docstring and the `if carry:` guard in `run_timed_task`.
4. Color changes were made directly by the user during execution (label:
   bold grey → bold blue → bold cyan → bold skyblue; phrase: the approved
   plain blue was later switched by the user to bold orange, then bold
   blue). Tests and docs are synced to the user's latest stable choice.
5. Aligned 3 stale `test_cli.py` error-string assertions
   (`'\nDandy ran into an error'` → `'Dandy ran into an error'`) — the
   user's WIP moved the leading newline into `Printer.error`.
