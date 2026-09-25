# Ubiquitous Language

The single most important DDD discipline: the language of the domain and the language of
the code are the same. This page is that language for Dandy. Use these terms in code,
comments, PR titles, and conversation. If a concept is missing here, it is not part of the
model yet.

## Glossary

### Intel

A typed, validated model for a unit of information the system exchanges with an LLM
(`BaseIntel` and subclasses, `dandy/domain/intel/`). Intel is the contract: it defines
what "done" means for a request. A `BaseListIntel` carries a list of Intels. Intel objects
behave like [value objects](tactical.md#value-objects): identity by value, validated on
construction, safe to share.

### Prompt

A structured, composable text object (`dandy/domain/llm/prompt/`) — the system's
outgoing message, built from snippets (headings, lists, embedded files, embedded Intel
schemata) rather than concatenating strings. A prompt is a [value object](tactical.md#value-objects):
immutable in use, compared by content.

### Bot

A named unit of AI behavior: a use-case object that owns *how* a task is performed
(role, task statement, guidelines, which endpoint config, which Intel class it returns).
Bots are how application code asks the domain for work. See
[Bots](../user_guide/bots.md).

### Message / MessageHistory

A `Message` is one wire-level turn (role, content, optional tool calls or tool results)
in a conversation. A `MessageHistory` is the ordered set of messages with two
invariants the framework enforces: exactly one leading system message, and no `tool`
result without its preceding assistant tool-call. History is the
[aggregate](tactical.md#entities-and-aggregates) of a conversation.

### LLM Config

A named endpoint configuration (`LlmConfig`): host, port, key, model, context size.
Configs are declared in the settings module under `LLM_CONFIGS`; a `DEFAULT` entry is
mandatory and other entries inherit its credentials. A config is a value object describing
*where* work goes — distinct from the Bot, which decides *how*.

### Tool (and tool call)

A `BaseTool` is a self-contained, callable capability exposed to the model: a name, a
description, and a typed `handle()` whose signature becomes the function schema the model
sees. A *tool call* is the model's request to invoke a tool, and a *tool round* is one
cycle of the model calling tools and the framework feeding results back.

### Decoder

A use case for **keyed selection**: given a mapping of string keys to values, the model
returns which key it chose. The Decoder enforces that keys are strings, that exactly the
right number come back, and re-prompts on empty or over-long answers.

### Diligence

A named, toggleable **quality policy** applied around an LLM call — e.g. stop-word
removal, vowel removal, a second validation pass. Diligences run as pre/post handlers in
the request pipeline; instructions they carry merge into the conversation's leading
system message. They are policy, not plumbing.

### Event / Recording

An `Event` is one recordable fact about the system's interaction with an LLM
(request, response, result, retry, failure, ...) carrying object name, callable name,
type, and attributes. A `Recording` is the identity-bearing container of a session of
events, renderable to HTML, JSON, or Markdown. Recording is the domain's
[domain events](tactical.md#domain-events) story: the framework's behavior is observable
as data, independent of how it was executed.

### Cache (and cache key)

A named, bounded store that memoizes the result of a function of its arguments. A cache
key is derived from the function identity and a layered hash of its arguments
(depth-capped by design). Caching is a *generic* capability — it knows nothing about LLMs.

### Future

An in-process, thread-pool execution of a callable with a timeout: the framework's
concurrency primitive for running LLM work off the calling thread. Generic, like caching.

### Seam

A deliberate, individually listed cross-layer import that the import-linter contracts
permit. Seams exist because the composition pattern must name adapter classes; each is
documented in [Layering and Dependency Rules](../architecture/layering.md#documented-seams).
An unlisted cross-layer import is a bug, not a style choice.

### Kernel (shared)

The bottom layer: services, exceptions, and utilities that three or more layers need and
that depend on nothing. The kernel is not a dumping ground — it is the last place code
goes, not the first.

## Anti-language

Terms that invite bugs, and their replacements:

| Say this | Not this |
|---|---|
| Intel | "DTO", "schema", "response model" |
| Bot | "client", "agent instance" (a *Bot* is a use case; the *coding agent* is a specific composition of Bots) |
| Seam | "exception to the rule", "technical debt import" |
| Diligence | "middleware", "interceptor" |
| Tool | "function calling handler" |
| Recording / Event | "log", "trace" (a Recording is identity-bearing, queryable, renderable) |
