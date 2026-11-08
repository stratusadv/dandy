# Split the CLI entry modules into single-purpose files

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-08-12-54

## End State

`dandy/interfaces/cli/` is a set of small single-concern modules — `main.py`
(bootstrap + dispatch + `main`), `one_shot.py` (the one-shot parser),
`usage.py` (usage text + banner), and `DandyCli` composed of three concern
mixins (`cli_commands.py`, `cli_sessions.py`, `cli_turn.py`) over a thin
`cli.py` core — every file under ~155 lines, with the public entry point, the
`DandyCli` surface, and the import-contract seam table unchanged, and
AGENTS.md recording small single-purpose modules (with mixin composition for
splitting classes) as the project's preferred module shape.

## Observable Concern

The refactor must be behavior-neutral: the public entry points
(`dandy.interfaces.cli.main:main`, `DandyCli` at `dandy.interfaces.cli.cli`),
the module-level names tests patch by string
(`session_name_for_request`, `question_gate` — both pinned to the `cli.cli`
namespace), and the import-linter seam table (the
interfaces-forbids-infrastructure contract matches **transitively**, which is
why `cli.cli` needs edges for `cli_agent` / `session_naming_bot`) must all
stay exact. A misplaced symbol surfaces immediately as a mock patch hitting
the wrong namespace or a contract going BOUND, so the completion test is a
pure diff-test: identical test results, identical `-h` bytes, identical
`dir(DandyCli)`, identical contracts.

## Current State

Verified by code read:

- Sizes: `cli.py` 373 lines (one module function + `DandyCli` with ~20
  methods), `main.py` 299 (env bootstrap, `OneShotPlan`, 4 parser functions,
  usage text, banner, 3 dispatch functions, `main()`), `commands.py` 82
  (registry, pure), `tui/tui.py` 203 (one cohesive class — out of scope).
- `main.py` layout: 1-32 env-file bootstrap + imports; 34-50 `OneShotPlan`;
  52-138 `_is_known_flag` / `_scan_flags` / `_plan_for` / `parse_one_shot`;
  141-182 `_usage_line` / `_usage_text` / `_USAGE` / `_print_usage`;
  185-194 `_print_banner`; 197-250 `_dispatch_repl` /
  `_dispatch_one_shot` / `_dispatch`; 253-299 `main()`.
- `cli.py` layout: `FILE_TOOL_ACTIONS` (20-25); `session_name_for_request`
  (28-38); `DandyCli` (41-373): construction
  (`__init__`, `_is_debug_enabled`, `_emit_verbose`, `_ask_user`,
  `_prompt_question`); routing (`process_user_input`); command dispatch
  (`process_command` + 5 handlers); session operations (`print_sessions`,
  `_session_row`, `load_named_session`, `run_sessions_list`,
  `run_in_session`, `run_new_one_shot`, `run_delete`,
  `continue_latest_session`); agent turn (`process_agent_input`, `run_init`);
  session persistence (`_save_session_after_turn`); REPL loop (`run`).
- Entry point: `pyproject.toml:52` `dandy = "dandy.interfaces.cli.main:main"`
  — `main` must stay importable from `main.py`.
- Import-linter: the only interface-facing contract is "Interface layer
  imports infrastructure only at documented seams" (forbidden, transitive):
  edges `cli.tui.printer -> infrastructure.llm.config`,
  `cli.cli -> application.agent.cli.cli_agent`, and
  `cli.cli -> application.agent.cli.intelligence.bots.session_naming_bot`.
  Pure-application imports (`AgentRecoverableError`, `SessionRecord`,
  `session`, `SessionStore`) need no seam (they don't reach
  infrastructure).
- Test pins: `test_main.py` imports `main as cli_main` and uses
  `cli_main.parse_one_shot` / `cli_main.OneShotPlan`; `test_cli.py` patches
  `dandy.interfaces.cli.cli.session_name_for_request` (8 sites) and
  `dandy.interfaces.cli.cli.question_gate` (1 site) — both names must keep
  living in `cli.py`'s namespace.
- House style: `Bot`'s mixin composition (each service mixin in its own
  file, mixins define no `__init__`, state lives on the owner) is the
  project's idiom for splitting a class across files.
