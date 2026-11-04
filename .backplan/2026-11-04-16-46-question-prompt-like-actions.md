# question-prompt-like-actions

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-04-16-46

## End State
When the agent asks a question mid-turn, the CLI prints, in order: an empty line, the
tool's action label (`Asking`) in the beat's label style (bold skyblue, bold orange when
`can_mutate_state`), then a `↳` line with the arrow in the label's color and the
question text in plain black to the right of the arrow on the same line, then the
numbered choices (plain purple, unchanged), a plain purple `─` divider, the `⦿ ` input
prompt — and after the answer, a plain purple `─` divider (previously bold purple under
the choices, bold grey after the answer; the `Question: ` prefix is gone).

## Observable Concern
The "empty line above" depends on the cursor state `pause_at_fresh_line` leaves (the
reused leftover phrase line, or a fresh column-zero line): the block must print its
own leading newline so the empty line is guaranteed regardless of which case occurs.
Second risk: the real `tui.term` in tests runs on a non-TTY, where blessed may emit no
color escapes at all, so color assertions need a `force_styling='default'` terminal
injected into both `tui.term` and `tui.printer.term`.

## Current State
Verified 2026-11-04, live tree (branch `v3/base`):
- Question prompt: `dandy/interfaces/cli/tui/tui.py` `Tui.get_user_input` (:28-39):
  `self._input_prefix = self.term.purple('⦿ ')`, then
  `printer.event(f'{term.purple}Question: {term.normal}{question}')` (the `Question: `
  prefix is purple, the question text itself prints in the default color), then one
  `event` per choice (`{term.purple}{index}){term.normal} {choice}`), then
  `printer.purple_divider()`. After input (:74-75): `if question: self.printer.divider()`.
- Dividers (`printer.py`): every divider method is BOLD — `purple_divider` =
  `term.bold_purple('─' * width)` (:342-343), `divider` = `term.bold_grey(...)`
  (:345-346), plus blue/green/red/grey bold variants. The only non-bold divider line in
  the codebase is the inline `term.blue('─' * width)` used by
  `Printer.file_change_sections` (:566).
- Single callers: `purple_divider()` is called only by the question branch (tui.py:35);
  `divider()` is called only by the post-question line (tui.py:75). No other
  `Printer.divider` references in `dandy/`, `tests/`, or the docs (the `divider` hits in
  `docs/reference/domain.md` / `docs/user_guide/prompts.md` are `Prompt.divider()`, a
  different class); `Printer` has no mkdocstrings member list, so removing the method
  cannot break the strict docs build.
- Story-beat layout the question should match (`_StoryProgress`, printer.py): a heading
  line begins with a leading `\n` (the blank line above; `_styled_label` :123-124),
  then each beat prints `{label_style}↳{normal} {description}` — the same `↳` arrow the
  user calls "Down Right Arrow" — all flush left at column zero.
- The question's story beat: `QuestionTool.action_label = 'Asking'` with
  `action_output` returning the question text, so the story already prints
  `Asking` / `↳ <question>` just before the prompt (the question text appears twice by
  design, as it does today).
- Tests: `tests/interfaces/cli/test_tui.py` — `TestTuiChoices` patches
  `tui.term.cbreak` and `builtins.print` and asserts
  `'Question: Which color?'` / `'1) red'` / `'2) blue'` in the printed text
  (`test_choices_are_printed_numbered_under_the_question`, :84-96). No test asserts the
  divider colors. `test_printer.py` uses `Terminal(force_styling='default')` and asserts
  raw escape strings (house pattern for color assertions).
- Docs: nothing documents the question prompt's styling (no `Question:` or purple
  mentions in `AGENTS.md`/`docs/` outside the unrelated bold-purple compaction note);
  the v3.1.0 `QuestionTool` changelog entry only says "the CLI renders the choices
  numbered and accepts either a number or free text" (still accurate). The Changed
  section of the changelog does track other TUI display changes (the `↳` arrow entry),
  so a short entry belongs there.
- The tree carries uncommitted work from the earlier tasks (file sections, clickable
  links) plus the user's own parallel edits (session_store, http connector) — none touch
  `tui.py` or the divider methods.

## Plan
1. New question block layout in `tui.py`
   - ~~Question branch of `get_user_input`: replace the `Question: ` event with
     `printer.event(f'\n{term.purple}↳{term.normal}')` (leading `\n` = the empty line
     above, matching the story heading pattern; arrow on its own line, flush left) and
     `printer.event(f'{term.purple}{question}{term.normal}')` (the question text on the
     next line, plain purple).~~ (superseded by deviation 4)
   - Question branch of `get_user_input`: replace the two purple events with a label
     line and an arrow line that mirror the story beats exactly —
     `label_style = term.bold_orange if QuestionTool.can_mutate_state else term.bold_skyblue`,
     then `printer.event(f'\n{label_style}{QuestionTool.action_label}{term.normal}')`
     (leading `\n` = the empty line above, same as `_styled_label`) and
     `printer.event(f'{label_style}↳{term.normal} {linkify_file_paths(question)}')`
     (arrow in the label's color, plain black question text to its right, paths
     linkified exactly like a beat description; `linkify_file_paths` comes from
     `dandy.interfaces.cli.tui.text`, `QuestionTool` from
     `dandy.application.agent.tools.question.question_tool` — an interfaces →
     application import the contracts already allow).
   - Keep the choices loop and the `⦿ ` prefix unchanged; post-input line stays
     `self.printer.purple_divider()` (plain purple).
   - Done when a unit test asserts the print sequence: empty line + label line,
     arrow + black question line, choices, divider, input, divider.
