# Options and Context

**Domain concepts:** [LLM Config](../domain_model/glossary.md#glossary), options, and the
[MessageHistory](../domain_model/glossary.md#glossary) aggregate's context invariant.

## `LlmOptions`

Per-call sampling knobs, set on the bot's LLM service:

```python
bot.llm.options.temperature = 0.1
bot.llm.options.top_p = 0.9
bot.llm.options.frequency_penalty = 0.2
bot.llm.options.presence_penalty = 0.0
bot.llm.options.prompt_retry_count = 2   # validation-retry budget, default 2
```

- `LlmOptions` is a pydantic model with `extra='allow'`; non-None values are range-checked
  (temperature 0–2, penalties ≥ 0) and a violation raises `LlmCriticalError`.
- Options can also be declared per-config in settings under an entry's `OPTIONS` key.
- **`max_completion_tokens` is not an option.** It is derived: `CONTEXT_SIZE * 0.20`, so
  the output budget always fits inside the window.

## `CONTEXT_SIZE`

Declared per LLM config in settings (non-`DEFAULT` configs inherit it from `DEFAULT`):

```python
LLM_CONFIGS = {
    'DEFAULT': {
        ...
        'CONTEXT_SIZE': 65536,
    }
}
```

`CONTEXT_SIZE` is the single source of truth for context management:

| Constant | Share of the window | Used for |
|---|---|---|
| `LLM_OUTPUT_TOKEN_RATIO = 0.20` | 20% | the derived `max_completion_tokens` sent on every request |
| `AGENT_COMPACTION_TARGET_RATIO = 0.70` | 70% | what long histories are compacted down to before a call |
| (error margin) | 10% | headroom so input + output never exceeds the window |

Token counts come from a dependency-free character-class heuristic
(`dandy/domain/llm/tokens/utils.py`) fitted to BPE tokenizer output, with per-message
overhead for roles, tool-call framing, images (by `detail`), and audio base64.

## Compaction

`compact_message_history` (domain, `dandy/domain/llm/request/message.py`) is what keeps
long sessions inside the window. It is called automatically:

- before every LLM call by the coding agent, and
- before every tool round by the tool-calling loop.

The rules: keep the system message and the newest exchange; drop oldest tool-use rounds
first, then oldest plain exchanges; never leave a `tool` result without its assistant
tool-call. Compaction reports progress (`Compacting conversation history (...) tokens...`)
through the agent's `progress_callback`.

Without any `CONTEXT_SIZE`, requests simply omit `max_completion_tokens` and compaction
falls back to a 65536-token window constant — the system still works, it just cannot
prove the fit.
