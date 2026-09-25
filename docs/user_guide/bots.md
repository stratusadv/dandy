# Bots

**Domain concept:** [Bot](../domain_model/glossary.md#glossary) — a named unit of AI
behavior: a use case object that owns *how* a task is performed.

**Lives in:** `dandy/application/bot/` (application layer), composed with infrastructure
adapters through the [service pattern](../architecture/service_pattern.md).

## Why a Bot

`Bot().process(...)` is one-shot. A Bot subclass is the framework's way of making
repeated, similar work a *named, configured, testable unit*: which endpoint config it
uses, what role it plays, what its task statement is, what guidelines constrain it, and
what Intel type it returns.

## A Bot

```python
from dandy import BaseIntel, Bot, Prompt


class CapitalIntel(BaseIntel):
    country: str
    capital: str


class CapitalBot(Bot):
    llm_config = 'DEFAULT'
    role = Prompt().text('You answer geography questions in one line.')
    task = 'Return the capital of the requested country.'
    guidelines = Prompt().list(['Country names are capitalized.'])
    intel_class = CapitalIntel


bot = CapitalBot()
intel = bot.process('France')
print(intel.capital)  # 'Paris'
```

The class attributes (`llm_config`, `role`, `task`, `guidelines`, `intel_class`) are the
Bot's configuration surface. They are enforced at class-creation time by the
`ServiceCriticalError` guards, so a Bot missing a required attribute fails the moment it
is defined, not on first use.

## Customizing `process`

Override `process` to accept your own signature and build your own prompt; the bot's
configuration still applies:

```python
class CandyBot(Bot):
    llm_config = 'THINKING'
    intel_class = CandyIntel

    def process(self, user_prompt: Prompt | str, candy_theme: str) -> CandyIntel:
        self.llm.options.temperature = 0.1

        prompt = (
            Prompt()
            .heading('Request')
            .prompt(user_prompt)
            .line_break()
            .heading('Theme')
            .prompt(candy_theme)
        )

        return self.llm.prompt_to_intel(prompt=prompt)
```

!!! warning

    - Call `super().__post_init__()` first if you define `__post_init__`.
    - Never override `__getattribute__` — the recorder wrapper is installed there.
    - `process` requires a prompt: the base forwards `args[0]` or raises.

## The service surface

A Bot exposes its services through properties, built lazily on first access:

| Attribute | Service |
|---|---|
| `bot.llm` | `LlmService` — prompts, options, history, `reset()` |
| `bot.llm.tools` | `LlmToolService` — the tool-calling loop |
| `bot.llm.decoder` | `DecoderService` — keyed selection |
| `bot.llm.diligence` | `DiligenceService` — toggle quality policies |
| `bot.file` | `FileService` — disk access |
| `bot.http` | HTTP connector |
| `bot.intel` | `IntelService` — schema/validation helpers |

`bot.reset()` clears the LLM history and re-applies options from settings (and resets the
other services through the MRO chain).

## Composing many Bots

There is no orchestrator class in the framework. A workflow is ordinary Python calling
several Bots, passing each one's Intel into the next:

```python
theme = ThemeBot().process(prompt)
title = TitleBot().process(theme)
plot = PlotBot().process(title)
```

The reference implementation is `tests/application/example_project/book/` in this
repository: theme → title → characters → world → plot → chapters, with Intel flowing
between every stage.
