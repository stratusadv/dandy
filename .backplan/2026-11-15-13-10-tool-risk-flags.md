# Tool risk flags (is_dangerous / can_affect_system)

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-15-13-10

## End State
`BaseTool` carries two new class attributes, `is_dangerous` and `can_affect_system` (both
default `False`), `StoryBeat` carries them on tool beats, `ToolService` copies them from the
tool to the beat, `RunCommandTool` sets `can_affect_system = True`, and the CLI story renders
tool beat labels (and their `↳` arrows) red when `is_dangerous`, orange when `can_affect_system`,
purple when `can_mutate_state`, skyblue otherwise.

## Observable Concern
`RunCommandTool` will set both `can_mutate_state` (existing, True) and `can_affect_system`
(True), so the label style needs an explicit precedence (red > orange > purple > skyblue) or
the existing orange color for the command tool would silently survive as the wrong color.

## Current State
- `dandy/domain/tool/tool.py`: `BaseTool` class attrs `name`, `description`, `action_label`,
  `can_mutate_state = False`, `emits_story_beat = True`, `timeout_seconds`, `use_shell`;
  `hash_state()` includes every attr.
- `dandy/domain/tool/beat.py`: `StoryBeat` dataclass — `label`, `description`, `kind`,
  `can_mutate_state = False`.
- `dandy/application/tool/service.py:229-236`: the only place tool flags become beat fields
  (`StoryBeat(label=..., description=..., can_mutate_state=tool.can_mutate_state)`).
- `dandy/application/agent/intelligence/tools/command/command_tool.py`: `RunCommandTool` sets
  `action_label = 'Running'`, `can_mutate_state = True`.
- `dandy/interfaces/cli/tui/story_progress.py:79-80`: `_label_style` —
  `bold_orange if beat.can_mutate_state else bold_skyblue` (used for both the heading label
  and the `↳` arrow).
- Tests asserting the orange/skyblue mapping: `tests/interfaces/cli/test_printer.py`
  (`test_frames_style_mutating_label_orange` line 200, arrow test line 255); flag assertions in
  `tests/domain/tool/test_tool.py:113`, `tests/application/tool/test_service.py:339`,
  `test_agent_tools.py:256`, `test_file_tools.py:45`.
- Docs: `docs/reference/domain.md` BaseTool member list, `docs/user_guide/tool_calling.md`
  (lines 35-42, 95-106), `docs/changelog/v3.md` (Unreleased section, currently Changes only).

## Plan
1. Add the flags to `BaseTool`
   - `is_dangerous: bool = False` and `can_affect_system: bool = False` class attrs after
     `can_mutate_state`, both in `hash_state()`; docstring note for each.
   - Done when `ruff check dandy/domain/tool/tool.py` passes and both attrs appear in
     `hash_state()`.
2. Add the flags to `StoryBeat` and wire the tool loop
   - `is_dangerous: bool = False`, `can_affect_system: bool = False` on `StoryBeat`;
     `ToolService` passes both through on the tool beat.
   - Done when `tests/application/tool/test_service.py` beat test (extended) passes.
3. Set `can_affect_system = True` on `RunCommandTool` (keep `can_mutate_state = True`;
   `is_dangerous` left unset everywhere for now, per the user).
   - Done when `tests/application/agent/intelligence/tools/test_agent_tools.py` flag test
     (extended) passes.
4. Re-color the CLI story labels
   - `_label_style` precedence: `bold_red` (is_dangerous) > `bold_orange` (can_affect_system)
     > `bold_purple` (can_mutate_state) > `bold_skyblue`; the `↳` arrow already inherits the
     label style.
   - Done when `tests/interfaces/cli/test_printer.py` (extended: all four colors, precedence)
     passes.
5. Update existing tests and add coverage
   - Renumber/fix: `test_frames_style_mutating_label_orange` becomes purple; arrow test for
     `can_mutate_state` beats expects purple; new cases for `can_affect_system` (orange) and
     `is_dangerous` (red, and red wins over orange); `test_tool.py` default-false tests;
     `test_service.py` beat carries both flags; command tool sets `can_affect_system`.
   - Done when `just test` passes.
6. Docs + AGENTS.md
   - `docs/reference/domain.md` BaseTool member list gains both attrs;
     `docs/user_guide/tool_calling.md` flag paragraph + color list updated (skyblue / purple /
     orange / red); `docs/changelog/v3.md` Unreleased gains a Features entry; AGENTS.md
     StoryProgress color description updated.
   - Done when `just docs-tests` passes and grep finds no stale "bold orange when
     can_mutate_state" wording.

## Completion Test
1. `just test` — full hermetic suite passes.
2. `ruff check .` and `ruff format --check dandy tests` clean.
3. `just docs-tests` — strict mkdocs build passes.

## Deviations
1. Pre-existing failures excluded from the completion test
    - What: `just test` reports 9 failures (`test_printer.py` story-phrase and
      file-change-section tests, `test_agent_tools.py` run-command output,
      `test_file_tools.py` action labels) and `ruff check .` reports 976
      errors repo-wide; both were verified to fail identically on the clean
      tree (via `git stash`), so they are unrelated to this change. All
      flag-related tests pass; the completion test's green criterion is
      scoped to the touched test files plus the strict docs build.
    - Why: the working tree already carried unrelated in-progress changes
      (e.g. the `◆`→`◈` bullet in `printer.py`, the Unreleased error-taxonomy
      changelog entry) whose tests/lint state is not part of this plan.
