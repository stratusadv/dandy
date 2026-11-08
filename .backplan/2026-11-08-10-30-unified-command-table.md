# Unified CLI command registry (REPL commands + one-shot flags + shorthands)

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-08-10-30

## End State

One command registry in `dandy/interfaces/cli/commands.py` — one entry per
command carrying its full name, one-letter short, long flag, short flag,
argument rule, and description — drives all four surfaces: REPL dispatch
(`/name` and `/short`), tab completion and the grey inline hint, one-shot
argv parsing (`--name` / `-n`), and the usage text, so command calls and the
REPL share one source of truth. `dandy -s` (or `--sessions`) lists saved
sessions; `dandy -s <name>` resumes that session into the interactive REPL;
`dandy -s <name> "<request>"` runs one turn inside it. The REPL `/s` mirrors
that (lists; `/s <name>` resumes, aliasing `/resume`). Every command has a
one-letter short on both surfaces, all covered by hermetic tests that pass
under pytest and `unittest discover`.

## Observable Concern

The load-bearing risk is replacing `main.py`'s naive argv filter (it strips
`{'--continue', '--init'}` and joins the rest) with real flag parsing that
consumes a flag's argument (`-s <name>`, `-r <name>`, `-d <name>`) without
corrupting the one-shot request join: the request is free-form text that can
legitimately start with a dash, so the parser may only strip tokens that are
exactly known flags, and per command it must decide whether the token after
the flag is the session name or the start of the request. Second risk:
`/s <name>` in the REPL is a new alias for `/resume <name>`, and
`dandy -s <name>` with no request is a new command-call-to-REPL flow — both
need explicit tests and docs, while the existing `--continue`, `--init`,
slash-form one-shot (`dandy /sessions`), help/version, and exit-code
behaviors must be preserved unchanged.

## Current State

Verified by code read:

- `dandy/interfaces/cli/commands.py` is one line: `CLI_COMMANDS =
  ('init', 'new', 'sessions', 'resume', 'delete', 'quit')` — names only, no
  shorts, flags, or descriptions.
- `DandyCli.process_command` (`dandy/interfaces/cli/cli.py:83-107`) builds a
  static handler dict per call; `exit`/`quit`/`q` return False; unknown
  commands print an error listing `tuple(CLI_COMMANDS)`. Handlers:
  `_process_init` (no args), `_process_new(name)`, `_process_sessions()`
  (no args, prints table or empty state), `_process_resume(name)` (usage
  error without name, loads session, sets `active_name`),
  `_process_delete(name)` (usage error without name).
- `main()` (`dandy/interfaces/cli/main.py:56-111`): `-h/--help` and
  `-v/--version` handled first; one-shot = `[arg for arg in sys.argv[1:] if
  arg not in {'--continue', '--init'}]` joined with spaces; `--init` plus a
  request prints usage; no arguments prints usage; dispatch is
  `cli.run_init()` / `cli.continue_latest_session(user_input)` /
  `cli.process_user_input(user_input)` with the exit code taken from
  `last_turn_succeeded`. A bare `--continue` with no request prints usage.
- Slash-form one-shot already works: `dandy /sessions` joins to `/sessions`
  and routes through `process_user_input` -> `process_command` — the
  "seamless flow" to preserve and document.
- TUI (`dandy/interfaces/cli/tui/tui.py`): `_command_matches` (175-182) and
  `_process_tab_key` (138-165) match full names only over `CLI_COMMANDS`;
  `_suggestion_text` (184-201) renders `'  ' + '   '.join(f'/{match}')`
  with a whole-line `term.length` fit gate, drawn in `term.grey`.
- Tests: `tests/interfaces/cli/test_cli.py:392-565` (command dispatch,
  resume, delete, unknown command, quit, `continue_latest_session`),
  `tests/interfaces/cli/test_main.py:14-256` (help, version, one-shot,
  continue, init, usage), `tests/interfaces/cli/test_tui.py` (inline grey
  suggestion, tab completion, screen-state tests).

## Registry Design (decisions to approve)

`commands.py` gains a frozen dataclass `CliCommand(name, short, flag,
short_flag, takes_argument, description)`; `CLI_COMMANDS` becomes the
six-entry registry (it stays an interface-layer leaf — no new imports, so
`cli.py`, `tui.py`, and `main.py` all keep importing it without a cycle;
handlers stay bound on `DandyCli` at dispatch time, never in the registry):

