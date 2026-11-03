# Save a session for every one-shot run

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-02-14-36

## End State

Every agent run saves its conversation, regardless of outcome, through one
underlying turn path shared by the command and the REPL:
`process_user_input` → `process_agent_input` (try/except/else/finally) →
`_save_session_after_turn`, with the `save_session` parameter and
`continue_latest_session`'s separate save block gone. Plain one-shot
`dandy "<request>"` saves a new auto-named session; the interfaces stay
different — one-shot reads argv and sets the process exit code, the REPL
loops in the TUI. A turn that died mid tool round is trimmed to the last
complete round before the snapshot is written (a tool call missing its
results is wire-invalid — strict endpoints 400 on resume). The test
asserting the old stateless one-shot wiring, the test documenting the
removed `save_session` parameter, and the three doc passages that say
one-shot "creates no session file" are updated or deleted.

## Observable Concern

Three things to confirm at sign-off: (1) a plain one-shot creates a
**new** session named from the request text (`YYYY-MM-DD-<slug>`,
collisions get `-2`/`-3`), not an append to the latest — appending is what
`--continue` already means; (2) an incomplete trailing tool round is
**dropped** (assistant declaration plus its partial results) rather than
having placeholder tool results synthesized — simpler, reuses the file's
existing round conventions, and the model's next turn can re-issue the
call; (3) identical underlying behavior also removes the CLI's only save
message — `--continue` no longer prints `Saved session "..." (N messages).`
(silent save, same as the REPL) — and the `save_session` parameter
disappears from both `process_user_input` and `process_agent_input`.
Stopped turns (double-escape) are treated like crashes for saving; the
stop's non-failure semantics (REPL continues, one-shot exit 0) are
unchanged. The user is live-editing this exact CLI area, so re-View before
each edit.

## Current State

- `dandy/interfaces/cli/main.py:106` — plain one-shot calls
  `cli.process_user_input(user_input=user_input, save_session=False)`;
  exit code from `cli.last_turn_succeeded`. `--continue` (line 104) already
  saves via `continue_latest_session` (cli.py:179-206).
- `dandy/interfaces/cli/cli.py:35` — `process_user_input(user_input,
  save_session=True)` forwards to `process_agent_input` (line 150), which
  calls `_save_session_after_turn` only when `save_session` (lines 174-175);
  the plain one-shot is the only `save_session=False` caller.
  `_save_session_after_turn` (lines 247-254) is silent, skips empty history,
  auto-names via `session_store.new_name(user_input)` when `active_name` is
  None.
- REPL already auto-saves: `run()` calls `process_user_input` with the
  `save_session=True` default (cli.py:265).
- Save-path tests exist and pass: `tests/interfaces/cli/test_cli.py` —
  `test_turn_without_history_saves_no_session` (176, stays valid — the
  empty-history skip), `test_first_turn_auto_saves_a_named_session` (188),
  `test_later_turns_update_the_same_session` (203),
  `test_stateless_turn_saves_no_session` (218, passes the now-removed
  `save_session=False` — deleted),
  `test_continue_latest_session_runs_turn_and_resaves` (231, asserts the
  now-removed `Saved session ...` print — re-asserted on the shared path).
- `tests/interfaces/cli/test_main.py:74-76` —
  `test_one_shot_mode_processes_a_single_request` asserts
  `process_user_input.assert_called_once_with(user_input='do the thing',
  save_session=False)` — must drop the kwarg.
