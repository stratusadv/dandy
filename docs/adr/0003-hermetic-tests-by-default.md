# 0003. Hermetic test suite by default

Status: Accepted
Date: 2026-09-25

## Context

A meaningful slice of the behavior is only observable against a live LLM
endpoint, which needs real host/key secrets. A suite that requires secrets
fails on every contributor laptop, and secrets are not available in every CI
context. Worse, live-LLM tests are slow and nondeterministic; letting them run
by default poisons trust in the whole suite, so people stop running it.

## Decision

The default suite is fully hermetic. `tests/dandy_settings.py` (the settings
module under test, selected via `DANDY_SETTINGS_MODULE`) fills `LLM_CONFIGS`
with placeholder values so configs validate without a live endpoint. Live-LLM
tests are decorated (`@live_llm_test`, `@run_llm_configs`) and skip unless
`AI_API_KEY` is set to a real, non-placeholder key. Hermetic LLM-dependent unit
tests mock at the connector boundary
(`HttpConnector.request_to_response`), returning canned `HttpResponseIntel`s,
so the domain and application layers are exercised with real objects.

## Consequences

- `just test` passes on any machine with no secrets; the suite is fast enough
  that people actually run it.
- Live coverage runs only in CI, where the secrets are injected as workflow
  env; a missing key never fails a local run.
- The mocking discipline is concentrated at the HTTP boundary, which is the
  seam the architecture already guarantees.
- Cost: regressions that only show up with a real model (prompt wording,
  response formatting) surface in CI, not locally, and live tests are treated
  as potentially flaky by design.
