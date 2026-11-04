# makes-changes-orange-label

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-03-16-38

## End State
`BaseTool.can_mutate_state: bool = False` (originally `makes_changes` — deviation 1) exists
(skill tools inherit it), `StoryBeat` carries a
`can_mutate_state` field set from the tool's attribute when the service emits a tool-action beat,
and the CLI's `_StoryProgress` renders a `can_mutate_state=True` beat's label in bold orange
instead of bold grey in both the animating and settled frames; the mutating agent tools
(`write_file`, `edit_file`, `delete_file`, `create_directory`, `run_command` — flagged) set
`can_mutate_state = True`; tests and docs (AGENTS.md, user guide, reference member list,
changelog) describe the attribute and the color rule.

## Observable Concern
`can_mutate_state` is a static per-class flag, not per-call: `run_command` is used for read-only
commands (`pytest`, `git status`) and mutating ones (installs, builds) alike. My default:
`RunCommandTool.can_mutate_state = True` — it is the only other tool with real write power (runs
arbitrary shell without confirmation), and the dedicated git tools stay `False`. Confirmed at
presentation: `RunCommandTool` sets it `True`.

## Current State
Verified 2026-11-03, live tree (branch `v3/base`, clean at snapshot):
- `dandy/domain/tool/tool.py:39-45` — BaseTool class attrs `name`, `description`,
  `action_label`, `action_ascii_char`, (blank), `timeout_seconds`, `use_shell`.
- `dandy/domain/tool/beat.py:20-23` — `StoryBeat(label, description, kind, ascii_char)`
  dataclass, all defaulted; docstring ends "UIs may style the label, the description, and the
  kind independently."
- `dandy/application/tool/service.py:266-271` — the one tool-beat emission:
  `StoryBeat(label=label, description=description, ascii_char=tool.action_ascii_char)`.
