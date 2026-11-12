# Guard chain and dandy_hash

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-11-20-03

## End State

The tool loop runs a pluggable `Guard` chain (repeat guard + context-pressure guard)
that course-corrects live and fails fast on identical repeated failures; a shared
`HashMixin` gives the framework's state classes two-level `shallow_hash()`/`deep_hash()`
digests (overriding the built-in `__hash__`), and the caching system and the repeat
guard both consume those digests — verified by a green hermetic suite, `just lint-imports`,
and `just docs-tests`.

## Observable Concern

`Message` and `LlmRequestBody` override `model_dump()` for the wire shape (tool content
collapses to a string, `exclude_none`), so `HashMixin` must hash the **raw field state**
(bypassing those overrides) or two distinct messages can share one "full" hash — this is
the assumption most likely to be wrong and is pinned by a discriminating test
(text message vs image message vs empty tool message must hash differently).

## Current State

Verified facts (step 0):

- **The 10-limit bug** — `RepeatedCallGuard` (`dandy/domain/tool/repeated_call.py`) keeps
  two counters: a signature counter over `(name, canonical args, result)` and a **result
  counter over `(name, result)` across any argument wording** (lines 135-145). Different
  arguments that keep producing the same result accumulate on the result counter and hit
  `REPEATED_CALL_STOP_THRESHOLD = 10` — exactly the reported misbehavior.
- **Guard wiring** — `ToolService.prompt_to_intel` (`dandy/application/tool/service.py:65`)
  builds one `RepeatedCallGuard` per loop; `_process_tool_call` calls
  `guard.observe(name, arguments, result_text)` (line 251) and feeds the (possibly
  note-appended) text back as the tool result. Per-round compaction runs in
  `_compact_history_before_next_round` (lines 146-178) against
  `COMPACTION_TRIGGER_RATIO = 0.80` / `COMPACTION_TARGET_RATIO = 0.70`
  (`dandy/domain/message/compaction.py`).
- **Compaction failure** — `compact_message_history` silently gives up when nothing
  droppable remains. `Agent.turn` catches the consequence via `_ensure_history_fits`
  (`dandy/application/agent/agent.py:125-144`, raises `AgentRecoverableError`), but a raw
  `bot.llm.tools.prompt_to_intel` loop has no such check and would send a 400-bound request.
- **Hashing today** — Pydantic 2.14.2 `BaseModel` instances are **unhashable** (verified:
  `hash(M())` raises `TypeError`), so `Message`, `MessageHistory`, `BaseIntel` subclasses,
  `LlmOptions`, and `LlmRequestBody` all lack `__hash__`. `Message`/`MessageHistory`
  (`dandy/domain/message/message.py:58,167`) are plain `BaseModel`; `Message` and
  `LlmRequestBody` override `model_dump()` for the wire shape; `ToolCallIntel` is a
  `BaseIntel` with `name`/`arguments: str`/`id`.
- **Caching** — `generate_cache_key` + `convert_to_hashable_str`
  (`dandy/infrastructure/cache/key.py`) hash `str(obj.model_dump())` for any `BaseModel`
  (layer limit 3), `str(obj.__class__.__qualname__)` for anything with
  `recorder_event_id`, `__dict__` otherwise. Tests in
  `tests/infrastructure/cache/test_cache_hashing.py`.
- **Guard tests/docs** — `tests/application/tool/test_service.py::TestRepeatedCallGuard`
  (line 789+) is the only test coverage; `RepeatedCallGuard` is exported from
  `dandy/domain/tool/__init__.py` and documented in `AGENTS.md` (tool-calling bullet),
  `docs/user_guide/tool_calling.md:64`, `docs/reference/domain.md:206` (mkdocstrings
  directive), and `docs/changelog/v3.md:188`.
- **Style** — one class per module, domain imports only shared, `unittest.TestCase` with
  fakes in nested `intelligence/` dirs, ruff ALL + single quotes + 100 cols, docs are a
  CI gate (`just docs-tests`, mkdocstrings member lists must stay in sync).

## Plan

