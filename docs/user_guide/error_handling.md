# Error Handling

**Domain concept:** the framework's failure taxonomy.

**Lives in:** `dandy/shared/exceptions.py` (the hierarchy) plus a per-subsystem
`exceptions.py` that extends it.

## Four branches, one base

```text
DandyError
├── DandyConfigurationError   # settings/config is wrong: fix the config, not the call
├── DandyUsageError           # bad arguments or API misuse: fix the call site
├── DandyExternalError        # something outside Dandy failed: network, LLM, disk, time
└── DandyFlowError            # flow control, not a fault (user stop)
```

The branch names **what is wrong**, not whether you can retry. Retry-ability is
a policy you apply — an external error is usually worth a retry, a usage error
usually isn't — but the hierarchy tells you where to look:

- **Configuration** means the settings are invalid or missing. Fix the settings
  file. Examples: a missing `LLM_CONFIGS.DEFAULT` entry, a settings module that
  cannot be imported (`DandyConfigurationError` raised from `dandy/shared/settings/`).
- **Usage** means the calling code passed a bad argument or misused the API. Fix
  the call site. Examples: a tool missing its `name` (`ToolUsageError`), a
  required service attribute unset (`ServiceConfigurationError` — the config of
  the *service wiring*), include+exclude used together on an Intel
  (`IntelUsageError`), a `Bot` missing a prompt (`ValueError` from `process`).
- **External** means Dandy did its part and something else failed: the network,
  the LLM's answer, the disk, the clock. Examples: an HTTP round trip failing
  after retries (`HttpConnectorError`), a future timing out
  (`FutureExternalError`), a decision returning too many or no keys
  (`DecisionTooManyChoicesExternalError` / `DecisionNoChoicesExternalError`), a
  tool loop exhausting a finite iteration cap (`LlmExternalError`), a session
  file that no longer parses (`AgentExternalError`).
- **Flow** means the run was directed to stop; nothing is broken. `RunStoppedError`
  (a `DandyFlowError`) is raised at stop checkpoints when the user asks to stop
  a running turn.

## Subsystem extensions

| Exception | Meaning |
|---|---|
| `IntelUsageError` | include+exclude used together, or unknown field names |
| `LlmUsageError` / `LlmExternalError` | request-construction/validation misuse vs. transient LLM failures |
| `HttpConnectorError` | the HTTP round trip failed after retries |
| `FutureUsageError` / `FutureExternalError` | non-positive timeout vs. timeout exceeded |
| `ServiceConfigurationError` | a required service attribute was `None` at class creation |
| `ToolUsageError` | a tool descriptor is missing its `name` |
| `CacheUsageError` | an unhashable cache argument |
| `FileUsageError` / `FileExternalError` | bad paths / bad media input vs. file-system failures |
| `RecorderUsageError` | recording misused (e.g. rendering while not recording) |

## How failures move through the system

1. **Validation errors are not exceptions to you.** A wrong-shape LLM response becomes a
   re-prompt (up to `prompt_retry_count`); only exhaustion surfaces as an error.
2. **External errors propagate** so *you* decide the retry policy (or use a
   `*_future` variant and let the timeout be the policy).
3. **Usage errors raise at the earliest possible moment** — class creation, argument
   validation, or the first invalid operation — with a message that names the object.
4. LLM errors quote the **settings module name**, because "your `LLM_CONFIGS` is not set"
   is a configuration fact about a specific file; fix that file, not the call site.