- Docs referencing internals: `docs/reference/interfaces.md` (directives for
  `main.main` and `cli.DandyCli`; "parse_one_shot in
  dandy/interfaces/cli/main.py" in the registry paragraph),
  `docs/architecture/agents.md:226`, `AGENTS.md` (entry-point line, layer
  table row, documented-seams section, CLI bullet's parser reference).
  `getting_started` / `user_guide` make no internal-module references.
- Baseline anchors: 821 passed / 81 skipped full suite; PTY smoke 14/14;
  ruff 975 repo-wide; 6/6 contracts KEPT; strict mkdocs build passes.

## Target layout (decisions to approve)

| File                | Contents                                                                                  | ~lines |
|---------------------|-------------------------------------------------------------------------------------------|--------|
| `one_shot.py` (new) | `OneShotPlan`, `_is_known_flag`, `_scan_flags`, `_plan_for`, `parse_one_shot` — pure, imports only `commands.py` | 85     |
| `usage.py` (new)    | `_usage_line`, `_usage_text`, `_USAGE`, `_print_usage`, `_print_banner`                   | 50     |
| `main.py`           | env bootstrap, `CWD_PATH`, deferred `session`/`utils` imports, `_dispatch_repl` / `_dispatch_one_shot` / `_dispatch`, `main()` | 150    |
| `cli_commands.py` (new) | `CliCommandsMixin` — `process_command` + the five `_process_*` handlers              | 70     |
| `cli_sessions.py` (new) | `CliSessionsMixin` — `print_sessions`, `_session_row`, `load_named_session`, `run_sessions_list`, `run_delete`, `run_in_session`, `run_new_one_shot`, `continue_latest_session` | 115    |
| `cli_turn.py` (new) | `CliTurnMixin` + `FILE_TOOL_ACTIONS` — `_prompt_question`, `process_agent_input`, `run_init` | 125    |
| `cli.py`            | `DandyCli(CliCommandsMixin, CliSessionsMixin, CliTurnMixin)`: `__init__`, `_is_debug_enabled`, `_emit_verbose`, `_ask_user`, `process_user_input`, `_save_session_after_turn` + `session_name_for_request`, `run` | 130    |

Deliberately kept in the `cli.py` core: `_ask_user` (needed by `__init__`,
and keeps the `question_gate` patch target in the `cli.cli` namespace) and
`session_name_for_request` / `_save_session_after_turn` (keeps the 8 test
patch targets and the two documented seam edges on `cli.cli`, since the core
is the only module that imports `CliAgent` / `SessionNamingBot`). No new
import-linter edges are expected.

## Plan

1. **Extract `one_shot.py`**
   - Move `OneShotPlan` + the four parser functions; `main.py` imports
     them; `test_main.py` imports from the new module.
   - Done when `test_main.py` is green and `main.py` no longer defines any
     parser symbol.
2. **Extract `usage.py`**
   - Move the usage text, `_print_usage`, and `_print_banner`; `main.py`
     imports them.
   - Done when `dandy -h` output is byte-identical to the pre-refactor
     capture and `test_main.py` is still green.
3. **Split `DandyCli` into concern mixins**
   - Create `cli_commands.py`, `cli_sessions.py`, `cli_turn.py`; the
     `cli.py` core composes them and keeps the pinned names.
   - Done when `dir(DandyCli)` equals the baseline capture and
     `tests/interfaces/cli` is green with **no** test patch-path changes.
4. **Contracts and lint**
   - `lint-imports` (expect 6/6 KEPT with no new seams), `ruff check .`
     (≤ 976), `ruff format --check` on changed files.
   - Done when all three are clean.
5. **Docs**
   - `AGENTS.md`: layer-table row for `dandy/interfaces/`, the CLI bullet
     (parser now in `one_shot.py`; `DandyCli` decomposition), and a new
     Conventions & style bullet recording the preferred module shape
     (small single-purpose modules; split classes by concern via mixin
     composition, keeping public entry points at stable paths).
   - `docs/reference/interfaces.md`: registry-paragraph path fix +
     `parse_one_shot` / `OneShotPlan` directives;
     `docs/architecture/agents.md:226` touch-up; `docs/changelog/v3.md`
     bullet.
   - Done when `mkdocs build --strict` passes.
6. **Gates**
   - Full suite, PTY smoke, live `dandy -h` / `-v` / `-s` spot checks.
   - Done when everything is green with real output captured.

## Completion Test

- `PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings python -m pytest
  . -q` → the same 821 passed / 81 skipped as the baseline.
- `lint-imports` → `Contracts: 6 kept, 0 broken`.
- `ruff check .` → ≤ 976 (baseline 975); `ruff format --check` clean on the
  changed files.
- `PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings python -m
  mkdocs build --strict` → success.
- `/tmp/dandy_pty_scenarios.py` → 14/14; `dandy -h` byte-identical to the
  pre-refactor capture; `dandy -v` prints the version.
- `python -c "import dandy.interfaces.cli.main; from dandy.interfaces.cli.cli import DandyCli; print(sorted(m for m in dir(DandyCli) if not m.startswith('__')))"`
  → equal to the baseline capture.

## Deviations

- `usage.py` exposes public cross-module names `print_usage` / `print_banner`
  (renamed from the planned private `_print_usage` / `_print_banner`); `-h`
  output is byte-identical either way.
- **The `DandyCli` mixin split was reverted at the user's request** after
  being fully implemented and verified (`cli_commands.py`,
  `cli_sessions.py`, `cli_turn.py` + a thin `cli.py` core all passed
  `dir(DandyCli)` parity, 237 CLI tests, 6/6 contracts, ruff). The user
  prefers `DandyCli` back as one class in one file — mixins only when
  truly necessary, not for line-count management. `cli.py` is restored
  verbatim (373 lines), the three mixin files are deleted, and the final
  shape is: the `main.py` split stands (`one_shot.py` + `usage.py`), and
  AGENTS.md's new Module-size convention records both halves of the
  preference: split *files* by concern into single-purpose modules, but
  keep each *class* in a single file (mixin composition is for behavior
  shared across classes, the `Bot`/`LlmServiceMixin` idiom) — `DandyCli`
  is one class in `cli.py` by design.
