# remove-ascii-char-fixed-transition-arrow

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-04-10-19

## End State
Every CLI story tool beat is prefixed by a fixed `↳` colored like its label
(bold grey for read-only tools, bold orange for `can_mutate_state` tools) in
both the animating and settled frames; `BaseTool.action_ascii_char` and
`StoryBeat.ascii_char` no longer exist.

## Observable Concern
Both names are public surface: `StoryBeat` is an exported dataclass
(`dandy.domain.tool`) and `action_ascii_char` is a documented `BaseTool` class
attribute with one real override (`run_command`'s `◦`, which becomes `↳`).
The removal is a small breaking change for hand-built StoryBeats / tool
subclasses; every test asserting a per-tool character must move to the styled
`↳`, and no `ascii_char` reference may remain anywhere under `dandy/` or
`tests/`.

## Current State
Verified 2026-11-04, live tree (branch `v3/base`):
- `dandy/domain/tool/tool.py:44` — `action_ascii_char: str = '•'`; docstring
  lines 26-27 describe it ("without one, a bullet is used").
- `dandy/domain/tool/beat.py` — `StoryBeat.ascii_char: str = ''` (line 26) +
  docstring lines 14-16 ("tool beats carry the tool's `action_ascii_char`").
- `dandy/application/tool/service.py:276` — `StoryBeat(...,
  ascii_char=tool.action_ascii_char)`.
- `dandy/interfaces/cli/tui/printer.py` — settled line
  `f'{self.term.normal}{beat.ascii_char or "•"} {description}'` (line 175);
  animating prefix `f'{self.term.normal}{beat.ascii_char or "•"} '` (line
  188); label style computed inline in `_styled_label` (lines 145-148:
  `bold_orange if beat.can_mutate_state else bold_grey`).
- `dandy/application/agent/tools/command/command_tool.py:19` —
  `action_ascii_char = '◦'` (the only real override).
- Tests: `tests/domain/tool/test_tool.py:113-116`
  (`test_action_ascii_char_defaults_to_bullet`); `tests/application/tool/
  test_service.py` (`AsciiCharWeatherTool` fake line 37,
  `test_prompt_to_intel_reports_tool_action_ascii_char` line 335, and
  `ascii_char='•'` / `'>'` kwargs in the StoryBeat expectations at lines
  195/227/229/253/329/353/380); `tests/interfaces/cli/test_printer.py`
  (`test_tool_beat_renders_its_own_ascii_char` lines 159-168 asserting `> `;
  `test_multiline_beat_animates_on_a_single_line` lines 170-185 using
  `ascii_char='>'`).
- Docs: `AGENTS.md:168` (three mentions: the beat field list "label,
  description, kind, ascii_char, and can_mutate_state"; "set next to `name` /
  `description` / `action_ascii_char`"; "prefixed by its `ascii_char` (the
  tool's `action_ascii_char` class attribute, defaulting to `•`) — bullets
  exist only on those tool output lines"); `docs/user_guide/tool_calling.md`
  (the `action_ascii_char` sentence in the action_label bullet, lines 35-37;
  the progress_callback bullet "its `action_ascii_char` as `ascii_char`",
  line 78; "prefixed by its `ascii_char`", line 86);
  `docs/reference/domain.md:57` (`action_ascii_char` in the explicit
  `BaseTool` member list; the `StoryBeat` directive has no member list, so it
  re-renders itself); `docs/architecture/agents.md:204` mentions it — **left
  untouched**: that file carries the user's uncommitted in-flight work, so
  its one stale sentence is flagged for the user instead.
- Changelog: v3.1.0 is unreleased; the historical entry at lines 210-216
  describes the ascii_char feature as shipped-at-the-time. Repo convention is
  to add a new entry, not rewrite history — a new `### Changed` entry goes on
  top.

## Plan
1. Domain, service, tool
   - `tool.py`: delete the `action_ascii_char` attribute + its docstring
     sentence. `beat.py`: delete the `ascii_char` field + docstring sentence.
     `service.py`: drop the `ascii_char=` kwarg. `command_tool.py`: delete
     `action_ascii_char = '◦'`.
   - Done when `grep -rn ascii_char dandy/ tests/` prints nothing.
2. Renderer
   - `printer.py`: extract `_label_style(beat)` (bold_orange when
     `can_mutate_state` else bold_grey), use it in `_styled_label`; settled
     line becomes `f'{style}↳{self.term.normal} {description}'`, animating
     prefix `f'{style}↳{self.term.normal} '`. Update the `_StoryProgress`
     class docstring and the `run_timed_task` docstring ("bulleted line"
     wording) to the fixed `↳` rule.
   - Done when the step-3 tests pass.
3. Tests
   - `test_tool.py`: delete `test_action_ascii_char_defaults_to_bullet`.
   - `test_service.py`: delete `AsciiCharWeatherTool` + its test; drop the
     `ascii_char=...` kwargs from every StoryBeat expectation.
   - `test_printer.py`: replace `test_tool_beat_renders_its_own_ascii_char`
     with `test_tool_beat_renders_an_arrow_in_the_label_color` (a read-only
     beat's arrow styled `bold_grey`, a `can_mutate_state` beat's arrow
     styled `bold_orange`, in both frames); the multiline test drops
     `ascii_char='>'` and expects the `↳` prefix.
   - Done when the targeted files (test_tool, test_service, test_printer,
     test_cli) are all green.
4. Docs
   - `AGENTS.md:168`: the three mentions become the fixed-`↳`-in-the-label-
     color wording. `docs/user_guide/tool_calling.md`: the three spots.
     `docs/reference/domain.md`: drop the member line. `docs/changelog/v3.md`:
     new top `### Changed` entry (fixed `↳` prefix colored like the label;
     `BaseTool.action_ascii_char` and `StoryBeat.ascii_char` removed).
   - Done when `just docs-tests` strict build passes.
5. Gate
   - Targeted pytest (four files); full suite; ruff mirror diff on touched
     Python files; `just lint-imports`; `just docs-tests`.
   - Done when every gate is green.

## Completion Test
```bash
DANDY_SETTINGS_MODULE=tests.dandy_settings PYTHONPATH=. .venv/bin/python -m pytest \
  tests/domain/tool/test_tool.py tests/application/tool/test_service.py \
  tests/interfaces/cli/test_printer.py tests/interfaces/cli/test_cli.py -q
```
all green, `grep -rn ascii_char dandy/ tests/` empty, full suite green,
`just lint-imports` → `Contracts: 6 kept, 0 broken.`, `just docs-tests`
exit 0, ruff mirror diff on touched files empty (no NEW findings).

## Deviations
none

## Observed Output
- Targeted pytest (final code): `130 passed in 2.54s`.
- `grep -rn ascii_char dandy/ tests/`: no source matches (stale `__pycache__`
  `.pyc` matches only).
- Full suite run 1: `722 passed, 81 skipped, 49 subtests passed in 182.07s`.
- Full suite run 2: `722 passed, 81 skipped, 49 subtests passed in 247.10s`.
- Ruff mirror on the 8 touched Python files: base 110 findings, current 107;
  per-file rule-multiset compare shows zero new findings — the only deltas are
  the deleted tests' own findings (`test_service.py` −{ANN001:1, ANN201:1},
  `test_tool.py` −{ANN201:1}; `service.py`, `printer.py`, `test_printer.py`
  identical). `ruff format`: `8 files already formatted`.
- `just lint-imports`: `Contracts: 6 kept, 0 broken.`
- `just docs-tests`: exit 0 (`Documentation built in 0.98 seconds`).
