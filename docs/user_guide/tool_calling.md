# Tool Calling

**Domain concepts:** [Tool](../domain_model/glossary.md#glossary), tool call, tool round.

**Lives in:** `dandy/domain/tool/` (the `BaseTool` descriptor — pure) and
`dandy/application/llm/tool/` (the calling loop — a use case).

## A tool is a class

`BaseTool` is an abstract, inheritance-style descriptor: set `name` and `description`,
override `handle()` with a typed signature. The signature *is* the schema the model sees
— there is no separate schema declaration, and nothing to keep in sync.

```python
from dandy import BaseTool


class GetWeatherTool(BaseTool):
    name = 'get_weather'
    description = 'Get the current weather for a location.'

    def handle(self, location: str = '', units: str = 'celsius') -> str:
        return weather_service.get(location, units)
```

- No default on a parameter ⇒ required in the schema; with a default ⇒ optional.
- A `handle(self)` with no parameters yields a no-argument tool (empty `properties`).
- `handle` is abstract: a tool class without an override cannot be instantiated.
- `tools=[...]` accepts a mix of classes and instances; everything is normalized to
  instances before the wire call.

## The execute-and-loop

```python
result = bot.llm.tools.prompt_to_intel(
    'What is the weather in Toronto?',
    intel_class=WeatherIntel,
    tools=[GetWeatherTool],
    max_tool_iterations=5,
    progress_callback=print,
)
```

`LlmToolService` keeps calling the model; when it requests tools, the framework validates
the arguments against the derived schema, calls `tool.handle(**arguments)` with Python
types (booleans and integers parsed, not left as JSON text), feeds the result back as a
`role='tool'` message, and loops until the model produces the final Intel.

- `max_tool_iterations` caps the rounds (default 5; `None` = no cap — the coding agent
  runs uncapped, at the cost of unbounded API spend).
- Invalid arguments are fed back to the model as a tool message so it can self-correct.
- An explicit `tool_functions={'name': handler}` entry wins over the tool's own
  `handle()`; handlers receive the parsed argument Intel and return a string or Intel.
- A `progress_callback` gets a beat per round (the model's narration sentence, if it
  wrote one) and a beat per executed tool via the tool's optional
  `action_sentence(**validated_args)` override.
- A `verbose_callback` gets one line per event for debugging, including a `GAVE UP` line
  when a finite cap is hit.

## Subprocess tools

`BaseTool` carries a subprocess helper. Subprocess tools set `working_directory` (or
override the property), `timeout_seconds = 30`, and `use_shell = False`, then call
`self.run_subprocess(command, timeout_seconds=None)` — an 8000-char output cap, never
raises, so the model always gets a string it can react to. The CLI's
`run_command` / `git_status` / `git_diff` tools are exactly this pattern.

## Wire behavior

- `tools` / `tool_choice` are explicit request-body fields.
- Passing tools **clears `response_format`** on the request (strict response_format plus
  non-strict tools 400-errors on OpenAI); the final answer is still validated by the
  Intel retry loop.
- Calling `bot.llm.prompt_to_intel(..., tools=[...])` directly returns
  `LlmToolCallsIntel` (the raw tool calls) instead of your Intel — the manual path for
  driving the conversation yourself.
