# Rename Decoder to Decision (industry alignment)

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed (user sign-off: "do it")
- Date: 2026-10-30-18-53

## End State

Every `decoder`/`Decoder` symbol in the codebase is renamed to `decision`/`Decision` per the mapping in Current State: `dandy/domain/decision/` and `dandy/application/decision/` replace the `decoder/` packages, `dandy/infrastructure/recorder/decision_events.py` replaces `decoder_events.py`, the property is `bot.llm.decision`, the 6 import-linter seams name the new modules, tests mirror the rename, the glossary and user guide define the concept with the industry's decision vocabulary, and the full 476-test suite passes under both pytest and unittest discover with the 90% coverage gate, all 6 import-linter contracts, and the strict mkdocs build green.

## Research (why "Decision")

A product class now exists for exactly what the Decoder does: **decision models** exposed via **Decisions APIs** (2026). Small, fast, specialized models whose job is one bounded judgment — choosing among a finite, developer-declared answer space — consumed as a decision signal, not prose. Concrete products: OpenAI Decisions API (`POST /v1/decisions`, DevDay 2026-09-29), TypeSafe Jev ("System One"), Microsoft Decision-1 (Foundry), Perplexity Decisions API, Liquid AI d1; benchmarked on JevBench / Decision Index. The industry's canonical vocabulary:

- **Decision model** — the model; **bounded decision** — a decision with a finite declared answer space.
- **State** — the evidence; **Question** — the single bounded judgment; **Choice / options / allowed answers** — the finite candidate set; **Criteria** — the description attached to each option.
- **Score** (ordered rubric) and **Predicate / Boolean / Noul** (yes/no) — the other answer types; **Probability** + **Confidence** — distribution over options and overall confidence.
- **Decision layer** — layer 3 of the agent stack (orchestrator → generative model → decision layer → policy → action); **decision trace** — the inspectable record of evidence, question, options, answer, outcome.

Dandy's Decoder is a bounded decision: `keys_values` = options with criteria, `keys_description` = the question, the returned key = the model's choice, `max_return_values` = answer cardinality, `as_enum()` = the typed answer space, the no-keys/too-many retry loop = answer-space enforcement. Differences we do NOT paper over: Dandy runs over a generic OpenAI-compatible chat endpoint, so it does not emit probabilities/confidence (no decision-model head) — the docs say so explicitly. "Decoder" is the old constrained-decoding coinage; "Decision" is the current industry term.

## Current State

Verified on branch `v3/base` (working tree carries the executed concise-ddd-renames plan; nothing committed by this plan):

