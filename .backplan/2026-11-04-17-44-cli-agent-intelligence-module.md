# cli-agent-intelligence-module

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-04-17-44

## End State
The CLI-specific agent logic lives under `dandy/application/agent/cli/` —
`cli_agent.py` holds `CliAgent` (renamed from `CodingAgent`),
`cli/intelligence/` holds the three CLI bots (`bots/`) and the four CLI
prompts (`prompts.py`), and `agents_md.py` holds the AGENTS.md helpers — the
universal tools live in the agent-level `intelligence/` package
(`intelligence/tools/`), and `session.py` stays with the generic core
(`agent.py`, `exceptions.py`, `intel.py`, `session_store.py`, `prompts.py`
with only `continuation_prompt`) at the `application/agent/` top level; tests
mirror the layout under `tests/application/agent/cli/` and
`tests/application/agent/intelligence/tools/`, `grep -rn
"coding_agent\|CodingAgent" dandy/ tests/ pyproject.toml` returns nothing,
and the hermetic suite, `just lint-imports`, and `just docs-tests` are all
green.

## Observable Concern
The move and rename touch exactly the places where consumers pin symbols by
string: ~30 `mock.patch('dandy.application.agent.coding_agent...')` targets in
`tests/interfaces/cli/`, the two exact module edges in the import-linter
`ignore_imports` seam list, and the six mkdocstrings directives in
`docs/reference/application.md`. A single stale reference fails silently or
loudly in three different ways: a mock that patches nothing (the test stays
green while the real code runs), a broken contract edge (`just lint-imports`
red), or a strict docs build failure — so every consumer must be re-pointed in
the same change as the move it depends on.

