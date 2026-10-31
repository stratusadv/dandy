# Agent

**Domain concept:** [Agent](../domain_model/glossary.md#glossary) — a stateful
composition of a Bot, designed to be looped.

**Lives in:** `dandy/application/agent/agent.py` (the base class; the turn-result
Intel and the agent exceptions sit beside it in the same package).

## The vocabulary

Every agent framework runs **the agent loop**: the model works, tools run, results
come back, the model works again. Dandy names the levels of that loop precisely:

| Term | Meaning |
|---|---|
| **run** | one autonomous drive: a request in, turns until the request is complete, the final result out |
| **turn** | one exchange: a message in, the agent works (possibly across many tool rounds), a final answer out; the conversation persists |
| **tool round** | one cycle of the model calling tools and the framework feeding results back ([tool calling](tool_calling.md)) |

A `run` is made of `turn`s; a `turn` is made of `tool round`s. Interactive use — a
human feeding one message at a time, like the CLI REPL — is a sequence of `turn`s;
the [coding agent](coding_agent.md)'s `turn` is one such interactive turn.

## The base class

`Agent` (exported from the `dandy` root) wraps a Bot and owns the conversation:

```python
from dandy import Agent, Bot


class WeatherAgent(Agent):
    def __init__(self) -> None:
        super().__init__(bot=WeatherBot(), tools=[GetWeatherTool()])


agent = WeatherAgent()
answer = agent.turn('What is the weather in Austin?')
answer = agent.turn('And in Dallas?')  # same conversation
```

`Agent(bot, tools=None, skills=None, max_turns=None, intel_class=None)`:

- `bot` — the Bot that performs the work (its role/task/guidelines become the
  system prompt; give it guidelines that say `done` means the *whole request* is
  complete, not just the current turn).
- `tools` — the tool set every turn may call; `None` means a plain
  conversation, no tools.
- `skills` — the [skills](skill.md) registered for this agent; active ones put
  their prompt in the system message and their methods in the tool list from the
  first request.
- `intel_class` — the per-turn result model; defaults to `AgentTurnIntel`
  (`text` + `done`).
- `max_turns` — the `run` budget; `None` (the default) means unbounded.

## `turn` — one exchange

`turn(message)` compacts the history if it is approaching the bot's `CONTEXT_SIZE`
(the same 70% target the coding agent uses), then runs one tool loop over the
persistent history and returns the turn's result Intel. The request is only sent
on the first LLM call of the turn; tool rounds after that run on the conversation
alone.

```python
result = agent.turn('Summarize the last commit', progress_callback=print)

if result.done:
    ...
```

## `run` — drive to completion

`run(request)` hands the agent a request and keeps running turns until the request
is complete:

```python
final = agent.run('Build the quarterly report and save it to out/')
print(final.text)
```

- The first turn receives the request; each later turn receives a continuation
  nudge, so the model keeps working instead of re-answering.
- **Completion signal.** By default a turn is finished when its result's `done`
  field is `true` — the model's own judgment that the request is complete, which
  is why the bot's guidelines must define what "complete" means. Pass
  `is_done=lambda result: ...` to override with your own predicate; the callback
  wins, and it is also what lets you `run` with an `intel_class` that has no
  `done` field.
- **Budget.** If `max_turns` is set and the request is still incomplete after
  that many turns, `run` raises `AgentRecoverableError` (the same
  give-up semantics as the tool loop). With no `done` field and no `is_done`,
  `run` fails fast with `AgentCriticalError` — an agent that cannot tell when it
  is finished should not be running.

## Sessions — save and load the conversation

Every agent can snapshot its conversation and restore it later, so a
conversation can outlive the process:

```python
from dandy import Agent
from dandy.application.agent.session_store import SessionStore

store = SessionStore.for_project(Path('my-project'))  # .dandy/agent/sessions/

store.save('my-task', agent.save_session())  # after any turn

agent.clear()
agent.load_session(store.load('my-task'))  # the conversation is back
```

- `save_session()` returns an `AgentSession`: the full message history plus
  metadata (the last request, the model and config names, an estimated token
count). `load_session(session)` restores the history into a fresh
  `MessageHistory` and resets the bot, so the next `turn` continues exactly
  where the saved conversation left off.
- `SessionStore` (`dandy/application/agent/session_store.py`) is the file side:
  one JSON record per named session under a directory (each record pairs the
  `AgentSession` with a name and created/updated timestamps). `for_project(path)`
  targets `<path>/.dandy/agent/sessions/` — agent-neutral, so any agent over the
  same project shares the location. It also gives you `list_sessions()`,
  `latest()`, `delete(name)`, and `new_name(text)`, which derives a fresh
  non-colliding `YYYY-MM-DD-<slug>` name from a piece of request text. Unknown
  names raise `AgentRecoverableError` listing the available sessions; invalid
  names (empty, `.`/`..`, or containing path separators) raise
  `AgentCriticalError`.

The [coding agent](coding_agent.md)'s REPL is the built-in consumer: it auto-saves
after every turn and exposes the store through the `/new`, `/sessions`, `/resume`,
and `/delete` commands plus the one-shot `--continue` flag.

## Relationship to Bot and to the coding agent

A Bot is one use case: in, work, out, stateless across calls. An Agent is the
same composition made stateful and loopable. The [coding agent](coding_agent.md)
is the framework's own agent: a planning bot plus a coding bot over a persistent
history — an interactive agent (you drive the turns); a base `Agent.run` is an
autonomous one (the agent drives them).