- **Domain** `dandy/domain/decoder/` (all `__init__.py` empty): `intel.py` (`DecoderKeyIntel` `key: T` generic, `DecoderKeysIntel` `keys: list[T]`, `DecoderValuesIntel` `values: list[Any]`), `exceptions.py` (`DecoderCriticalError`, `DecoderRecoverableError`, `DecoderNoKeysRecoverableError`, `DecoderToManyKeysRecoverableError`), `prompts.py` (`decoder_guidelines_prompt`, `decoder_max_key_count_error_prompt`, `decoder_no_key_error_prompt`).
- **Application** `dandy/application/decoder/`: `decoder.py` (`Decoder`: `keys_description`, `keys_values`, `__getitem__`, `as_enum()`, `process()`, private prompt/validate helpers), `service.py` (`DecoderService(BaseService['dandy.application.decoder.mixin.DecoderServiceMixin'])`: `prompt_to_value(s)`, `*_future`, `options` property, `reset()`), `mixin.py` (`DecoderServiceMixin` with property `decoder` + `reset()` chaining `self.decoder.reset()`). `LlmService` MRO: `BaseService, DecoderServiceMixin, DiligenceServiceMixin, ToolServiceMixin`; the decoder service is deliberately not reset (its `reset()` is a no-op).
- **Recorder** `dandy/infrastructure/recorder/decoder_events.py`: `recorder_add_process_decoder_value_event`, `recorder_add_chosen_values_event`, `_EVENT_OBJECT_NAME = 'Decoder Service'`, TYPE_CHECKING import of `Decoder`.
- **Importers of domain decoder symbols**: `application/decoder/{decoder,service}.py`, `tests/domain/decoder/test_decoder.py` (1 test class) + fixture `tests/domain/decoder/intelligence/decoders.py` (`FunDecoderBot`).
- **Importers of application decoder symbols**: `application/llm/service.py` (MRO + import), `tests/application/bot/test_reset_chain.py` (`bot._DecoderService_instance` cache attr, `bot.llm.decoder.reset()`), `tests/application/bot/test_bot_instances.py` (`bot.llm.decoder.prompt_to_values` ×4), book example `tests/application/example_project/book/{intelligence/decoders.py (BookThemeDecoderBot), workflow.py}`.
- **6 pyproject seam edges** naming decoder modules: `dandy.infrastructure.recorder.decoder_events -> dandy.application.decoder.decoder`; `dandy.application.decoder.decoder -> dandy.infrastructure.llm.connector` / `-> recorder.decoder_events` / `-> recorder.llm_events`; `dandy.application.decoder.service -> dandy.infrastructure.future.future` / `-> future.process`.
- **Docs**: `docs/domain_model/glossary.md` ("### Decoder" + anti-language table), `docs/domain_model/tactical.md` (2 lines), `docs/domain_model/contexts.md` (2 lines), `docs/reference/application.md` (## Decoder + 3 directives), `docs/reference/domain.md` (heading + 2 directives), `docs/user_guide/decoders.md`, `mkdocs.yml` nav line 50 (`Decoders: user_guide/decoders.md`), `docs/migration/v2_to_v3.md` (v2 `dandy.llm.decoder.*` rows + sed line), `AGENTS.md` (package map line 71, seams line 87, package-map line 94, Reset chain line 119, "### Decoder" section lines 173-178, gotcha 5 line 231), `docs/changelog/v3.md` (v3.1.0 "holds exactly ... decoder" line).
- **Pre-existing docs bug**: `user_guide/decoders.md:20` shows `bot.llm.decoder.make_decoder(...)` — no `make_decoder` exists anywhere in the codebase (verified by grep); the guide is stale. The rewrite fixes the example to the real API (`prompt_to_value(s)`).
- **House conventions**: same-basename module (`decision/decision.py`), empty `__init__.py`, tests mirror packages, `ruff` no-new-findings gate (baseline 648 errors / 155 format files from the previous plan), Sphinx docstrings, single quotes.

## Rename map

| Now | To |
|---|---|
| `dandy/domain/decoder/` | `dandy/domain/decision/` |
| `DecoderKeyIntel` / `DecoderKeysIntel` | `DecisionChoiceIntel` / `DecisionChoicesIntel` (the model's *choice*) |
| `DecoderValuesIntel` | `DecisionValuesIntel` (resolved outcomes stay "values") |
| `DecoderCriticalError` / `DecoderRecoverableError` | `DecisionCriticalError` / `DecisionRecoverableError` |
| `DecoderNoKeysRecoverableError` / `DecoderToManyKeysRecoverableError` | `DecisionNoChoicesRecoverableError` / `DecisionTooManyChoicesRecoverableError` (fixes the "ToMany" typo) |
| `decoder_guidelines_prompt` / `decoder_max_key_count_error_prompt` / `decoder_no_key_error_prompt` | `decision_guidelines_prompt` / `decision_too_many_choices_error_prompt` / `decision_no_choices_error_prompt` |
| `dandy/application/decoder/` | `dandy/application/decision/` |
| `Decoder` / `DecoderService` / `DecoderServiceMixin` | `Decision` / `DecisionService` / `DecisionServiceMixin` |
| `bot.llm.decoder` (property) | `bot.llm.decision` — the one user-visible API break in this rename |
| `dandy/infrastructure/recorder/decoder_events.py` | `decision_events.py` |
| `recorder_add_process_decoder_value_event` | `recorder_add_process_decision_value_event` (`recorder_add_chosen_values_event` unchanged) |
| `_EVENT_OBJECT_NAME = 'Decoder Service'` | `'Decision Service'` |
| `tests/domain/decoder/` (+ `intelligence/decoders.py` `FunDecoderBot`) | `tests/domain/decision/` (+ `intelligence/decisions.py`, `FunDecisionBot`) |
| `BookThemeDecoderBot` (+ `book/intelligence/decoders.py`) | `BookThemeDecisionBot` (+ `book/intelligence/decisions.py`) |
| pyproject 6 decoder seam edges | rewritten 1:1 to the `decision` modules |

Deliberately NOT renamed (documented as options/criteria in the glossary instead): the `keys_values` / `keys_description` parameter and attribute names (public API; `options` would collide with `DecisionService.options` / `LlmOptions`), the `prompt_to_value(s)` methods, `as_enum()`, and `max_return_values`. No probability/confidence fields — Dandy has no decision-model head (stated in the docs).

## Observable Concern

The `bot.llm.decoder` → `bot.llm.decision` property rename is the only user-visible break, and it is pinned by `tests/application/bot/test_reset_chain.py` through the `_DecoderService_instance` cache attribute and the `super().reset()` chain — a missed re-point there (or in the `BaseService['...mixin.DecoderServiceMixin']` string annotation in `decision/service.py`) breaks the reset-chain tests or service instantiation. Secondary: the 6 import-linter seam edges must be rewritten in lockstep with the module moves or `lint-imports` fails.

## Plan

1. **Baseline re-check**
   - Hermetic pytest, clean-env unittest discover, `lint-imports`; expect 447/29, 476 OK, 6 kept.
   - Done when all three report baseline counts.
2. **Rename `dandy/domain/decoder/` -> `dandy/domain/decision/`**
   - Move the package (empty `__init__.py`), apply the domain-row renames of the map (intel classes, exceptions, prompt functions), re-point importers (`application/decoder/{decoder,service}.py`), move `tests/domain/decoder/` -> `tests/domain/decision/` incl. `intelligence/decoders.py` -> `decisions.py` + `FunDecoderBot` -> `FunDecisionBot` + the 1 test class name.
   - Done when suite green (both runners), `grep -rn 'domain\.decoder\|domain/decoder\|DecoderKey\|DecoderValue\|DecoderNo\|DecoderToMany\|decoder_guidelines\|decoder_no_key\|decoder_max_key' dandy tests` -> zero hits.
3. **Rename `dandy/application/decoder/` -> `dandy/application/decision/`**
   - Move the package (`decision/decision.py` same-basename convention), rename `Decoder`/`DecoderService`/`DecoderServiceMixin`, the `decoder` property -> `decision` (reset chain `self.decision.reset()`), the `BaseService['dandy.application.decision.mixin.DecoderServiceMixin'->'...DecisionServiceMixin']` string annotation, re-point `application/llm/service.py` (import + MRO), `tests/application/bot/test_reset_chain.py` (`_DecoderService_instance` -> `_DecisionService_instance`, `bot.llm.decoder` -> `bot.llm.decision`), `tests/application/bot/test_bot_instances.py` (`bot.llm.decoder` ×4).
   - Done when suite green (both runners, reset-chain tests pass), `grep -rn 'application\.decoder\|application/decoder\|DecoderService\|Decoder\b' dandy tests` -> zero hits.
4. **Rename `recorder/decoder_events.py` -> `decision_events.py` + seams**
   - Move the module, rename `recorder_add_process_decoder_value_event`, `_EVENT_OBJECT_NAME` -> `'Decision Service'`, re-point `application/decision/decision.py` (runtime import + TYPE_CHECKING `Decoder` -> `Decision`); rewrite the 6 pyproject seam edges 1:1.
   - Done when suite green, `lint-imports` -> 6 kept 0 broken, `grep -rn 'decoder_events\|recorder_add_process_decoder' dandy tests pyproject.toml` -> zero hits.
5. **Rename book example fixtures**
   - `tests/application/example_project/book/intelligence/decoders.py` -> `decisions.py`, `BookThemeDecoderBot` -> `BookThemeDecisionBot`, re-point `book/workflow.py`.
   - Done when suite green (both runners), `grep -rn 'Decoder\|decoders\.' tests/application/example_project` -> zero hits.
6. **Docs, AGENTS.md, changelog, nav**
   - `docs/user_guide/decoders.md` -> `decision.md`: rewrite with the decision vocabulary (state / question / options + criteria / choice; name the 2026 Decisions API category — OpenAI, TypeSafe Jev, Microsoft Decision-1, Perplexity, Liquid AI — and state Dandy's generic-endpoint difference: no probabilities/confidence); fix the stale `make_decoder` example to the real `prompt_to_value(s)` API.
   - `mkdocs.yml` nav `Decoders: user_guide/decoders.md` -> `Decision: user_guide/decision.md`.
   - Glossary: "### Decoder" -> "### Decision" (bounded decision; industry term); anti-language row `Decision | "decoder", "keyed selection", "classifier"`; `tactical.md`, `contexts.md` mentions; `reference/application.md` (## Decision + 3 directives), `reference/domain.md` (heading + 2 directives); `docs/migration/v2_to_v3.md` v3-column targets + sed line; `AGENTS.md` (package map lines 71/94, seams line 87, reset-chain line 119, "### Decoder" section -> "### Decision", gotcha 5); `docs/changelog/v3.md` v3.1.0: update the "holds exactly ... decoder" line and add the rename to the in-progress release's restructure table.
   - Done when `just docs-tests` strict build clean and `grep -rn 'decoder\|Decoder' docs AGENTS.md` returns only the changelog old->new table and the migration v2 left column.
7. **Final verification**
   - Run the completion test, quote real output, set `Status: Executed`.
   - Done when every check passes with unchanged test counts (476 / 29 skipped).

## Completion Test

All run from `/home/nathanj/PycharmProjects/dandy`, all must pass:

1. Hermetic pytest: `AI_API_KEY=test-key PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings .venv/bin/python -m pytest . -q` -> 447 passed, 29 skipped, 0 failed.
2. CI-parity unittest (clean env): `env -i PATH="$PATH" HOME="$HOME" .venv/bin/python -m unittest discover -t . ./tests` -> 476 tests, 0 failures, 29 skipped.
3. Coverage gate: `PYTHONPATH=. AI_API_KEY=placeholder DANDY_SETTINGS_MODULE=tests.dandy_settings .venv/bin/python -m coverage run -m unittest discover -t . ./tests && .venv/bin/python -m coverage report --fail-under=90` -> TOTAL >= 90%, exit 0.
4. Architecture: `lint-imports` -> all 6 contracts KEPT.
5. Docs: `just docs-tests` -> strict mkdocs build clean.
6. Style: `ruff check .` <= 648 errors and `ruff format --check .` reformat count == 155 (no new findings vs the concise-ddd-renames baseline).
7. Old-name grep gates (zero hits over `dandy tests docs AGENTS.md pyproject.toml`, excluding `docs/changelog/v3.md` and `docs/migration/v2_to_v3.md` which intentionally carry old->new mappings): `decoder|Decoder` (case-sensitive), `llm\.decoder`, `recorder_add_process_decoder`, `FunDecoderBot`, `BookThemeDecoderBot`, `_DecoderService_instance`.
8. Structure: `ls dandy/domain` -> `decision intel message prompt request tokens tool`; `ls dandy/application` -> `agent bot diligence llm tool decision`; `ls dandy/infrastructure/recorder` has `decision_events.py` no `decoder_events.py`; `dandy/domain/decoder/` and `dandy/application/decoder/` do not exist.
9. API smoke: `PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings .venv/bin/python -c 'import dandy; b = dandy.Bot(); print(b.llm.decision)'` -> prints the DecisionService instance, exit 0.

## Deviations

1. **Step 2 — fixture import missed the filename rename.** `tests/domain/decision/test_decision.py`
   imported the fixture as `tests.domain.decision.intelligence.decoders` after the fixture
   file was renamed to `decisions.py`; the prefix sed covered `tests.domain.decoder.` ->
   `tests.domain.decision.` but not the module filename. unittest discover silently dropped
   4 tests (472 vs 476). Fixed with one extra sed; count restored to 476.
2. **Step 3 — same-basename module references + a missed class.** `dandy.application.decoder.decoder`
   became `dandy.application.decision.decoder` under prefix sed, but the module is
   `decision.py`; fixed in `application/decision/service.py` and in the recorder's
   TYPE_CHECKING import. `class Decoder:` inside `decision.py` was missed because the file
   did not contain the grep pattern used to build the `grep -rl` file list; fixed directly.
   The retry-event description strings ("Decoder keys intel object...") were also updated
   to "Decision...".
3. **Step 4 — keyword-argument rename at the call site.** After renaming the
   `recorder_add_process_decision_value_event(decoder=...)` parameter to `decision`, the
   call site in `application/decision/decision.py` still passed `decoder=self` -> TypeError
   in 2 retry tests. Fixed to `decision=self`.
4. **Intentional grep-gate exclusion: generated recordings.** `tests/.dandy/recordings/*.html`
   are gitignored generated test artifacts containing stale "Decoder" text. They are
   excluded from the old-name grep gates and not cleaned; the artifacts regenerate on the
   next recording run.
5. **Step 6 — earlier docs sed corrupted the migration doc's v2 column.** The docs sed pass
   had hit `docs/migration/v2_to_v3.md` (it was supposed to be excluded) and rewrote the
   historical 2.x left column (`dandy.llm.decoder.*` -> `dandy.llm.decision.*`). The v2
   layout really was `dandy.llm.decoder.*` (verified against `git ls-tree HEAD` and the
   v3.0.0 package map), so the left column was restored to the real v2 names, and the
   sed one-liner was split so the v2 domain modules (`intel` / `exceptions` /
   `intelligence.prompts`) map to `dandy.domain.decision.*` while the remaining
   `dandy.llm.decoder.*` modules map to `dandy.application.decision.*`.
6. **Step 6 — stale anti-language phrasing in `docs/user_guide/bots.md`.** The service
   table still described `bot.llm.decision` as "keyed selection", which the new glossary
   anti-language row explicitly forbids. Reworded to "a bounded decision over a declared
   answer space".
7. **Step 7 — one new `ruff format` finding from the rewritten user guide.**
   `docs/user_guide/decision.md` (fully rewritten in Step 6) was missing the magic
   trailing comma in its Python example, pushing `ruff format --check` to 156 files.
   Fixed; count back to the 155 baseline. (All other plan-touched Python files were
   verified already unformatted in their pre-rename HEAD versions, i.e. pre-existing
   drift, not introduced by this plan.)
8. **Post-execution live evaluation — Step 3 local-variable rename shadowed a result.**
   The 29 live-LLM tests were then evaluated by running them with the real
   `development.env` key: 56 passed, 1 failed. The failure was
   `tests/application/bot/test_bot_instances.py` — the Step-3 rename of the
   `new_decoder`/`new_decoder_answer` locals to `new_bot`/`new_bot_answer` made the
   `prompt_to_values` result overwrite the `prompt_to_intel` result, so the
   `.text` assertion ran against a `DecisionValuesIntel` (no `text` attribute).
   At HEAD the two results lived in distinct variables. Fixed by giving the four
   decision results their own names (`new_bot_decision`, `another_bot_decision`,
   `alterative_bot_decision`, `end_bot_decision`); the test now passes live and the
   hermetic suite is unchanged (447 passed / 29 skipped). Note: the 9-point
   completion test is hermetic by design and could not catch this — only the live
   run (as CI does with real secrets) does.

## Execution Report

Completion test (all commands run from the repo root, 2026-10-30):

1. `AI_API_KEY=test-key PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings .venv/bin/python -m pytest . -q`
   -> `447 passed, 29 skipped in 4.03s`
2. `env -i PATH="$PATH" HOME="$HOME" .venv/bin/python -m unittest discover -t . ./tests`
   -> `Ran 476 tests in 3.502s` / `OK (skipped=29)`
3. Coverage gate (unittest + `coverage report --fail-under=90`)
   -> `TOTAL   3959   247   94%` (exit 0)
4. `.venv/bin/lint-imports` -> `Contracts: 6 kept, 0 broken.`
5. `just docs-tests` -> exit 0, 0 ERROR lines, `Documentation built in 0.93 seconds`
   (run twice: once before, once after the final doc edits)
6. `.venv/bin/ruff check .` -> `Found 648 errors.` (== baseline); `.venv/bin/ruff format --check .`
   -> `155 files would be reformatted, 242 files already formatted` (== baseline, after
   deviation 7 fix)
7. Old-name grep gates, all zero hits over `dandy tests docs AGENTS.md pyproject.toml`
   (excluding `docs/changelog/v3.md`, `docs/migration/v2_to_v3.md`, and the
   `tests/.dandy/recordings/` generated artifacts per deviation 4):
   `decoder|Decoder` -> 0; `llm\.decoder` -> 0; `recorder_add_process_decoder` -> 0;
   `FunDecoderBot` -> 0; `BookThemeDecoderBot` -> 0; `_DecoderService_instance` -> 0.
   The broad `decoder|Decoder` docs sweep's only remaining hits are intentional: the
   changelog's old->new rows, the changelog's v3.0.0 release section (the name at that
   release), the glossary anti-language row, and the migration doc's v2 left column +
   sed patterns.
8. Structure: `ls dandy/domain` -> `decision intel message prompt request tokens tool`;
   `ls dandy/application` -> `agent bot decision diligence llm tool`;
   `dandy/infrastructure/recorder/` has `decision_events.py` and no `decoder_events.py`;
   `dandy/domain/decoder/` and `dandy/application/decoder/` do not exist.
9. API smoke: `PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings .venv/bin/python -c
   'import dandy; b = dandy.Bot(); print(b.llm.decision)'`
   -> `<dandy.application.decision.service.DecisionService object at 0x78880903d150>`, exit 0.

All 9 points pass. Nothing was committed (working tree left dirty, per standing instruction).