## Current State
Verified 2026-11-04, branch `v3/base`:
- `dandy/application/agent/` mixes a generic core and a CLI slice that do not
  entangle (nothing in the generic core imports the CLI side):
  - Generic (consumed by the base `Agent` and/or any consumer): `agent.py`
    (the public `dandy.Agent`), `exceptions.py`, `intel.py`, `session_store.py`,
    and `prompts.py` — only `continuation_prompt` (consumed by `agent.py`).
  - CLI-only (every consumer is the CLI agent, the CLI interface, or another
    CLI piece): `coding_agent.py` (`CodingAgent`, consumed by
    `dandy/interfaces/cli/cli.py:4`), `bots/coding_bot.py` (consumed only by
    `CodingAgent`), `bots/init_bot.py` (consumed only by
    `CodingAgent.run_init_pass`), `bots/session_naming_bot.py` (consumed only
    by `dandy/interfaces/cli/cli.py:3` — a documented seam), `tools/**` (the
    whole `AGENT_TOOLS` tree: `file/` with 7 tools, `command/`, `git/`,
    `question/`, plus `paths.py` and `tool_errors.py`; consumed by
    `CodingBot`, `InitBot`, `CodingAgent`,
    `dandy/interfaces/cli/tui/tui.py:6` for `QuestionTool`, and tests),
    `agents_md.py` (consumed only by `CodingAgent` + `CodingBot`), and
    `session.py` (the `DandyCliSession` intel + the `session` singleton — the
    base `Agent` never touches it; consumed by the CLI bots/tools and by
    `interfaces/cli`'s `main.py`, `cli.py`, `tui/printer.py`, `tui/text.py`).
    Fact for the redirect: the tools also import `session` — `tools/paths.py`
    (used by every file tool), `command/command_tool.py`, and both `git/`
    tools resolve against `session.project_base_path` — so the tools'
    universality depends on `session` staying reachable at the agent level.
- `dandy/application/agent/__init__.py` and `bots/__init__.py` are empty
  files; `tools/__init__.py` assembles `AGENT_TOOLS` and re-exports the tool
  classes; `bots/` has no re-exports (importers go to module paths directly).
- `CodingAgent` is **not** in the public root API (`dandy/__init__.py`
  verified: it exports `Agent` only), so the rename and move are internal —
  no `from dandy import ...` breakage.
- `prompts.py` holds `continuation_prompt` (generic) plus the four CLI prompts
  (`coding_guidelines_prompt`, `init_guidelines_prompt`, `init_prompt`,
  `session_name_prompt`) and their three private section helpers
  (`_paths_section`, `_narration_section`, `_tool_calling_section`) — all
  helpers are CLI-only.
- Seam edges in `pyproject.toml` (`ignore_imports`, exact
  `source -> imported` pairs): `dandy.interfaces.cli.cli ->
  dandy.application.agent.coding_agent` and `dandy.interfaces.cli.cli ->
  dandy.application.agent.bots.session_naming_bot`. The
  `tui.py -> tools.question.question_tool` edge is interfaces → application,
  which is permitted without a seam entry. No new cross-layer edge is
  introduced by the move (everything moves within application).
- Test files: CLI-only (`test_coding_agent.py`, `test_coding_bot.py`,
  `test_init_bot.py`, `test_session_naming_bot.py`, `test_agents_md.py`,
  `test_session.py`, `test_file_tools.py`, `test_agent_tools.py`,
  `test_question_tool.py`) versus generic (`test_agent.py`,
  `test_agent_skills.py`, `test_session_store.py`). The shared fixture
  `tests/application/agent/intelligence/llm_responses.py` is imported by both
  sides through the absolute path `tests.application.agent.intelligence.llm_responses`
  — it stays where it is, so moving the CLI tests changes no fixture imports.
- Out-of-set importers of moved modules: `dandy/interfaces/cli/` — `cli.py`
  (SessionNamingBot, CodingAgent), `main.py` (session), `tui/printer.py`
  (session), `tui/text.py` (session), `tui/tui.py` (QuestionTool);
  `tests/interfaces/cli/` — `test_cli.py` (QuestionTool import + ~28
  `mock.patch` strings), `test_error_log.py` (2 `mock.patch` strings),
  `test_printer.py` / `test_markdown.py` (session); and
  `tests/application/tool/test_service.py` (EditFileTool import + session).
- Docs that pin the old paths: `docs/reference/application.md` (six
  directives: `CodingAgent`, `DandyCliSession`, `read_agents_md`,
  `agents_md_section`, `CodingBot`, `InitBot` — no `SessionNamingBot`
  directive exists), `docs/user_guide/coding_agent.md` (+ the nav entry at
  `mkdocs.yml:57`), `docs/architecture/agents.md` (lines 141, 159, 171, 177),
  `docs/architecture/layering.md` (lines 105-106),
  `docs/reference/interfaces.md` (line 21), `AGENTS.md` (package-map line 72,
  agent-convention line 122, tool-calling bullet line 169, agent bullet line
  187, CLI bullet line 234), and `docs/changelog/v3.md` (the unreleased
  v3.1.0 section references `bots/init_bot.py` line 114 and
  `tools/question/question_tool.py` line 123 — updatable in place; v3.0.0
  entries are historical).
- A stale comment at `dandy/application/tool/service.py:27` cites the pre-v3
  path `dandy/cli/intelligence/coding_agent.py` — grouping the LLM-facing
  parts under an `intelligence` module is the project's own prior convention
  (v2), and the test fixtures already use `intelligence/` directories.
- The tree carries the user's parallel WIP (printer divider renames, the
  non-question prefix hunk in `tui.py`) — untouched by this plan.

## Plan
1. Rename `CodingAgent` to `CliAgent` in place
   - `git mv dandy/application/agent/coding_agent.py dandy/application/agent/cli_agent.py`;
     the class becomes `CliAgent`; update `dandy/interfaces/cli/cli.py` (import
     + the `CodingAgent(ask_user=...)` construction); rename the test file
     `test_coding_agent.py` → `test_cli_agent.py` and its test classes
     (`TestCodingAgentMultiTurn` → `TestCliAgentMultiTurn`,
     `TestCodingAgentCompaction` → `TestCliAgentCompaction`,
     `TestCodingAgentQuestionTool` → `TestCliAgentQuestionTool`); re-point
     every import and every `mock.patch('...coding_agent...')` string
     (`tests/interfaces/cli/test_cli.py` ~28, `tests/interfaces/cli/test_error_log.py`
     2, `tests/application/agent/test_init_bot.py`).
   - Done when `grep -rn "CodingAgent" dandy/ tests/` is empty and
     `just test-app` is green for `tests/application/agent/test_cli_agent.py`
     and `tests/interfaces/cli`.
