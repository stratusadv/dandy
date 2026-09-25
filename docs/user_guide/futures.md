# Futures

**Domain concept:** [Future](../domain_model/glossary.md#glossary) — the framework's
concurrency primitive: a callable on a shared thread pool, with a timeout.

**Lives in:** `dandy/infrastructure/future/`.

## Run a callable off the calling thread

```python
from dandy import process_to_future


def add(a: int, b: int) -> int:
    return a + b


future = process_to_future(add, 1, 2)
print(future.get_result(timeout_seconds=5))   # 3
```

(Verified: the callable runs on a worker thread; `get_result` blocks up to the timeout
and returns the value.)

- The pool is module-level with `FUTURES_MAX_WORKERS` workers (from settings).
- Timeout exceeded ⇒ `FutureRecoverableError`; a non-positive timeout ⇒
  `FutureCriticalError`.
- `future.cancel()`, `future.cancelled()`, `future.done()` track the worker's state;
  `future.result` is the result property once complete; `future.set_timeout(seconds)`
  adjusts the wait.

## LLM-specific futures

Every LLM-facing call has a `*_future` variant that returns an `AsyncFuture` instead of
blocking:

- `bot.process_to_future(...)`
- `bot.llm.prompt_to_intel_future(...)`
- `bot.llm.decoder.prompt_to_values_future(...)`

Fan out several calls and collect them in your own order — the futures do not impose one:

```python
futures = [bot.process_to_future(p) for p in prompts]
results = [f.get_result(timeout_seconds=60) for f in futures]
```
