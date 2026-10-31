# Real session system for the CLI and agents

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Planning
- Date: 2026-10-31-00-25

## End State

Conversations in `dandy` are named sessions, auto-saved to
`.dandy/agent/sessions/` after every turn: the REPL manages them with
`/new [name]`, `/sessions`, `/resume <name>`, `/delete <name>` (no auto-
resume, no `/clear`), one-shot mode stays stateless unless
`dandy --continue "req"` extends the latest session (and reports which
one), and session save/load is owned by the base `Agent` — with
`CodingAgent` reborn as its child class and a single `turn()` entry
point — all covered by hermetic tests that pass under both pytest and
`unittest discover` alongside the full gate.

## Observable Concern

The load-bearing risk is the `CodingAgent` -> `Agent` subclass
refactor: it renames the public entry point (`chat()` -> inherited
`turn()`), deletes CodingAgent's duplicated compaction helpers, and
lifts `_ensure_history_fits` into base `Agent.turn` (so every agent
gains the pre-flight overflow check). Compaction behavior is pinned by
the deterministic tests plus the six-property hypothesis battery from
the last two efforts; those must pass unchanged. Second risk: dropping
`/clear` and the fake `session.json` persistence are breaking changes
to existing muscle memory and to `.dandy/cli/` contents.

## Current State

Verified by code read:

- `DandyCliSession` (`dandy/application/agent/session.py:9`, a
  `BaseIntel`): holds only `project_base_path: Path` + `is_loaded:
  bool`. `load()`/`save()` round-trip `.dandy/cli/session.json`, which
  contains only the project path — tautological, since `main.py:71`
  re-sets it from `Path.cwd()` on every start. `post_init` is a plain
  setter called manually from `main` (not a Dandy `__post_init__`
  hook). The module singleton `session` is imported by the four path-
  sensitive agent tools (`tools/paths.py`, git, command),
  `printer.py`, and `main.py` — its one real job today is
  `project_base_path` for tool path resolution.
- `main()` (`dandy/interfaces/cli/main.py:53`): settings +
  `session.post_init(CWD)` + `session.load()` + `session.save()` (when
  not loaded) -> `DandyCli()` -> REPL or one-shot. Nothing from the
  session ever reaches the agent; the saved file carries no
  conversational state at all.
- `DandyCli` (`dandy/interfaces/cli/cli.py:10`): builds a fresh
  `CodingAgent()`; commands are only `/clear` and `/quit`/`/exit`/`q`
  (plus escape-escape exit); every other line goes through
  `process_agent_input` -> `agent.chat(...)` with all exceptions
  caught and printed.
- `CodingAgent` (`dandy/application/agent/coding_agent.py:18`): a
  standalone class (does NOT extend `Agent`). Owns `CodingBot`,
  `PlanningBot`, `MessageHistory`. `chat()` = fresh planning pass ->
  build prompt (user input + 'Implementation Plan' section) -> compact
  against 0.70 x `CONTEXT_SIZE` minus the incoming prompt's estimate ->
  `_ensure_history_fits` (raises `AgentRecoverableError`) ->
  `prompt_to_intel(AGENT_TOOLS, DefaultIntel, persistent history,
  unbounded tool rounds)`. `clear()` resets history + planning + bot.
- `Agent` (`dandy/application/agent/agent.py:23`): the base class —
  `__init__(bot, tools, skills, max_turns, intel_class)`; `turn()` =
  compact + one `prompt_to_intel` over persistent history; `run()`
  drives turns until done; `clear()`; `_resolve_context_size` reads the
  resolved `bot.llm.config.context_size`. CodingAgent duplicates
  `_incoming_token_count`, `_compaction_target_token_count`, and
  `_compact_history_for_next_message` (same logic, copied) plus has its
  own raw-settings `_resolve_context_size` and its
  `_ensure_history_fits`, which the base lacks (a base `Agent`/`run`
  conversation can still 400 on overflow today).
- `LlmConfig.model` (`dandy/infrastructure/llm/config.py:64`) supplies
  the model name for session metadata; agent ints live in
  `dandy/application/agent/intel.py`.
- Compaction semantics are pinned by deterministic tests
  (`tests/application/agent/test_coding_agent.py`,
  `tests/domain/message/test_message_content.py`) and the six-property
  hypothesis battery (`tests/domain/message/test_compaction_fuzz.py`)
  — the safety net for the refactor.
