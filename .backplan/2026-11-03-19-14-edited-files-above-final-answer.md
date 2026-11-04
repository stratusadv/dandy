# edited-files-above-final-answer

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-03-19-14

## End State
After a successful CLI turn (REPL, one-shot, or `--continue`), when the agent
executed any of the four file-mutating tools, the CLI prints an
`Edited files:` block — bold grey heading, then one `• path` line per path,
each path a clickable OSC 8 `file://` link, duplicates collapsed in first-use
order — between the green divider and the model's final answer; nothing is
printed when no such tool ran.

## Observable Concern
The path must come from the validated Python kwargs of each executed tool call
— never parsed from the beat description text or from the (compactable)
history. The callback therefore has to thread ToolService → `Agent.turn` →
`DandyCli`, fire exactly once per executed call, and must NOT be passed into
`_prepare_message`: `CodingAgent`'s planning pass calls
`planning_bot.llm.tools.prompt_to_intel` directly and its tool calls must not
land in the turn's edited-files list.

## Current State
Verified 2026-11-03, live tree (branch `v3/base`):
- `ToolService.prompt_to_intel` (service.py:93-178) already threads
  `progress_callback`/`verbose_callback` into `_process_tool_call` (service.py:
  223-304), which validates arguments into `arguments_kwargs =
  arguments_intel.model_dump()` (line 264) and dispatches
  `tool.handle(**arguments_kwargs)` / `tool_function(arguments_intel)` (278-281);
  invalid arguments return early (line 262) before any execution.
- `Agent.turn` (agent.py:80-107) passes `progress_callback`/`verbose_callback`
  to `bot.llm.tools.prompt_to_intel(..., message_history=self.history,
  replace_message_history=True)`; `Agent.run` (139-183) forwards both to
  `turn`; `_prepare_message` (109-116) is the subclass hook that receives them.
- `CodingAgent` (coding_agent.py) overrides only `_prepare_message` (planning
  pass calls `prompt_to_intel` directly, lines 61-68) and `run_init_pass`;
  `turn` is inherited from `Agent`.
- `DandyCli.process_agent_input` (cli.py:164-191): success path is
  `green_divider()` then `output(result_intel.text)`; one-shot and `--continue`
  both funnel through it; `run_init` is a separate path (out of scope).
- The four tools: `write_file(file_path, content)`,
  `edit_file(file_path, old_string, new_string, replace_all=False)`,
  `delete_file(file_path)`, `create_directory(directory_path)` — all
  `can_mutate_state = True`, all resolve via `resolve_project_path`, all return
  error strings instead of raising (`@tool_error`).
- `linkify_file_paths` (printer.py:66-90) is module-level, resolves relative
  paths against `session.project_base_path`, and is already importable in
  tests; `Printer` (printer.py:195+) has `event`/`output`/`green_divider` and
  takes a `Terminal`.
- Test patterns verified: `tests/application/tool/test_service.py`
  (`mock.patch('...HttpConnector.request_to_response')` +
  `tool_call_response`/`content_response` side effects, `ToolBot`, callbacks
  as `list.append`; `HandleWeatherTool.handle(location: str, units: str =
  'celsius')` so validated kwargs include the `units` default);
  `tests/application/agent/test_agent.py` (`Agent(ToolBot(), tools=[WeatherTool()])`,
  `WeatherTool.handle(location: str = '', units: str = 'celsius')`);
  `tests/interfaces/cli/test_cli.py` (patches `CodingAgent.turn`,
  `tui.printer.output`/`green_divider`, `session.project_base_path` →
  TemporaryDirectory); `tests/interfaces/cli/test_printer.py` (mock
  `builtins.print`, `Terminal(force_styling='default')`).
- `docs/reference/application.md` lists `Agent`/`ToolService` members
  explicitly; no new public symbols are added, only optional parameters, so no
  member-list change is needed.

