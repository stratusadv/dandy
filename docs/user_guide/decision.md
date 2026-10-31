# Decision

**Domain concept:** [Decision](../domain_model/glossary.md#glossary) — a bounded
decision: the model picks from a declared answer space.

**Lives in:** `dandy/application/decision/` (the use case and its service; the value
objects and exceptions sit in the domain at `dandy/domain/decision/`).

## The industry shape

"Pick one of these" is the most common classification-shaped LLM task, and free-text
answers make it brittle. The 2026 **decision model** category (the Decisions APIs from
OpenAI, TypeSafe Jev, Microsoft Decision-1, Perplexity, and Liquid AI) names the shape
`decision = f(state, question, allowed answers)`: evidence in, one bounded judgment, a
finite developer-declared answer space out. Dandy's `Decision` is that shape implemented
over a standard OpenAI-compatible chat-completions endpoint — same vocabulary, with one
honest difference: a generic chat endpoint has no decision head, so Dandy does not emit
per-option probabilities or a confidence score.

| Industry term | In Dandy |
|---|---|
| State | the `prompt` (plus the conversation the LLM service carries) |
| Question | `keys_description` — the bounded judgment being asked |
| Options / allowed answers + criteria | `keys_values` — the key is the option label, the value its criteria |
| The model's choice | the key(s) the model returns, mapped back to your values |
| Answer cardinality | `max_return_values` |

## Using the decision service

Decisions are not standalone components; they hang off the LLM service:

```python
value = bot.llm.decision.prompt_to_value(
    'This product is wonderful!',
    keys_description='sentiment of this review',
    keys_values={
        'positive': 'positive sentiment',
        'negative': 'negative sentiment',
        'neutral': 'neutral sentiment',
    },
)
print(value)  # 'positive sentiment'
```

`prompt_to_values` returns the full selection (`max_return_values` caps how many
options may come back); `prompt_to_value` wraps it to a single value. `*_future`
variants run on the thread pool.

## Rules the decision enforces

1. **All keys must be strings.** Non-string keys raise `DecisionCriticalError` (values
   can be any type).
2. **The keys are auto-numbered 1..n** in the prompt, and the model returns the number
   it chose; the framework validates it against the declared answer space.
3. **Retry with a reason.** An empty selection raises
   `DecisionNoChoicesRecoverableError` and a too-long one raises
   `DecisionTooManyChoicesRecoverableError` — each re-prompts the model with a specific
   instruction until `prompt_retry_count` is exhausted, then re-raises.
4. **Typed answer space.** `as_enum()` builds a runtime `Enum` from the mapping, so the
   model's choice is validated as an enum member before it is mapped back to your value.