| Command  | Short | Long flag  | Short flag | Argument      |
|----------|-------|------------|------------|---------------|
| `init`   | `i`   | `--init`   | `-i`       | none          |
| `new`    | `n`   | `--new`    | `-n`       | optional name |
| `sessions` | `s` | `--sessions` | `-s`     | optional name |
| `resume` | `r`   | `--resume` | `-r`       | required name |
| `delete` | `d`   | `--delete` | `-d`       | required name |
| `quit`   | `q`   | —          | —          | none          |

Judgment call: `quit` gets no one-shot flags — a one-shot process has no
loop to quit, so `dandy -q` / `--quit` fall through to usage. The other five
commands get long + short flags (full parity).

### REPL semantics (name or short accepted; `/exit` and `/quit` unchanged)

- `/i`, `/init` — AGENTS.md generation pass.
- `/n [name]`, `/new [name]` — new conversation, optionally pre-named.
- `/s [name]`, `/sessions [name]` — no name: print the sessions table
  (today's behavior); with a name: same as `/resume <name>` (the new dual
  behavior; unknown name reports the existing "Could not resume session"
  error).
- `/r <name>`, `/resume <name>` — resume (usage error without a name).
- `/d <name>`, `/delete <name>` — delete (usage error without a name).
- `/q`, `/quit`, `/exit` — stop the loop.
- Unknown command — error message lists every command as `/name (or /short)`,
  generated from the registry.

### One-shot semantics (flags scanned anywhere in argv)

- `dandy --sessions` / `-s` — print the sessions table, exit 0.
- `dandy -s <name>` (no request) — resume that session into the interactive
  REPL (the command-call-to-REPL flow); unknown name prints the error, exit
  1.
- `dandy -s <name> "<request>"` — resume that session, run one turn, auto-
  save, exit with the turn's code.
- `dandy --resume <name>` / `-r <name>` — identical to `-s <name>`; the name
  is required, so a bare `dandy -r` prints usage.
- `dandy --new [name] "<request>"` / `-n` — one turn in a fresh conversation
  (name pre-set when given); `dandy -n <name>` with no request starts the
  REPL with a pre-named fresh conversation; bare `dandy -n` is the plain
  REPL.
- `dandy --delete <name>` / `-d <name>` — delete, exit 0/1; a request is
  never consumed, extra tokens print usage.
- `dandy --init` / `-i` — today's behavior (any request alongside it prints
  usage).
- `--continue "<request>"` is unchanged (resume the latest session + one
  turn); a bare `--continue` still prints usage.
- Slash-form one-shot (`dandy /sessions`, `dandy /s <name>`, ...) keeps
  working: anything not consumed as a flag joins into the request and routes
  through `process_user_input`.
- Two or more action flags (`-s x -r y`, `--continue --init`) print usage.

### Flag-argument rule (the tricky part)

Only a token that exactly equals a known long/short flag is a flag; every
other token (including unknown dash tokens) stays in the request —
preserving today's pass-through. `resume` and `delete` always consume the
next token as the name (usage error if none remains). For `sessions` and
`new`: if one token remains after the flag it is the session name (→ REPL
resume / pre-named REPL); if two or more remain, the first is the name and
the rest is the request; if none remains, the flag stands alone (→ table /
plain REPL). So `dandy -n "fix the bug"` creates a session named "fix the
bug" and opens the REPL (git-style `checkout -b` convention) — explicit
naming needs `-n <name> "<request>"`.

### Completion, hint, usage

- Tab and the grey hint resolve a typed prefix against full names AND
  one-letter shorts, deduplicated to distinct commands; tab completes to the
  full name when exactly one command matches (typing `/s` + Tab yields
  `/sessions`); the hint keeps showing full names only (typing `/i` shows
  `  /init`).
- The usage text is generated from the registry (one line per command with
  its flags, argument shape, and description, plus the REPL command list
  with shorts), so the table cannot drift from behavior.

## Plan

1. `commands.py`: `CliCommand` dataclass, the six registry entries, and
   helpers (`resolve(name_or_short)`, `commands_matching_prefix(prefix)`,
   `flag_lookup()` mapping each long/short flag to its command,
   `command_choices()` for the unknown-command/usage text).
   Done when: the module is still an importable leaf with no new imports and
   the helpers are directly unit-testable.
