# BaseAgent — Framework Plan

A framework-level `BaseAgent` class, `Bot`-shaped but built for **long-running,
multi-turn, tool-using tasks with planning and thinking**. It is the foundation
the CLI connects to, and the first public "orchestrator" the framework has had
since the old Agent module was removed in v2.0.0.

Status: **PLAN** — nothing in this file is implemented yet.

---

## 1. Why this exists

Today the only agent in the codebase is CLI-only: `dandy/cli/intelligence/coding_agent.py`
(`CodingAgent`). It already demonstrates every hard problem (multi-turn memory,
compaction, plan-first execution, unbounded tool loops) but it is:

- **Trapped in the CLI** — `dandy/cli/...` imports `session`, `tui`, and
  `get_cli_llm_config('CODING')`. No non-CLI code can drive it.
- **A bespoke class** — `CodingAgent` hardcodes `CodingBot` + `PlanningBot`,
  `AGENT_TOOLS`, the `0.70` compaction ratio, and `_resolve_context_size`'s
  hand-rolled settings walk, all duplicated in a second class shape that a
  third-party agent would have to reinvent.
- **The right ideas, the wrong home** — the framework already provides the
  machinery (`LlmToolService`'s execute-and-loop, `compact_message_history`,
  `MessageHistory`, `DefaultIntel` prose tolerance, the `THINKING`-config split)
  but no public assembly point.

`BaseAgent` makes that assembly point a first-class framework citizen: **a `Bot`
subclass that owns the full task lifecycle**, so third-party developers write:

```python
class RefactorAgent(BaseAgent):
    role = 'Senior Software Engineer'
    task = 'Implement the user coding request by editing the project.'
    guidelines = coding_guidelines_prompt()
    worker_config = 'CODING'
    planner_config = 'THINKING'
    worker_tools = MY_TOOLS
    planner_tools = MY_TOOLS


agent = RefactorAgent()
result = agent.chat('Extract the checkout flow into its own module')
```

and the CLI becomes a thin driver over it.

---

## 2. Design goals and non-goals

### Goals

1. **`BaseAgent(Bot)`** — inherits the full mixin stack (`llm`, `decoder`,
   `diligence`, `file`, `http`, `intel`), the recorder auto-wrapping of
   `process`, `process_to_future`, and the `reset()` chain. Zero new framework
   abstractions to learn; "a Bot that remembers and loops."
2. **Long tasks are the default** — persistent `MessageHistory`, per-turn and
   per-round compaction, `max_tool_iterations=None` (the loop never gives up).
3. **Tool calling is first-class** — `worker_tools` / `planner_tools` class
   attrs feeding `LlmToolService.prompt_to_intel`, exactly as the CLI does
   today (`to_tool_instances`, `ProgressCallback`, `verbose_callback`).
4. **Planning** — an optional *plan-first* pass on a separate
   `THINKING`-config bot, whose output feeds the worker turn (current CLI
   behavior), upgraded to a structured `PlanIntel`.
5. **Thinking** — an optional reasoning pass distinct from planning: open
   consideration surfaced through the story, not fed to the worker verbatim.
6. **The CLI connects to it** — `CodingAgent(BaseAgent)`; `DandyCli` pulls from
   `dandy.agent` instead of `dandy.cli.intelligence`. The `session`/`tui`
   concerns stay in the CLI.
7. **Framework-conventional** — `dandy/agent/` package with an
   `intelligence/` subtree, `exceptions.py`, Sphinx docstrings, exports from
   `dandy.__init__`, tests in `tests/agent/`. Passes `ruff {check,format}`,
   `ty`, and both test runners.

### Non-goals (explicitly out of scope)

- **Not a replacement for `Bot`.** `Bot` is the single prompt↔intel primitive.
  `BaseAgent` *is* a `Bot`; it adds orchestration on top. One-shot
  prompt↔intel still goes through `Bot`/`LlmService`.
- **No UI / terminal code in the framework.** `tui`, `printer`, thinking
  phrases, and `session.file` persistence stay in `dandy/cli/`.
