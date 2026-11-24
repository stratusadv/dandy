# CLI long-session performance

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-24-08-51

## End State
On the real 883 KB / 509-message session, the per-turn local CPU overhead from token
estimation and recorder event construction drops from ~2.7 s (30-round turn) to
< 0.1 s; compaction replaces the droppable middle of a long history with one ~1–2k-token
structured summary (keeping the system/skills message, the opening request, and recent
rounds verbatim), so the post-compaction per-round payload drops from ~183k tokens to
tens of thousands; the hermetic suite + ruff + import-linter stay green and every
compacted history stays wire-valid. Reasoning effort (xhigh), unlimited rounds, and
model-controlled command timeouts are unchanged per the user's decisions.

## Observable Concern
The token-count cache must invalidate on *every* message mutation path — especially
the direct `message.content = [...]` assignment in `CliAgent.reload_agents_md` and
compaction's `del history.messages[...]` — or stale counts silently corrupt the
compaction budget and the context-fit guard, which is worse than the slowdown.

## Current State
Verified by reading the code and benchmarking the largest real session
(`.dandy/agent/sessions/2026-11-17-19-48-complete-all-v3-point-zero-alpha-six-tas.json`,
883 KB on disk, 509 messages, 534 KB of text, **197,440 estimated tokens**):

- **Token estimation is an uncached per-character Python loop.**
  - `get_estimated_token_count_for_string` (`dandy/domain/tokens/estimate.py:58`)
    iterates every character calling `isascii/isalpha/isdigit/isspace`.
  - `Message.estimated_token_count` (`message.py:87`) and
    `MessageHistory.estimated_token_count` (`message.py:187`) are pure properties,
    recomputed from scratch on every access; no memoization anywhere.
  - Measured: one full-history scan = **28.6 ms**; an 8 KB tool result = 0.34 ms.
- **The full history is re-scanned many times per turn.** Call sites that each do a
  full O(history) scan:
  - `ToolService.prompt_to_intel` round start (`application/tool/service.py:77`) — 1/round.
  - `ToolService._process_tool_call` guard event (`service.py:267`) — 1/tool call.
  - `recorder_add_llm_request_event` (`infrastructure/recorder/llm_events.py:70`) — 1/round.
  - `Agent._watch_turn_start` / `_watch_turn_end` / `_ensure_history_fits` /
    `_compact_history_for_next_message` / `save_session` (`agent.py:202,217,247,411,342`).
  - Measured projection: a 30-round turn ≈ **95 full scans ≈ 2.7 s CPU**, growing
    linearly with history (so it worsens every turn of a long session).
- **Recorder events are built even when nothing is recording.** The CLI never calls
  `Recorder.start_recording` (confirmed: `Recorder.is_recording()` is False). Yet
  `recorder_add_llm_request_event` still does `request_body.model_dump()` (full
  history dump, 3.7 ms) + a full token scan (28.6 ms) + builds an attribute per
  message, then `Recorder.add_event` discards it. Measured **30.2 ms/round of pure
  waste**.
- **The dominant wall-clock cost is the per-round LLM payload.** The live CLI config
  (`~/.config/dandy/dandy.json`) maps CODING→THINKING→`stratus.thinking` with
  `reasoning_effort: xhigh` and `CONTEXT_SIZE: 262144`. Compaction target
  `0.70 × 262144 ≈ 183k`, trigger `0.80 × 262144 ≈ 209k`
  (`domain/message/compaction.py:9,14`), so a long session rides at ~180–210k tokens
  and **every tool round sends the whole history** to a thinking model. Prefill +
  reasoning latency grows with the session — this is the "crawl".
- **Tool rounds are unbounded.** `AGENT_MAX_TOOL_ROUNDS_DEFAULT = None`
  (`agent.py:47`); the comment and AGENTS.md still say 200. It was deliberately
  changed 200→None in commit `7585091` ("v3.0.0a6 fixes"), so this is a recent
  intentional choice, not an obvious bug to silently revert.
