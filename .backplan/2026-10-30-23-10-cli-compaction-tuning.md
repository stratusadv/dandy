# Tune up CLI compaction

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-10-30-23-10

## End State

The CLI's conversation compaction survives realistic scenarios — tool results
can no longer overflow the context window or silently erase the file the agent
just read — and the scenario battery exists as hermetic tests in the suite
(`tests/application/agent/`, `tests/application/tool/`, `tests/domain/message/`),
all passing alongside the full gate (pytest, unittest, coverage >= 90%,
lint-imports, ruff baseline, `just docs-tests`).

## Observable Concern

Two of the changes are user-visible behavior changes, not just fixes:
`CodingAgent.chat` will run the planning bot *before* compaction (progress
beats reorder: 'Planning' now precedes 'Compacting conversation history...'),
and the planning bot starts from a fresh conversation on every chat (it
currently accumulates all prior chats' planning turns, verified to grow across
chats in the probe). Existing `TestCodingAgentPlanning` and multi-turn tests
encode the current call order and must be re-verified, not assumed.

## Current State

Verified by code read plus a scenario probe (`probe_compaction.py`, run
hermetic with `tests.dandy_settings`):

- Three compaction call sites share `compact_message_history`
  (`dandy/domain/message/message.py:231`) but compute their own targets:
  `CodingAgent._compact_history_for_next_message`
  (`dandy/application/agent/coding_agent.py:109`, 0.70 x max_context_tokens
  minus the raw user input), `Agent._compact_history_for_next_message`
  (`dandy/application/agent/agent.py:150`, same ratio, subtracts Prompt-or-str
  incoming), and `ToolService._compact_history_before_next_round`
  (`dandy/application/tool/service.py:128`, 0.70 x resolved config
  `context_size`, no incoming subtraction, runs before every tool round
  including round 1).
- Fixed per-request costs are small and fit the 30% margin at every window
  (measured): coding system message 353 tokens, `AGENT_TOOLS` schema 1422
  tokens (10 tools), typical plan section ~178 tokens; total 1953 vs margin
  2458 at an 8192 window. Wire audit at 65536: 47172 input vs 52429 cap
  (20% output) — fits. The 70/20/10 split itself is sound.
- **Broken: `read_file` has no output cap** (`dandy/application/agent/tools/file/read_file_tool.py:29`
  returns the whole file, line-numbered). `search_files` caps at 8000 chars
  and `run_command` inherits the 8000-char subprocess cap; `list_directory`
  is also uncapped. Probe: a 200,000-char read result (86,144-token history)
  was dropped *entirely* by mid-loop compaction, leaving `[system, user]` —
  the file the agent just read silently disappears from context before the
  model sees it; a large enough file exceeds the whole 65536 window and the
  provider 400s.
- **Broken: one message bigger than the budget cannot be dropped** —
  `[system, user(giant)]` compacts to nothing and is sent as-is (probe:
  86,057 tokens, unchanged) — opaque provider 400, no Dandy error.
- **Docstring false**: `compact_message_history` claims "the newest message
  is always kept"; when the newest message is a `tool` result, its whole
  round (assistant tool-call declaration + results) is dropped (probe S3:
  4444 -> 100, newest tool result gone). Wire-correct, but the docstring is
  wrong and the consequence (losing the just-executed round) is undocumented.
- **Planning conversation accumulates across chats**: `CodingAgent._create_plan`
  never resets the planning bot; probe shows 3 messages after chat 1, 5 after
  chat 2, compaction only at ~45,875 tokens (~100+ chats). Each chat's plan is
  polluted by every prior chat's planning turns.
- **Pre-chat compaction under-reserves**: it subtracts the raw `user_input`
  only, but with planning on the sent prompt is user_input + 'Implementation
  Plan' + plan text (~178-1000+ tokens extra).
- Not a bug (checked): `CodingAgent._resolve_context_size` (raw settings with
  coding-config-then-DEFAULT fallback) and `ToolService` (resolved
  `LlmConfig.context_size`, which inherits `CONTEXT_SIZE` from DEFAULT,
  `dandy/infrastructure/llm/config.py:46`) agree in every settings shape;
  `default_settings.py` ships `CONTEXT_SIZE: 65536`. The CLI
  (`dandy/interfaces/cli/cli.py:61`) catches any exception from
  `agent.chat` and prints it via `printer.error`, so a recoverable Dandy
  error surfaces cleanly without killing the REPL.
- Test conventions: hermetic `unittest.TestCase`, mock
  `dandy.infrastructure.http.connector.HttpConnector.request_to_response`,
  fakes in `intelligence/` dirs; existing compaction tests in
  `tests/application/agent/test_coding_agent.py` (`TestCompactMessageHistory`,
  `TestCodingAgentCompaction`) and `tests/domain/message/test_message_content.py`.