- **No scheduling/orchestrator-of-agents** (that's what the removed
  "processor-pipeline" was; the framework deliberately composes `Bot`s, see
  `AGENTS.md` Gotcha #2). `BaseAgent` orchestrates *one* task's phases, not a
  DAG of agents.
- **No async engine.** `process_to_future` covers the async escape hatch, as
  for `Bot`.

---

## 3. Package layout

```
dandy/
  agent/
    __init__.py                      # BaseAgent, AgentError, exports
    agent.py                         # BaseAgent (the orchestrator)
    exceptions.py                    # AgentError (critical) hierarchy
    recorder.py                      # (only if extra events needed; see §11)
    state.py                         # AgentStateIntel for persistence (Phase 4)
    intelligence/
      __init__.py
      prompts.py                     # agent_worker_guidelines(), planner_guidelines_prompt(),
                                     #   _paths_section(), _narration_section(),
                                     #   _tool_calling_section(), _thinking_section()
      intel.py                       # PlanIntel, ThinkingIntel, AgentReportIntel
      bots/
        __init__.py
        planner_bot.py               # PlannerBot (framework generic)
tests/
  agent/
    test_agent.py                    # BaseAgent behaviors (multi-turn, plan, think, compaction)
    test_state.py                    # persistence round-trip (Phase 4)
    intelligence/                    # fakes: FakeTaskAgent, fake tools, fake planner
```

Mirrors `dandy/bot/` (exceptions, recorder, no `intelligence/` there yet) and
the established convention that every subsystem keeps its support models and
prompts under a nested `intelligence/` directory.

---

## 4. `BaseAgent` — class surface

### Class attributes (all overridable)

```python
from collections.abc import Callable
from typing import ClassVar

from dandy.bot.bot import Bot
from dandy.intel.intel import BaseIntel, DefaultIntel
from dandy.llm.prompt.prompt import Prompt
from dandy.llm.request.message import MessageHistory, compact_message_history
from dandy.tool.tool import ToolType


class BaseAgent(Bot):
    """A long-running, tool-calling, planning-aware Bot.

    BaseAgent is the worker itself (its ``role``/``task``/``guidelines``/``llm_config``
    describe the executing pass) and composes a separate planner bot for the
    optional plan/think pre-passes. It owns a persistent MessageHistory and
    drives the unbounded execute-and-loop tool service.
    """

    # ---- worker identity (inherited by Bot -> LlmServiceMixin) ----
    role: Prompt | str = 'Assistant'
    task: Prompt | str | None = 'Provide a response based on the users request, context or instructions.'
    guidelines: Prompt | str | None = None
    llm_config: str = 'DEFAULT'          # worker config name

    # ---- tools ----
    worker_tools: ClassVar[list[ToolType]] = []
    planner_tools: ClassVar[list[ToolType]] = []

    # ---- orchestration toggles ----
    plan_enabled: bool = True            # run a plan pass before the worker turn
    plan_every_turn: bool = True         # True: re-plan per chat(); False: only the first
    think_enabled: bool = False          # optional reasoning pre-pass (see §8)
    max_tool_iterations: int | None = None   # long tasks: never give up (None)

    # ---- planner bot configuration ----
    planner_role: Prompt | str = 'Planning Engineer'
    planner_config: str = 'THINKING'
    planner_task: Prompt | str | None = None     # framework default if unset
    planner_guidelines: Prompt | str | None = None

    # ---- context/compaction ----
    compact_target_ratio: float = 0.70   # AGENT_COMPACTION_TARGET_RATIO today
    max_context_tokens: int = 65536      # safe default; resolved from CONTEXT_SIZE
```

### Constructor

```python
    def __init__(
        self,
        plan_enabled: bool | None = None,
        think_enabled: bool | None = None,
        max_tool_iterations: int | None = 0,   # 0 => use class value; mirror Bot kwarg style
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)             # Bot: llm_config/temperature/arbitrary attrs
        self.history: MessageHistory = MessageHistory()
        self.planner_bot: Bot | None = None
        self._plans_created: int = 0
        self.__post_init__()
```

Constructor follows the `Bot` convention (kwargs become attributes after
`super().__init__`), sets up the two pieces the LLM layer doesn't give us
(persistent history, planner composition), then calls `__post_init__` so
subclasses can build guidelines without touching the base wiring.

### Public methods

```python
    def chat(self, user_input, *, no_plan=False, progress_callback=None,
             verbose_callback=None) -> DefaultIntel:
        """Send one turn, keeping conversation across calls."""

    def process(self, user_input, *args, **kwargs) -> DefaultIntel:
        """One-shot alias for chat() (recorder-wrapped by Bot.__init_subclass__)."""

    def think(self, user_input, progress_callback=None, verbose_callback=None) -> ThinkingIntel | None:
        """Run the optional reasoning pre-pass and return its notes."""

    def plan(self, user_input, progress_callback=None) -> PlanIntel | None:
        """Run the planner bot, returning a structured plan (or None when disabled)."""

    def clear(self) -> None:
        """Reset history and both bots (used by the CLI /clear command)."""

    # inherited: process_to_future, reset(), llm/decoder/etc service properties

    def _create_planner_bot(self) -> Bot:
        """Instantiate the planner; subclasses override to swap in their own."""
```

---

## 5. Execution flow (current CLI behavior, generalized)

`chat()` orchestrates the phases. This is a faithful generalization of
`dandy/cli/intelligence/coding_agent.py::chat/_create_plan/(pre-turn compaction)`
today:

```
chat(user_input, ...)
  1. compact self.history for the incoming turn          (§ on long tasks)
  2. if plan_enabled and (plan_every_turn or first turn):
        plan_intel = planner_bot.llm.tools.prompt_to_intel(
            prompt=user_input, tools=planner_tools,
            intel_class=PlanIntel, max_tool_iterations=None, callbacks...)
        progress_callback('Planning')
  3. if think_enabled and not plan_enabled: think pass   (§8)
  4. build worker prompt:
        Prompt().text(user_input)
                .line_break().heading('Implementation Plan').intel(plan_intel)
     (when a plan exists; prose user_input otherwise)
  5. worker turn:
        self.llm.tools.prompt_to_intel(
            prompt=worker_prompt, tools=worker_tools,
            intel_class=DefaultIntel,
            message_history=self.history, replace_message_history=True,
            max_tool_iterations=self.max_tool_iterations,   # None => never gives up
            progress_callback=..., verbose_callback=...)
  6. return result (DefaultIntel)
```

Where it differs from the CLI only by *generality*:

- `planner_tools` / `worker_tools` replace the one `AGENT_TOOLS`.
- `PlanIntel` replaces `intel_class=DefaultIntel` in the plan pass (structured
  plans, §7) — the worker still consumes `DefaultIntel` for prose tolerance.
- The hand-rolled `_resolve_context_size` settings walk moves to a single
  `BaseAgent` helper using the same code path (and prefers
  `self.llm.config.context_size`, addressing CLI_TODOS §6).
- The planner is built once via `_create_planner_bot()` instead of a module
  global `PlanningBot()`.

---

## 6. Long tasks: history, compaction, and the no-give-up contract

Everything the CLI learned to keep a session alive for many turns:

- **Persistent `MessageHistory`** — `self.history` lives on the agent, is
  passed with `replace_message_history=True` so the connector *accumulates
  into the caller's object* (the `if message_history is not None:` guard in
  `connector.py`, never `if message_history:`, because `MessageHistory` is
  falsy-when-empty — keep that).