2. Divider colors in `printer.py`
   - `purple_divider`: `term.bold_purple` → `term.purple` (only the question flow uses
     it, so the change is scoped to the question).
   - `divider()` has no remaining callers after step 1 → delete the method (flagged
     structural decision: it is TUI-internal, not exported from `dandy`, not in any
     docs member list).
   - Done when a unit test shows both dividers are plain purple and
     `grep -rn 'printer.divider(' dandy tests` returns nothing.
3. Tests in `test_tui.py`
   - `TestTuiQuestionPrompt` (built and green for the first layout; now re-pointed at
     the redirected one): build `Terminal(force_styling='default')`, patch it into both
     `tui.term` and `tui.printer.term`, mock its `cbreak`, patch `builtins.print` and
     `sys.stdout.write`; drive `get_user_input(question=..., choices=...)` to a
     double-escape.
     - layout test: the first print is the label event with a leading `\n` (empty line
       above, then `Asking` in `term.bold_skyblue`), the second print is
       `{bold_skyblue}↳{normal} Which color?` (arrow in the label's color, plain
       question text to its right, same line), choices and both dividers follow in
       order;
     - color test: label and arrow use `term.bold_skyblue`, the question text carries no
       color code, the choice lines use `term.purple`, and both divider lines equal
       `term.purple('─' * term.width)` with neither `term.bold_purple` nor
       `term.bold_grey` anywhere in the block.
   - `test_choices_are_printed_numbered_under_the_question` (already updated for the
     first layout; still valid): assert the question text, `↳`, and the choices print
     and `'Question: ' not in printed` (plain-text asserts only — the real non-TTY
     terminal may emit no color escapes).
   - Done when `just test-app tests/interfaces/cli/test_tui.py` is green.
4. Docs
   - `docs/changelog/v3.md` v3.1.0 **Changed**: the entry added for the first layout is
     rewritten in place for the final layout — the agent question prompt displays like a
     story action (empty line, the tool's action label in the beat's label style, a
     `↳` arrow in the label's color with the question text in plain black on the same
     line; the `Question: ` prefix is removed) and both dividers around the prompt
     (under the choices, after the answer) are plain purple instead of bold purple /
     bold grey.
   - No other docs changes (verified: no page documents the prompt's styling;
     `Printer` has no reference member list).
   - Done when `just docs-tests` strict build passes.
5. Gate
   - `just test-app tests/interfaces/cli/test_tui.py`, ruff check + `ruff format --check`
     on the touched files (no NEW findings), `just test` (full suite),
     `just lint-imports`, `just docs-tests`, plus a live smoke: drive
     `get_user_input(question=..., choices=...)` to a double-escape with mocked `inkey`,
     pipe stdout through `cat -v`, and inspect the raw sequences.
   - Done when every gate is green and the smoke shows the plain-purple (never bold)
     sequences.

## Completion Test
```bash
cd /home/nathanj/PycharmProjects/dandy
just test-app tests/interfaces/cli/test_tui.py
.venv/bin/ruff check dandy/interfaces/cli/tui/tui.py dandy/interfaces/cli/tui/printer.py \
  tests/interfaces/cli/test_tui.py
.venv/bin/ruff format --check dandy/interfaces/cli/tui/tui.py dandy/interfaces/cli/tui/printer.py \
  tests/interfaces/cli/test_tui.py
just test
just lint-imports
just docs-tests
```
All green, plus the live smoke print of the question block showing: empty line,
`Asking` label in the beat's label color, `↳` arrow with the plain question text to its
right on the same line, numbered choices, plain purple `─` dividers (no `\x1b[1m` before
any purple sequence), and the trailing plain purple divider after the answer.

## Assumptions (flagged)
- "The question should have a purple line not bold_purple" is read as the divider under
  the choices going from bold purple to plain purple; the question text itself also
  becomes plain purple (today only the `Question: ` prefix is purple), which satisfies
  either reading.
- The arrow and the question lines are both flush left at column zero (no indentation
  under the arrow), matching "the question on the next line" literally; the story
  description's same-line-after-arrow layout does not apply because the user asked for
  the question on the next line.
