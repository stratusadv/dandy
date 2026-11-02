# Split action_sentence into action_label + action_output

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-02-09-37

## End State

`BaseTool.action_sentence` is gone; tools declare an `action_label: str` class
attribute plus an `action_output(**kwargs)` method, `ToolService`/`Agent` emit
`StoryBeat(label=..., description=...)` objects through `progress_callback`,
and the CLI story renders the label in bold grey with the description in plain
black (animating and settled) — with all tests, docs, and CI gates green.

## Observable Concern

The `progress_callback` payload type changes from `str` to `StoryBeat` and
ripples through `ToolService.prompt_to_intel` → `Agent.turn` → the CLI
`_StoryProgress`; the risk is a missed string emitter/consumer (summary
sentence, 'Planning', compaction line, initial thinking phrase) that would
crash story rendering or leave a test asserting on strings.

## Current State

- `BaseTool` (`dandy/domain/tool/tool.py:14`): class attrs `name`,
  `description`, `timeout_seconds`, `use_shell`; `action_sentence(**kwargs)`
  at line 65 returns `str | None` (default `None`).
- `ToolService._process_tool_call`
  (`dandy/application/tool/service.py:234`): builds
  `step_sentence = tool.action_sentence(**arguments_kwargs) or
  pascal_to_title_case(tool_call.name)` and emits
  `progress_callback(step_sentence.removesuffix('.'))`. `progress_callback` is
  `Callable[[str], None]`. Other string emitters: model summary (line 129),
  compaction line (line 189).
- `Agent` (`dandy/application/agent/agent.py`): `turn(...,
  progress_callback: Callable[[str], None])`; compaction beat at line 252.
  `CodingAgent._create_plan` (`coding_agent.py:53`) emits `'Planning'`.
- CLI: `Printer.run_timed_task` (`dandy/interfaces/cli/tui/printer.py:152`)
  passes `progress.update` as the callback; `_StoryProgress` (line 47) holds
  `list[str]` beats (seeded with a random `THINKING_PHRASES` string), renders
  the animating beat fully `bold_blue` and settled beats plain black.
- 10 agent tools override `action_sentence` (file: read/write/edit/delete/
  create_directory/list_directory/search, command: run_command, git:
  status/diff); `SkillMethodTool`/`ActivateSkillTool` do not (name fallback).
- Tests: `tests/domain/tool/test_tool.py` (ActionSentenceTool fake + 2 tests),
  `tests/application/tool/test_service.py` (ActionSentenceWeatherTool fake +
  4 string-asserting tests), `tests/application/agent/test_agent_tools.py`
  (`TestToolActionSentences`), `tests/application/agent/test_file_tools.py`
  (`test_file_tools_provide_action_sentences`),
  `tests/application/agent/test_coding_agent.py` (4 tests asserting
  `'Compacting conversation history'` / `'Planning'` in string lists),
  `tests/interfaces/cli/test_printer.py` (frame tests on strings).
- Docs: `docs/reference/domain.md` (BaseTool member list includes
  `action_sentence`), `docs/user_guide/tool_calling.md` (progress_callback
  bullet), `AGENTS.md` execute-and-loop paragraph, `docs/changelog/v3.md`
  (v3.1.0 has `### Changed` at line 76 and `### Removed (breaking)` at 127).
- Import contracts (`pyproject.toml`): no contract forbids
  application → domain or interfaces → domain; a `StoryBeat` in
  `dandy/domain/tool` is importable by both the tool service and the CLI
  printer without new seam entries.

## Plan

1. Add `StoryBeat` dataclass
   - New `dandy/domain/tool/beat.py`: `@dataclass StoryBeat` with
     `label: str = ''` and `description: str = ''` (description-only beat for
     plain sentences, label+description for tool actions). Export from
     `dandy/domain/tool/__init__.py`.
   - Done when `from dandy.domain.tool import StoryBeat` imports cleanly and
     `ruff check dandy/domain` passes.
2. Rework `BaseTool`
   - Add `action_label: str = ''` class attribute next to `name`/
     `description`; replace `action_sentence` with
     `action_output(self, **_kwargs: Any) -> str | None` (default `None`);
     update the class docstring example.
   - Done when `dandy/domain/tool/tool.py` passes ruff and the module imports.
3. Update `ToolService`
   - `progress_callback: Callable[[StoryBeat], None] | None`; tool beat built
     as `StoryBeat(label=tool.action_label or pascal_to_title_case(tool_call.name),
     description=tool.action_output(**arguments_kwargs) or '')`; summary and
     compaction beats become `StoryBeat(description=...)`; drop the
     `removesuffix('.')`.
   - Done when `tests/application/tool/test_service.py` passes with updated
     `ActionSentenceWeatherTool` fake (label `'Fetching the weather'` + output
     `f'for {location}'`) and StoryBeat assertions.
