# CLI AGENTS.md support (read + generate)

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Implemented
- Date: 2026-11-02-11-41

## End State

`dandy` reads `<project>/AGENTS.md` (when present) into the coding and planning
agents' system prompts; `/init` (REPL) and `dandy --init` (one-shot) run an
agent pass that explores the project, reads the existing AGENTS.md when one
exists, and writes a refreshed AGENTS.md at the project root, with the updated
file effective for the next turn without needing /new.

## Observable Concern

The system message is prepended once and lives inside the agent's persistent
`MessageHistory` (saved sessions carry it too), so a mid-session refresh must
rewrite the history's system message in addition to the connector's
`system_prompt_str`; missing either leaves the old AGENTS.md on the wire.

## Current State

- CLI REPL: `DandyCli` (`dandy/interfaces/cli/cli.py:16`) — commands
  `new/sessions/resume/delete/quit` in `process_command` (line 47); one-shot +
  `--continue` in `main.py:50-108`; exit code via `last_turn_succeeded`.
- `CodingAgent` (`dandy/application/agent/coding_agent.py:14`) is a child of
  base `Agent`; `CodingBot`/`PlanningBot`
  (`dandy/application/agent/bots/`) set `role`/`task`/`guidelines` in
  `__post_init__`; `LlmService.__post_init__`
  (`dandy/application/llm/service.py:34`) builds the system prompt from those
  via `service_system_prompt` and passes it to
  `LlmConnector(system_prompt=...)`; `LlmConnector.reset()`
  (`connector.py:223-225`) keeps `system_prompt_str` across resets.
- System message: the connector prepends it only when the merged history does
  not already lead with one (`connector.py:198-199`); with
  `replace_message_history=True` it is stored in the agent's own history and
  persists across turns and saved sessions;
  `MessageHistory.has_system_message` is `messages[0].role == 'system'`
  (`message.py:189`).
- `session` singleton (`dandy/application/agent/session.py`) carries
  `project_base_path`, set in `main.py` before `DandyCli()`; the agent tools
  resolve all paths against it.
