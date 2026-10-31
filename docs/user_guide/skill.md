# Skills

**Domain concepts:** [Skill](../domain_model/glossary.md#glossary), active skill, passive
skill, skill activation.

**Lives in:** `dandy/domain/skill/` (the `BaseSkill` descriptor — pure) and
`dandy/application/skill/` (the `SkillService` registry — a use case).

## A skill is a prompt plus methods

A **skill** bundles instructions (a `prompt`) with a set of Python methods the model
can call. It is a [tool](tool_calling.md) with a payload: the tool carries execution,
the skill carries *when and how* the model should use it.

```python
from dandy import BaseSkill


class WeatherSkill(BaseSkill):
    name = 'weather'
    description = 'Get current weather. Use when the user asks about the weather.'
    prompt = 'Answer weather questions using the weather tool.'
    active = False
    tools = ['current']

    def current(self, location: str) -> str:
        """Get the current weather for a location."""
        return weather_service.get(location)
```

- `tools` lists method names; each method is exposed as a tool named
  `{skill}_{method}` (here, `weather_current`).
- The method's docstring first line is the tool description; the method's typed
  signature is the tool's parameter schema — same rules as a tool's `handle`
  (every parameter needs an annotation; no default = required).
- `active` (default `True`) decides the registration mode (below). It can be
  overridden at instantiation: `WeatherSkill(active=True)`.
- A skill with an empty `tools` list is legal: it contributes instructions only.

## Active and passive

| | Active | Passive |
|---|---|---|
| System message | Full `prompt` from the first request | `name: description` line only |
| Tools | All method tools from the first request | Method tools appear after activation |
| `activate_skill` offered | Never | Until every passive skill is active |
| Context cost | Always in context | Metadata only, until the model needs it |

A **passive skill** is activated by the model calling the built-in `activate_skill`
tool with the skill's `name`. The tool's result is the skill's `prompt`, delivered
as a `role='tool'` message — the instructions enter the conversation at the moment
the model decides it needs them, instead of sitting in the system prompt of every
conversation.

Activation is one-way within a conversation: once active, a skill stays active
(there is no de-activation), so the tool list only ever grows. `bot.reset()` (or
`Agent.clear()`) clears activation, so the next conversation starts fresh.

## Registering skills

On a `Bot`, skills are a class attribute — the same registration surface as `role`,
`task`, and `guidelines`:

```python
class AssistantBot(Bot):
    role = 'Assistant'
    skills = [NotesSkill, WeatherSkill]  # classes or instances
```

The skill section is appended to the bot's system message. A bot without skills
behaves exactly as before.

On an `Agent`, skills are a constructor argument; they register on the agent's
shared bot at construction, after the bot's own skills:

```python
agent = Agent(bot, tools=[...], skills=[GitSkill])
```

## Naming and collisions

- Two registered skills cannot share a `name`.
- Generated tool names (`{skill}_{method}`) cannot collide with each other or with a
  tool you pass to `prompt_to_intel`; a collision fails fast with
  `LlmCriticalError` before any request goes out.
- `activate_skill` is reserved; a skill must not generate it as a tool name.
- A passive skill must have a `description` — it is the only thing the model sees
  before activation, so write it as a trigger: what the skill does and *when* to
  use it.

## How it maps to the wire

- The skill section is static per conversation: it is part of the system message
  at/before the first request and is never rewritten mid-loop.
- Skill tools join the per-round tool array of the [execute-and-loop](tool_calling.md):
  the `tools=...` you pass at call time, plus whatever skills are active in that
  round. When a passive skill activates mid-loop, its tools join the next round's
  array and `activate_skill` drops off once every passive skill is active.
- Everything downstream of the tool array is unchanged: argument validation,
  `handle()`-style dispatch, `progress_callback` action sentences, and recording.
