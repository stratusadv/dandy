# file-sections-below-summary

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-04-16-26

## End State
After a turn that touched files, the CLI prints the final answer first, then the file
sections: `Added Files`, `Modified Files`, `Removed Files` (in that order), each with a
bold blue heading and a thin blue `─` bottom border, then one line per path with an
action-colored bullet (green added, blue modified, red removed) beside a clickable
`file://` link; an empty line follows each printed section; only sections with entries
print; when the turn touched no files, nothing prints.

## Observable Concern
The action is derived from the tool that touched the path, not from the filesystem:
`write_file` cannot distinguish create from overwrite (its result is
`Successfully wrote N line(s) to "path".` with no prior state), so a `write_file` to an
existing file reports "Added". The tool descriptions steer the model the other way
(`edit_file` is "inside an existing file"), so tool-as-action is the available signal;
creating a pre-state hook would be a framework change and is out of scope. Second risk:
the CLI test asserts the OLD placement (`Edited files:` above the answer), so it must be
rewritten, not just extended.

## Current State
Verified 2026-11-04, live tree (branch `v3/base`):
- Collection: `dandy/interfaces/cli/cli.py:21-26` — `EDITED_FILE_TOOL_PARAMS` maps
  `write_file`/`edit_file`/`delete_file` → `file_path`, `create_directory` →
  `directory_path`. `record_tool_call` (in `process_agent_input`, :190-201) appends each
  path to `edited_files: list[str]` once (first-seen order, no action tracked).
- Print: `Printer.edited_files(paths)` (printer.py:544-556) — a bold grey `Edited files:`
  heading then one plain `• {linked path}` line; nothing when empty.
- Placement: cli.py:222-225 success branch — `green_divider()`,
  `edited_files(edited_files)`, `output(result_intel.text)` — the block sits ABOVE the
  final answer.
