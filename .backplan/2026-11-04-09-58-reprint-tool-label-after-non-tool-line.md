# reprint-tool-label-after-non-tool-line

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-04-09-58

## End State
In the CLI's running story, a tool beat re-prints its heading line whenever the
line immediately above it is not a same-label tool line — so after a thought
(bold blue narration) or a system notice, the tool label appears again above
the bulleted detail line; consecutive same-label tool beats still share one
heading.

## Observable Concern
The heading decision runs on every 120 ms animation tick for the newest beat
(`frame()`) and once at settle (`settled_frame()`); it must depend only on the
beat list (which only ever grows) so the per-tick answer is stable, and the
`id(beat)` guard in `_heading_emitted` must still ensure a heading prints at
most once per beat under the new rule.

## Current State
Verified 2026-11-04, live tree (branch `v3/base`, Task B committed):
- `_StoryProgress` (`dandy/interfaces/cli/tui/printer.py:94-203`):
  `_needs_heading(beat)` (line 142) = labeled AND
  `beat.label != self._previous_tool_label(beat)`; `_previous_tool_label`
  (line 129) scans backwards **skipping non-tool beats** to the nearest
  earlier labeled beat — so a thought between two same-label tool beats
  suppresses the second heading (the behavior being changed).
- `_emit_heading` (line 159) guards with `id(beat) in self._heading_emitted`;
  `frame()` (line 179) emits the heading on the first tick for a beat whose
  `_heading_beat is not beat`; `settled_frame()` (line 168) emits at settle.
- The list's first beat is always a description-only THINKING_PHRASE (no
  label), so the first tool beat always gets a heading — unchanged outcome
  under the new rule (its earlier beat has no label).
- `StoryBeat` (`dandy/domain/tool/beat.py`) unchanged: `label`, `description`,
  `kind` ('system' default / 'narration'), `ascii_char`,
  `can_mutate_state`. A non-tool beat is exactly a beat with an empty
  `label`.
- `TestStoryProgressHeadingGrouping` (`tests/interfaces/cli/test_printer.py:
  391-495`), 7 tests: `test_non_tool_beat_does_not_break_the_group` (line
  466) encodes the old rule and flips; the other six (first beat, consecutive
  repeats, once-across-frames, label change, A-B-A, settle-only) keep their
  expectations under the new rule.
- Docs stating the rule: `AGENTS.md` (tool-calling bullet, story sentence —
  one giant line, extract live at edit time), `docs/user_guide/tool_calling.md`
  (the `progress_callback` bullet, "printed exactly once when the label
  appears and again when it reappears after a change"),
  `docs/changelog/v3.md` (v3.1.0 `### Changed` top entry describes the old
  rule; last night's work added entries, re-read live).
- Last night's uncommitted work (planning-bot removal, question tool, eval
  changes) does not touch `_StoryProgress` or `StoryBeat`; the full-suite
  baseline count is whatever the gate run reports (not the 696 from Task B).

## Plan
1. New heading rule
   - `printer.py`: collapse `_previous_tool_label` + `_needs_heading` into one
     `_needs_heading(beat)`: labeled AND (no earlier beat, OR the immediately
     earlier beat has no label, OR its label differs). Delete
     `_previous_tool_label` (single caller). Update the class docstring
     (lines 99-104) and the `run_timed_task` docstring (lines 290-292) to the
     new rule.
   - Done when the step-2 tests pass.
2. Tests
   - `test_printer.py`: flip `test_non_tool_beat_does_not_break_the_group` to
     `test_non_tool_beat_breaks_the_group_and_reprints_the_label` (narration
     between two same-label tool beats → the second beat's frame carries the
     heading again); add `test_system_beat_also_breaks_the_group` (a
     'system'-kind notice between same-label beats re-prints the label).
   - Done when `pytest tests/interfaces/cli/test_printer.py -q` is all green.
3. Docs
   - `AGENTS.md`: the story sentence's "printed exactly once when the label
     appears and again when it reappears after a change" → "printed once when
     the label appears and again whenever the label changes or a non-tool
     line (a thought or a notice) has printed in between" (extract the exact
     substring live). `docs/user_guide/tool_calling.md`: same sentence in the
     `progress_callback` bullet. `docs/changelog/v3.md`: new entry at the top
     of v3.1.0 `### Changed`.
   - Done when `just docs-tests` strict build passes.
4. Gate
   - Targeted `test_printer.py`; full suite; ruff mirror diff on the two
     touched Python files; `just lint-imports`; `just docs-tests`.
   - Done when every gate is green.

## Completion Test
```bash
DANDY_SETTINGS_MODULE=tests.dandy_settings PYTHONPATH=. .venv/bin/python -m pytest \
  tests/interfaces/cli/test_printer.py -q
```
all green, plus the full suite green, `just lint-imports` → `Contracts: 6
kept, 0 broken.`, `just docs-tests` exit 0, and the ruff mirror diff on the
touched files empty (no NEW findings).

## Deviations
none

## Observed Output
```text
# targeted (completion test)
DANDY_SETTINGS_MODULE=tests.dandy_settings PYTHONPATH=. .venv/bin/python -m pytest \
  tests/interfaces/cli/test_printer.py -q
41 passed in 2.29s

# full suite
724 passed, 81 skipped, 49 subtests passed in 144.81s (0:02:24)

# ruff mirror diff (mirror /tmp/ruffbase8, 2 touched Python files)
NEW: none
REMOVED: none
base findings: 0 cur findings: 0

# just lint-imports
Contracts: 6 kept, 0 broken.

# just docs-tests (mkdocs build --strict)
exit=0
Documentation built in 1.05 seconds
```
