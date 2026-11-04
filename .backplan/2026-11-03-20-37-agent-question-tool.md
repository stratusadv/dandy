# Agent question tool

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-03-20-37

## End State

`CodingAgent` can call a new `question` tool mid-turn: the CLI pauses the turn,
shows the question (with optional numbered choices), waits for the user to type an
answer (a choice number or free text), and feeds that answer back to the model as
the tool result; double-escape while the question is up stops the run.

## Observable Concern

The tool loop runs on a worker thread while the main thread owns the terminal
(blessed cbreak). The question hand-off must never let both threads touch the
terminal or block each other forever: the worker parks the question in a shared
gate and blocks on an event; only the main render loop may prompt, and a stop
signal releases the worker even if no prompt ever happens.

## Current State

- Verified facts:
  - `dandy/interfaces/cli/tui/printer.py:276` `Printer.run_timed_task` runs the
    agent turn on a daemon worker thread; the calling thread renders story beats
    and polls for double-escape (which sets the `stop_signal` singleton from
    `dandy/shared/cancellation.py:28`).
  - `dandy/application/tool/service.py:116,161` the tool loop raises
    `RunStoppedError` at the round boundary and before each tool call when
    `stop_signal` is set, so a stop during a question aborts the turn cleanly.
  - `dandy/application/agent/tools/` is organized in subpackages (`file/`,
    `git/`, `command/`) with `*_TOOLS: list[ToolType]` exports; `AGENT_TOOLS`
    (`tools/__init__.py:16`) is used by planning, init, and coding turns.
  - `BaseTool` (`dandy/domain/tool/tool.py:14`) derives the parameter schema from
    the `handle` signature; `to_tool_instances` accepts classes and instances, so
    a configured `QuestionTool(ask_user=...)` instance can join a class-only list.
  - `Tui.get_user_input` (`dandy/interfaces/cli/tui/tui.py:25`) already renders a
    `question=` variant (purple "Question:" line) and returns `None` on
    double-escape; it takes no choices yet.
  - `DandyCli.process_agent_input` (`dandy/interfaces/cli/cli.py:173`) drives a
    turn through `run_timed_task(..., stop_signal=stop_signal)`; one-shot mode
    reuses the same path, so no separate wiring is needed there.
  - Pydantic `create_model` handles `list[str] | None` annotations from
    `handle` signatures (the signature mapper passes annotations through).
  - `printer.py` cannot import `tui.py` at module level (circular: `tui.py`
    imports `Printer`), so the question prompt must be injected as a callback.

## Plan

1. Shared question gate
   - New `dandy/shared/interaction.py`: `UserQuestion` dataclass, `QuestionGate`
     (`ask` parks the question and blocks the worker until `deliver` runs or the
     stop signal fires; `deliver(None)` sets the stop signal and answers with a
     stop sentinel), `STOPPED_ANSWER`, and a `question_gate` singleton.
   - Done when `tests/shared/test_interaction.py` passes (round trip, stop via
     deliver, stop via external signal, pending cleared).
2. QuestionTool
   - New `dandy/application/agent/tools/question/` subpackage: `QuestionTool`
     with `name='question'`, `handle(question: str, choices: list[str] | None)`
     that returns the `ask_user(question, choices)` result, or a "no user
     available, assume and proceed" string when no `ask_user` was injected;
     `action_label='Asking'`. Export `QUESTION_TOOLS` and register the import in
     `tools/__init__.py`.
   - Done when `tests/application/agent/test_question_tool.py` passes (schema has
     required `question` + optional `choices` string array; both handle paths).
3. CodingAgent wiring
   - `CodingAgent.__init__` gains `ask_user: QuestionHandler | None = None`; its
     tools become `[*AGENT_TOOLS, QuestionTool(ask_user=ask_user)]` (planning and
     init keep `AGENT_TOOLS` without the question tool).
   - Done when a hermetic `CodingAgent` turn (mocked `request_to_response`) in
     `test_coding_agent.py` shows the model's `question` tool call answered and
     the final response returned.
4. TUI choice prompt
   - `Tui.get_user_input(question=None, choices=None)`: print numbered choices
     under the question; an entered number in range returns that choice's text,
     anything else returns the raw text; double-escape still returns `None`.
   - Done when `tests/interfaces/cli/test_tui.py` covers number, free text,
     out-of-range number, and escape.
5. Render-loop hand-off
   - `run_timed_task` gains `question_gate: QuestionGate | None = None` and
     `question_handler: Callable[[str, list[str]], str | None] | None = None`;
     the render loop breaks out of cbreak when a question is pending, calls the
     handler on the main thread, and delivers the result (a `None` result
     means stop).
   - Done when `tests/interfaces/cli/test_printer.py` covers answer delivery and
     stop-while-asking; existing `run_timed_task` tests still pass unchanged.
6. CLI wiring
   - `DandyCli` builds `CodingAgent(ask_user=self._ask_user)` where `_ask_user`
     asks the shared `question_gate` with `stop_signal`; `process_agent_input`
     passes `question_gate=question_gate, question_handler=self._prompt_question`
     (which calls `tui.get_user_input`).
   - Done when `test_cli.py` asserts both are passed, and the agent's question
     tool is wired to the shared gate.
7. Docs and AGENTS.md
   - `docs/user_guide/coding_agent.md` (toolset + stop behavior),
     `docs/reference/application.md` and `docs/reference/shared.md` member lists,
     `docs/changelog/v3.md`, and the CLI bullet in `AGENTS.md`.
   - Done when `just docs-tests` passes and the docs describe the new behavior.

## Completion Test

1. `just test` (full hermetic suite, including the new tests).
2. `ruff check . && ruff format --check .` and `just lint-imports`.
3. `just docs-tests` (strict mkdocs build).

## Deviations

1. The render loop re-prompted a delivered question in a tight loop (4,336
   prompts in one test run) because `deliver` did not clear the parked
   question — only the waking worker did, and the pump checked in the gap
   between.
    - What: `QuestionGate.deliver` now clears `pending` under the lock.
    - Why: the UI thread must never see a question it has already answered;
      the worker-side clear stays as an idempotent belt-and-braces.
2. `just test` (the `pytest .` recipe) fails with 107 collection errors on the
   pristine branch tree too — a pre-existing breakage, not this change.
    - What: verified the CI forms instead: `python -m pytest tests -q`
      (698 passed, 29 skipped, 49 subtests) and
      `python -m unittest discover -t . ./tests` (Ran 727 tests, OK
      skipped=29), plus `just lint-imports` and `just docs-tests`.
    - Why: those are what CI's hermetic job actually runs; the broken
      recipe is out of scope.
3. Pre-existing ruff 0.17.3 debt on this branch (ARG001/ANN001/EM101/TRY003 in
   old tests, W291 in `ascii.py`, ANN201 in `printer.py`/`tui.py`, etc.) was
   left untouched; new code was kept violation-free of those rules, but test
   closures intentionally mirror the neighbors' existing patterns
   (`work(update)`, `mock_write`).
    - What: no changes to pre-existing code.
    - Why: fixing unrelated branch debt is out of scope; consistency with the
      adjacent tests wins.