1. `HashMixin` in the shared kernel
   - New `dandy/shared/hashing.py`: a `canonicalize(value, shallow)` helper (sorted keys,
     whitespace-folded strings, sha256 truncated to 32 hex chars) and `HashMixin` with
     `shallow_hash() -> str` (class qualname + scalar fields, containers reduced to
     type+length — cheap, for high-volume counting), `deep_hash() -> str` (class qualname +
     full recursively canonicalized state — the true duplicate detector), and
     `__hash__()` returning `hash(self.deep_hash())` (the built-in override; pydantic
     models are unhashable today, so this adds content-based identity everywhere).
     `hash_state()` returns `model_dump(mode='json')` for pydantic models and `vars(self)`
     otherwise; `Message` overrides it to bypass the wire-shape `model_dump` (same
     `super()` pattern `LlmRequestBody` uses) so hashing sees raw content lists.
   - Apply the mixin: `Message`, `MessageHistory` (domain/message), `BaseIntel`
     (domain/intel — every Intel inherits), `LlmOptions` + `LlmRequestBody`
     (domain/request), `BaseTool` (domain/tool), `LlmConfig`
     (infrastructure/llm — resolved model/host/port/context_size identity).
   - Export `HashMixin` from the `dandy` root (thin re-export) so user classes outside the
     Intel hierarchy can opt in.
   - Hermetic `tests/shared/test_hashing.py` including the Observable-Concern discriminator
     (text vs image vs empty tool message) and the mutation-changes-deep-hash check.
   - Done when all listed classes are hashable, `deep_hash` is stable across equal state
     and changes on any state change, `shallow_hash` is coarser, and the new tests pass
     under both pytest and unittest.

2. Wire `deep_hash` into the caching system
   - `convert_to_hashable_str` (`dandy/infrastructure/cache/key.py`) prefers
     `obj.deep_hash()` for any object exposing it (checked before the `BaseModel` branch);
     non-mixin objects keep today's layered behavior. `generate_cache_key` is unchanged in
     shape.
   - Update `tests/infrastructure/cache/test_cache_hashing.py` to pin the new behavior
     (mixin objects key by deep hash; layer limit still bounds non-mixin nesting).
   - Done when cache keys for framework state objects are derived from `deep_hash` and the
     cache suite passes; key-format change (an invalidation of any pre-existing sqlite
     cache file) is noted in the changelog.

3. The `Guard` middleware chain (domain)
   - New `dandy/domain/tool/guard.py`: `GuardEvent` (frozen dataclass: tool name, shallow
     signature, deep signature, result text, round number, history token count, context
     window), `GuardOutcome` (dataclass: `note` steering text, `compact` flag, `failed`
     flag + failure message), `Guard` base (per-signature `_correction_counts` — a
     signature that re-trips after a correction was already issued counts as an identical
     failure; `observe(event) -> GuardOutcome`), and `GuardChain` (ordered guards;
     `on_round_start(...)` for compaction decisions, `on_tool_call(...) -> str` returning
     the result text with any guard notes appended; a failed outcome raises
     `LlmRecoverableError` naming the guard, so existing CLI/Agent handling is untouched).
   - New `dandy/domain/tool/repeat_guard.py`: `RepeatGuard` converts the current
     `RepeatedCallGuard` — **args-only counting** (the result counter is deleted), counting
     the shallow signature at volume and computing the deep signature only when the shallow
     count crosses the warning threshold, steering or stopping only on a confirmed
     identical deep signature; keeps `REPEATED_CALL_WARNING_THRESHOLD = 3` and
     `REPEATED_CALL_STOP_THRESHOLD = 10` and the steering-note wording (minus the
     result-counter note). `canonical_tool_arguments` moves here.
   - New `dandy/domain/tool/context_guard.py`: `ContextPressureGuard` — on round start,
     requests compaction when the estimate passes `COMPACTION_TRIGGER_RATIO`; when the
     estimate still exceeds the **whole** window after a prior compaction (compaction
     exhausted everything droppable), it fails the loop instead of letting the provider
     400. This is the "identical failures in a row → fail" pattern applied to compaction.
   - Delete `dandy/domain/tool/repeated_call.py`; `dandy/domain/tool/__init__.py` exports
     `Guard`, `GuardChain`, `GuardEvent`, `GuardOutcome`, `RepeatGuard`,
     `ContextPressureGuard` (and keeps `canonical_tool_arguments`).
   - Hermetic `tests/domain/tool/test_guard.py` (chain mechanics, identical-failure stop,
     compaction-request path, over-window failure path) and
     `tests/domain/tool/test_repeat_guard.py` (args-only: different args / same result /
     15 calls never trips; identical args steer at 3 and stop at 10; whitespace/key-order
     drift still accumulates; a shallow collision with a different deep signature does not
     steer).
   - Done when the unit suites pass and no module outside domain/tool imports the deleted
     file (grep clean; `just lint-imports` green — all new edges stay inside
     domain → shared).