- **Two compaction layers** (both already exist in the framework):
  1. **Pre-turn** (`_compact_history_for_next_message`): counts the incoming
     user input and trims `self.history` to
     `(max_context_tokens * compact_target_ratio) - incoming`, via the shared
     `compact_message_history` (`dandy/llm/request/message.py`) which keeps the
     system message + newest exchange, drops tool rounds first, never leaves a
     dangling `assistant` tool-calls message without its `tool` results.
  2. **Per-round** (`LlmToolService._compact_history_before_next_round`): the
     tool service already protects `self.obj.messages` every round with
     `TOOL_LOOP_CONTEXT_DEFAULT = 65536` and `TOOL_LOOP_COMPACTION_TARGET_RATIO
     = 0.70`. Because the agent merges into `self.history`, both layers trim
     the *same* object.
- **The 0.20 / 0.70 / 0.10 window geometry** (document in `agent.py` docstring):
  `LlmConfig` derives `max_completion_tokens = CONTEXT_SIZE * 0.20` for output;
  the agent compacts to `0.70`; `0.10` stays as safety margin so input+output
  always fit under `CONTEXT_SIZE`.
- **Never-give-up loop**: `max_tool_iterations=None` is the default for an
  agent (the CLI already chooses this); a finite value stays available.
  Reaching a finite cap raises `LlmRecoverableError` (unchanged).