## Plan
1. `ToolService` tool-call callback
   - `prompt_to_intel` gains `tool_call_callback: Callable[[str, dict[str,
     object]], None] | None = None`; forwarded to `_process_tool_call`, which
     calls it with `(tool_call.name, arguments_kwargs)` right after the
     handle/tool_function dispatch (so invalid-argument calls never fire it).
   - Done when a new hermetic `test_service.py` test asserts the callback gets
     the validated kwargs for executed calls (including defaulted fields) and
     stays silent for invalid-argument calls.
2. `Agent` threading
   - `turn` and `run` gain the same optional kwarg and pass it to the coding
     loop's `prompt_to_intel` only — `_prepare_message` does not receive it, so
     the planning pass never tracks.
   - Done when a new `test_agent.py` test asserts `turn(tool_call_callback=...)`
     receives `('get_weather', {'location': 'Austin', 'units': 'celsius'})`.
3. CLI collection + rendering
   - `cli.py`: module-level `EDITED_FILE_TOOL_PARAMS = {'write_file':
     'file_path', 'edit_file': 'file_path', 'delete_file': 'file_path',
     'create_directory': 'directory_path'}`; `process_agent_input` builds a
     first-use-ordered dedup list via a `record_tool_call` closure passed as
     `tool_call_callback`; the success path prints
     `tui.printer.edited_files(edited_files)` between `green_divider()` and
     `output(result_intel.text)`.
   - `printer.py`: new `Printer.edited_files(paths)` — no-op when empty;
     otherwise a bold grey `Edited files:` heading then one
     `{normal}• {linkify_file_paths(path)}` line per path.
   - Done when a new `test_cli.py` test (mocked `turn` side effect firing the
     callback for write/edit/edit/read calls) shows `src/foo.py` once,
     `src/bar.py` once, no `src/baz.py`, the OSC 8 sequence, and `Edited
     files:` printed before the answer; and `test_printer.py` unit tests cover
     the empty and non-empty shapes.
4. Docs
   - `AGENTS.md`: tool-calling bullet gains a `tool_call_callback` sentence
     next to `verbose_callback`; the CLI paragraph gains the edited-files
     sentence. `docs/user_guide/tool_calling.md`: callback bullets gain the
     same. `docs/changelog/v3.md`: v3.1.0 **Added** entry.
   - Done when `just docs-tests` strict build passes.
5. Gate
   - Targeted pytest on the four touched test files; full suite; ruff
     mirror-path diff on touched files (no NEW findings); `just lint-imports`;
     `just docs-tests`.
   - Done when every gate is green.

## Completion Test
```bash
DANDY_SETTINGS_MODULE=tests.dandy_settings PYTHONPATH=. .venv/bin/python -m pytest \
  tests/interfaces/cli/test_cli.py tests/interfaces/cli/test_printer.py \
  tests/application/tool/test_service.py tests/application/agent/test_agent.py -q
```
all green, plus the full suite green, `just lint-imports` → `Contracts: 6 kept,
0 broken.`, `just docs-tests` exit 0, and the ruff mirror diff on touched files
empty.

## Assumptions (flagged)
- A tool call that returned an error string (e.g. editing a missing file) still
  lists its path: the callback fires on every executed call, regardless of the
  tool's success string.
- The planning pass and the `/init` pass are not tracked (their tool calls do
  not join the list); only the coding turn's own tool loop counts.
- Duplicates collapse to one line in first-use order; `run_command` is excluded
  (it has no path argument).
- The block prints below the green divider, directly above the model's final
  answer (the "summary").

## Deviations
none

## Observed Output
```text
# targeted (completion test)
DANDY_SETTINGS_MODULE=tests.dandy_settings PYTHONPATH=. .venv/bin/python -m pytest \
  tests/interfaces/cli/test_cli.py tests/interfaces/cli/test_printer.py \
  tests/application/tool/test_service.py tests/application/agent/test_agent.py -q
124 passed in 2.28s

# full suite
696 passed, 15 skipped, 49 subtests passed in 137.83s (0:02:17)

# ruff mirror diff (mirror /tmp/ruffbase7, 8 touched Python files)
NEW: none
REMOVED: none
base findings: 0 cur findings: 0

# just lint-imports
Contracts: 6 kept, 0 broken.

# just docs-tests (mkdocs build --strict)
exit=0
Documentation built in 0.98 seconds
```