- No existing AGENTS.md awareness anywhere in `dandy/` (grep: only `.backplan/`
  docs and the repo's own AGENTS.md).
- `AGENT_TOOLS` (`tools/__init__.py:16`) = file + search + command + git tools;
  `read_file` caps output at 8000 chars — too lossy for a full-file refresh
  read, so the existing content goes into the init prompt itself.
- Hermetic test conventions: mock
  `HttpConnector.request_to_response` (e.g.
  `tests/application/agent/test_coding_agent.py`) with the
  `content_response`/`tool_call_response` helpers; `TemporaryDirectory` +
  `session.project_base_path` swap; CLI tests mock `CodingAgent.turn`
  (`tests/interfaces/cli/test_cli.py`); main tests mock `DandyCli`
  (`test_main.py`).
- Import-linter contracts tolerate everything planned (application→domain/shared
  free; interfaces→application free; no new cross-layer seams).
- The `specs/` directory referenced by the repo AGENTS.md does not exist (no
  `specs/README.md`); the de-facto planning practice in this repo is the
  `.backplan/` docs (14 in history) — this doc is the spec.
- `development.env` exists, so a live smoke in a scratch project is feasible.

## Plan

1. Core helpers + constant
   - `AGENTS_MD_FILE_NAME = 'AGENTS.md'` in `dandy/shared/constants.py` (Agent
     section); `DandyCliSession.agents_md_path` property; new
     `dandy/application/agent/agents_md.py` with `read_agents_md(path) -> str |
     None` and `agents_md_section(agents_md) -> Prompt` (a 'Project
     Instructions' sub-heading + the raw file text).
   - Done when hermetic unit tests cover absent/blank/populated reads, the
     session path property, and section rendering.
2. System-prompt injection
   - `CodingBot`/`PlanningBot` gain `build_guidelines()` that appends the
     section when the file exists; `LlmService` extracts `build_system_prompt()`
     and gains `rebuild_system_prompt()`; `CodingAgent.reload_agents_md()`
     re-runs the bot's guidelines, rebuilds the connector's prompt, and rewrites
     the running history's system message when one exists.
   - Done when a hermetic test asserts the first turn's wire system message
     contains the file's marker text, and that after rewriting the file +
     `reload_agents_md()` the next turn's wire system message carries the new
     content and not the old.
3. InitBot + prompts + pass
   - New `dandy/application/agent/bots/init_bot.py` (CODING config,
     AGENT_TOOLS); `prompts.py` gains `init_guidelines_prompt()` and
     `init_prompt(existing_agents_md)` (existing content inlined between
     delimiter lines for a full refresh, not truncated by the 8000-char read
     cap).
   - `CodingAgent.run_init_pass(progress_callback, verbose_callback) -> str |
     None` runs a fresh InitBot tool loop (capped at
     `AGENT_MAX_TOOL_ROUNDS_DEFAULT`), verifies the file exists, reloads the
     coding agent's system prompt, and returns the bot's summary.
   - Done when a hermetic test with a mocked tool loop (write_file call +
     summary response) writes AGENTS.md into the temp project, returns the
     summary, and reloads the coding bot's guidelines; and returns None when
     the file is not written.
4. CLI wiring
   - `/init` in `DandyCli` (`CLI_COMMANDS` + `_process_init` + `run_init()`
     that renders through `run_timed_task`, handles `RunStoppedError` and
     exceptions, verifies the file, and reports the byte count); `dandy --init`
     one-shot in `main.py` (same banner as one-shot, exit code from
     `run_init()`, usage when combined with a request); the welcome banner
     gains an AGENTS.md status line.
   - Done when CLI tests cover /init success + missing-file failure and main
     tests cover --init exit codes plus the usage guard.
5. Docs
   - Root `AGENTS.md` CLI bullet (commands, one-shot, banner line);
     `docs/user_guide/coding_agent.md` (new AGENTS.md section + command list);
     `docs/reference/application.md` member lists (InitBot,
     DandyCliSession); `docs/changelog/v3.md` Added entry.
   - Done when `just docs-tests` (mkdocs strict) passes.
6. Verify
   - `just test`, `ruff check .`, `ruff format .`, `just lint-imports`,
     `just docs-tests`, plus a `unittest discover` run over the new test files.
   - Live smoke in a scratch /tmp project (real keys via development.env):
     `dandy --init` creates AGENTS.md; a follow-up one-shot question about a
     fact written only in that file is answered from it.
   - Done when every command is green and the live smoke shows both the file
     and the injection evidence.

## Completion Test

1. `just test` — the suite passes including the new tests; additionally
   `python -m unittest discover -v -t . ./tests/application/agent
   ./tests/interfaces/cli` passes (both runners, per CI).
2. `ruff check . && ruff format --check . && just lint-imports && just
   docs-tests` — all clean.
3. Live smoke (scratch project, real keys): a temp project with a README + one
   module + a copied dandy_settings; `dandy --init` inside it → `AGENTS.md`
   exists with non-trivial content; then `dandy "<question whose answer is
   only in the generated AGENTS.md>"` answers from the injected content.

## Deviations

- `ruff check .` does not pass repo-wide: HEAD already carries 766 pre-existing
  violations (ruff is not a CI gate). Every violation introduced by this change
  was fixed; the files this change adds/edits pass `ruff check` and
  `ruff format --check` (verified against the diff's added lines).
- `just test` (bare `pytest .`) picks up `evals/task/`, whose hidden tests
  shell out to a bare `python` that is not on this machine's PATH (15 local
  failures, environmental). CI's hermetic gate is
  `python -m unittest discover -t . ./tests` + `python -m pytest tests -q`,
  both of which pass here (650 OK / 621 passed, 29 live-LLM skipped).
- Live smoke done in `/tmp/dandy-agentsmd-smoke`: `dandy --init` wrote a
  1406-byte AGENTS.md (exit 0); a one-shot question about a code word appended
  to that file (and nowhere else) was answered with zero tool calls, proving
  the system-prompt injection path.