~~2. Move the CLI slice into `application/agent/cli/` with an `intelligence/` package~~
~~   (superseded by deviation 1: `intelligence/` holds only the universal tools at the agent level; the CLI-specific pieces go to `cli/`; `session.py` stays put)~~
2. Move the CLI slice into `cli/` and the universal tools into `intelligence/`
   - ~~`git mv`: `tools/` → `intelligence/tools/` (the whole tree; empty
     `intelligence/__init__.py` in the existing `bots/__init__.py` style),
     `cli_agent.py` → `cli/cli_agent.py`, `bots/` → `cli/bots/`,
     `agents_md.py` → `cli/agents_md.py`; `session.py` stays at the agent
     level; create `cli/__init__.py`.~~ (superseded by deviation 2: the bots
     and prompts sit in their own `cli/intelligence/`)
   - `git mv`: `tools/` → `intelligence/tools/` (the whole tree; empty
     `intelligence/__init__.py` in the existing `bots/__init__.py` style),
     `cli_agent.py` → `cli/cli_agent.py`, `bots/` → `cli/intelligence/bots/`,
     `agents_md.py` → `cli/agents_md.py`; `session.py` stays at the agent
     level; create `cli/__init__.py` and `cli/intelligence/__init__.py` (both
     empty).
   - ~~Split `prompts.py`: the four CLI prompts plus their three private
     section helpers move to `cli/prompts.py`; the top-level `prompts.py`
     keeps only `continuation_prompt`.~~ (superseded by deviation 2)
   - Split `prompts.py`: the four CLI prompts plus their three private
     section helpers move to `cli/intelligence/prompts.py`; the top-level
     `prompts.py` keeps only `continuation_prompt`.
   - Re-point every import inside the moved modules and in the remaining
     consumers: the five `dandy/interfaces/cli/` files,
     `tests/application/tool/test_service.py`, the test files that stay
     (`test_cli.py`, `test_error_log.py`, `test_printer.py`,
     `test_markdown.py`), and the two seam edges in `pyproject.toml`, which
     become `dandy.interfaces.cli.cli -> dandy.application.agent.cli.cli_agent`
     and `dandy.interfaces.cli.cli ->
     dandy.application.agent.cli.intelligence.bots.session_naming_bot` (the
     mock `patch`
     strings get their module path re-pointed again on top of the step-1
     class rename).
   - Update the stale `dandy/cli/intelligence/coding_agent.py` comment in
     `dandy/application/tool/service.py:27` to the new path.
   - Done when `DANDY_SETTINGS_MODULE=tests.dandy_settings .venv/bin/python -c
     "import dandy.interfaces.cli.main"` is clean, `just lint-imports` is
     green, and `just test-app` is green for `tests/application/agent` and
     `tests/interfaces/cli`.
~~3. Mirror the tests to `tests/application/agent/cli/`~~
~~   (superseded by deviation 1: the tool tests mirror to `intelligence/tools/`)~~
3. Mirror the tests to `cli/` and `intelligence/tools/`
   - `git mv` the five CLI test files (`test_cli_agent.py`, `test_coding_bot.py`,
     `test_init_bot.py`, `test_session_naming_bot.py`, `test_agents_md.py`)
     into `tests/application/agent/cli/` and the three universal-tool test
     files (`test_file_tools.py`, `test_agent_tools.py`,
     `test_question_tool.py`) into
     `tests/application/agent/intelligence/tools/`, each with an
     `__init__.py` (unittest discovery requires the package chain); re-point
     their imports to the new module paths. `test_session.py` stays at the
     agent level (it tests `DandyCliSession`, which does not move).
   - Done when `just test-app tests/application/agent` and
     `just test-app tests/interfaces/cli` are green.
4. Docs
   - `docs/reference/application.md`: re-point the six directives to the new
     paths, one-for-one (no new directives added).
   - `docs/user_guide/coding_agent.md` → `cli_agent.md` (rename the file,
     update the in-page paths and the pipeline diagram, rename the `mkdocs.yml`
     nav entry); `docs/architecture/agents.md` (the CodingAgent section, the
     bots/agents_md/tools path lines) and `docs/architecture/layering.md`
     (the agent bullet); `docs/reference/interfaces.md` (the `CodingAgent`
     mention).
   - `AGENTS.md`: rewrite the clauses that name the moved paths — the package
     map row (line 72), the agent-exception convention line (line 122), the
     tool-calling bullet's "Every CLI tool (`dandy/application/agent/tools/`)"
     clause (line 169), the agent bullet's `CodingAgent` sentence (line 187),
     and the CLI bullet (line 234, the biggest — verify each clause with
     `grep -c` immediately before editing the giant one-line bullets).
   - `docs/changelog/v3.md` v3.1.0 (unreleased): update the two in-place path
     references (lines 114, 123) and add one Changed entry documenting the
     move and the `CodingAgent` → `CliAgent` rename; v3.0.0 entries stay
     historical.
   - Done when `just docs-tests` (strict mkdocs build) passes.