## Plan

1. Cap `read_file` and `list_directory` output
   - 8000-char cap matching the house pattern (`_SEARCH_RESULT_CHARACTER_LIMIT`
     in `search_tool.py`, `_COMMAND_OUTPUT_CHARACTER_LIMIT` in
     `dandy/shared/subprocess.py`), same `'\n... (truncated)'` marker; the
     `read_file` notice also states the total line count and to page with
     `start_line`/`end_line`. `read_file`'s tool description gains one line
     telling the model long files come back truncated.
   - Done when new tests in `tests/application/agent/test_file_tools.py`
     (long file truncated + notice + correct head; long directory listing
     truncated) pass and existing file-tool tests still pass.

2. Framework guard: truncate any tool result in `ToolService`
   - In `dandy/application/tool/service.py::_process_tool_call`, after
     `result_text` is computed (str or `model_dump_json()`), truncate beyond
     a module constant `_TOOL_RESULT_CHARACTER_LIMIT = 8000` with the same
     marker, before the verbose preview, recorder event, and
     `add_message` — so the model, the recorder, and the verbose trace all
     see the same text. Protects user-supplied tools, not just `AGENT_TOOLS`.
   - Done when a new test in `tests/application/tool/test_service.py` (fake
     tool returning a 20,000-char result) asserts the stored tool message is
     capped, and the existing tool-loop suite passes.

3. Reorder `CodingAgent.chat` and account for the real prompt
   - Plan first (`_create_plan`), then build the prompt (user input +
     'Implementation Plan' section when planning ran), then compact with the
     *actual* prompt's estimated token count (`Prompt.estimated_token_count` /
     `get_estimated_token_count_for_string`), then the coding turn. Add a
     `_incoming_token_count` mirroring `Agent._incoming_token_count`
     (`dandy/application/agent/agent.py:137`).
   - Done when a new test proves the plan section is subtracted (same history
     compacts harder with a plan prompt than with the raw string) and the
     existing planning/multi-turn tests pass.

4. Fresh planning conversation per chat
   - `CodingAgent._create_plan` resets the planning bot before each chat
     (`self.planning_bot.reset()` — verified to rebuild the connector's
     request body and messages), so each plan starts from a clean slate;
     `clear()` behavior is unchanged.
   - Done when a new two-chat test asserts the planning bot's conversation is
     3 messages (system, user, assistant) after the second chat, not 5.

5. Pre-flight overflow error in `CodingAgent.chat`
   - After compaction, if `history.estimated_token_count + incoming` exceeds
     `max_context_tokens` (the whole window, not the 0.70 working set), raise
     `AgentRecoverableError` saying the conversation still does not fit and
     to clear it and retry with a shorter message. The CLI already prints
     recoverable errors cleanly.
   - Done when a new test (giant unpasteable user message + small
     `max_context_tokens`) asserts the raise with a useful message, and
     `test_agent_compacts_history_before_sending` is recalibrated (its
     40-token window is smaller than any real one; bump so post-compaction
     history fits the window while still exercising compaction).

6. Fix the `compact_message_history` docstring
   - State the real contract: the system message (position 0) is always kept;
     the newest message is kept unless it is a `tool` result, in which case
     its whole round is dropped because a tool result without its assistant
     declaration is invalid on the wire. Add two behavior tests: newest-is-
     tool-result round drop; oversized newest message left in place without
     raising.
   - Done when the new tests in `tests/application/agent/test_coding_agent.py`
     pass and the docstring matches observed behavior.

7. Docs
   - `AGENTS.md`: tool-calling bullet (tool results capped at 8000 chars,
     `read_file`/`list_directory` now capped), coding-agent bullet (planning
     before compaction, fresh planning per chat, plan section counted,
     pre-flight overflow error), token-estimation/compaction bullet (docstring
     semantics). `docs/user_guide/options_and_context.md` compaction section
     and `docs/changelog/v3.md` (Changed + Fixed) to match.
   - Done when `just docs-tests` passes and the bullets match the code.

8. Full gates + close-out
   - Pre-change baseline captured first (pytest / unittest / coverage /
     lint-imports / ruff / docs-tests), then re-run everything after; update
     this doc with the real outputs and set Status: Executed. Delete
     `probe_compaction.py`.
   - Done when every gate meets or beats the baseline and the probe is gone.

## Completion Test

```bash
cd /home/nathanj/PycharmProjects/dandy

# targeted
AI_API_KEY=test-key PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings \
  .venv/bin/python -m pytest tests/application/agent tests/application/tool \
  tests/domain/message -q

# full parity
AI_API_KEY=test-key PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings \
  .venv/bin/python -m pytest . -q
env -i PATH="$PATH" HOME="$HOME" .venv/bin/python -m unittest discover -t . ./tests
PYTHONPATH=. AI_API_KEY=placeholder DANDY_SETTINGS_MODULE=tests.dandy_settings \
  .venv/bin/python -m coverage run -m unittest discover -t . ./tests \
  && .venv/bin/python -m coverage report --fail-under=90
.venv/bin/lint-imports
.venv/bin/ruff check .
.venv/bin/ruff format --check .
just docs-tests
```