- The arrow is plain purple (the question's theme color), not bold skyblue/orange like
  tool-beat arrows, consistent with "not bold_purple".
- `Printer.divider()` is deleted once step 1 removes its only caller (dead TUI-internal
  method, verified absent from docs and the public API).
- The `Asking` story beat above the prompt is untouched (the question text already
  appears there as the beat description, same as today).
- The prompt reads its label and style from `QuestionTool` (`action_label`,
  `can_mutate_state`) via a new `dandy/interfaces/cli/tui/tui.py` →
  `dandy/application/agent/tools/question/question_tool.py` import (interfaces →
  application, already permitted by the contracts) so the prompt stays in sync with the
  beat's label if the tool ever changes; the Tui only ever renders the question tool's
  prompt today.

## Deviations
1. The question line's first test run failed on my own expectation, not the
   implementation: I expected a leading `\n` in the question text's print, but the
   blank line belongs to the arrow event (the question prints on its own line with no
   leading newline). Fixed the expectation; production code unchanged.
2. The choices assertions `'1) red'` / `'2) blue'` failed on the first run because the
   forced-styling terminal interleaves an escape between the number and the text
   (`1)\x1b[m red`). Changed the assertions to check the fragments (`'1)'` + `'red'`).
3. The user's parallel in-progress divider rename (`green_divider` →
   `bold_green_divider` in `printer.py`/`cli.py`/`main.py`) left five
   `@mock.patch.object(tui.printer, 'green_divider')` decorators in
   `tests/interfaces/cli/test_cli.py`, failing 5 tests with
   `AttributeError: ... does not have the attribute 'green_divider'` and blocking the
   full-suite gate.
   - What: updated those five decorators to `bold_green_divider` (the name is unambiguous
     in the tree; the user's call sites in `cli.py`/`main.py` already use it).
   - Why: the completion test requires the full suite green; the failure was a mechanical
     leftover of the user's rename, not of this task.
4. User redirect after the first layout ran live (their session paste showed the
   prompt as a bare purple `↳` line with the purple question on the next line):
   "The question label isn't showing up like the other labels, and the question text
   should be in black text to the right of the down right arrow."
   - What: step 1's layout re-derived — the prompt now prints the tool's action label
     (`Asking`, read from `QuestionTool.action_label` in the beat's label style) after
     the empty line, then a `↳` arrow in the label's color with the question text in
     plain black to its right on the same line (linkified like a beat description). The
     purple divider changes from step 2 and the choices loop are unchanged.
   - Why: the first reading of "display like the other actions" put the arrow alone on
     its line with a purple question below; live, the user wanted the same
     label + arrow + black-text shape as the story beats.
5. The re-pointed layout test's first run failed on its own expectation, not the
   implementation: the arrow line's expectation ended with a double `{term.normal}`
   (assuming the `linkify_file_paths` output carried a trailing reset), but
   `linkify_file_paths` returns path-free input as plain text, so the arrow line ends
   with the event wrapper's single trailing `{term.normal}` only. Fixed the test
   expectation; production code unchanged.

## Observed Output
Observed 2026-11-04, branch `v3/base` (all gates run after every step was complete):

Targeted tests:
```
.venv/bin/python -m pytest tests/interfaces/cli/test_tui.py -q
9 passed in 0.21s

.venv/bin/python -m pytest tests/interfaces/cli/test_tui.py tests/interfaces/cli/test_printer.py tests/interfaces/cli/test_cli.py -q
95 passed in 2.97s
```

Lint/format (no NEW findings; all 46 findings across the four touched files are
pre-existing, none on lines this task touched):
```
.venv/bin/ruff format --check dandy/interfaces/cli/tui/tui.py dandy/interfaces/cli/tui/printer.py tests/interfaces/cli/test_tui.py tests/interfaces/cli/test_printer.py
4 files already formatted
```

Full suite:
```
just test
757 passed, 81 skipped in 147.81s (0:02:27)
```

Contracts and docs:
```
just lint-imports
Contracts: 6 kept, 0 broken.

just docs-tests
Documentation built in 0.98 seconds
```

Live smoke (`DANDY_SETTINGS_MODULE=tests.dandy_settings .venv/bin/python
/tmp/smoke_question.py | cat -v`; drives `get_user_input(question='Do you have a
cat?', choices=['yes', 'no'])` to a double-escape with a
`Terminal(force_styling='default')` injected, asserts the exact six-line sequence
and prints `SMOKE OK`):
```
^[[m
^[[1m^[[38;2;135;206;235mAsking^[[m^[[m
^[[m^[[1m^[[38;2;135;206;235mM-bM-^FM-3^[[m Do you have a cat?^[[m
^[[m^[[38;2;160;32;240m1)^[[m yes^[[m
^[[m^[[38;2;160;32;240m2)^[[m no^[[m
^[[38;2;160;32;240m<80 x M-bM-^TM-^@>^[[m
^[[38;2;160;32;240m<80 x M-bM-^TM-^@>^[[m
SMOKE OK
```
Reading: empty line, `Asking` in bold skyblue (`^[[1m^[[38;2;135;206;235m`), the `↳` arrow
(`M-bM-^FM-3`) in the label's color with the question in plain black to its right on the
same line, plain purple numbered choices, and both dividers plain purple with no
`^[[1m` (bold) anywhere in the block.