- `dandy/interfaces/cli/tui/printer.py` — `_StoryProgress.styled_beat` (86-93) wraps the label
  in `term.bold_grey`; `settled_frame` (95-98) and `frame` (100-114) both call it (97, 112);
  line 113 already uses `term.bold_orange` (the 'Evaluating ...' suffix), so the blessed color
  exists; docstrings at 56-57 ("tool labels in grey") and ~199 ("a grey label when the beat has
  one") need updating.
- Agent tools: `action_label` set on write/edit/delete/create_directory/read/list/search
  (`dandy/application/agent/tools/file/`), `command/command_tool.py` (`'Executing'`,
  `action_ascii_char = '◦'`), `git/git_status_tool.py` + `git/git_diff_tool.py`.
- `SkillMethodTool` (`dandy/application/skill/tools.py:11`) subclasses `BaseTool` setting only
  `name`/`description` → inherits the new default `False` for free.
- `tests/application/tool/test_service.py` beat-equality assertions (191, 222-225, 249, 271,
  297-298) build expected `StoryBeat`s with explicit kwargs → a new defaulted field keeps them
  green.
- `tests/interfaces/cli/test_printer.py:105-116` pins the grey-label behavior for a default
  beat (stays green as the grey regression pin); fakes in
  `tests/application/tool/intelligence/tools.py` set no `can_mutate_state`.
- Tool-flag test homes: `tests/application/agent/test_file_tools.py` (the six file tools) and
  `TestRunCommandTool` at `tests/application/agent/test_agent_tools.py:86`.
- Docs: `AGENTS.md:168` (beat field list "label, description, kind, and ascii_char" +
  "styles the label in bold grey"); `docs/user_guide/tool_calling.md:71-82` (beat bullet,
  "with the label in bold grey"); `docs/reference/domain.md:51-65` (BaseTool member list;
  `StoryBeat` is an autofunc at 73, so its new field renders automatically);
  `docs/changelog/v3.md` `v3.1.0` Added section.

## Plan
1. `can_mutate_state` attribute on BaseTool
   - `tool.py`: `can_mutate_state: bool = False` after `action_ascii_char` (line 42); extend the
     class docstring if it enumerates class attrs.
   - Done when the attr exists with default `False` and ruff is clean on the file.
2. Flag the mutating agent tools
   - `can_mutate_state = True` next to `action_label` on `WriteFileTool`, `EditFileTool`,
     `DeleteFileTool`, `CreateDirectoryTool`, and `RunCommandTool` (the flagged decision).
     Read/list/search/git tools keep the default.
   - Done when grep shows exactly these five tools setting it.
3. Carry the flag on StoryBeat
   - `beat.py`: `can_mutate_state: bool = False` field plus one docstring sentence (tools that
     mutate state set it; UIs may style it — the CLI uses orange).
   - Done when the field exists with default `False` and every existing beat construction
     still validates.
4. Wire the service beat
   - `service.py:270`: add `can_mutate_state=tool.can_mutate_state` to the `StoryBeat(...)` build.
   - Done when a tool-action beat carries the tool's flag.
5. Orange label in the story printer
   - `styled_beat` gains `can_mutate_state: bool = False` (last param, after `kind`); label color
     = `term.bold_orange` when true, else `term.bold_grey`; `settled_frame` (97) and `frame`
     (112) pass `beat.can_mutate_state`; docstrings at 56-57 and ~199 updated (grey → orange when
     `can_mutate_state`).
   - Done when a `can_mutate_state=True` labeled beat renders an orange label in both frames and a
     default beat renders grey exactly as before.
6. Tests
   - `tests/domain/tool/test_tool.py`: default-`False` test beside the ascii-char default test.
   - `tests/application/tool/intelligence/tools.py`: a `MutatingTool` fake with
     `can_mutate_state = True`.
   - `tests/application/tool/test_service.py`: the mutating fake's beat carries
     `can_mutate_state=True`.
   - `tests/application/agent/test_file_tools.py` + `test_agent_tools.py`: the five mutating
     tools assert `True`; read/list/search/git assert `False`.
   - `tests/interfaces/cli/test_printer.py`: a labeled `can_mutate_state=True` beat renders the
     label in `bold_orange` in both frames, with no `bold_grey` in the settled frame.
   - Done when targeted pytest on all five touched test files is green.
7. Docs
   - `AGENTS.md:168` (add `can_mutate_state` to the beat field list; grey→orange clause),
     `docs/user_guide/tool_calling.md` beat bullet (flag + color rule),
     `docs/reference/domain.md` BaseTool member list (add `can_mutate_state` after
     `action_ascii_char`), `docs/changelog/v3.md` v3.1.0 Added entry.
   - Done when `just docs-tests` strict build passes.
8. Gate
   - Targeted pytest (step 6 files); full suite
     (`DANDY_SETTINGS_MODULE=tests.dandy_settings PYTHONPATH=. .venv/bin/python -m pytest -q`);
     ruff mirror-path diff on touched files (no NEW findings vs baseline — baseline is red
     repo-wide, so diff, don't clean); `just lint-imports`; `just docs-tests`.
   - Done when every gate is green.

## Completion Test
```bash
DANDY_SETTINGS_MODULE=tests.dandy_settings PYTHONPATH=. .venv/bin/python -m pytest \
  tests/domain/tool/test_tool.py tests/application/tool/test_service.py \
  tests/application/agent/test_file_tools.py tests/application/agent/test_agent_tools.py \
  tests/interfaces/cli/test_printer.py -q
```
all green, plus the full suite green, `just lint-imports` → `Contracts: 6 kept, 0 broken.`,
`just docs-tests` strict build OK, and the ruff mirror diff on touched files empty.

## Deviations
1. Attribute renamed from `makes_changes` to `can_mutate_state`.
   - What: Every reference in the End State and Plan steps 1-7 now uses `can_mutate_state`
     (the original name is struck through at its first mention).
   - Why: On presentation the user asked to work-shop the name. The shortlist was
     `makes_changes` / `mutates` / `is_mutating` / `has_side_effects`; the user proposed
     `can_mutate_state`, which names the class-level *capability* (what a tool can do) with an
     explicit object, in the house's verb-phrase boolean family (`use_shell`, `prepend`).
2. The mutating test fake lives in `test_service.py`, not `intelligence/tools.py`.
   - What: `MutatingWeatherTool` is defined beside the other beat fakes in
     `tests/application/tool/test_service.py` (`HandleWeatherTool`,
     `ActionOutputWeatherTool`, `AsciiCharWeatherTool`).
   - Why: `test_service.py` keeps every beat-specific fake locally, and the shared
     `intelligence/tools.py` fakes are only those consumed by multiple test modules.

## Observed Output
- Targeted pytest (the five touched test files): `114 passed in 2.27s`
- Full suite: `677 passed, 15 skipped, 49 subtests passed in 124.66s (0:02:04)` (5 new tests)
- ruff mirror-path diff on the 14 touched Python files: NO NEW FINDINGS (`Found 125 errors`
  on both the HEAD mirror and the working tree)
- `just lint-imports`: `Contracts: 6 kept, 0 broken.`
- `just docs-tests`: exit 0 (strict mkdocs build)
