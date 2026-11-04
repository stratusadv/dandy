# file-sections-empty-line-above

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-04-17-03

## End State
After the final answer, each non-empty file section (`Added Files`, `Modified Files`,
`Removed Files`) prints with an empty line above its bold blue heading and no empty line
after its bullets; the block still sits below the answer and nothing prints when the
turn touched no files.

## Observable Concern
The empty line is per-section (not once per block): with two sections there is a blank
line before each heading and still no blank line between the last bullet and the next
REPL divider; the existing line-count/position tests in `TestPrinterFileChangeSections`
were written for the trailing-empty-line shape and must be re-pointed, not just extended.

## Current State
Verified 2026-11-04, live tree (branch `v3/base`):
- `Printer.file_change_sections` (`dandy/interfaces/cli/tui/printer.py`): per non-empty
  section — `print(bold_blue title)`, `print(term.blue('─' * term.width))`, one
  `print(f'{normal}{bullet_style}•{normal} {linkify_file_paths(path)}')` per path, then
  `print()` (the trailing empty line). Docstring says "an empty line after each
  section".
- Placement: `cli.py` success branch — `green_divider()` (now `bold_green_divider`
  after the user's in-progress rename), `output(result_intel.text)`,
  `file_change_sections(...)` — unchanged by this task.
- Tests: `tests/interfaces/cli/test_printer.py::TestPrinterFileChangeSections` —
  `test_all_empty_prints_nothing` (0 prints), `test_section_prints_heading_border_bullet_and_link`
  (4 lines: heading/border/bullet/`''`), `test_bullets_are_colored_per_action` (3
  bullet lines, color-agnostic to position), `test_sections_print_in_order_and_skip_empty`
  (2 sections → 8 lines; `lines[0]` = Added heading, `lines[4]` = Removed heading),
  `test_empty_line_after_each_section` (3 sections → 12 lines; empties at 3/7/11).
- `tests/interfaces/cli/test_cli.py::test_process_agent_input_prints_file_sections_below_the_answer`
  asserts relative ordering via `printed.index(...)` — unaffected by moving the empty
  line.
- Docs: `AGENTS.md` CLI bullet says the sections print "with an empty line after each
  section (nothing prints when no such tool ran)"; the v3.1.0 Added changelog entry
  does not mention the empty line (no change needed there).
- This is a redirect on the executed plan
  `.backplan/2026-11-04-16-26-file-sections-below-summary.md` (its "empty line after
  each section" end state is superseded by this doc).

## Plan
1. Move the empty line in `Printer.file_change_sections`
   - Replace the trailing `print()` after the bullets with a `print()` before the
     bold blue title (inside the per-section loop, so every printed section gets one);
     update the docstring ("an empty line before each section").
   - Done when the printer tests assert empty-above / no-trailing-empty.
2. Tests in `test_printer.py`
   - `test_section_prints_heading_border_bullet_and_link`: 4 lines become
     `['', heading, border, bullet]`.
   - `test_sections_print_in_order_and_skip_empty`: 8 lines; Added heading at
     `lines[1]`, Removed heading at `lines[5]`, empties at 0 and 4.
   - `test_empty_line_after_each_section` → `test_empty_line_before_each_section`:
     3 sections → 12 lines; empties at 0/4/8 and `lines[11]` is the last bullet (no
     trailing empty line).
   - `test_all_empty_prints_nothing` and `test_bullets_are_colored_per_action` stay as
     is.
   - Done when `just test-app tests/interfaces/cli/test_printer.py` is green.
3. Docs
   - `AGENTS.md` CLI bullet: "with an empty line after each section" → "with an empty
     line before each section".
   - Done when `just docs-tests` strict build passes.
4. Gate
   - `just test-app tests/interfaces/cli/test_printer.py` +
     `just test-app tests/interfaces/cli/test_cli.py`, ruff check +
     `ruff format --check` on the touched files (no NEW findings), `just test`
     (full suite), `just lint-imports`, `just docs-tests`.
   - Done when every gate is green.

## Completion Test
```bash
cd /home/nathanj/PycharmProjects/dandy
just test-app tests/interfaces/cli/test_printer.py
just test-app tests/interfaces/cli/test_cli.py
.venv/bin/ruff check dandy/interfaces/cli/tui/printer.py tests/interfaces/cli/test_printer.py
.venv/bin/ruff format --check dandy/interfaces/cli/tui/printer.py tests/interfaces/cli/test_printer.py
just test
just lint-imports
just docs-tests
```
All green.

## Assumptions (flagged)
- One empty line per printed section (two sections → two empty lines, one before each
  heading), matching "below each file section" read per-section; the first section's
  empty line separates it from the final answer.
- No other behavior changes (heading/border/bullet/link styling, ordering, placement
  below the answer, last-action-wins collection all stay as shipped).

## Deviations
none yet

## Observed Output
Observed 2026-11-04, branch `v3/base` (all gates run after every step was complete):

Targeted tests:
```
.venv/bin/python -m pytest tests/interfaces/cli/test_tui.py tests/interfaces/cli/test_printer.py tests/interfaces/cli/test_cli.py -q
95 passed in 2.97s
```

Lint/format (no NEW findings; all findings on the two touched files are pre-existing,
none on lines this task touched):
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
