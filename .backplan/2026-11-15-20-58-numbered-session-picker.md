# Numbered session picker

- Developer: (v3/base working tree)
- Status: Executed
- Date: 2026-11-15-20-58

## End State
In the Dandy CLI REPL, `/s` prints the saved-sessions table numbered 1..N with the
**most recently updated session on the bottom row**, and `/r <n>` (and `/s <n>`,
one-shot `-s <n>`) resumes that row by number; full names and bare (latest)
resumes keep working exactly as today.

## Observable Concern
The store's `list_sessions()` is currently "newest first" — every consumer
(`latest()`, error messages) relies on that order, so the reversal for display
must not leak into the store API: the number→name mapping has to be explicit and
shared by the REPL and the one-shot dispatchers, or the two surfaces will drift.

## Current State
- `SessionStore.list_sessions()` (dandy/application/agent/session_store.py:77)
  returns records sorted newest-first; `latest()` takes the max of that list.
- `DandyCli.print_sessions()` (dandy/interfaces/cli/cli.py:207) prints an
  unnumbered markdown table, newest first (bottom = oldest).
- Resume paths: REPL `_process_resume`/`_process_sessions` (cli.py:135,152) →
  `load_named_session(name)`; one-shot `_dispatch_repl`/`_dispatch_one_shot`
  (main.py:32,52) → `load_latest_session`/`load_named_session`/`run_in_session`.
- `load_named_session` catches `AgentExternalError` and prints
  'Could not resume session' — so a resolver that raises the same exception for
  bad numbers gets the right error UX for free.
- `_raise_unknown_session` already lists available names in its message.
- Docs that describe resume: `docs/user_guide/cli_agent.md` (Sessions + TUI
  bullets), `docs/getting_started/cli.md` (command list + one-shot table),
  `docs/reference/interfaces.md` (CLI loop), `docs/changelog/v3.md` (Unreleased).
- Hermetic tests in `tests/interfaces/cli/test_cli.py` (TestDandyCli session
  cases ~lines 380–750) and `tests/application/agent/test_session_store.py`.
- Confirmed decisions (asked via the question tool): numbered table via /s;
  bare /r keeps jumping to the newest; no 'last' keyword (bare = latest);
  row numbers, full names, and bare all work in both the REPL and one-shot.

## Plan
1. Store: add `resolve_selection(selection: str) -> str | None`
   - Empty string → None (caller treats it as "latest"); an integer is a
     1-based row into the sessions sorted oldest-first (so row N = newest);
     anything else is an exact session name. Unknown row/name raises
     `AgentExternalError` listing what is available.
   - Done when new unit tests in `tests/application/agent/test_session_store.py`
     pass: number picks the right row (latest = highest number), empty → None,
     name passthrough, bad number/name raise with the available list.
2. CLI: numbered table + row-aware resume
   - `print_sessions()` reverses to oldest-first and prefixes each row with its
     number; footer line: "Resume one with `/r <row>` or its name — the newest
     session is on the bottom."
   - `_process_resume`/`_process_sessions` resolve the argument through
     `SessionStore.resolve_selection` before `load_named_session`;
     `load_named_session` keeps taking a resolved name.
   - One-shot: both name slots in `_dispatch_repl` and `_dispatch_one_shot`
     (main.py) go through the same resolver (bare still = latest), so
     `dandy -s 2 "req"` and `dandy -s 2` work.
   - Done when `just test-app tests/interfaces/cli/test_cli.py` passes,
     including new cases: table shows numbers with the newest session on the
     bottom row, `/r 1` resumes the oldest, `/r 2` (or `/s 2`) resumes the
     newest, `/r 99` reports the error without changing the active session,
     and one-shot `run_in_session('2', ...)` resolves by row.
3. Docs + usage text
   - `usage.py` prose and the `CLI_COMMANDS` descriptions for sessions/resume;
     `docs/user_guide/cli_agent.md`, `docs/getting_started/cli.md`,
     `docs/reference/interfaces.md`, new Unreleased changelog entry.
   - Done when `just docs-tests` passes.
4. Full gate
   - `just test`, `ruff check .`, `ruff format --check .`, `just lint-imports`.
   - Done when all four are clean.

## Completion Test
`just test` (hermetic, includes the new numbered-picker cases) plus
`ruff check . && ruff format --check . && just lint-imports` — all green.

## Deviations
none yet
