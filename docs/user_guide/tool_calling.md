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
  without an output override, the label stands alone. The `can_mutate_state`
  class attribute (default `False`) marks tools that can change state; the CLI
  renders their beat labels in bold orange instead of grey, and the fixed `↳`
  arrow that prefixes each tool beat line is colored like the label. The
  `emits_story_beat` class attribute (default `True`) suppresses the execution
  beat entirely for a tool that renders its own story while it runs; the CLI's
  `question` tool sets it `False` because the interactive prompt that renders
  while it waits is the display of the action.

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
- Guards watch the loop live (`dandy/domain/guard/`): the service runs a
  `GuardChain` of middleware-style `Guard` watchers, each observing the loop's
  events and returning a verdict — a steering note appended to the tool result,
  a request to compact the conversation, or a failure that stops the loop with
  `LlmRecoverableError` before the next request. The shipped `RepeatGuard`
  counts every executed call against a canonical signature (whitespace runs
  folded in every string value, sorted-key compact JSON of the validated
  kwargs), so re-typed calls with line-wrap, indent, or key-order drift share
  one signature, while different arguments are different calls that never
  accumulate against each other no matter how often they produce the same
  result: the result fed back to the model carries a steering note from the
  third identical call, and the loop raises `LlmRecoverableError` at ten. The
  shipped `ContextPressureGuard` requests compaction once the conversation's
  estimated token count passes 80% of the resolved context window, and fails
  the loop if the pressure re-asserts after a compaction while the conversation
  still exceeds the whole window.
- Invalid arguments are fed back to the model as a tool message so it can self-correct.
- An explicit `tool_functions={'name': handler}` entry wins over the tool's own
  `handle()`; handlers receive the parsed argument Intel and return a string or Intel.
- A `progress_callback` (typed `Callable[[StoryBeat], None]`) gets a `StoryBeat`
  per event: one for the model's narration sentence (when it wrote one, a
  description-only beat marked `kind='narration'`), and one per executed tool
  that emits a story beat (a tool sets `emits_story_beat = False` to render its
  own story instead of a beat), carrying the tool's `action_label` as `label`, its
  `action_output(**validated_args)` result as `description`, and its
  `can_mutate_state` flag as `can_mutate_state`. Compaction notices are description-only
  beats too. The split exists so a UI can style the parts independently (the CLI
  renders every line flush left as a running list: consecutive tool beats with
  the same label share one heading line — the label in bold skyblue, bold orange
  when `can_mutate_state` is set — printed once when the label appears and
  again whenever the label changes or a non-tool line (a thought or a notice)
  has printed in between, with each description on its own
  line below the heading prefixed by a `↳` arrow colored like the label, so
  arrows exist only on tool output lines; each heading, and each narration, is
  preceded by a blank line; the model's narration renders in bold blue and
  compaction notices in bold purple, both with no prefix, and system beats
  print plain). The newest beat animates: a bold blue thinking-phrase line
  sits on its own line below the beat, a random phrase is drawn once and held
  for three seconds (the phrase line carries no animated dots), and the
  region is redrawn in place every tick so it never appends to the scrollback;
  the animating frame folds a multi-line description onto the single line above
  the phrase line, and the settled frame prints the beat's text in full,
  clearing every line it overwrites so no tail of the longer animating frame
  survives. The leftover phrase line is reused as the first line of the next
  region, so beats within a group settle with no blank line between them.
  File paths in a tool beat's description are emitted as clickable `file://`
  links (raw OSC 8, resolved against the project root), so clicking one opens
  the file with the OS default handler.
- A `verbose_callback` gets one line per event for debugging, including a `GAVE UP` line
  when a finite cap is hit.
- A `tool_call_callback` (typed `Callable[[str, dict[str, object]], None]`) is fired once
  per executed tool call with the tool name and its validated keyword arguments — after
  the `handle()` / `tool_function` dispatch, so a call whose arguments fail validation
  never fires it. `Agent.turn` and `Agent.run` accept and forward it; the CLI uses it to
  track the paths its file tools touched and the action taken (`write_file` /
  `create_directory` → added, `edit_file` → modified, `delete_file` → removed) and print
  file-change sections (clickable links) below the final answer.

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