All pass/fail gates exit 0 (`ruff check` / `ruff format --check` are
baseline comparisons, see Execution Report). Pre-change baseline
(hermetic): `508 passed, 29 skipped, 49 subtests passed in 3.98s`;
post-change: `517 passed, 29 skipped, 49 subtests passed in 4.06s` — the
delta is the 9 new scenario tests.

## Deviations

1. Rewrote the existing `test_prompt_to_intel_compacts_overgrown_history` instead of only adding a new cap test
    - What: the pre-existing test (3 tool rounds of 200,000-char results) no longer exercises compaction once step 2 caps every result at 8000 chars; it now runs 2 capped tool rounds plus the final answer and forces the compaction path by setting `bot.llm.config.context_size = 3000`, asserting the 'Compacting conversation history' beat and that the post-compaction history fits the 0.70 target.
    - Why: with the new 8000-char result cap, three capped rounds no longer exceed the 45,875-token compaction target, so the old setup would have passed without ever compacting; the shrunken resolved context forces the same code path deterministically.
2. Annotated only the new test methods in the two annotation-free test files
    - What: added `-> None` to the 3 new tests in `tests/application/agent/test_file_tools.py` and to `test_prompt_to_intel_caps_oversized_tool_results` (with its `mock.MagicMock` parameter annotation) in `tests/application/tool/test_service.py`; the un-annotated pre-existing sibling methods were left untouched.
    - Why: AGENTS.md requires new code to pass ruff, and annotating the whole files would have churned unmodified siblings; per-file ruff line counts vs HEAD are now identical (165=165, 549=549), which keeps the repo-wide count flat at the cost of mixed style in those two files.
3. Corrected two pre-existing stale claims in AGENTS.md bullet 7 while editing it
    - What: replaced "`max_completion_tokens` is not an option anymore: `LlmConfig` derives it as `CONTEXT_SIZE * LLM_OUTPUT_TOKEN_RATIO` (constant `0.20`)" with "`max_completion_tokens` is a normal option in a config's `OPTIONS` (when omitted, no output cap is sent)" — verified against `dandy/domain/request/options.py` and the v3.1 changelog in this repo — and fixed the token-test path `tests/domain/tokens/test_utils.py` (does not exist) to `tests/domain/tokens/test_estimate.py`.
    - Why: the bullet being rewritten was adjacent to claims the restructure had already made false; leaving them would have shipped a doc that contradicted its own neighboring sentences.
4. The ruff/format baselines had to be re-measured, not compared against the previous session's numbers
    - What: the previous session's baselines (648 ruff errors; 155/268 format) no longer hold because the user's restructure commits (`2e0dc15`, `83294e2`, `2b5f6b9`) landed between sessions and moved modules (`dandy/application/llm/tool/` → `dandy/application/tool/`, `dandy/domain/llm/request/` → `dandy/domain/request/`, `dandy/shared/conf/` → `dandy/shared/settings/`, ...). The comparison that holds is per-file ruff vs HEAD, which is zero for every file this plan touched.
    - Why: a repo-wide absolute count conflates the user's restructure with this work; per-file vs HEAD isolates this plan's delta (note for the report — not a change to the plan's own steps).

## Execution Report

Pre-change baseline (hermetic): `508 passed, 29 skipped, 49 subtests passed in 3.98s`.

Post-change, all gates re-run at close-out:

| Gate | Observed output |
|---|---|
| targeted pytest (`tests/application/agent tests/application/tool tests/domain/message -q`) | `125 passed, 1 skipped in 0.43s` |
| full pytest (`pytest . -q`) | `517 passed, 29 skipped, 49 subtests passed in 4.06s` (508 + 9 new) |
| unittest discover | `Ran 546 tests in 3.627s` / `OK (skipped=29)` |
| coverage (`--fail-under=90`) | `TOTAL 4286 253 94%` (previous repo state: 4254 statements / 94%) |
| lint-imports | `Contracts: 6 kept, 0 broken.` |
| ruff check . | `Found 668 errors.` — per-file vs HEAD, zero delta on every touched file (test_file_tools.py 165=165, test_service.py 549=549, all `dandy/` sources identical) |
| ruff format --check | all 8 touched files `already formatted` (repo-wide: 156 would be reformatted / 269 already formatted; the old 155/268 baseline is stale, see deviation 4) |
| just docs-tests | `Documentation built in 0.96 seconds`, exit 0 |

`probe_compaction.py` deleted. Nothing committed.
