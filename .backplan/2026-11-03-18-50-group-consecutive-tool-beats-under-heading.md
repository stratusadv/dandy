# group-consecutive-tool-beats-under-heading

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-03-18-50

## End State
Consecutive tool beats with the same label render as one list under a heading: the
label prints once as a plain heading line (no bullet), each tool beat's description
prints below it on its own line prefixed by its bullet (the beat's `ascii_char`,
default `•`), and a new heading appears whenever the label changes. The bullet is now
only on tool action output lines: heading lines and non-tool beats (narration, system,
the opening thinking phrase) have no prefix at all. The animating frame keeps the bold
orange 'Evaluating ...' suffix on the newest beat's description line, and the heading is
written exactly once, when the beat first becomes the animated beat.

## Observable Concern
The heading must be printed exactly once per label group across the animating →
settling handoff: the render loop rewrites the animated line in place every ~120 ms
(`frame()` output is written every tick, starting with `\r`), so a heading included in
every tick would duplicate and drift; and a beat that settles without ever animating
(two beats landing between ticks) must still get its heading. `_StoryProgress` tracks
which animated beat emitted its heading (`_heading_beat` identity + a `_heading_emitted`
id-set) so `frame()` emits the heading on the beat's first tick only and
`settled_frame()` skips it if already printed. Grouping is a pure function of the beat
list (compare the label to the nearest earlier labeled beat), so no ordering state can
drift between the two render paths.

## Current State
Verified 2026-11-03, live tree (branch `v3/base`):
- `run_timed_task` render loop (printer.py:285-306): settles `beats[settled_count:-1]`
  via `settled_frame` when a new beat arrives, then writes `frame(beats[-1], dots)` every
  120 ms tick; a final settle loop after the thread dies. One in-place animated line.
- `frame()` (printer.py:151-165) prefixes every beat line with
  `f'{normal}{beat.ascii_char or "•"} '`, truncates the combined label+description, and
  calls `styled_beat(label_part, description_part, kind, can_mutate_state)`.
- `settled_frame()` (printer.py:144-148) does the same prefix, one line.
- `styled_beat` (printer.py:130-142) is the only label/description styler: no label →
  plain (narration bold blue); label → `bold_grey` (or `bold_orange` when
  `can_mutate_state`) + linkified description. Used only by frame/settled_frame —
  verified no other consumers (dandy/ or tests/).
- `linkify_file_paths` (previous plan) is applied in `styled_beat`'s labeled branch;
  `tests/interfaces/cli/test_printer.py` pins the current per-line prefix at lines 84, 92,
  115, 142, 155, 166 (`startswith(f'\r{normal}• ')` / `> `) and asserts the full
  `src/foo.py lines 1-10` string.
- Beat list access is lock-guarded via the `beats` property; frame/settled_frame run only
  on the render thread.

## Plan
1. Grouping + rendering in `_StoryProgress`
   - Add `self._heading_beat: StoryBeat | None` and `self._heading_emitted: set[int]` to
     `__init__`.
   - `_previous_tool_label(beat)`: nearest earlier beat in `self.beats` with a label, its
     label, else ''. `_needs_heading(beat)`: labeled and different from that.
   - `_styled_label(beat)`: `bold_orange`/`bold_grey` per `can_mutate_state` + `normal`.
   - Rewrite `settled_frame(beat)`: labeled beat → optional heading line
     (`_needs_heading` and not already emitted) + `char description` line (char =
     `ascii_char or '•'`); unlabeled beat → plain description line, no prefix.
   - Rewrite `frame(beat, dots)`: same optional heading (emitted on the beat's first tick
     via the identity check, marking `_heading_emitted`); the description line keeps the
     bullet for labeled beats and none otherwise; truncation now applies to the
     description alone (the heading has its own line); 'Evaluating' suffix unchanged.
   - Replace `styled_beat` with the label/description helpers (description keeps:
     linkify for labeled beats, bold blue for narration, plain otherwise).
   - Done when a same-label beat pair settles as `Reading\n• a.py\n• b.py\n` and a
     label change settles as a new heading line.
2. Docstrings
   - `_StoryProgress` docstring and `run_timed_task` docstring rewritten to the heading +
     bulleted-list rendering (grey/orange heading, bullets only on tool output lines,
     plain non-tool lines).
   - Done when both docstrings describe the new behavior.
3. Tests (`tests/interfaces/cli/test_printer.py`)
   - Rework the six existing prefix assertions (lines 84, 92, 115, 142, 155, 166) to the
     new shapes; the grey test now expects `Reading\n• ...` in the first animating frame
     and `• ...` in the settled frame (heading already emitted by the frame call).
   - New: repeated label omits the second heading; label change emits a new heading;
     label reappearing after another label emits a heading again; a non-tool beat between
     same-label beats does not break the group; heading is emitted once across repeated
     `frame()` calls; non-tool beats have no `•`/prefix.
   - Done when the file is green.
4. Docs
   - `AGENTS.md` story bullet: replace the "each beat is prefixed by its ascii_char ...
     styles the label in bold grey ..." clause with the heading + bulleted list
     description; `docs/user_guide/tool_calling.md` beat bullet: same;
     `docs/changelog/v3.md` v3.1.0 **Changed** entry.
   - Done when `just docs-tests` strict build passes.
5. Gate
   - Targeted pytest (`tests/interfaces/cli/test_printer.py`); full suite
     (`DANDY_SETTINGS_MODULE=tests.dandy_settings PYTHONPATH=. .venv/bin/python -m pytest -q`);
     ruff mirror-path diff on touched files (no NEW findings); `just lint-imports`;
     `just docs-tests`.
   - Done when every gate is green.

## Completion Test
```bash
DANDY_SETTINGS_MODULE=tests.dandy_settings PYTHONPATH=. .venv/bin/python -m pytest \
  tests/interfaces/cli/test_printer.py -q
```
all green, plus the full suite green, `just lint-imports` → `Contracts: 6 kept, 0 broken.`,
`just docs-tests` exit 0, and the ruff mirror diff on touched files empty.

## Assumptions (flagged)
- A non-tool beat (narration/system) between two same-label tool beats does NOT break the
  group; the heading follows the label sequence of tool beats only ("until the tool call
  changes").
- A label that reappears after a different label gets a fresh heading.
- The tool output line keeps the tool's own `ascii_char` (e.g. `◦` for `run_command`) as
  its bullet; `•` is the default.
- Non-tool beats lose their prefix entirely (narration stays bold blue, system plain).

## Deviations
none yet

## Observed Output
- Targeted: `pytest tests/interfaces/cli/test_printer.py -q` → `36 passed in 2.04s`
  (six reworked prefix assertions + 7 new `TestStoryProgressHeadingGrouping` tests:
  first-labeled-beat heading, repeated label shares the first heading, heading
  once across animating + settling, label change emits a new heading, reappearing
  label gets a fresh heading, non-tool beat does not break the group, settled
  frame emits the heading when the beat never animated).
- Full suite: `690 passed, 15 skipped, 49 subtests passed in 124.76s`.
- Ruff mirror diff (HEAD vs current on `printer.py` + `test_printer.py`):
  21 findings each, NEW findings: none.
- `just lint-imports` → `Contracts: 6 kept, 0 broken.`
- `just docs-tests` → `Documentation built in 0.97 seconds` (strict build OK).