- **Long-running commands are model-driven and uncapped.** `RunCommandTool.handle`
  (`.../command/command_tool.py:32`) exposes `timeout_seconds` to the model (default
  30, model may pass more); its description encourages running tests/linters/builds.
  With huge context + xhigh reasoning + unbounded rounds, the model issues many
  redundant/expensive commands. `RepeatGuard` only catches *identical* canonicalized
  calls, so varied full-suite runs never trip it.
- Minor: `SessionStore.save` re-parses the prior file for `created_at` (6.3 ms) and
  `list_sessions` parses all 62 files (48.8 ms) — only on save//sessions, not per round.

### Prototyped fixes (measured, equivalence-checked)
- `collections.Counter(string)` + classify distinct chars: **2.3× faster** (23.9→10.3 ms
  full text; 0.336→0.148 ms per 8 KB), byte-identical counts on prose/code/unicode/empty.
- Cached per-message counts summed as ints: **0.001 ms vs 28.6 ms** live (~28,000×).

## Research (how production agents compact, fetched 2026-11-24)
- **Claude Code** (https://code.claude.com/docs/en/context-window.md,
  https://code.claude.com/docs/en/how-claude-code-works.md):
  - Auto-compacts near the limit by **replacing the conversation with a structured
    summary** that keeps the user's requests and key code snippets; their example session
    goes 22,225 → 17,095 tokens with a **1,725-token conversation summary**.
  - Survives compaction: system prompt; CLAUDE.md/AGENTS.md and rules **re-injected from
    disk**; skill descriptions rebuilt and invoked skill bodies re-injected (capped 5k
    tokens/skill, 25k total); **re-reads up to 5 most-recently-modified files** (a file
    over 5k tokens returns as a path reference only); running background tasks are
    reminded. Everything else (tool outputs, analysis, hook context) is summarized.
  - Persistent instructions belong in AGENTS.md, not conversation history (Dandy already
    folds AGENTS.md into the system prompt). Thrashing protection: stop auto-compacting
    after a few failed attempts (Dandy's ContextPressureGuard identical-failure rule
    already mirrors this). `/compact focus on ...` lets the user steer the summary.
- **OpenAI** (https://developers.openai.com/api/docs/guides/compaction.md,
  https://developers.openai.com/api/docs/guides/keep-prefix-unchanged.md):
  - Compaction is threshold-triggered and carries key prior state forward in fewer
    tokens; items before the newest compaction item can be dropped. Their server-side
    compaction is Responses-API-only, so a chat-completions framework like Dandy must
    summarize client-side.
  - Editing old history (shortening tool results, replacing turns with a summary) is a
    **prefix change**: it breaks prompt caching and can drop reasoning items. Guidance
    for custom compaction: place the compacted item at the end of the context rather
    than before recent turns, or accept the tradeoff; and shorten long tool outputs
    **before they are first sent** (Dandy's 8000-char cap already does this).
- **Wire constraint** (matches this repo's strict-endpoint gotcha): an assistant
  `tool_calls` declaration must be followed by `tool` results for every call id, so
  "keep the tool calls but delete their feedback" is invalid on the wire. The
  research-backed equivalent: keep **recent** rounds verbatim (declaration + results)
  and fold **older** rounds into the summary as command → outcome lines, preserving the
  record of what ran without the bulky feedback.

## Plan
1. Faster character-class estimator (parallel-safe, no behavior change)
   - Rewrite `get_estimated_token_count_for_string` to count with `collections.Counter`
     (C-level) and classify only the distinct characters; keep the exact constants and
     calibration so counts are identical.
   - Done when `tests/domain/tokens/test_estimate.py` passes unchanged and the 8 KB
     benchmark is ≥2× faster with identical output.
2. Cache per-message token counts with correct invalidation
   - Add a private cached count to `Message`; compute lazily; invalidate on
     `add_content_from_*`, on `content`/`tool_calls`/`tool_call_id` assignment (cover
     `reload_agents_md`'s direct `.content =`), so `MessageHistory.estimated_token_count`
     becomes a sum of cached ints. Compaction deletes whole messages, so per-message
     caching stays correct without a running total.
   - Done when a repeated full-history total is O(messages) (µs, not ms), new invalidation
     unit tests pass, and compaction/context-fit/reset tests stay green.
3. Gate recorder event construction behind `Recorder.is_recording()`
   - Early-return in the `recorder_add_*` builders (the request event is the expensive
     one) when nothing is recording, so the CLI skips the redundant dump + scan + attrs.
   - Done when the idle request-event benchmark is ~0 ms and all recorder tests
     (which start a recording) still pass.
4. Summarization compaction: domain split/rebuild helpers + a summarizer bot
   - Domain (`dandy/domain/message/compaction.py`): pure helpers to split a history into
     protected head (system slot + opening exchange), droppable middle (older tool rounds
     and plain exchanges), and protected tail (the newest rounds, kept verbatim within a
     token budget), and to rebuild head + one summary message + tail wire-validly.
     `compact_message_history` (drop-only) stays as the fallback.
   - Application: a `CompactionBot` following the `SessionNamingBot` pattern (fresh Bot,
     fast DEFAULT config, structured Intel out) summarizing the middle into sections:
     goal, key decisions/findings, files touched + changes, commands run + outcomes,
     errors + fixes, pending tasks, current work, next step. Target ~1–2k tokens.
   - Structural decision to flag: the base `Agent` is universal, so the summarizer lives
     at the agent level (not the CLI slice) and must not depend on `CLI_CONFIG`.
   - Done when helpers + bot exist with hermetic unit tests (mocked HTTP), and the
     rebuilt history passes the wire-validity rules (tool rounds atomic, system first).
5. Wire summarize-then-keep-recent into both compaction sites, with fallback
   - `Agent._compact_history_for_next_message` and `ToolService._compact_history` call the
     summarization path when over the trigger; on any summarizer failure they fall back to
     today's drop-only compaction so the loop never blocks. Summary placement: after the
     opening exchange, before the recent tail (Claude Code style); the prefix-change
     cache tradeoff is accepted (drop-only compaction already rewrites the prefix).
   - Keep the 80% trigger / 70% target ratios, xhigh reasoning, unlimited rounds, and
     model-controlled timeouts unchanged (user decisions).
   - Done when a mocked long-session turn compacts to head + summary + recent tail, the
     fallback path is tested, and the progress beat still reports compaction.
6. Tests, docs, and measured verification
   - Update the compaction fuzz invariants: the result is no longer a pure subsequence —
     protected head/tail survive verbatim and the middle is replaced by exactly one
     summary message; wire-validity and fixed-point invariants still hold.
   - Update AGENTS.md + docs (compaction bullet, user guide, changelog) per repo rules.
   - Done when `just test`, `ruff check .`, `ruff format --check .`, `just lint-imports`
     are green and the benchmark shows the payload/CPU targets in the Completion Test.

## Completion Test
- Hermetic gates: `just test` (or `PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings
  AI_API_KEY=placeholder python -m pytest tests -q`), `ruff check .`, `ruff format --check .`,
  `just lint-imports` — all green.
- New unit tests: estimator equivalence vs the old loop; cache invalidation on content
  assignment / add_content / compaction; recorder builders no-op when not recording;
  summarization compaction (mocked summarizer) keeps head + recent tail verbatim, inserts
  one summary message, stays wire-valid, and falls back to drop-only on summarizer failure;
  updated fuzz invariants pass.
- Benchmark (re-run `/tmp/dandy_perf_probe.py` on the real 883 KB session) and quote
  before/after for: full-history scan, cached total, idle recorder request event, and the
  projected 30-round-turn CPU. Target: projected per-turn CPU < 0.1 s (from ~2.7 s).
- Payload check: compact the real 197k-token session with a mocked summarizer and measure
  the rebuilt history's estimated token count. Target: tens of thousands, not ~183k
  (head + ~1–2k summary + recent tail).

### Observed (2026-11-24, real 883 KB / 509-message / 197,440-token session)
- Hermetic suite: `python -m pytest tests -q` → **1064 passed, 29 skipped, 68 subtests
  passed** (live-LLM tests skip without a real key).
- Architecture: `lint-imports` → **Contracts: 6 kept, 0 broken** (no new seams needed).
- Docs: `mkdocs build --strict` → **Documentation built in 1.37 seconds** (new reference
  members resolved). `codespell` on the changed files → **exit 0**.
- Formatting: `ruff format --check .` → **527 files already formatted**. `ruff check` on
  every changed file → **All checks passed**. Note: `ruff check .` reports 6 pre-existing
  errors in the tracked scratch file `.backplan/repro_tail.py` (unmodified by this work);
  CI's gates are unittest/pytest/coverage/lint-imports/codespell, not ruff.
- Benchmark before → after:
  - full-history token scan (cold): **28.6 ms → 6.1 ms**; warm cached scan: **0.4 ms**.
  - idle recorder request event: **30.2 ms → 0.0 ms**.
  - projected CPU per 30-round turn (1 cold + 94 warm scans): **~2.7 s → 0.045 s**
    (target < 0.1 s met).
- Payload: summarization compaction (mocked `CompactionBot`) rebuilt the real session
  **197,440 → 46,700 estimated tokens (−76.3%), 509 → 85 messages** (target "tens of
  thousands" met; the kept system prompt carries AGENTS.md, hence ~47k). Wire-valid.

## Deviations
1. Step 4 re-scoped from "config tuning menu" to "summarization-based compaction redesign".
    - What: User locked keep-xhigh / unlimited-rounds / no-timeout-clamp, and asked for
      research into how agent context compaction is supposed to work (summarize non-critical
      history into a compact message; keep system/skills, tool calls and commands, drop bulky
      tool feedback) instead of picking a smaller context window.
    - Why: The user wants the model to keep its full capability and memory of critical work;
      the speed win should come from carrying a compact summary, not from forgetting more or
      reasoning less.
2. Research done by direct fetch; design settled as summarize-middle / keep-recent-tail.
    - What: The three background search agents errored on every web_fetch and were stopped;
      the parent fetched the Claude Code and OpenAI docs directly. The user's "keep tool
      calls, drop feedback" became "keep recent rounds verbatim, fold older rounds into the
      summary as command → outcome lines", and step 4 split into steps 4–6.
    - Why: A tool_calls declaration without matching tool results is a 400 on strict
      endpoints, so feedback can only be dropped by folding the whole round into the
      summary; Claude Code and OpenAI both keep recent work and summarize the rest.
3. Fixed a pre-existing broken test uncovered by the green-suite gate.
    - What: `test_agent_turn_caps_tool_rounds` did `AGENT_MAX_TOOL_ROUNDS_DEFAULT + 1`,
      which raises TypeError because the constant was deliberately set to `None` in
      commit `7585091` (before this work). Rewrote it to set an explicit finite
      `max_tool_rounds = 3` on the agent, so it tests the opt-in cap independent of the
      now-unlimited default.
    - Why: The completion test requires a green hermetic suite; this failure pre-dated
      the change and is directly about the tool-round cap the user chose to keep
      unlimited by default.
4. Kept the drop-only fuzz invariants intact; tested the summarize path separately.
    - What: Step 6 originally said to update the compaction fuzz invariants (result no
      longer a pure subsequence). Instead, `compact_message_history` (the drop-only
      fallback) is unchanged, so its existing hypothesis fuzz suite still applies
      verbatim; the new summarize path got its own hermetic tests
      (`tests/application/agent/test_compaction.py`) asserting head/tail preservation,
      one summary message, wire-validity, token reduction, fallback, and stop re-raise.
    - Why: The summarize path is a separate orchestrator over the unchanged drop-only
      primitive, so the proven drop-only invariants stay valid and the new behavior is
      covered directly without weakening the fuzz guarantees.