4. Update the agent layer
   - `agent.py` and `coding_agent.py`: `progress_callback` typed
     `Callable[[StoryBeat], None]`; `'Planning'` and compaction beats become
     description-only `StoryBeat`s.
   - Done when `tests/application/agent/test_coding_agent.py` passes with
     `progress_calls: list[StoryBeat]` assertions.
5. Migrate all 10 agent tools
   - Per tool: `action_label` class attribute + `action_output(**kwargs)`
     returning the per-call detail (no trailing periods):
     ReadFileTool `'Reading'` / `src/foo.py lines 1-10`; WriteFileTool
     `'Writing'`; EditFileTool `'Editing'` (+ ` everywhere`); DeleteFileTool
     `'Deleting'`; CreateDirectoryTool `'Creating directory'`;
     ListDirectoryTool `'Listing'` (+ ` recursively`); SearchFilesTool
     `'Searching'` / `for "weather" in src`; RunCommandTool `'Running'` /
     `"pytest -q"`; GitStatusTool `'Checking git status'` (no output);
     GitDiffTool `'Showing git diff'` (+ `for <path>`).
   - Done when `tests/application/agent/test_agent_tools.py`
     (`TestToolActionLabelsAndOutputs`) and `test_file_tools.py` pass.
6. Update the CLI story rendering
   - `_StoryProgress` beats become `list[StoryBeat]` (seeded thinking phrase
     description-only); `update(beat: StoryBeat)`; `settled_frame` and
     `frame` render `bold_grey` label + plain description in both states
     (description-only beats render exactly as today); `run_timed_task`
     `work` signature takes `Callable[[StoryBeat], None]`.
   - Done when `tests/interfaces/cli/test_printer.py` passes, including a new
     test asserting the label renders with `term.bold_grey` and the
     description without a color prefix.
7. Update docs and changelog
   - `docs/reference/domain.md`: BaseTool members `action_sentence` →
     `action_label`, `action_output`. `docs/user_guide/tool_calling.md`:
     progress_callback bullet describes label + output. `AGENTS.md`
     execute-and-loop paragraph rewritten for `StoryBeat`, `action_label`,
     `action_output` (no period-stripping; name the printer styling).
     `docs/changelog/v3.md`: v3.1.0 `### Changed` entry (label/output split,
     StoryBeat callback) and `### Removed (breaking)` entry
     (`action_sentence`).
   - Done when `just docs-tests` (mkdocs build --strict) passes.
8. Run the full gate
   - `just test`, `ruff check .`, `ruff format --check .`,
     `just lint-imports`, `just docs-tests`; plus a smoke run of
     `run_timed_task` with a fake `work` pushing a label+description beat,
     capturing stdout to show the grey label + plain description.
   - Done when every command is green and the smoke output shows the styled
     beat.

## Completion Test

1. `just test` → full suite passes (unittest-compatible, hermetic).
2. `ruff check .` and `ruff format --check .` → zero findings/diffs.
3. `just lint-imports` → all contracts kept.
4. `just docs-tests` → `mkdocs build --strict` succeeds.
5. Smoke: a small script drives `Printer.run_timed_task` with a fake `work`
   pushing `StoryBeat(label='Reading', description='src/foo.py lines 1-10')`
   and a description-only beat; captured stdout contains the grey-styled
   label line and the plain description line.

## Deviations

none — executed as planned.

## Completion Test Results (observed 2026-11-02)

- `pytest tests -q` → `620 passed, 49 subtests passed in 140.22s` (run twice, after the
  E501/format fixes as well).
- `ruff check` on every touched file → no new findings (remaining findings in those
  files — PLR0917/TRY003/EM101/ANN — are pre-existing branch-wide; repo-wide `ruff
  check .` has ~600 pre-existing findings on this branch, untouched here).
- `ruff format --check` on every touched file → `52 files already formatted`
  (the only unformatted file in the repo, `tests/shared/test_subprocess.py`, is
  pre-existing and untouched).
- `just lint-imports` → `Contracts: 6 kept, 0 broken.`
- `just docs-tests` → exit 0 (mkdocs build --strict).
- Smoke: `run_timed_task` with fake work pushing
  `StoryBeat(label='Reading', description='src/foo.py lines 1-10')`,
  `StoryBeat(label='Running', description='"pytest -q"')`, and a description-only
  beat; captured stdout shows the label in `bold_grey`
  (`\x1b[1m\x1b[38;2;190;190;190mReading\x1b[m`) with the description plain, in both the
  animating (trailing dots) and settled frames; description-only beats render plain.
- Note: `pytest .` also collects `evals/task/hidden_tests/` (15 pre-existing
  failures: `No module named 'stockroom'` — the eval project module lives in
  `evals/task/project` and needs its own PYTHONPATH; unrelated to this change,
  and CI's `unittest discover ./tests` never collects it).
