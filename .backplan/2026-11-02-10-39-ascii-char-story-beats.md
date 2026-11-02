# ASCII char story beats, no indentation, printer cleanup

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-02-10-39

## End State

Every CLI story-output line is flush left at column 0: story beat lines are
prefixed by a single ASCII character (the tool's `action_ascii_char` for tool
beats, `.` for narration/system beats), and the `↳` arrow plus its indentation
are gone from the task header, completion, error, and question lines.
`printer.py` contains no dead code: the `step_indent`/`indent` parameters are
removed, `indented_event` becomes a plain `event` helper, and the already-orphaned
`start_task`, `end_task`, and `blank_line` methods are deleted.

## Observable Concern

The printer tests anchor on the old layout in several places that are easy to
miss: `tests/interfaces/cli/test_printer.py:97` filters story lines with
`'↳ ' in line`, four `_StoryProgress(..., step_indent=2)` constructors exist
(lines 42, 49, 57, 69), the frame/settled-frame expected strings embed the
`   ↳ ` prefix, and `tests/application/tool/test_service.py` compares exact
`StoryBeat(...)` objects that will now carry `ascii_char='.'`. Missing any of
these leaves silently-passing or failing assertions against the old layout.

## Current State

- `dandy/interfaces/cli/tui/printer.py:58-108` — `_StoryProgress.__init__(term, step_indent=2)`;
  `settled_frame` (line 92) and `frame` (line 96) both build
  `indent = ' ' * ((self.step_indent * 2) + 1)` and prefix beats with
  `{indent}↳ `.
- `dandy/interfaces/cli/tui/printer.py:296-301` — `indented_event(text, indent=0, end='\n')`
  prints `{" " * ((indent * 2) + 1)}↳ {text}`. Call sites: `running_phrase`
  (line 165, indent 0), `start_task` (line 168, indent 1, `end=''`),
  `run_timed_task` header (line 206, indent 1), completion (line 253, indent 2),
  `error` (line 311), and `dandy/interfaces/cli/tui/tui.py:28` (question line,
  indent 1).
- Dead code in `printer.py` (zero callers, verified by grep across `dandy/` and
  `tests/`): `start_task` (line 167, returns `perf_counter()`), `end_task`
  (line 176), `blank_line` (line 128). `running_phrase`'s `action_name`
  parameter is unused by its body (sole caller `dandy/interfaces/cli/cli.py:145`).
- `dandy/interfaces/cli/cli.py:31` — `DandyCli._emit_verbose` writes
  `f'\r   ↳ {message}\n'` for DEBUG-mode verbose tracing. This is the raw
  tool-round trace stream, not the story; **assumed out of scope** (flagged here
  for the approval pass).
- `dandy/domain/tool/tool.py` — `BaseTool` class attrs: `name`, `description`,
  `action_label`, `timeout_seconds = 30`, `use_shell = False`; method
  `action_output(self, **_kwargs) -> str | None` (default `None`). No
  `action_ascii_char` yet.
- `dandy/domain/tool/beat.py` — `StoryBeat` dataclass: `label: str = ''`,
  `description: str = ''`, `kind: str = 'system'`. No ascii-char field yet.
- `dandy/application/tool/service.py` — `_process_tool_call` builds
  `StoryBeat(label=..., description=...)` for tool beats; the model summary beat
  uses `kind='narration'`; the compaction beat uses defaults.
- 10 built-in agent tools set `action_label`/`action_output`; none override any
  ascii char (decision: they stay at the `.` default).
- No `↳` occurrences in `docs/`, `AGENTS.md`, or `specs/` (verified by grep),
  so no doc text references the arrow itself.
- Styling rules from the two prior tasks stay: tool labels bold grey, narration
  beats bold blue, system beats plain.

## Plan

1. Domain: ascii char on the tool and the beat
   - Add `action_ascii_char: str = '.'` class attr to `BaseTool`
     (`dandy/domain/tool/tool.py`); add `ascii_char: str = ''` to `StoryBeat`
     (`dandy/domain/tool/beat.py`; empty means "renderer falls back to `.`").
   - In `dandy/application/tool/service.py::_process_tool_call`, pass
     `ascii_char=tool.action_ascii_char` on the tool beat only; narration and
     compaction beats stay at the default.
   - Done when `test_tool.py` asserts the `'.'` default, `test_service.py`
     expectations carry `ascii_char='.'` on tool beats, and both suites pass.