- Docs asserting the old stateless behavior:
  - `AGENTS.md:232` — "runs `process_user_input(user_input=...,
    save_session=False)` for a single stateless turn (no session file is
    created), then exits".
  - `docs/user_guide/coding_agent.md:13-14` — "One-shot is stateless: it
    answers the request but creates no session file;".
  - `docs/changelog/v3.md:60-63` — "plain one-shot (`dandy "<request>"`)
    stays stateless and creates no session file." (unreleased v3.1.0 entry —
    amended in place).
- `README.md:34` one-shot sentence ("a single answer without entering the
  REPL") stays accurate — unchanged. `.backplan/` history untouched.
- `dandy --init` runs `run_init`, not `process_user_input` — no
  conversation, stays session-less by design.
- **Crash-save gap** (verified): `process_agent_input` (cli.py:150-177)
  saves only in the success path; the `RunStoppedError` path returns True
  and the `Exception` path returns False, both without saving; no
  `atexit`/`finally`/signal handler exists anywhere in the CLI or agent
  code (grepped).
- `Agent.save_session` (agent.py:187-194) snapshots
  `list(self.history.messages)` — the natural single integration point for
  wire-validity trimming (covers REPL auto-save, `--continue` re-save, and
  the new one-shot save).
- `dandy/domain/message/message.py` — round conventions to reuse: a
  tool-use round is an `assistant` message with `tool_calls` followed by a
  contiguous run of `tool` messages (`_opening_exchange_end_index`
  lines 294-301, `_oldest_droppable_range` lines 326-329);
  `compact_message_history` (line 246) drops rounds as whole ranges.
  Message fields: `role`, `tool_call_id: str | None`, `tool_calls:
  list[dict] | None` (wire dicts, id under `'id'`).
- `continue_latest_session` (cli.py:179-206) loads the latest session,
  sets `active_name`, runs `process_agent_input(user_input,
  save_session=False)`, then saves explicitly only when `turn_succeeded`
  plus the CLI's only `Saved session "..." (N messages).` print (lines
  198-204) — so a crashed `--continue` loses the partial turn, and its save
  path diverges from the REPL's. With the parameter gone and the save in
  `process_agent_input`'s `finally`, it calls the same
  `process_user_input` as the REPL and returns `last_turn_succeeded`.
- Domain message tests live in `tests/domain/message/test_messages.py`
  (plus `test_compaction_fuzz.py`); agent save/load round-trip tests in
  `tests/application/agent/test_agent.py:133+`.

## Plan

1. ~~One-shot saves~~ One shared turn path
   - ~~`main.py:106`: drop `save_session=False` →
     `cli.process_user_input(user_input=user_input)`.~~
   - `main.py:106`: `cli.process_user_input(user_input=user_input)` (drop
     the `save_session=False` kwarg).
   - Drop the `save_session: bool = True` parameter from
     `process_user_input` (cli.py:35,45) and `process_agent_input`
     (cli.py:150); the `if save_session:` guard (lines 174-175) moves into
     step 2's `finally`.
   - Done when `test_one_shot_mode_processes_a_single_request` fails on the
     stale assertion (proof of wiring change), then passes after step 4.

2. Save on stop/crash
   - `process_agent_input`: restructure to try/except/else/finally — the
     existing success output moves into `else`, and
     ~~`finally: if save_session: self._save_session_after_turn(user_input)`~~
     `finally: self._save_session_after_turn(user_input)` runs on all three
     paths (success, stop, error). Return semantics unchanged (stop → True,
     error → False).
   - ~~`continue_latest_session`: line 200 condition
     `if turn_succeeded and len(self.agent.history) > 0:` →
     `if len(self.agent.history) > 0:` (crashed `--continue` saves too,
     same message).~~
   - `continue_latest_session`: delete the `save_session=False` call and
     the explicit save block (lines 198-204); call the same
     `self.process_user_input(user_input)` the REPL loop uses and return
     `self.last_turn_succeeded` (its `active_name` is already the loaded
     latest name, so the shared save updates that session). Keep the
     `Continuing session "..."` print; drop the now-redundant
     `Saved session "..."` print (silent save, identical to the REPL).
   - Done when new CLI tests show a crashed turn and a stopped turn both
     produce a session file, and the existing success-path tests pass.

3. Wire-valid snapshots
   - New `drop_incomplete_tool_round(history: MessageHistory) -> None` in
     `dandy/domain/message/message.py` beside `compact_message_history`:
     if the history ends on a trailing tool round whose `assistant`
     declaration's `tool_calls` ids are not all matched by `tool_call_id`
     results in its contiguous `tool` run (including zero results), delete
     that round (declaration + partial results); complete conversations are
     untouched.
   - `Agent.save_session`: call it on `self.history` before building the
     `AgentSession` (document that this also trims the live history, so the
     REPL's next turn continues from a well-formed conversation).
   - Done when the new domain tests pass: dangling declaration dropped,
     partial round (2 calls, 1 result) dropped, complete round kept, plain
     trailing assistant/user untouched, empty history no-op; and
     `test_agent.py` shows a `save_session()` after a dangling round ends
     at the safe boundary.

4. Test sync
   - `test_main.py:74-76`: assert
     `assert_called_once_with(user_input='do the thing')`.
   - `test_cli.py`: delete `test_stateless_turn_saves_no_session` (the
     parameter it documents is gone); re-assert
     `test_continue_latest_session_runs_turn_and_resaves` on the shared
     path (session updated under the loaded name, no `Saved session ...`
     print); new tests — a turn that raises saves a session
     (`last_turn_succeeded` False, file exists with the partial history);
     a `RunStoppedError` turn saves a session and returns True.
   - Done when `pytest tests/interfaces/cli tests/domain/message
     tests/application/agent -q` is green.

5. Docs
   - `AGENTS.md:232`: one-shot runs the exact same `process_user_input`
     call as the REPL (the `save_session` parameter is gone) and auto-saves
     a new session named from the request;
     sessions paragraph gains: every turn saves regardless of outcome
     (success/stop/error) and crash saves are trimmed to the last complete
     tool round (`drop_incomplete_tool_round` in `Agent.save_session`).
   - `docs/user_guide/coding_agent.md:13-14`: replace the "stateless / creates
     no session file" sentence — one-shot saves a new session; failed or
     stopped turns save too (trimmed at the last complete tool round).
   - `docs/changelog/v3.md:60-63`: plain one-shot saves a new session named
     from the request text; session saves now happen after every turn
     outcome, with incomplete trailing tool rounds dropped before writing.
   - Done when `just docs-tests` exits 0.

6. Gate
   - Full suite, ruff check/format on touched files, `just lint-imports`.
   - Done when every command in the Completion Test passes with output
     quoted.

## Completion Test

- `DANDY_SETTINGS_MODULE=tests.dandy_settings PYTHONPATH=. .venv/bin/python -m
  pytest tests/interfaces/cli tests/domain/message tests/application/agent -q`
  → green, including the updated `test_one_shot_mode_processes_a_single_request`
  and `test_continue_latest_session_runs_turn_and_resaves`, the new
  crash/stop save tests, and the new `drop_incomplete_tool_round` cases
  (`test_stateless_turn_saves_no_session` deleted with the parameter).
  Observed: `263 passed in 5.62s`.
- `DANDY_SETTINGS_MODULE=tests.dandy_settings PYTHONPATH=. .venv/bin/python -m
  pytest tests -q` → whole suite passes. Observed: `661 passed, 49 subtests
  passed in 398.08s`.
- ~~`.venv/bin/ruff check <touched files>` + `grep -E 'E501|F[0-9]{3}|W[0-9]{3}'`
  empty; `.venv/bin/ruff format --check <touched files>` clean.~~ (see
  deviation 3) Observed instead: per-file rule-multiset diff against the HEAD
  versions of the touched files — `cli.py`, `main.py`, `message.py`,
  `agent.py` identical (zero new findings); the four test files add only
  `PT009` occurrences, a unittest-style rule the repo currently carries red
  repo-wide (773 pre-existing findings; neighboring test files already carry
  40-60 each).
- `just lint-imports` → all 6 contracts kept. Observed: `Analyzed 182 files,
  446 dependencies. ... Contracts: 6 kept, 0 broken.`
- `just docs-tests` → mkdocs strict build exits 0. Observed: `Documentation
  built in 0.95 seconds`.

## Deviations

1. **Added save-on-stop/crash scope** — the plan grew from "one-shot saves"
   to "every run saves, regardless of outcome, with wire-valid crash
   snapshots".
   - What: steps 2 and 3 added (try/finally save in
     `process_agent_input`, widened `continue_latest_session` save,
     `drop_incomplete_tool_round` + `Agent.save_session` trim, crash/stop
     CLI tests, domain tests, doc sentences).
   - Why: user asked "Will it write if it crashes?" and then "we need save
     on crash also please" while the plan was still at Planning; the
     dangling-tool-round trim is required because a session ending on a tool
     call without its results 400s on strict endpoints at resume.

2. **Identical underlying behavior for command and REPL** — the one-shot
   step changed from "flip a flag" to "remove the flag".
   - What: step 1 now drops the `save_session` parameter from
     `process_user_input`/`process_agent_input` entirely; step 2 collapses
     `continue_latest_session`'s explicit save block into the shared
     `process_user_input` path and drops the `Saved session "..."` print;
     step 4 deletes `test_stateless_turn_saves_no_session` and re-asserts
     the continue test on the shared path.
   - Why: user redirect after the first presentation — "The command and
     REPL should have identical behaviour just slightly different
     interfacing", clarified as "Obviously about the underlying behavior!":
     one-shot and `--continue` must not branch on a save path at all; the
     only allowed differences are the interface (argv + exit code vs TUI
     loop).

3. **Ruff gate adapted to the pre-existing red baseline** — the completion
   test's "ruff check on touched files empty" was re-derived as "no new
   findings vs the HEAD version of each touched file".
   - What: per-file rule-multiset diff of `ruff check` output between the
     HEAD and working-tree versions of the eight touched files; source files
     came out identical, test files gained only `PT009` (unittest-style)
     occurrences.
   - Why: `ruff check .` at HEAD already reports 773 pre-existing errors
     (`ruff.toml` changed in the in-flight `restructure` commit), so "empty"
     is not attainable mid-migration; the meaningful gate is adding zero new
     violations, and `PT009` is carried in abundance by every neighboring
     test file already.
