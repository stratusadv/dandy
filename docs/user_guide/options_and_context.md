# Options and Context

**Domain concepts:** [LLM Config](../domain_model/glossary.md#glossary), options, and the
[MessageHistory](../domain_model/glossary.md#glossary) aggregate's context invariant.

## `LlmOptions`

Per-call sampling knobs, set on the bot's LLM service. `LlmOptions` mirrors the
[OpenAI Chat Completions](https://platform.openai.com/docs/api-reference/chat/create)
request parameters, so any option the endpoint accepts can be set here or declared
per-config in settings under an entry's `OPTIONS` key:

```python
bot.llm.options.temperature = 0.1
bot.llm.options.top_p = 0.9
bot.llm.options.frequency_penalty = 0.2
bot.llm.options.presence_penalty = 0.0
bot.llm.options.max_completion_tokens = 13107
bot.llm.options.seed = 42
```

Supported fields: `frequency_penalty`, `logit_bias`, `logprobs`,
`max_completion_tokens`, `max_tokens`, `n`, `presence_penalty`,
`reasoning_effort`, `response_format`, `seed`, `service_tier`, `stop`,
`temperature`, `top_logprobs`, `top_p`. `LlmOptions` is a pydantic model with
`extra='allow'`, so any other option the endpoint understands is forwarded as-is.
Non-None values are range-checked (temperature 0–2, penalties –2 to 2,
`top_p` 0–1, and positive minimums for `max_completion_tokens` / `max_tokens` /
`n`) and a violation raises `LlmCriticalError`.

### `max_completion_tokens`

Declared per config in `OPTIONS` (or set on `bot.llm.options`). When omitted the
request simply does not send it — it is no longer derived from `CONTEXT_SIZE`, so
the model's own output budget applies. To cap output at a share of the window,
set it explicitly (the previous default was `CONTEXT_SIZE * 0.20`).

### `prompt_retry_count`

`prompt_retry_count` is **not** an OpenAI option — it is Dandy's validation-retry
budget. It is declared per config as a top-level `PROMPT_RETRY_COUNT` key (default
`2`), not inside `OPTIONS`:

```python
LLM_CONFIGS = {
    'DEFAULT': {
        ...,
        'PROMPT_RETRY_COUNT': 3,
    }
}
```

## `CONTEXT_SIZE`

Declared per LLM config in settings (non-`DEFAULT` configs inherit it from
`DEFAULT`):

```python
LLM_CONFIGS = {
    'DEFAULT': {
        ...
        'CONTEXT_SIZE': 65536,
    }
}
```

`CONTEXT_SIZE` is the single source of truth for the agent's history compaction:

| Constant | Share of the window | Used for |
|---|---|---|
| `AGENT_COMPACTION_TARGET_RATIO = 0.70` | 70% | what long histories are compacted down to before a call |

Token counts come from a dependency-free character-class heuristic
(`dandy/domain/tokens/estimate.py`) fitted to BPE tokenizer output, with per-message
overhead for roles, tool-call framing, images (by `detail`), and audio base64.

## Compaction

`compact_message_history` (domain, `dandy/domain/message/message.py`) is what keeps
long sessions inside the window. It is called automatically:

- before every LLM call by the coding agent, and
- before every tool round by the tool-calling loop.

The rules: keep the system message and the newest exchange; drop oldest tool-use rounds
first, then oldest plain exchanges; never leave a `tool` result without its assistant
tool-call. Compaction reports progress (`Compacting conversation history (...) tokens...`)
through the agent's `progress_callback`.

Without any `CONTEXT_SIZE`, compaction falls back to a 65536-token window constant —
the system still works, it just cannot prove the fit. If you want a bounded output,
declare `max_completion_tokens` in the config's `OPTIONS`.