2. Printer: flush-left char prefixes, drop the arrow and dead code
   - `_StoryProgress.__init__` loses `step_indent`; `settled_frame` and `frame`
     render `{char} {beat_text}` at column 0 with `char = beat.ascii_char or '.'`
     (the `frame` truncation formula keeps using the new shorter prefix).
   - Rename `indented_event` to `event`; body becomes
     `print(f'{self.term.normal}{text}{self.term.normal}', end=end, flush=True)`
     (no indent, no arrow). Update all call sites in `printer.py`
     (`running_phrase`, `run_timed_task` header and completion, `error`) and
     `dandy/interfaces/cli/tui/tui.py:28`.
   - Delete dead `start_task`, `end_task`, `blank_line`; drop the unused
     `action_name` parameter from `running_phrase` and its call in
     `dandy/interfaces/cli/cli.py:145`.
   - Done when `grep -rn '↳\|step_indent\|indented_event\|start_task\|end_task\|blank_line'
     dandy tests --include='*.py'` returns nothing and ruff check/format pass
     on the touched files.

3. Tests: re-anchor on the new layout
   - `tests/interfaces/cli/test_printer.py`: remove `step_indent=2` from the
     four `_StoryProgress` constructors; update frame/settled-frame expected
     strings to the `{char} ` prefix; re-anchor the line-97 story filter from
     `'↳ ' in line` to the new char-prefix shape; add cases: a tool beat with a
     custom `ascii_char` renders that char, a non-tool beat renders `.`, and
     `event` output has no prefix at all.
   - `tests/application/tool/test_service.py`: exact-`StoryBeat` expectations
     gain `ascii_char='.'` on tool beats (narration/compaction beats unchanged).
   - Done when the full `pytest tests -q` suite passes.

4. Docs
   - `AGENTS.md` (Execute-and-loop paragraph, ~line 168): beats render flush
     left prefixed by the tool's `action_ascii_char` (default `.`); header and
     completion lines are plain flush-left (no arrow).
   - `docs/reference/domain.md`: add `action_ascii_char` to the `BaseTool`
     member list and `ascii_char` to the `StoryBeat` directive members.
   - `docs/user_guide/tool_calling.md`: add an `action_ascii_char` bullet
     beside `action_label`; note the flush-left char-prefixed rendering.
   - `docs/changelog/v3.md`: v3.1.0 `### Changed` entry for the new beat prefix
     and the removed indentation.
   - Done when `just docs-tests` exits 0.

5. Gate
   - Full suite, lint, contracts, docs build, and a smoke run of
     `run_timed_task` capturing stdout to verify the rendered layout.
   - Done when every command in the Completion Test passes with output quoted.

## Completion Test

- `DANDY_SETTINGS_MODULE=tests.dandy_settings PYTHONPATH=. .venv/bin/python -m pytest tests -q`
  → whole suite passes.
- `grep -rn '↳\|step_indent\|indented_event\|start_task\|end_task\|blank_line'
  dandy tests --include='*.py'` → no hits.
- `.venv/bin/ruff check <touched files>` + `.venv/bin/ruff format --check <touched files>`
  → clean (no new findings; `grep -E 'E501|F[0-9]{3}|W[0-9]{3}'` empty).
- `just lint-imports` → all 6 contracts kept.
- `just docs-tests` → mkdocs strict build exits 0.
- Smoke: the `run_timed_task` stdout-capture script (thinking beat, narration
  beat, custom-char tool beat, compaction-style system beat) prints every line
  flush left; beat lines start with `.` (or the tool's char); header and
  completion lines carry no arrow and no indentation.
- Observed 2026-11-02: full suite `625 passed, 49 subtests passed in
  188.54s`; grep across `dandy/` + `tests/` returns only the flagged out-of-scope
  `DandyCli._emit_verbose` line at `dandy/interfaces/cli/cli.py:31`; ruff
  check/format clean on touched files (no new E501/F/W); `just lint-imports`
  "Contracts: 6 kept, 0 broken"; `just docs-tests` "Documentation built in
  0.97 seconds" (exit 0). Smoke capture:

  ```text
  'Coding "fix the weather bug"'
  '. Fluffing a Silk Cravat with Anti-Gravity Puffs'
  '. Let me check the weather for you.'
  '> Reading src/weather.py lines 1-10'
  '. Running "pytest -q"'
  'I have completed your request in 0.6 seconds.'
  ```

## Deviations

none yet
