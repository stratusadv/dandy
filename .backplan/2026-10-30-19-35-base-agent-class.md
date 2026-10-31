# Base Agent class with `turn` and a run-to-completion method

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed (user sign-off: "lets do it")
- Date: 2026-10-30-19-35

## Research (naming, from the industry)

Question: what do the major agent frameworks call (a) the base class, (b) the
per-exchange method, (c) the method that drives the agent until its request is
finished, and (d) how is "finished" signaled?

**Verified primary source — OpenAI Agents SDK docs ("Running agents", fetched
2026-10-30):**
- Drive methods: `Runner.run(agent, input)`, `Runner.run_sync()`,
  `Runner.run_streamed()`. The unit of work is a **run**; the result carries
  `final_output`.
- "The agent loop": call the LLM -> if output is final the loop ends, if it is
  tool calls, execute and re-run. Verbatim: "The rule for whether the LLM
  output is considered as a 'final output' is that it produces text output with
  the desired type, and there are no tool calls."
- Budget: `max_turns` parameter; exceeding it raises `MaxTurnsExceeded`;
  "`max_turns=None` to disable this turn limit." A **turn** there is one LLM
  cycle.

**Other frameworks (established API knowledge, converging):**
- Pydantic AI: `agent.run()` / `run_sync()` / `run_stream()` — again **run**;
  completion = model produces its output (no tool calls), or `stop_on` a
  finish tool.
- OpenAI Assistants API: a **run** is a first-class object that executes to a
  terminal status (`completed` / `failed` / `requires_action`).
- LangGraph: `graph.invoke()` / `stream()`; per-node cycles are **steps**,
  capped by `recursion_limit`.
- AutoGen: `agent.reply()` plus **TerminationCondition** (e.g. max messages);
  a `terminate`-style tool/message ends the conversation.
- CrewAI: `crew.kickoff()`, `agent.execute_task()`.
- Anthropic agent docs: a **turn** is one user-to-model exchange (a turn may
  include several tool-use cycles); the "agent loop" is model -> tool call ->
  tool result -> model.

