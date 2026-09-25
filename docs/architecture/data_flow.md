# Anatomy of an LLM Call

What happens between `bot.process('...')` and the validated Intel in your hand — and
which layer owns each step.

## The pipeline

```text
Bot.process(prompt, intel_class=..., include/exclude=..., intel_object=...)
  │  application: the use case
  ▼
LlmService.prompt_to_intel
  │  application: options, history, diligence wiring
  ▼
LlmConnector.prompt_to_intel
  │  infrastructure: the port's implementation
  │
  │  1. build LlmRequestBody
  │       - system message (prepended only if the history does not
  │         already lead with one — diligence instructions merge
  │         into that leading message)
  │       - your prompt as a user message
  │  2. build the JSON schema from the Intel type
  │       (IntelFactory.intel_to_json_inc_ex_schema, trimmed by
  │        include_fields / exclude_fields)
  │  3. run pre-diligence handlers
  ▼
HttpConnector.request_to_response
  │  infrastructure: the actual HTTP, retried
  ▼
  │  4. run post-diligence handlers
  │  5. IntelFactory.json_str_to_intel_object
  │       validates the response into your Intel
  │  6. pydantic ValidationError?
  │       re-prompt with the validation errors
  │       (up to prompt_retry_count, default 2)
  ▼
Your validated Intel
```

## Ownership table

| Step | Layer | Module |
|---|---|---|
| Prompt assembly | domain | `dandy/domain/llm/prompt/` |
| Request body, messages, history | domain | `dandy/domain/llm/request/` |
| Intel → JSON schema, response → Intel | domain | `dandy/domain/intel/factory.py` |
| Options, retry policy, diligence orchestration | application | `dandy/application/llm/service.py` |
| Endpoint config, URL, diligence handlers | application / infrastructure | `dandy/application/llm/diligence/`, `dandy/infrastructure/llm/` |
| HTTP transport | infrastructure | `dandy/infrastructure/http/` |
| Events along the way | infrastructure | `dandy/infrastructure/recorder/` |

## Behaviors that surprise people (and why they exist)

- **Fenced-JSON recovery.** Live models often wrap their final JSON in markdown fences.
  When the response contains exactly one fenced block whose body validates against the
  target Intel, the connector uses it as the answer. Multiple fences or a non-validating
  body changes nothing — you get the normal retry path.
- **Prose tolerance for `DefaultIntel`.** When the target is the "whatever the model
  said" model and the response is unparseable prose, the raw text lands in
  `DefaultIntel.text` instead of raising. Agent REPLs answer free-form questions because
  of this one fallback.
- **Tools clear strict mode.** Passing `tools` clears `response_format` on the request —
  strict response_format plus non-strict tools is a 400 error on OpenAI. The final answer
  is still validated locally by the Intel retry loop.
- **Context is bounded by design.** `CONTEXT_SIZE` on the LLM config drives the derived
  `max_completion_tokens` (20% of the window). Long sessions compact the history to 70%
  of the window before every call, leaving a 10% margin — so input plus output fits by
  construction. See [Options and Context](../user_guide/options_and_context.md).
- **Strict endpoints are respected.** vLLM/litellm reject a second or trailing system
  message, so the connector never adds one where the history already leads with one.