4. Wire the chain into the tool loop
   - `ToolService.prompt_to_intel` builds `GuardChain([RepeatGuard(), ContextPressureGuard()])`
     per loop (replacing the bare `RepeatedCallGuard()`); `on_round_start` drives the
     existing compaction (the service still calls `compact_message_history` and emits the
     story beat — guards decide, the service acts); `_process_tool_call` takes the chain
     and uses `on_tool_call` for the feedback text; a failed guard raises before the next
     HTTP call.
   - Update `tests/application/tool/test_service.py`: convert
     `TestRepeatedCallGuard` to the chain, add the bug-case test (distinct arguments,
     identical result, >10 rounds → loop completes, no steering notes), and add the
     over-window-after-compaction failure test (mocked history estimate, no HTTP).
   - Done when the bug case passes, every pre-existing loop/compaction/beat assertion still
     passes, and verbose/progress output is unchanged apart from the guard lines.

5. Docs and the record
   - `AGENTS.md`: rewrite the repeated-call portion of the tool-calling bullet (args-only
     guard, the chain, the context-pressure guard), the caching bullet (deep-hash keys),
     and the public API bullet (new root export `HashMixin`); add the hashing design to the
     environment/settings or caching section where the token/calibration prose lives.
   - `docs/user_guide/tool_calling.md` (guard section), `docs/user_guide/caching.md`,
     `docs/reference/domain.md` (replace the `RepeatedCallGuard` directive with the new
     guard modules), `docs/reference/shared.md` (hashing module), and a
     `docs/changelog/v3.md` entry.
   - Done when `just docs-tests` (mkdocs `--strict`) passes and AGENTS.md matches the
     implemented behavior.

## Completion Test

1. `just test` — full hermetic suite green (both pytest parity and fast).
2. `python -m unittest discover -t . ./tests -q` — CI's runner green.
3. Targeted: `just test-app tests/shared/test_hashing.py tests/domain/tool tests/application/tool/test_service.py tests/infrastructure/cache`
   — the new bug case (different args / same result / >10 calls → no stop) must pass, and
   the identical-call stop-at-10 test must still pass.
4. `just lint-imports && ruff check . && ruff format --check .` — clean.
5. `just docs-tests` — mkdocs strict build green.
6. Smoke: a quick REPL one-shot (`just cli` style manual turn is optional; the hermetic
   multi-turn `CliAgent` tests already assert loop behavior) — rely on the hermetic
   agent/CLI tests as the smoke.

## Deviations

1. The guard package lives at `dandy/domain/guard/` (not `dandy/domain/tool/` as
   step 3 wrote): a user redirect ("the whole guard system should be in its own
   module not tool") moved `guard.py`, `repeat_guard.py`, and `context_guard.py`
   into the new `dandy/domain/guard/` package, with the tests at
   `tests/domain/guard/` (step 3's test paths and completion-test step 3's
   `tests/domain/tool` target mean `tests/domain/guard` accordingly).
   `dandy/domain/tool/__init__.py` reverted to its original exports;
   `dandy/domain/tool/repeated_call.py` was deleted as planned. `GuardOutcome`
   carries a `failure_message` field rather than a `failed` flag.
2. `RepeatGuard` computes the full signature (tool name plus a digest of the
   exact canonical arguments) on every call, not only after the shallow count
   crosses the warning threshold: the cost equals the per-call canonicalization
   the old guard already performed, and it keeps the exact legacy thresholds
   (steer at the 3rd, stop at the 10th) without a second-pass re-scan.
3. `HashMixin` does not override `__eq__`: pydantic's field equality already
   gives semantically correct equality (and an override would break set
   deduplication for whitespace-different objects); duplicate detection compares
   `deep_hash()` directly, and `__hash__` derives from the deep hash as planned.
4. `ContextPressureGuard` requests compaction at most once per pressure episode
   (the flag clears when the estimate settles back under the trigger), so a loop
   whose rounds keep re-adding what compaction just dropped does not re-compact
   every round; it fails the loop only when the pressure re-asserts after an
   issued compaction and the conversation still exceeds the whole window.
5. The shallow signature is no longer counted by `RepeatGuard`: once the full
   signature is computed on every call (deviation 2), the shallow counter has
   no consumer, so `_shallow_counts` / `_count_shallow` were dropped and the
   guard counts every call by full signature alone. The shallow level itself
   (`canonicalize(shallow=True)`, `canonical_tool_arguments(shallow=True)`,
   `shallow_hash`) stays in the shared kernel and is exported, just not
   maintained as a per-loop counter.