- `.dandy*/` is gitignored; `DANDY_LOCAL_DIRECTORY_NAME = '.dandy'`,
  `CLI_WORKING_DIRECTORY = 'cli'` (`dandy/shared/constants.py`).
  `Printer.welcome()` is at `dandy/interfaces/cli/tui/printer.py:107`;
  CLI loop tests live in `tests/interfaces/cli/test_cli.py` and
  one-shot/main tests in `test_main.py`.
- House patterns: hermetic `unittest.TestCase` (both pytest and CI's
  `unittest discover`), mock at the `HttpConnector.request_to_response`
  boundary, `intelligence/` fixture packages beside tests, pydantic
  JSON via `save_to_file`/`create_from_file`, AGENTS.md + mkdocs +
  changelog v3.1.0 keep in sync.

## Confirmed Decisions (from the question rounds)

- Full session system: conversations auto-save after every turn.
- No auto-resume: the REPL starts fresh; resume is explicit
  (`/resume <name>` in the REPL, `dandy --continue "req"` one-shot).
- Multiple named sessions per project: `/new [name]`, `/sessions`,
  `/resume <name>`, `/delete <name>`. `/clear` is dropped (start fresh
  = `/new`; destruction = `/delete`).
- Names are auto-generated from the first request (`YYYY-MM-DD-<slug>`);
  `/new <name>` takes an explicit one.
- Persisted state: conversation history + metadata (created/updated,
  last request, model + config, token count). No planning-bot state,
  no agent options.
- Architecture: the base `Agent` owns session save/load; `CodingAgent`
  becomes its extended child; a new `SessionStore` owns directory,
  file format, listing, rename-free name management, and delete.
- Entry point converges on `turn()` — `chat()` is removed (breaking,
  documented).
- Storage: `.dandy/agent/sessions/<name>.json` (new agent-neutral
  directory; `SessionStore` takes an explicit path so other consumers
  can point elsewhere).
- The welcome banner always shows a session-status line (count +
  latest name + `/resume` hint, or an empty-state hint).

## Plan

1. `AgentSession` int + base `Agent` session support
   - New `AgentSession` pydantic int in
     `dandy/application/agent/intel.py`: `messages: list[Message]`,
     `last_request: str | None`, `model: str | None`, `config:
     str | None`, `token_count: int`. Base `Agent`: records
     `self.last_request` in `turn`; gains `save_session() ->
     AgentSession` (history + metadata from `bot.llm.config`) and
     `load_session(session: AgentSession) -> None` (swap in the
     history, `bot.reset()` so connector state never dangles off a
     dropped conversation).
   - Done when a hermetic test round-trips a multi-message history
     (with tool rounds) through save_session -> load_session on the
     base Agent (HTTP mocked).

2. `SessionStore`
   - New `dandy/application/agent/session_store.py`:
     `SessionStore(sessions_path: Path)` with `save(name, session)`,
     `load(name)`, `delete(name)`, `latest() -> str | None` (by
     updated time), `list_sessions()` (name, created/updated, message
     count, token count, model; newest first). File per session at
     `<sessions_path>/<name>.json`: a `SessionRecord` wrapper
     (`name`, `created_at`, `updated_at`, `session: AgentSession`).
     Auto-naming helper `new_name(from_text)`: `YYYY-MM-DD-<slug>`
     (lowercased, non-alphanumerics -> dashes, trimmed to ~40 chars);
     collisions get `-2`, `-3`; unknown-name errors name the available
     sessions.
   - Done when a hermetic `tmp_path` suite covers save/load/
     list/delete/latest/collision/naming/unknown-name.

3. `CodingAgent` becomes a child of `Agent`
   - `CodingAgent(run_planning=True)` calls `super().__init__(
     bot=CodingBot(), tools=AGENT_TOOLS, intel_class=DefaultIntel)`
     and adds `planning_bot` + `run_planning`. The base `Agent.turn`
     gains an overridable hook `_prepare_message(message, callbacks) ->
     Prompt | str` (identity by default); `CodingAgent` implements it
     with the planning pass + 'Implementation Plan' section. `chat` is
     removed (CLI, tests, and docs move to `turn`); the duplicated
     compaction helpers and raw-settings `_resolve_context_size` are
     deleted (inherited); `_ensure_history_fits` moves into base
     `Agent.turn` (after compaction, before the LLM call) so every
     agent gets the pre-flight check; `clear()` keeps the planning
     reset via `super()`.
   - Done when the existing CodingAgent compaction / planning /
     multi-turn / fuzz tests pass with behavior unchanged (only the
     entry-point name moves), plus a new test proving a base
     `Agent.turn` (no tools, no planning) raises the pre-flight
     `AgentRecoverableError` on overflow.