5. Gate
   - `ruff check` + `ruff format --check` on every touched file (no NEW
     findings — the branch carries ~1145 pre-existing), full `just test`
     (backgrounded; rerun once on a known flake before marking executed),
     `just lint-imports`, `just docs-tests`, and the final
     `grep -rn "coding_agent\|CodingAgent" dandy/ tests/ pyproject.toml` plus
     `grep -rn "application.agent.bots\|application.agent.tools" dandy/ tests/
     pyproject.toml` (both must be empty).
   - Done when every gate is green and both greps are empty.

## Completion Test
```bash
cd /home/nathanj/PycharmProjects/dandy
grep -rn "coding_agent\|CodingAgent" dandy/ tests/ pyproject.toml
# expect: no matches
grep -rn "application.agent.bots\|application.agent.tools" dandy/ tests/ pyproject.toml
# expect: no matches
DANDY_SETTINGS_MODULE=tests.dandy_settings .venv/bin/python -c \
  "import dandy.interfaces.cli.main; from dandy.application.agent.cli.cli_agent import CliAgent; from dandy.application.agent.intelligence.tools import AGENT_TOOLS"
just test-app tests/application/agent
just test-app tests/interfaces/cli
just test
just lint-imports
just docs-tests
```
All green, the tree shows `dandy/application/agent/cli/` (`cli_agent.py`,
`agents_md.py`, and `intelligence/` holding `bots/` + `prompts.py`) and
`dandy/application/agent/intelligence/tools/` (the universal tools), and the
CLI imports cleanly under the new names.

## Assumptions (flagged)
- The class name is `CliAgent` in `cli_agent.py` (per the request).
- There are **two `intelligence/` packages** (per the user): the universal
  one at the `application/agent/` level holds the shared tools under
  `intelligence/tools/` (the tools are shared — multiple bots, the generic
  `ToolService` tests, and any library `Agent` can use them), and the CLI one
  at `cli/intelligence/` holds the three CLI bots (`bots/`) and the four CLI
  prompts (`prompts.py`), which are consumed only by the CLI pieces.
  `agents_md.py` (a file-I/O helper consumed only by `CliAgent` +
  `CodingBot`) goes to `cli/` directly — it is a file helper, not a
  bot/prompt/tool.
- `session.py` (`DandyCliSession`) stays at the `application/agent/` level
  rather than moving to `cli/`: the universal tools' `paths.py`, `command/`,
  and `git/` modules resolve every path through `session.project_base_path`,
  so moving it under `cli/` would make the universal layer depend on the CLI
  subpackage. The class name is kept as-is (a rename is out of scope).
- `prompts.py` splits on the verified consumer boundary:
  `continuation_prompt` stays generic, the other four prompts plus their
  private helpers move to `cli/prompts.py`.
- The user-guide page is renamed `coding_agent.md` → `cli_agent.md` (nav
  updated); the reference directive set is re-pointed one-for-one with no new
  directives (`SessionNamingBot` remains undirected, as today).
- Historical v3.0.0 changelog entries and existing `.backplan/` docs keep the
  old names — history is never rewritten; only the unreleased v3.1.0 section
  changes.
- The pre-existing stale path comment in `tool/service.py:27` is updated as a
  drive-by (it names the same symbol being moved).

## Deviations
1. `intelligence/` placement revised after user redirect
    - What: `intelligence/` moves from under `cli/` to the `application/agent/`
      level and holds only the universal tools (`intelligence/tools/`); the
      bots, the four CLI prompts, `agents_md.py`, and `cli_agent.py` go to
      `cli/`; `session.py` stays at the agent level (steps 2-3 struck through
      above and re-derived).
    - Why: user redirect — the tools are shared/universal, not CLI-specific,
      so they belong at the agent level; `cli/` carries only the CLI-specific
      pieces. `session.py` cannot follow into `cli/` because the universal
      tools resolve paths through `session.project_base_path` — putting it
      under `cli/` would make the universal layer depend on the CLI subpackage.
