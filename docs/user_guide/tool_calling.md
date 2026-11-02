# Tool Calling

**Domain concepts:** [Tool](../domain_model/glossary.md#glossary), tool call, tool round.

**Lives in:** `dandy/domain/tool/` (the `BaseTool` descriptor — pure) and
`dandy/application/tool/` (the calling loop — a use case).

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
- An optional `action_label` class attribute (next to `name` / `description`) and an
  `action_output(**validated_args)` override let a UI show exactly what the tool is
  doing while it runs — for example, label `'Reading'` with output
  `'src/foo.py lines 1-10'`. Without a label, the title-cased tool name is used;
  without an output override, the label stands alone. An optional
  `action_ascii_char` class attribute (default `'•'`) sets the character the CLI
  prefixes the tool's beat lines with.

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

`ToolService` keeps calling the model; when it requests tools, the framework validates
the arguments against the derived schema, calls `tool.handle(**arguments)` with Python
types (booleans and integers parsed, not left as JSON text), feeds the result back as a
`role='tool'` message, and loops until the model produces the final Intel.

- `max_tool_iterations` caps the rounds (default 5; `None` = no cap — the coding agent
  runs uncapped, at the cost of unbounded API spend).
- The repeated-call guard breaks degenerate loops with two per-loop counters,
  neither consecutive-only: a signature counter over (name, canonical arguments,
  result) — arguments are canonicalized (whitespace runs folded in every string
  value, sorted-key compact JSON) so re-typed calls with line-wrap, indent, or
  key-order drift still accumulate — and a result counter over (name, result)
  pairs that counts across any argument wording, so a reworded call that keeps
  producing the same output is caught too. The result fed back to the model
  carries a steering note from the third occurrence, and the loop raises
  `LlmRecoverableError` at ten. A changed result never accumulates toward either
  counter, so time-varying commands never trip them.
- Invalid arguments are fed back to the model as a tool message so it can self-correct.
- An explicit `tool_functions={'name': handler}` entry wins over the tool's own
  `handle()`; handlers receive the parsed argument Intel and return a string or Intel.
- A `progress_callback` (typed `Callable[[StoryBeat], None]`) gets a `StoryBeat`
  per event: one for the model's narration sentence (when it wrote one, a
  description-only beat marked `kind='narration'`), and one per executed tool
  carrying the tool's `action_label` as `label`, its
  `action_output(**validated_args)` result as `description`, and its
  `action_ascii_char` as `ascii_char`. Compaction notices are description-only
  beats too. The split exists so a UI can style the parts independently (the CLI
  renders every line flush left, each beat prefixed by its `ascii_char` — the
  tool's character, or a bullet when the beat carries none — with the label in
  bold grey, the description in plain black, and the model's narration in bold
  blue).
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
  `ToolCallsIntel` (the raw tool calls) instead of your Intel — the manual path for
  driving the conversation yourself.