- **`DefaultIntel` prose tolerance** means "how do I …?" turns don't crash the
  loop when the model answers in prose (the `json_invalid` fallback in
  `dandy/llm/connector.py`). Keep `DefaultIntel` for the worker result.

**Consolidation note**: `CodingAgent`'s `AGENT_COMPACTION_TARGET_RATIO` alias
and `_resolve_context_size` should not be duplicated in the framework — the
agent uses `self.llm.config.context_size` (falling back to `65536`) and the
`TOOL_LOOP_*` constants in `dandy/llm/tool/service.py` become the single source
of truth for the per-round safety net (optionally rename to
`AGENT_LOOP_*`/promote shared constants into `dandy/llm/tokens/`).

---

## 7. Planning

### Planner bot

A framework generic `PlannerBot(Bot)` in
`dandy/agent/intelligence/bots/planner_bot.py`:

```python
class PlannerBot(Bot):
    role = 'Planning Engineer'
    def __post_init__(self):
        super().__post_init__()
        self.llm_config = self.obj.agent.planner_config   # via owner hook, see below
        self.guidelines = planner_guidelines_prompt()
    task = 'Create a concise, actionable plan … the coding agent can execute directly.'
    def process(self, user_input):
        return self.llm.tools.prompt_to_intel(prompt=user_input,
                                              tools=???, intel_class=PlanIntel,
                                              max_tool_iterations=None)
```

Two construction options to decide (call out in §14):

- **(A) Agent-owned**: the agent builds the planner with
  `planner_bot = PlannerBot(role=..., task=..., guidelines=..., llm_config=...)`
  seeding its `LlmServiceMixin` attributes so each agent can set its own
  planner role/guidelines without subclassing. Cleanest for a framework where
  the variety lives in *configuration* not class hierarchy.
- **(B) Subclass-per-planner** (current CLI shape): `class MyPlanner(PlannerBot)`
  with hardcoded class attrs. Familiar, but restarts the 
  `CodingBot`-vs-`PlanningBot` verbosity the CLI already has.

Recommend **(A)** with the agent passing `planner_config`/`planner_task`/
`planner_guidelines`; the CLI's `PlanningBot` becomes a thin
`PlannerBot(llm_config=get_cli_llm_config('THINKING'), …)` or disappears.

### PlanIntel

```python
class PlanIntel(BaseIntel):
    goal: str = ''
    steps: list[str] = []
    key_files: list[str] = []        # optional; raw models handle it or omit
    summary: str = ''                # single-sentence narration line
```

Today the planner returns `DefaultIntel` (raw text). Switching to `PlanIntel`:

- gives a validated, structured contract (and keeps models honest about "list
  of steps");
- relies on the existing fenced-JSON recovery + validation-retry loop in the
  connector (models wrapping `PlanIntel` JSON in markdown is already handled);
- feeds the worker with
  `Prompt().heading('Implementation Plan').intel(plan_intel)` (a better worker
  prompt than embedding raw prose).

Risk: some strict endpoints won't like `response_format` + tools (already
documented: `response_format` is cleared when tools are passed, and local
validation retries cover the rest — unchanged). Keep `PlanIntel` optional:
`plan_intel_class: type[BaseIntel] = PlanIntel`, settable to `DefaultIntel` for
total leniency. The **module-level `run_subprocess`/`BaseTool` work is
orthogonal** — the agent only passes tool lists through.

---

## 8. Thinking

"Thinking" in the CLI today is three overlapping things; the framework should
name and separate them:

1. **The plan pass on a `THINKING` config** (`LLM_CONFIGS['THINKING']`) — a
   distinct model for higher-quality reasoning. → §7.