2. The CLI bots and prompts get their own `intelligence/` inside `cli/`
    - What: `cli/bots/` becomes `cli/intelligence/bots/` and `cli/prompts.py`
      becomes `cli/intelligence/prompts.py`; a second `intelligence/` package
      now exists (deviation 1's step-2 bullets struck through and re-derived).
      The test layout is unchanged — the CLI bot tests stay flat in
      `tests/application/agent/cli/`, matching the existing flat bot-test
      convention (`bots/coding_bot.py` is tested by a flat
      `test_coding_bot.py` today).
    - Why: user redirect — the `intelligence` grouping applies at both
      levels: universal LLM-facing parts under `agent/intelligence/`,
      CLI-specific LLM-facing parts under `cli/intelligence/`.
3. The stale `service.py` comment points at the base `agent.py`, not the moved file
    - What: step 2's bullet said to update the `dandy/application/tool/service.py:27`
      comment "to the new path"; the comment instead now cites
      `dandy/application/agent/agent.py (0.70)`, because the `0.70` constant it
      references (`AGENT_COMPACTION_TARGET_RATIO`) is defined in the base
      `agent.py`, which was not moved.
    - Why: the plan bullet assumed the constant lived in the moving file; it
      does not, so pointing the comment at the moved file would have made it
      wrong.

## Observed Output
Run 2026-11-04, branch `v3/base` (nothing committed). First the grep noise
was purged — stale `__pycache__/` bytecode (including
`dandy/application/agent/__pycache__/coding_agent.cpython-31{1,3}.pyc`) and a
`tests/.dandy/recordings/` HTML artifact from a v2-era live run; both are
gitignored, untracked, and predate this change.

Completion greps:
```
$ grep -rn "coding_agent\|CodingAgent" dandy/ tests/ pyproject.toml
(no output, exit 1)
$ grep -rn "application.agent.bots\|application.agent.tools" dandy/ tests/ pyproject.toml
(no output, exit 1)
```

Import smoke:
```
$ DANDY_SETTINGS_MODULE=tests.dandy_settings PYTHONPATH=. .venv/bin/python -c \
    "import dandy.interfaces.cli.main; from dandy.application.agent.cli.cli_agent import CliAgent; from dandy.application.agent.intelligence.tools import AGENT_TOOLS; print('IMPORT SMOKE OK', len(AGENT_TOOLS))"
IMPORT SMOKE OK 10
```

Full hermetic suite, `just test` (supersedes the two `just test-app` runs):
```
================= 758 passed, 81 skipped in 205.48s (0:03:25) ==================
```
No flake on this run.

Architecture contracts, `just lint-imports`:
```
Domain layer must not import outer layers KEPT
Shared kernel must not import any layer KEPT
Application layer must not import interface layer KEPT
Infrastructure layer must not import application or interface layers KEPT (3 ignored imports)
Application layer imports infrastructure only at documented seams KEPT (21 ignored imports)
Interface layer imports infrastructure only at documented seams KEPT (3 ignored imports)

Contracts: 6 kept, 0 broken.
```

Strict docs build, `just docs-tests`:
```
INFO    -  Documentation built in 1.00 seconds
```
Built output check: `site/reference/application/index.html` renders `CliAgent`
(17 occurrences) and `cli.intelligence.bots` (42) with zero `CodingAgent` /
`coding_agent` mentions; `site/user_guide/cli_agent.html` exists.

Ruff on the 46 touched `.py` files: 94 findings, all present at HEAD
(verified per file via `git show HEAD:<oldpath>` + `ruff format
--stdin-filename`). The only three findings introduced by this change —
E501s on the re-pointed import lines in
`intelligence/tools/__init__.py`, `intelligence/tools/file/__init__.py`, and
`intelligence/tools/question/__init__.py` — were fixed with `ruff format`,
which now passes on all four affected files (the fourth,
`tests/interfaces/cli/test_error_log.py`, had a format delta in the
re-pointed `mock.patch` decorator). The remaining 4 format-check failures
(`session_naming_bot.py`, `edit_file_tool.py`,
`test_session_naming_bot.py`, `test_file_tools.py`) fail identically at HEAD
and were left as-is.