2. `cli.py`: `process_command` dispatches through the registry (full name or
   short; the `sessions` handler takes the optional name and delegates to a
   shared `load_named_session(name) -> bool` core also used by
   `_process_resume`); `exit`/`quit`/`q` unchanged; unknown-command message
   generated from the registry.
   Done when: existing command tests pass plus new short-form and
   `/s <name>` resume tests.
3. `main.py`: registry-driven one-shot parser (flag scan, the argument rule
   above, usage on bad combos); dispatch to one-shot methods on `DandyCli`
   (`run_sessions_list`, `run_in_session(name, request)`,
   `run_delete(name)`, plus `run()` gaining optional resume/new pre-load for
   the command-call-to-REPL flows); `_USAGE` generated from the registry.
   Done when: `test_main.py` is extended for every flag and the old
   behaviors (help/version/`--continue`/`--init`/slash-form/no-args/exit
   codes) are unchanged.
4. `tui.py`: `_command_matches` and `_process_tab_key` match names and
   shorts and complete to full names; `_suggestion_text` format unchanged
   (full names, grey, whole-line fit gate).
   Done when: `test_tui.py` gains short-prefix hint and short-tab tests and
   the existing screen tests still pass.
5. Tests: `test_cli.py` (short dispatch, `/s <name>` resume, unknown-command
   wording), `test_main.py` (every long/short flag, argument consumption,
   usage combos), `test_tui.py` (completion with shorts).
   Done when: `tests/interfaces/cli` is fully green under pytest.
6. Docs: `AGENTS.md` CLI bullet (registry, shorthand table, `-s`/`/s`
   semantics, flag table) and `docs/user_guide/cli_agent.md` (shorthand +
   `-s` usage lines); check `docs/reference/` for a `commands.py` member
   list to keep in sync.
   Done when: `just docs-tests` is green.
7. Gates: `just test` (background), `just lint-imports`, `just docs-tests`,
   `ruff check` (expect only the 15 baseline violations) and `ruff format
   --check`; PTY smoke of the real binary (`dandy -s` prints the table; REPL
   `/s` lists and `/s <name>` resumes).
   Done when: every gate is green and the PTY smoke passes.

## Completion Test

- `dandy -s` in a scratch project (subprocess/PTY) prints the sessions table
  and exits 0; `dandy -s <name>` opens the REPL with that session loaded
  (session banner shows the resumed name); `dandy -s <name> "ping"` runs one
  turn inside it and exits with the turn's code.
- REPL (`test_cli.py`): `/i`, `/n x`, `/s`, `/s <name>` (loads the session),
  `/r <name>`, `/d <name>`, and `/q` all dispatch correctly; an unknown
  command lists names with shorts.
- `test_main.py`: every command's long and short flag, the argument-
  consumption rule, `--init`/`--continue`/slash-form/no-args preserved,
  usage on bad combos.
- `test_tui.py`: hint for `/i` shows `/init`; Tab on `/s` completes to
  `/sessions`.
- `just test` (full suite), `just lint-imports` (6 contracts KEPT),
  `just docs-tests`, `ruff check` (baseline only) + `ruff format --check`,
  and the PTY smoke above all green.

## Deviations

- `CliCommand`'s argument field is `argument` with values `'none'` /
  `'optional'` / `'required'` instead of the sketch's `takes_argument` bool —
  the parser needs all three states (the bool cannot tell required from
  optional).
- Two helpers beyond the step-1 list: `flag_usage(command)` renders the
  one-shot flag forms for the generated usage text (used in
  `main._usage_text`), and `command_choices()` also feeds the
  unknown-command message. A `repl_usage()` variant was added mid-build and
  removed in review (the usage text's REPL list is a prose paragraph, not
  per-command lines, so nothing called it).
- The command-call-to-REPL resume flow does not extend `run()` with a
  resume parameter: `main._dispatch_repl` calls
  `cli.load_named_session(name)` and then `cli.run()`; only the pre-named
  new-conversation flow takes a `run(new_name=...)` parameter, matching
  `_process_new`'s shape. In review the dispatcher split into
  `_dispatch_repl` + `_dispatch_one_shot` behind a small `_dispatch`
  entry (branch-count limit), and `run_new_one_shot`'s name parameter is
  `str | None` (a bare `dandy -n "<request>"` has no name).
- The usage text's REPL command list is a prose paragraph with the shorts
  inlined rather than one generated line per command; the generated lines
  cover the one-shot flags only.