2. **The narrated story** — `progress_callback` beats from
   `LlmToolService.prompt_to_intel` (model narration sentence via
   `LlmToolCallsIntel.summary` + per-tool `action_sentence(...)`), rendered by
   the CLI's thinking phrases/`_StoryProgress`. → §9. Stays CLI-side.
3. **A true pre-reasoning pass** — a new, opt-in `think()`:

```python
class ThinkingIntel(BaseIntel):
    considerations: list[str] = []
    decision: str = ''
    confidence: float | None = None    # 0..1, optional
```

`think()` runs the *planner* bot (same `THINKING` config, same planner tools)
with thinking guidelines ("reason out loud, consider alternatives, then state a
decision — do not act"), returns `ThinkingIntel`, and:

- by default its `considerations` are surfaced through `progress_callback` as
  story beats, **not** injected into the worker prompt (choice of
  `think_feed_worker: bool = False`);
- with `think_enabled=True` + `think_feed_worker=True`, the decision is folded
  into the worker prompt like a plan, giving a "plan → consider → execute" chain.

`think_enabled` is `False` by default (extra LLM spend); the CLI can enable it
in `DEBUG` mode or via a `/think`-style toggle later.

---

## 9. Callbacks and the story (stays CLI, but the contract is framework)

`BaseAgent.chat/think/plan` accept and forward the existing callbacks
unchanged (`dandy/llm/tool/service.py`):

- `progress_callback: Callable[[str], None]` — one beat per tool round
  (narration summary + each `action_sentence`), and agent-level beats the CLI
  already emits (`'Planning'`, `'Compacting conversation history (N tokens)...'`).
- `verbose_callback: Callable[[str], None]` — the debug trace (round number,
  tool args/results previews, validation failures, `GAVE UP`).

The agent adds an internal convenience so CLI code doesn't interpolate
`'Planning'` strings:

```python
    def _emit(self, message: str, progress_callback=None):
        if progress_callback is not None:
            progress_callback(message)
```

`Printer.running_phrase(action_name)`/`_StoryProgress`/thinking phrases remain
100% CLI-side (`dandy/cli/tui/`, `dandy/cli/thinking_phrases.py`) — the
framework only guarantees the callback contract.

---

## 10. Tool calling wiring

- `worker_tools`/`planner_tools`: `ClassVar[list[ToolType]]`, normalized via
  `to_tool_instances` (already happens inside `LlmToolService.prompt_to_intel`)
  so they accept classes, instances, or a mix.
- The agent does **not** reimplement dispatch: it hands the lists to
  `self.llm.tools.prompt_to_intel` (framework execute-and-loop), which already
  handles `tool_functions` override, argument validation feedback loops, and
  `_process_tool_call` (`handle(**validated_args)`, `action_sentence` fallback).
- `planner_tools` is typically a read-mostly subset (git status/diff, search,
  read) but that choice is the subclass's.
- A `BaseAgent`-specific validation in `__init__`: raise
  `AgentCriticalError` if either tool list contains a non-tool object (catch
  the failure early, consistent with `_required_attrs` philosophy).

---

## 11. Recording and futures

- `BaseAgent(Bot)` gets the recorder auto-wrapping for free: `Bot.__init_subclass__`
  installs the `__getattribute__` that records `process(...)` — so an agent run
  is one `EventType.RUN` with the original `__getattribute__` workaround intact.
  **Do not override `__getattribute__` in `BaseAgent`** (AGENTS.md Gotcha #1).
- The planner bot is also a `Bot`, so its calls get their own
  `recorder_event_id` (via `BaseService`), composing a coherent recording.
- `process_to_future` is inherited — `agent.chat_to_future` would be a thin
  alias; consider adding `chat_to_future` for parity in Phase 4.
- No new `dandy/agent/recorder.py` needed unless Phase 3 adds
  agent-level rollup events (a single "Agent run" enclosing plan+exec). Defer.

---

## 12. Persistence / session

Framework side (Phase 4):

```python
class AgentStateIntel(BaseIntel):
    messages: list[dict]        # wire-form Message.model_dump() records
    summary: str = ''
    plans_created: int = 0
```

- `BaseAgent.to_state() -> AgentStateIntel`, `BaseAgent.from_state(state)`:
  rebuild `self.history` from the dumped messages (respecting the leading
  system message constraint — `MessageHistory.add_message(…, rebuild_prompt=…)`
  or re-inject the leader). This is deliberately framework-side and
  serialization-neutral.
- The CLI already persists `DandyCliSession` to `.dandy/…/session.json`
  (`dandy/cli/session.py`); it would store the serialized `AgentStateIntel`
  rather than reinvent agent memory. **Session file management stays in the
  CLI**; the agent only supplies `to_state`/`from_state`.

---

## 13. Configuration

- `LLM_CONFIGS`/`CONTEXT_SIZE`/`DEFAULT` inheritance are untouched — the agent
  leans entirely on `LlmConfig` (`dandy/llm/config.py`), which already resolves
  HOST/PORT/API_KEY from `DEFAULT` and derives `max_completion_tokens`.
- `worker_config` = the agent's own `llm_config` (a `Bot` attribute already);
  `planner_config` = `THINKING` by default (a plain config name like any other
  Bot's, no special casing).
- `CLI_CONFIG` (`dandy/cli/utils.py::get_cli_llm_config`) and the welcome
  banner's model name stay CLI-side; `CodingAgent(BaseAgent)` works because the
  subclass sets `llm_config = get_cli_llm_config('CODING')` in `__post_init__`
  exactly as `CodingBot` does today. A non-CLI user just sets
  `llm_config = 'DEFAULT'`.
- `dandy.json` fallback (JSON settings) requires no changes — `LlmConfig`
  reads the same `settings` object.

---

## 14. Open questions (decide before implementing)

1. **Planner construction**: agent-owned generic `PlannerBot` seeded from
   `planner_config/planner_task/planner_guidelines` (recommend A) vs.
   subclass-per-planner (B). A is more configurable and kills the
   `CodingBot`/`PlanningBot` duplication; B matches today's docs/tests.
2. **`PlanIntel` vs prose plans**: adopt structured `PlanIntel` by default with
   `plan_intel_class` override (recommend), or stay on `DefaultIntel` until the
   strict-endpoint behavior is battle-tested? The fenced-JSON recovery already
   mitigates the model-wraps-JSON risk.
3. **`think()` semantics**: separate `think_enabled` pass (recommend) vs.
   folding "thinking" into planning only. If added, does its output feed the
   worker (`think_feed_worker`) or only narrate?
4. **`process()` vs `chat()`**: `process` currently *replaces* chat's param
   set. Decide whether `process(user_input, **kwargs)` should be the recorder-
   wrapped entry point that internally calls `chat`, or remain a thin alias.
5. **Naming of the framework prompt builders**: `agent_worker_guidelines()` /
   `planner_guidelines_prompt()` vs moving the CLI's existing
   `coding_guidelines_prompt`/`planning_guidelines_prompt` (with their
   narration/tool-calling sections) into `dandy/agent/intelligence/prompts.py`
   nearly verbatim and having the CLI import them. Recommend: move, de-CLI them
   (drop path-root talk or make it a parameter), keep CLI wording intact.
6. **Export surface**: `from dandy import BaseAgent` + `PlanIntel`/`ThinkingIntel`,
   or keep intels importable only from `dandy.agent.intelligence.intel`? Follow
   `BaseTool` precedent (export the class from the root, intels stay internal).
7. **Recorder rollup**: one enclosing "Agent run" event (needs new
   `dandy/agent/recorder.py`) or rely on per-bot events for Phase 1?

---

## 15. CLI migration (what collapses into `BaseAgent`)

When `BaseAgent` lands, `CodingAgent` becomes a two-liner:

```python
class CodingAgent(BaseAgent):
    role = 'Senior Software Engineer'
    task = 'Implement the user coding request by editing the project. …'
    guidelines = coding_guidelines_prompt()
    worker_config = 'CODING'
    planner_config = 'THINKING'
    worker_tools = AGENT_TOOLS
    planner_tools = AGENT_TOOLS

    def __post_init__(self):
        super().__post_init__()
        self.llm_config = get_cli_llm_config('CODING')
```

Deleted/moved from `dandy/cli/`:

- `coding_agent.py` → **delete** `_resolve_context_size`,
  `_compaction_target_token_count`, `_compact_history_for_next_message`,
  `_create_plan`, `chat` body, `AGENT_COMPACTION_TARGET_RATIO` (all move to
  `BaseAgent`); keep the class for the CLI's config/tools wiring.
- `bots/coding_bot.py` + `bots/planning_bot.py` → fold into the framework
  (`PlannerBot`) and the agent's own identity; the worker is the agent itself.
- `intelligence/prompts.py` → move builders to `dandy/agent/intelligence/prompts.py`
  and re-import (or keep as thin wrappers for the CLI).
- `main.py`, `cli.py`, `session.py`, `tui/` → unchanged; `DandyCli.agent` keeps
  the same `chat(..., progress_callback, verbose_callback)` / `clear()` surface,
  so CLI tests are untouched in behavior.

Result: the user-visible CLI is identical, but the engine is framework code.

---

## 16. Testing plan

Hermetic, mock at the connector boundary, mirrors existing conventions.
`tests/agent/` (new) + ported `tests/cli/intelligence/test_coding_agent.py`.

**`tests/agent/test_agent.py`** (mock `dandy.http.connector.HttpConnector.request_to_response`
with a `side_effect` list of `HttpResponseIntel`s):

1. **Multi-turn**: turn 2's request body contains turn 1's user/assistant
   messages (the `replace_message_history=True` merge persists into
   `agent.history`).
2. **Plan on**: first chat emits a planning call (planner bot's request shows
   `PlanIntel` schema + planner tools), and the worker prompt contains an
   `Implementation Plan` section / `PlanIntel` fields (mirrors
   `test_chat_creates_plan_and_feeds_it_to_coding_bot`).
3. **Plan off**: `plan_enabled=False` skips the planner request entirely.
4. **Think pass**: `think_enabled=True` emits a reasoning call and surfaces
   `considerations` via `progress_callback`.
5. **No-give-up**: `max_tool_iterations=None` keeps looping past 5 rounds
   (mirrors `test_agent_does_not_give_up_after_five_tool_rounds`); a finite cap
   still raises `LlmRecoverableError`.
6. **Compaction**: `compact_message_history` behaviors on `agent.history`
   (keep system+newest, drop tool rounds first, no dangling tool messages,
   no-op under budget, ratio math) — directly ported from
   `TestCompactMessageHistory`; plus "compacts before sending"
   (`test_agent_compacts_history_before_sending`).
7. **Context resolution**: from `CONTEXT_SIZE`, string int values, and the
   `65536` fallback (port `test_agent_resolves_context_size_*`).
8. **Verbose forwarding**: `verbose_callback` receives round/tool events
   (port `test_agent_forwards_verbose_details`).
9. **clear/reset**: `clear()` empties `history` and resets planner+worker
   (port `test_agent_clear_resets_history`).
10. **Tool dispatch is untouched**: a tool fake's `handle(**validated_args)`
    executes; invalid args are fed back to the model (covered by the existing
    `tests/llm/tool/test_service.py` — no duplication).

**`tests/agent/intelligence/`** fixtures: `FakeTaskAgent(BaseAgent)` with two
tiny fake tools, a fake `PlanIntel`-returning planner via
`mock.patch`, and a `NoOpProgress` recorder list for callback assertions.

**`tests/cli/`**: existing `test_coding_agent.py` stays green (the class
surface `chat`/`clear` is unchanged); add one test asserting
`CodingAgent` is-a `BaseAgent` so future regressions can't fork the engines.

**Lint/type gates**: `ruff check .` + `ruff format .` (single quotes, 100
cols), `ty` (warn-only; new code should not add diagnostics), `codespell`.

---

## 17. Export surface & docs

- `dandy/__init__.py`: add `from dandy.agent.agent import BaseAgent` and
  `__all__` entry (thin re-export layer only — no logic, per AGENTS.md).
- Decision (§14.6) on exporting `PlanIntel`/`ThinkingIntel` from the root.
- `AGENTS.md`:
  - new row in the architecture table for `agent/`;
  - new "Agent" section (or fold into the CLI/tool-calling sections) describing
    `BaseAgent` as the CLI's engine;
  - note in Gotchas that `BaseAgent` inherits `Bot`'s no-`__getattribute__`
    rule and that the `Agent`/processor module was **not** restored — this is a
    bounded orchestrator, not a DAG pipeline.
- `docs/tutorials/agents.md` (exists) — rewrite to lead with `BaseAgent`; add a
  `docs/changelog/v2_changelog.md` entry; update mkdocs `reference` via
  `docs/scripts/generate_api_reference.py` (generated, don't hand-edit).
- `tests/example_project/book/` — the multi-bot book example stays as-is
  (proves composition without agents); no forced sweep.

---

## 18. Roadmap / phases

| Phase | Scope | Exit criteria |
|---|---|---|
| **1. Skeleton + port** | `dandy/agent/` package, `BaseAgent` with `chat`, pre-turn compaction, `_create_planner_bot`, `plan_enabled`, worker loop. Move prompts. Port CLI tests to `tests/agent/`. | `pytest tests/agent tests/cli/intelligence/test_coding_agent.py` green; ruff/ty clean |
| **2. Structured planning** | `PlanIntel` (with `plan_intel_class` fallback), planner seeded from agent attrs, `_plans_created`/`plan_every_turn`. | planner tests use `PlanIntel` schema; worker prompt shows rendered plan |
| **3. Thinking** | `ThinkingIntel`, `think()`, `think_enabled`, `think_feed_worker`, story beats via existing callbacks. | think on/off/feed tests; no new callback types |
| **4. CLI migration** | `CodingAgent(BaseAgent)`, delete CLI dupes, `DandyCli` unchanged, `to_state`/`from_state` + session persistence, `chat_to_future`, recorder rollup decision. | CLI behavior identical; `tests/cli/test_cli.py` + manual REPL pass; docs/AGENTS updated |
| **5. Hardening** | Example-project agent (`tests/example_project`), export surface finalization, `docs` pass, `mkdocs build --strict`. | full suite green; strict docs build green |

---

## 19. Key existing pieces this builds on (do not reimplement)

| Concern | Where it lives today |
|---|---|
| Execute-and-loop tool calling (dispatch, validation feedback, `max_tool_iterations`) | `dandy/llm/tool/service.py::LlmToolService.prompt_to_intel` |
| Per-round compaction safety net | `LlmToolService._compact_history_before_next_round` (`TOOL_LOOP_*` constants) |
| Message history + remember/compact semantics | `dandy/llm/request/message.py` (`MessageHistory`, `compact_message_history`) |
| Context size + derived output budget | `dandy/llm/config.py::LlmConfig.context_size/max_completion_tokens` (`LLM_OUTPUT_TOKEN_RATIO = 0.20`) |
| Prose tolerance for long-task answers | `DefaultIntel` + connector `json_invalid` fallback |
| Fenced-JSON recovery / strict validation | `LlmConnector._validate_fenced_json_response`, retry loop |
| Bot base, mixins, recorder wrapper, futures | `dandy/bot/bot.py`, `dandy/core/service/*` |
| Decoder (quick decisions inside a task) | `self.llm.decoder.prompt_to_value(s)` |
| Tool executor + subprocess helper | `BaseTool` (`dandy/tool/tool.py`, now with `run_subprocess`) |
| CLI story/UI | `dandy/cli/tui/`, `thinking_phrases.py`, `session.py` |

---

## 20. One-paragraph summary

`BaseAgent` is a `Bot` subclass that turns the framework's existing-but-scattered
agent machinery (tool loop, `MessageHistory` + compaction, `CONTEXT_SIZE`
budgeting, `THINKING`-config planner, `DefaultIntel` prose tolerance) into one
configurable class: it is its own worker, composes a planner for optional
plan/think pre-passes, owns persistent conversation memory that never gives up,
and exposes the same `progress_callback`/`verbose_callback` contract the CLI
already renders. The CLI stops carrying agent logic and becomes a thin driver
(`CodingAgent(BaseAgent)`); the plan lands in phases (skeleton/port →
structured planning → thinking → CLI migration → hardening), each gated by the
hermetic test suite and governed by the framework's conventions (mixins,
`intelligence/` subtrees, exceptions, exports, ruff/ty).
