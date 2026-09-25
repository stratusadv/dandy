# Tactical Patterns

The strategic design says *where* the boundaries are. This page says *what* lives inside
them, in terms of the standard DDD tactical patterns, mapped to the actual classes.

## Value objects

Identity by value, validated at construction, safe to share.

| Pattern instance | Class / module | Notes |
|---|---|---|
| Intel | `BaseIntel` subclasses — `dandy/domain/intel/` | The primary VO: the contract for an LLM answer. Trimmed copies are created at runtime with `model_inc_ex_class_copy`. |
| Prompt | `Prompt` — `dandy/domain/llm/prompt/prompt.py` | A builder-as-value-object: chain snippets, `to_str()` renders. |
| Message | `Message` — `dandy/domain/llm/request/message.py` | One conversation turn in wire form. |
| Options | `LlmOptions` — `dandy/domain/llm/options.py` | Sampling knobs; range-checked, non-None values only. |
| Tool descriptor | `BaseTool` — `dandy/domain/tool/tool.py` | Name + description + typed `handle()` signature; the signature *is* the schema. |
| Tool call | `LlmToolCallIntel` — `dandy/domain/llm/tool/intel.py` | The model's request to invoke a tool (id, name, arguments). |
| LLM Config | `LlmConfig` — `dandy/infrastructure/llm/config.py` | A VO describing an endpoint. It sits in infrastructure because it is built from the http wire types (`Url`, request/response Intel) it will talk to. |
| Event / EventAttribute | `dandy/infrastructure/recorder/events.py` | VOs of the observability context. |

## Entities and aggregates

Identity-bearing objects with invariants the system must keep true.

### MessageHistory (aggregate)

`dandy/domain/llm/request/message.py`. The aggregate root of a conversation. Invariants:

1. At most one system message, and it must lead the history.
2. No `tool` result message without its preceding assistant `tool_calls` message.
3. The history compacts under pressure: `compact_message_history` keeps the system
   message and the newest exchange, drops oldest tool rounds first, and never breaks
   invariant 2. (This is what keeps long agent sessions inside the context window.)

It also has a quirk worth knowing: an empty history is *falsy* in Python, so framework
guards use `is not None` checks, never truthiness.

### Recording (entity)

`dandy/infrastructure/recorder/recording.py`. Identity by name, lifecycle
(start → events → stop), an event store, token usage, run time. Renderers project it to
HTML/JSON/Markdown without mutating it.

### The Recorder (singleton domain service over the aggregate)

`dandy/infrastructure/recorder/recorder.py`. One process-wide instance that owns the
current Recording, validates recording state (`check_recording_is_valid`), and routes
events. It is a singleton because a process has exactly one "what is happening right
now" — and because `Bot` auto-records through it.

## Domain services

Stateless logic that belongs to the domain but to no single VO.

| Service | Where | Does |
|---|---|---|
| `IntelFactory` | `dandy/domain/intel/factory.py` | Python type ↔ JSON schema mapping; validates LLM responses into Intel; derives schemas from call signatures (this is how tool parameters get their schema). |
| Token estimation | `dandy/domain/llm/tokens/utils.py` | A dependency-free, character-class heuristic for token counts — domain policy, not an adapter. |
| History compaction | `compact_message_history` in `dandy/domain/llm/request/message.py` | Enforces the MessageHistory invariants under space pressure. |
| `generate_cache_key` | `dandy/infrastructure/cache/tools.py` | The key policy: function identity + layered, depth-capped argument hashing. It detects framework services structurally (by `recorder_event_id`) precisely so it never has to import them. |
| Diligences | `dandy/application/llm/diligence/` | Named quality policies executed around a request (stop-word removal, vowel removal, second pass). Policy lives here as application because it drives the connector; the *instructions* are domain prompts. |

## Domain events

The observability context is built on them. `EventType` names the facts the system can
record — `run`, `retry`, `request`, `response`, `result`, `success`, `warning`,
`failure`, `other`. Events are emitted *as behavior happens* (the framework installs a
recorder wrapper around every `Bot.process` call at class-creation time), not scraped
after the fact. Attributes carry the payload; images and audio can ride along as base64.

## Ports and adapters

The one place the framework practices classic hexagonal discipline:

- **Port:** `BaseConnector` (`dandy/shared/connector/`) — the ABC an LLM/HTTP adapter
  implements.
- **Adapters:** `LlmConnector` (infrastructure: builds requests, runs diligence hooks,
  validates, retries) and `HttpConnector` (infrastructure: the actual HTTP with retries).
- **Consumers:** application services depend on the port's behavior, not on the network.
  Hermetic tests patch the port's boundary (`HttpConnector.request_to_response`) and the
  entire application runs without a network.

The rest of the framework uses the [service pattern](../architecture/service_pattern.md)
rather than constructor injection — composition happens at attribute access through
mixins, which is what produces the
[documented seams](../architecture/layering.md#documented-seams) between application and
infrastructure.

## Domain rules that are easy to break

- Decoder keys must be strings (`DecoderCriticalError` otherwise).
- `Bot.process` requires a prompt argument (it forwards `args[0]`).
- `Bot` subclasses must call `super().__post_init__()` first, and must never override
  `__getattribute__` (the recorder wrapper lives there).
- `reset()` chains through the MRO; the decoder service is deliberately excluded.
- Strict endpoints reject a second system message — the connector merges diligence
  instructions into the leading system message, never adds one.
