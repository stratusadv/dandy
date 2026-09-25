# Error Handling

**Domain concept:** the framework's failure taxonomy.

**Lives in:** `dandy/shared/exceptions.py` (the hierarchy) plus a per-subsystem
`exceptions.py` that extends it.

## Two branches, one base

```text
DandyError
├── DandyCriticalError      # programming error: fail fast, do not retry
└── DandyRecoverableError   # transient: retry or fall back
```

The branch is a **semantic contract**, not a severity label:

- **Critical** means "this cannot be fixed by waiting or retrying — the code or
  configuration is wrong." Examples: a tool missing its `name`
  (`ToolCriticalError`), a required service attribute unset
  (`ServiceCriticalError`), a decoder given non-string keys
  (`DecoderCriticalError`), a `Bot` missing a prompt (`ValueError` from `process`).
- **Recoverable** means "the operation can succeed on a later attempt." Examples: an HTTP
  round trip failing (`HttpConnectorRecoverableError`), a future timing out
  (`FutureRecoverableError`), a decoder returning too many or no keys
  (`DecoderToManyKeysRecoverableError` / `DecoderNoKeysRecoverableError`), a tool loop
  exhausting a finite iteration cap (`LlmRecoverableError`).

## Subsystem extensions

| Exception | Meaning |
|---|---|
| `IntelCriticalError` | include+exclude used together, or unknown field names |
| `LlmCriticalError` / `LlmRecoverableError` | request-construction/validation vs. transient LLM failures |
| `HttpConnectorRecoverableError` | the HTTP round trip failed after retries |
| `FutureCriticalError` / `FutureRecoverableError` | non-positive timeout vs. timeout exceeded |
| `ServiceCriticalError` | a required service attribute was `None` at class creation |
| `ToolCriticalError` | a tool descriptor is missing its `name` |
| `CacheCriticalError` | an unhashable cache argument |
| `FileCriticalError` / `FileRecoverableError` | missing paths / transient file failures |
| `RecorderCriticalError` | recording misused (e.g. rendering while not recording) |

## How failures move through the system

1. **Validation errors are not exceptions to you.** A wrong-shape LLM response becomes a
   re-prompt (up to `prompt_retry_count`); only exhaustion surfaces as an error.
2. **Recoverable errors propagate** so *you* decide the retry policy (or use a
   `*_future` variant and let the timeout be the policy).
3. **Critical errors raise at the earliest possible moment** — class creation, argument
   validation, or the first invalid operation — with a message that names the object.
4. LLM errors quote the **settings module name**, because "your `LLM_CONFIGS` is not set"
   is a configuration fact about a specific file; fix that file, not the call site.