4. CLI session flow
   - `DandyCli` owns a `SessionStore` rooted at
     `.dandy/agent/sessions/` (via `session.project_base_path`) and an
     `active_name: str | None`. After each successful turn with
     non-empty history: save (auto-name from the request when
     `active_name` is unset, else update under it). Commands:
     `/new [name]` (fresh conversation, optionally pre-named),
     `/sessions` (table via `Printer`), `/resume <name>` (exact
     match; unknown -> error listing sessions), `/delete <name>`
     (delete; unbind when active). `/clear` removed (tests updated).
     `Printer.welcome()` gains the always-on session-status line.
   - Done when hermetic CLI tests cover auto-save-on-first-turn,
     update-on-later-turns, resume, new (with and without name),
     delete (active and inactive), sessions listing, and the banner
     line (agent + store mocked).

5. One-shot mode
   - `dandy "req"` stays stateless (no session file created).
     `dandy --continue "req"` loads the latest session (clear error
     when none exist), runs one `turn`, re-saves under the same name,
     and prints the session name + message count with the answer.
     Usage text updated.
   - Done when hermetic tests cover `--continue` success, the no-
     session error, and that plain one-shot creates no files.

6. Retire the fake session persistence
   - `DandyCliSession` keeps only the `project_base_path` binding and
     its two path properties (the tools' contract); `load`, `save`,
     `is_loaded`, and `session_file_path` are removed, along with the
     `main.py` calls. Legacy `.dandy/cli/session.json` files are left
     on disk but never read or written again.
   - Done when nothing references the removed members (grep clean)
     and `main` no longer creates `session.json`.

7. Docs
   - `AGENTS.md`: rewrite the CLI bullet (session flow, the four
     commands, `--continue`, `/clear` gone, `chat` -> `turn`), the
     agent bullet (base `Agent` session save/load + `SessionStore` +
     the `_prepare_message` hook, pre-flight check now on every
     agent), and the testing-approach notes where test locations
     change. `docs/user_guide/`: a sessions page (or extension of the
     CLI page) in the mkdocs nav. `docs/reference/`: member lists for
     `SessionStore`/`AgentSession`/`Agent` session methods where the
     agent reference page exists. `docs/changelog/v3.md` v3.1.0:
     Added (sessions + `SessionStore` + base-Agent session support),
     Changed (CodingAgent extends Agent; `chat` -> `turn` breaking;
     `/clear` removed; banner line), Fixed (fake `session.json`
     persistence retired).
   - Done when `just docs-tests` passes and every bullet matches the
     code.

8. Full gates + close-out
   - Full pytest, `unittest discover`, coverage >= 90%,
     `lint-imports`, `ruff check` (zero per-file delta), `ruff format
     --check`, `just docs-tests`; close this doc with the real
     outputs; Status: Executed.
   - Done when every gate meets the current baseline (523 passed /
     29 skipped / 49 subtests; `Ran 552 tests`; 94%; 6 kept / 0
     broken; ruff 648 under 0.17.3).

## Completion Test

```bash
cd /home/nathanj/PycharmProjects/dandy

AI_API_KEY=test-key PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings \
  .venv/bin/python -m pytest tests/application/agent tests/interfaces/cli \
  tests/application/agent/test_agent.py -q
env -i PATH="$PATH" HOME="$HOME" .venv/bin/python -m unittest discover -t . ./tests
AI_API_KEY=test-key PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings \
  .venv/bin/python -m pytest . -q
PYTHONPATH=. AI_API_KEY=placeholder DANDY_SETTINGS_MODULE=tests.dandy_settings \
  .venv/bin/python -m coverage run -m unittest discover -t . ./tests \
  && .venv/bin/python -m coverage report --fail-under=90
.venv/bin/lint-imports
.venv/bin/ruff check .
.venv/bin/ruff format --check .
just docs-tests
# live smoke (manual): start the REPL in a scratch dir, run a turn,
# exit, list .dandy/agent/sessions/, re-enter, /resume it, and verify
# the agent answers from the loaded context.
```

pytest/unittest counts at or above baseline (the new session tests are
the delta); ruff/format clean on touched files; coverage still >= 90%.

## Deviations

none yet