**Verdict:**
| Concept | Winner | Losers and why |
|---|---|---|
| Base class | `Agent` | `Assistant` (Assistants-API artifact), `Worker` (no precedent) |
| One exchange | **`turn`** (user's pick, endorsed) | `step` (LangGraph node / plan-and-execute granularity), `round` (Dandy already reserves this for one tool cycle), `act` / `move` (ReAct / classic planners, weak in LLM docs) |
| Drive-to-completion | **`run`** | `chat` (interactive, human-in-the-loop; Dandy already uses it for the CodingAgent REPL), `reply` / `respond` (one-shot, no loop), `execute` (CrewAI task-level), `work` (no precedent), `complete` (collides with token completion and Assistants status vocabulary) |
| Budget guard | `max_turns: int \| None` | `max_steps` (LangGraph), `max_iterations` (generic) |
| Completion signal | typed **`done`** field on the turn Intel (+ optional `is_done` callback) | finish/terminate tool (industry pattern, but stops require surgery on Dandy's core tool loop — out of scope for v1), judge model (extra LLM spend per turn) |

Note the granularity ladder this fixes in Dandy's glossary:
**run** (autonomous, request to completion) > **turn** (one user-visible
exchange: message in, N tool rounds, answer out, state persists) > **tool
round** (one model->tools->results cycle, already Dandy vocabulary) > raw LLM
call.

## End State

`dandy/application/agent/agent.py` defines a base `Agent` class that owns a
`MessageHistory` and exposes `turn()` (one stateful exchange, like
`Bot.process` but history-persistent and designed to be called repeatedly) and
`run(request)` (drives `turn()` until the agent's result signals completion or
`max_turns` is exhausted); `from dandy import Agent` works, hermetic
multi-turn tests pass under both runners, all six import-linter contracts stay
green with no new seams, and the docs (glossary, new user-guide page,
reference, changelog) define the agent/turn/run vocabulary.

## Observable Concern

The completion-signal design — a typed `done` field on the turn Intel
(default `AgentTurnIntel(text, done)`, overridable via `intel_class` +
`is_done` callback) — is the assumption most likely to be wrong. If the user
prefers a finish-tool convention (model calls `finish(answer=...)`) the tool
loop itself must learn to stop early, which is a much larger core change; the
plan proceeds with the `done` field and flags the alternative here for
approval. Secondary: `turn`/`run`/`round` granularity must be documented so it
does not collide with the existing "tool round" term.

## Current State

Verified facts (step 0):
- `dandy/application/agent/` currently holds: `coding_agent.py`
  (`CodingAgent`, plain class, owns `CodingBot` + `PlanningBot` +
  `MessageHistory`, methods `chat()`, `_create_plan()`,
  `_compact_history_for_next_message()` (compacts to
  `AGENT_COMPACTION_TARGET_RATIO = 0.70` of the resolved `CONTEXT_SIZE`),
  `clear()`), `prompts.py` (`coding_guidelines_prompt()`,
  `planning_guidelines_prompt()`), `session.py`, `bots/`, `tools/`;
  `__init__.py` is empty (house convention).
- `Bot.process(*args, **kwargs)` (`dandy/application/bot/bot.py:70`) is the
  single-use-case primitive: requires `prompt`, delegates to
  `self.llm.prompt_to_intel`.
- The tool loop is `ToolService.prompt_to_intel`
  (`dandy/application/tool/service.py:37`): loops while the model returns
  `ToolCallsIntel`, feeds results back as `role='tool'` messages, sends the
  prompt only on the first iteration, supports
  `max_tool_iterations` (default 5, `None` disables -> `LlmRecoverableError`
  on exhaustion), `progress_callback` / `verbose_callback`, and persists into a
  caller-owned history via `message_history=...` +
  `replace_message_history=True`.
- `CodingAgent.chat` is exactly one interactive turn: compact -> optional
  planning bot -> one tool loop over persistent `self.history` with
  `max_tool_iterations=None`; the CLI REPL loops it by hand, one message at a
  time.
- `dandy/__init__.py` (composition root) re-exports the public API
  (`Bot`, `Prompt`, `BaseIntel`, `BaseTool`, `Recorder`, caches, futures,
  exceptions); no `Agent` today.
- Layering: an `Agent` that imports `Bot` (application), `MessageHistory`
  (domain), `Prompt` (domain), `AgentTurnIntel` (same package), and
  exceptions (same package) creates **no cross-layer edges** — no new
  import-linter seams.
- Tests: `tests/application/agent/` exists with `intelligence/` fixtures,
  `test_coding_agent.py` (hermetic multi-turn test patching
  `dandy.infrastructure.http.connector.HttpConnector.request_to_response` with
  a `side_effect` list and asserting turn-2 request contains turn-1 messages),
  and tool/session tests.
- House conventions: package-per-concept with same-basename module
  (`agent/agent.py`); the agent package is the documented exception to the
  `intelligence/` subdirectory convention (it keeps `bots/`, `tools/`,
  `prompts.py` flat); exceptions per subsystem in `<package>/exceptions.py`
  (`DandyCriticalError` / `DandyRecoverableError` children); tests mirror
  packages; hermetic tests patch at the connector boundary.
- Baseline (from the just-completed decoder-to-decision plan, to re-check in
  step 1): pytest 447 passed / 29 skipped; unittest 476 OK (skipped=29);
  coverage 94%; `lint-imports` 6 kept / 0 broken; `just docs-tests` clean;
  ruff 648 errors / 155 format files.
- Live-LLM gate: 29 tests skip without a real key; `development.env` holds a
  real key, so a live smoke is possible after execution (optional, like the
  earlier live evaluation).

## Proposed API

```python
# dandy/application/agent/intel.py
class AgentTurnIntel(BaseIntel):
    text: str
    done: bool = False

# dandy/application/agent/exceptions.py
class AgentCriticalError(DandyCriticalError): ...
class AgentRecoverableError(DandyRecoverableError): ...

# dandy/application/agent/agent.py
class Agent:
    def __init__(
        self,
        bot: Bot,
        tools: list[ToolType] | None = None,
        max_turns: int | None = None,        # None = unbounded (coding-agent convention)
        intel_class: type[IntelType] | None = None,   # default AgentTurnIntel
    ) -> None:
        ...                                   # self.history = MessageHistory()

    def turn(
        self,
        message: Prompt | str | None = None,  # None on continuation turns
        progress_callback: Callable[[str], None] | None = None,
        verbose_callback: Callable[[str], None] | None = None,
    ) -> IntelType:
        # compact history (0.70 of resolved CONTEXT_SIZE, CodingAgent pattern)
        # -> bot.llm.tools.prompt_to_intel(prompt=message, tools=self.tools,
        #    intel_class=..., message_history=self.history,
        #    replace_message_history=True, max_tool_iterations=None, ...)

    def run(
        self,
        request: Prompt | str,
        is_done: Callable[[IntelType], bool] | None = None,
        progress_callback=None, verbose_callback=None,
    ) -> IntelType:
        # first turn receives the request; subsequent turns receive a
        # continuation nudge (agent/prompts.py) so the model keeps working
        # stop: is_done(result) if given, else getattr(result, 'done', False)
        # budget: max_turns exhausted -> AgentRecoverableError
        # neither signal available -> AgentCriticalError (fail fast)

    def clear(self) -> None:
        # new MessageHistory + bot.reset() (mirrors CodingAgent.clear)
```

Usage:

```python
class ReportAgent(Agent):
    def __init__(self) -> None:
        super().__init__(bot=ReportBot(), tools=[ReadFileTool(), ...])


agent = ReportAgent()
final = agent.run('Build the quarterly report and save it to out/')
# or interactively:
answer = agent.turn('What are you doing?')
```

## Assumptions (flagged for approval)

1. `run(request)` is one-shot (request passed as the argument), matching
   `Runner.run(agent, input)` / `agent.run(prompt)`; no separate
   submit-then-run pair.
2. Completion = typed `done` field on the turn Intel by default, with an
   `is_done` callback override; a finish-tool is deliberately out of scope
   (would modify the core tool loop).
3. `max_turns` defaults to `None` (unbounded), consistent with the coding
   agent's deliberate `max_tool_iterations=None`; spend risk is documented,
   and a finite value is a one-arg opt-in.
4. `CodingAgent` is NOT refactored in this plan (its planning-bot step is
   coding-specific); a follow-up plan can make it subclass `Agent`.
5. `Agent` is exported from the `dandy` root (public API, like `Bot`).
6. `AgentTurnIntel` and the continuation prompt live in
   `dandy/application/agent/` following the agent package's flat convention
   (`intel.py`, `prompts.py`).
7. `turn()` uses `max_tool_iterations=None` inside each turn (a turn may run
   as many tool rounds as needed; the guard is at the turn level via
   `max_turns`).

## Plan

1. **Baseline re-check**
   - Re-run the hermetic battery (pytest, unittest 476-count, lint-imports,
     ruff counts, docs strict) on the current tree.
   - Done when all numbers match the recorded baseline.
2. **Agent core**
   - Add `dandy/application/agent/intel.py` (`AgentTurnIntel`),
     `dandy/application/agent/exceptions.py` (`AgentCriticalError`,
     `AgentRecoverableError`), `dandy/application/agent/agent.py`
     (`Agent` with `turn`, `run`, `clear`, history compaction per the
     CodingAgent pattern), and a `continuation_prompt()` in
     `dandy/application/agent/prompts.py`.
   - Done when a scratch script can construct `Agent(Bot())` and `turn` /
     `run` / `clear` exist; no new cross-layer imports (verify with
     lint-imports).
3. **Hermetic tests**
   - `tests/application/agent/test_agent.py` patching
     `dandy.infrastructure.http.connector.HttpConnector.request_to_response`
     with a `side_effect` list; a fixture bot in
     `tests/application/agent/intelligence/`. Cover: one `turn` persists
     history; a second `turn`'s request contains the first turn's
     user/assistant messages; `run` stops on `done=True`; `run` with a finite
     `max_turns` raises `AgentRecoverableError`; `run` with an `intel_class`
     lacking `done` and no `is_done` raises `AgentCriticalError`; `is_done`
     override wins; `clear()` resets history.
   - Done when the new tests pass under both pytest and unittest discover,
     and the full suite is green.
4. **Public API**
   - Re-export `Agent` from `dandy/__init__.py`.
   - Done when `from dandy import Agent` works from a clean interpreter.
5. **Docs**
   - Glossary: `Agent` entry + the run/turn/round ladder; anti-language rows
     (Agent: "assistant", "chatbot object"; run: "chat", "loop", "process";
     turn: "step", "round", "iteration").
   - New `docs/user_guide/agent.md` (concept, the API, a worked example, the
     done-signal semantics, max_turns, relationship to Bot and to
     CodingAgent) + `mkdocs.yml` nav entry.
   - `docs/reference/application.md`: `Agent` directive + members
     (`turn`, `run`, `clear`, `AgentTurnIntel`, exceptions).
   - `docs/changelog/v3.md` v3.1.0: Added entry.
   - Done when `just docs-tests` strict build is clean.
6. **Completion test + close**
   - Run the full completion test below, quote real output, append deviations,
     set `Status: Executed`.
   - Done when every completion-test line passes.

## Completion Test

All run from `/home/nathanj/PycharmProjects/dandy`, all must pass:

1. Hermetic pytest:
   `AI_API_KEY=test-key PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings .venv/bin/python -m pytest . -q`
   -> 447+N passed, 29 skipped, 0 failed (N = new test count).
2. CI-parity unittest (clean env):
   `env -i PATH="$PATH" HOME="$HOME" .venv/bin/python -m unittest discover -t . ./tests`
   -> 476+N tests, 0 failures, 29 skipped.
3. Coverage gate:
   `PYTHONPATH=. AI_API_KEY=placeholder DANDY_SETTINGS_MODULE=tests.dandy_settings .venv/bin/python -m coverage run -m unittest discover -t . ./tests && .venv/bin/python -m coverage report --fail-under=90`
   -> TOTAL >= 90%, exit 0.
4. Architecture: `.venv/bin/lint-imports` -> `Contracts: 6 kept, 0 broken.`
   (no new seams expected).
5. Docs: `just docs-tests` -> strict mkdocs build clean.
6. Style: `.venv/bin/ruff check .` <= 648 errors; `.venv/bin/ruff format --check .`
   reformat count <= 155.
7. API smoke:
   `PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings .venv/bin/python -c "from dandy import Agent; print([m for m in ('turn', 'run', 'clear') if hasattr(Agent, m)])"`
   -> `['turn', 'run', 'clear']`, exit 0.
8. Multi-turn history assertion (inside the new hermetic test, step 3): the
   second turn's request body contains the first turn's user and assistant
   messages — same pattern as `tests/application/agent/test_coding_agent.py`.
9. Optional live smoke (only with a real `development.env` key, like the
   earlier live evaluation): a tiny `Agent` with one tool, `run()` a two-tool
   task, assert `done=True` came back — reported separately, not a gate.

## Deviations

1. `AGENT_MAX_CONTEXT_TOKENS_DEFAULT` / `AGENT_COMPACTION_TARGET_RATIO` now live in
   `dandy/application/agent/agent.py` (shared by both agents); `coding_agent.py`
   imports them from there instead of defining its own copies.
    - What: one-line import added to `coding_agent.py`, its two constant
      definitions removed; the module-level re-export keeps
      `test_coding_agent.py`'s `from ...coding_agent import AGENT_MAX_CONTEXT_TOKENS_DEFAULT`
      working unchanged.
    - Why: the base `Agent` needs the same compaction constants; two sources of
      truth for the 0.70 ratio would drift. This touches `coding_agent.py`
      contrary to assumption 4 ("CodingAgent untouched") — the class itself, its
      planning behavior, and its API are unchanged.
2. `agent.py` needed `from __future__ import annotations`: the `Bot` parameter
   annotation is TYPE_CHECKING-only (house rule: avoid the eager import where a
   deferred one suffices), and without the future import the class body raised
  `NameError` at import time.
  - What: added the future import (same style as `dandy/domain/intel/intel.py`).
  - Why: runtime annotation evaluation of a TYPE_CHECKING-only name fails;
  `Agent` annotations are never introspected at runtime (plain class, no
  pydantic/dataclass).
3. Step 5 also updated `AGENTS.md` (public-API list, the agent-package exception
line, a new "### Agent" architecture section, the compaction-constant location,
and the testing-approach coverage sentence).
  - What: five small prose edits in `AGENTS.md`.
  - Why: `AGENTS.md` is the repo's single source of truth for agent rules; the
  new public export and package contents would have left it stale. Not a plan
  change — the plan's docs step was meant to keep the documentation set
  consistent, and `AGENTS.md` is part of it.
4. Step 6 style gate: four new files needed `ruff format`, and the new test
   file carried two E501 line-length errors.
  - What: `ruff format` on `dandy/application/agent/agent.py`,
    `dandy/application/agent/prompts.py`, `docs/user_guide/agent.md`, and
    `tests/application/agent/test_agent.py`. The formatter itself split the
    two over-long lines in `test_agent.py` (a list comprehension and a method
    signature), clearing both E501 errors without a manual edit.
  - Why: the completion test requires `ruff check .` <= 648 and
    `ruff format --check .` <= 155; the pre-feature tree sat exactly at both
    baselines, so any new dirt was a regression. Both counts returned to
    baseline (648 / 155) after formatting, and the full test suites were
    re-run green after the format pass.

## Execution Report (2026-10-30, after sign-off)

All commands run from `/home/nathanj/PycharmProjects/dandy`.

1. Hermetic pytest:
   `AI_API_KEY=test-key PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings .venv/bin/python -m pytest . -q`
   -> `456 passed, 29 skipped in 3.92s` (447 + 9 new tests).
2. CI-parity unittest (clean env):
   `env -i PATH="$PATH" HOME="$HOME" .venv/bin/python -m unittest discover -t . ./tests`
   -> `Ran 485 tests` / `OK (skipped=29)` (476 + 9).
3. Coverage gate:
   `PYTHONPATH=. AI_API_KEY=placeholder DANDY_SETTINGS_MODULE=tests.dandy_settings .venv/bin/python -m coverage run -m unittest discover -t . ./tests && .venv/bin/python -m coverage report --fail-under=90`
   -> `TOTAL  4033  250  94%`, exit 0.
4. Architecture: `.venv/bin/lint-imports`
   -> `Contracts: 6 kept, 0 broken.` (no new seams, as predicted).
5. Docs: `just docs-tests`
   -> `Documentation built in 0.91 seconds`, exit 0.
6. Style: `.venv/bin/ruff check .` -> `Found 648 errors.` (baseline 648);
   `.venv/bin/ruff format --check .` -> `155 files would be reformatted,
   248 files already formatted` (baseline 155). See deviation 4.
7. API smoke:
   `PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings .venv/bin/python -c "from dandy import Agent; print([m for m in ('turn', 'run', 'clear') if hasattr(Agent, m)])"`
   -> `['turn', 'run', 'clear']`, exit 0.
8. Multi-turn history: `TestAgentTurn.test_turns_keep_conversation_history`
   asserts the second turn's request body carries the first turn's user and
   assistant messages; passes in both runners.
9. Optional live smoke: not run in this session (optional item; can be run
   with the real `development.env` key if desired).

Working tree left uncommitted, as instructed.