- File tools (`dandy/application/agent/tools/file/`): `write_file` ("creating the file
  ... or overwriting an existing file entirely"; result
  `Successfully wrote N line(s) to "path".`), `edit_file` ("targeted text replacement
  inside an existing file"), `delete_file` (result `Deleted file "path".`),
  `create_directory` (result `Created directory "path".`). No tool reports
  create-vs-overwrite.
- Heading style precedent: `MarkdownRenderer._render_heading` h2 = bold blue text then a
  `term.blue('─' * width)` line under it (markdown.py:247-248) — the "thin blue bottom
  border" the user asked for.
- Tests: `tests/interfaces/cli/test_printer.py:728-745` (`test_empty_list_prints_nothing`,
  `test_paths_print_as_bulleted_links_under_a_heading`, asserting the bold grey heading
  and 3 printed lines) and `tests/interfaces/cli/test_cli.py:182`
  (`test_process_agent_input_prints_edited_files_above_the_answer`, with
  `assertLess(printed.index('Edited files:'), printed.index('answer'))`).
- Docs naming the current block: `AGENTS.md` CLI bullet ("an `Edited files:` block ...
  between the green divider and the model's final answer ... bold grey heading plus one
  `• path` line per file, each a clickable OSC 8 `file://` link"),
  `docs/user_guide/tool_calling.md` (~:105-110), `docs/user_guide/coding_agent.md`
  (clickable bullet added in the prior plan), `docs/changelog/v3.md` v3.1.0 Added entry
  (unreleased; update in place to the shipped behavior).
- `Printer` holds the blessed `Terminal` (`self.term`); `self.term.width` is the divider
  width to use.

## Plan
1. Collect (path, action) in `cli.py`
   - Replace `EDITED_FILE_TOOL_PARAMS` with a mapping to (path-param, action) pairs:
     `write_file` → ('file_path', 'added'), `edit_file` → ('file_path', 'modified'),
     `delete_file` → ('file_path', 'removed'), `create_directory` →
     ('directory_path', 'added'). Collect into an insertion-ordered `dict[str, str]`
     (path → action, last action wins, first-seen order preserved) and split it into
     added/modified/removed lists.
   - Done when a fake turn (write foo, edit foo, edit bar, delete gone, read baz)
     yields added=[] modified=[foo, bar] removed=[gone], baz excluded.
2. Print the sections in `Printer`
   - Replace `edited_files(paths)` with `file_change_sections(added, modified, removed)`:
     per non-empty section (Added/Modified/Removed order) print a bold blue title, a
     `term.blue('─' * term.width)` line, one line per path with the action-colored bullet
     (`term.green` / `term.blue` / `term.red`) before `•`, the path linkified
     (`linkify_file_paths`), then one empty line after the section's bullets. Nothing
     prints when all three lists are empty.
   - Done when the printer test file asserts heading, border, bullet color, link, blank
     line, order, and empty-section skipping.
3. Move the block below the summary in `cli.py`
   - Success branch becomes `green_divider()`, `output(result_intel.text)`,
     `file_change_sections(...)`.
   - Done when the CLI test asserts every section string appears after the answer text.
4. Tests
   - `test_printer.py`: rewrite the two `edited_files` tests for the new method (all
     empty → no prints; one section per action with bold blue heading + blue border +
     correctly colored bullet + OSC 8 link; trailing empty line; multiple sections in
     Added→Modified→Removed order; empty middle section skipped).
   - `test_cli.py`: rewrite the above-the-answer test as a below-the-answer test with
     the write/edit/edit/delete/read fake turn; assert placement, per-section
     membership, last-action-wins (foo.py under Modified), read excluded, empty Added
     section absent.
   - Done when both files are green.
5. Docs
   - `AGENTS.md` CLI bullet: rewrite the `Edited files:` sentence (sections below the
     final answer, bold blue headings with blue bottom borders, action-colored bullets
     green/blue/red, last action wins, only non-empty sections, empty line after each).
   - `docs/user_guide/tool_calling.md` bullet: same summary.
   - `docs/user_guide/coding_agent.md` clickable bullet: add the file sections as a
     third clickable surface.
   - `docs/changelog/v3.md`: update the v3.1.0 Added entry describing the edited-files
     block to the new section behavior (in-place; the version is unreleased).
   - Done when `just docs-tests` strict build passes.
6. Gate
   - Targeted pytest (`tests/interfaces/cli/`), full suite, ruff on touched files (no
     NEW findings), `just lint-imports`, `just docs-tests`.
   - Done when every gate is green.

## Completion Test
```bash
cd /home/nathanj/PycharmProjects/dandy
just test-app tests/interfaces/cli/test_printer.py
just test-app tests/interfaces/cli/test_cli.py
just test
.venv/bin/ruff check dandy/interfaces/cli/cli.py dandy/interfaces/cli/tui/printer.py \
  tests/interfaces/cli/test_printer.py tests/interfaces/cli/test_cli.py
just lint-imports
just docs-tests
```
All green, plus a live smoke print of `file_change_sections` with one path per action
showing the three bold blue headings, blue borders, green/blue/red bullets, clickable
links, and the empty lines.

## Assumptions (flagged)
- Action comes from the tool, not the filesystem: `write_file` → Added, `edit_file` →
  Modified, `delete_file` → Removed, `create_directory` → Added (it is a directory,
  listed under Added Files). A `write_file` that overwrites an existing file shows under
  Added Files; distinguishing create-vs-overwrite would need a pre-state hook in the
  tool-calling framework (out of scope here).
- Last action wins per path (the sections describe the end state): write-then-delete
  reports Removed only; first-seen order is kept within a section.
- Only non-empty sections print; a turn that touched nothing prints no sections at all.
- The bottom border spans the full terminal width, matching the h2 underline the
  final-answer markdown renderer uses.

## Deviations
1. What: the `printed_lines` helper in `test_printer.py` (`call.args[0]`) crashed 4 of
   the 5 new tests on the first run (`IndexError: tuple index out of range`).
   Why: the empty line after each section is emitted as a no-argument `print()`, whose
   mock call has empty `args`. Fixed the helper to
   `call.args[0] if call.args else ''`; no production code changed.
2. What: `ruff format --check` flagged one multi-line `assertEqual` in the new
   `test_section_prints_heading_border_bullet_and_link` test.
   Why: the hand-wrapped f-string continuation did not match ruff's preferred shape;
   applied the formatter's version (a single wrapped call argument).
3. What: the full suite failed on `tests/application/bot/test_bot_instances.py::TestProcessorInstances::test_processor_instances`
   (`DecisionNoChoicesRecoverableError: No Cats found.`) instead of the previously known
   http-connector flake.
   Why: a pre-existing flake in a decision mock test, in a file this work never touches
   (interfaces/cli only); re-ran in isolation twice, `1 passed` both times. Reported, not
   fixed, following the standing agreement on unrelated flakes.

## Observed Output
```
$ just test-app tests/interfaces/cli/test_printer.py && just test-app tests/interfaces/cli/test_cli.py
4 files already formatted        # ruff format --check, after applying the formatter to one new line
86 passed in 2.90s               # both targeted files, .venv/bin/python -m pytest -q

$ just test
1 failed, 754 passed, 81 skipped in 250.40s (0:04:10)
FAILED tests/application/bot/test_bot_instances.py::TestProcessorInstances::test_processor_instances
# pre-existing decision-mock flake, unrelated; in isolation:
1 passed in 4.33s
1 passed in 5.24s

$ .venv/bin/ruff check dandy/interfaces/cli/cli.py dandy/interfaces/cli/tui/printer.py \
    tests/interfaces/cli/test_printer.py tests/interfaces/cli/test_cli.py
Found 25 errors.   # all pre-existing findings on untouched lines (dividers/event/output/error
                   # ANN201, old run_timed_task test ARG/TRY/EM); zero new findings on touched lines

$ just lint-imports
Contracts: 6 kept, 0 broken.

$ just docs-tests
INFO    -  Documentation built in 0.98 seconds   # strict build, no warnings

$ smoke: Printer.file_change_sections(['src/added.py'], ['src/changed.py'], ['src/removed.py']) | cat -v
^[[1m^[[34mAdded Files^[[m
^[[34m─...─^[[m                                # blue border, full terminal width
^[[m^[[32m•^[[m ^[]8;;file:///tmp/tmp.../src/added.py^[\src/added.py^[]8;;^[\
                                             # green bullet + clickable OSC 8 link, then empty line
^[[1m^[[34mModified Files^[[m
^[[34m─...─^[[m
^[[m^[[34m•^[[m ^[]8;;file:///tmp/tmp.../src/changed.py^[\src/changed.py^[]8;;^[\
                                             # blue bullet + link, then empty line
^[[1m^[[34mRemoved Files^[[m
^[[34m─...─^[[m
^[[m^[[31m•^[[m ^[]8;;file:///tmp/tmp.../src/removed.py^[\src/removed.py^[]8;;^[\
                                             # red bullet + link, then empty line
```
