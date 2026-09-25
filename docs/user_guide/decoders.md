# Decoders

**Domain concept:** [Decoder](../domain_model/glossary.md#glossary) — keyed selection:
the model picks from a set of string keys.

**Lives in:** `dandy/application/llm/decoder/` (the use case and its service; the value
objects and exceptions sit in the domain at `dandy/domain/llm/decoder/`).

## The idea

"Pick one of these" is the most common classification-shaped LLM task, and free-text
answers make it brittle. A `Decoder` hands the model a mapping of string keys to values
and gets back which key it chose — validated.

## Using the decoder service

Decoders are not standalone components; they hang off the LLM service:

```python
decoder = bot.llm.decoder.make_decoder(
    keys_values={
        'positive': 'positive sentiment',
        'negative': 'negative sentiment',
        'neutral': 'neutral sentiment',
    }
)

value = bot.llm.decoder.prompt_to_value('This product is wonderful!', decoder)
print(value)  # 'positive sentiment'
```

`prompt_to_values` returns the full selection; `prompt_to_value` wraps it to a single
value. `*_future` variants run on the thread pool.

## Rules the decoder enforces

1. **All keys must be strings.** Non-string keys raise `DecoderCriticalError` (values can
   be any type).
2. **The keys are auto-numbered 1..n** in the prompt, and the model returns the key it
   chose.
3. **Retry with a reason.** An empty selection raises
   `DecoderNoKeysRecoverableError` and a too-long one raises
   `DecoderToManyKeysRecoverableError` — each re-prompts the model with a specific
   instruction until `prompt_retry_count` is exhausted, then re-raises.

## Enum output

```python
enum = decoder.as_enum()
```

Builds a runtime `Enum` from the mapping, so the result is type-safe in your code.
