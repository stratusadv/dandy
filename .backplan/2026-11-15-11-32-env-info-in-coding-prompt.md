# Environment info in the CLI coding prompt

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-15-11-32

## End State
The CLI coding agent's system prompt (CodingBot guidelines) contains a compact,
static "Environment" section — host OS/user/Python, project root, top-level
directory listing, detected manifests (pyproject.toml, package.json, justfile,
Makefile, requirements.txt), and git branch/dirty status — captured once per
conversation so the agent understands the project without spending tool rounds.

## Observable Concern
The git/subprocess lookups run inside prompt construction (bot init and the
first turn after `/new`); they must be bounded (short timeouts, no raises, no
network) so `CodingBot()` never hangs or crashes in a project with a broken or
absent repo.

## Current State
- `CodingBot` (`dandy/application/agent/cli/intelligence/bots/coding_bot.py`)
  builds guidelines in `build_guidelines()`: `coding_guidelines_prompt()` + the
  AGENTS.md "Project Instructions" section; `__post_init__` calls it and
  `CliAgent.reload_agents_md` (init pass) re-runs it.
- Guidelines come from `coding_prompts.py`, composed of section helpers:
  `_paths_section`, `_narration_section`, `_tool_calling_section`.
- `session.project_base_path` (`dandy/application/agent/session.py`) holds the
  project root; `session.agents_md_path` is the pattern to follow.
- `run_subprocess` (`dandy/shared/subprocess.py`) always prefixes output with
  an "Exit code: N" line and never raises — but the exit-code prefix is noise
  for prompt content, so the environment collector calls `subprocess.run`
  directly with short timeouts inside its own try/except (the shared helper's
  contract is aimed at the tool layer).
- The system message is (re)built at the first turn of each conversation
  (history is reset by `/new` / `clear()`), so a snapshot captured during
  guideline construction is effectively once-per-conversation — matching the
  "static" choice; the CLI process re-builds it for each process start anyway.
- Tests: `tests/application/agent/cli/test_coding_bot.py` swaps
  `session.project_base_path` to a temp dir — same pattern for env tests.
- Layering: `dandy/application/agent/cli/` already uses `dandy.shared.*`
  directly; a new `environment.py` there importing `subprocess`/`platform`/
  `sys` + `dandy.shared` is contract-clean.
- Scope decision (confirmed with user): static snapshot, host + project info,
  CodingBot only — the InitBot prompt is untouched (it is meant to explore,
  not be told).

## Plan
1. Environment collector + section
   - New `dandy/application/agent/cli/environment.py`:
     `collect_environment() -> dict[str, str]` (os description via
     `platform.platform()`, username via `os.getlogin()`/`os.environ`, Python
     version, venv status via `sys.prefix` vs `sys.base_prefix`, project root,
     top-level listing hiding noise dirs: `.git`, `.venv`, `node_modules`,
     `__pycache__`, `.hypothesis`, `.dandy`; manifest presence + Python
     `requires-python`/package `name`/`version` when cheaply readable; git
     branch + short dirty status via bounded `git rev-parse`/`git status`
     calls with ~5s timeouts, each failure → `'not a git repository'` or
     omitted line, never a raise) and `environment_section() -> Prompt`
     rendering a `### Environment` sub-heading with a compact key: value list.
   - Done when `environment_section()` renders the section for a temp project
     (git and non-git, with and without manifests) without raising.
2. Wire into the coding guidelines
   - `coding_prompts.py`: `coding_guidelines_prompt(environment: Prompt | None
     = None)` — when given, insert the environment section right after
     `_paths_section()` (before "Editing Code").
   - `coding_bot.py`: `build_guidelines()` passes
     `environment_section()` (or `None` when collection yields nothing).
   - Done when a constructed `CodingBot().guidelines.to_str()` contains the
     "Environment" section on a temp project with `session.project_base_path`
     swapped.
3. Hermetic tests
   - New `tests/application/agent/cli/test_environment.py`: temp-dir cases —
     non-git project (section renders without git lines), git project with a
     staged change (branch + dirty line present), manifest parsing
     (pyproject.toml + package.json), noise dirs hidden, missing project root
     (no raise, section still renders).
   - Extend `test_coding_bot.py` with one assertion that guidelines include
     the "Environment" section.
   - Done when `python -m pytest tests/application/agent -q` and
     `python -m unittest discover -v -t . ./tests` both pass.
4. Lint, docs, close-out
   - `ruff check .` + `ruff format --check .` clean on touched files.
   - Update `docs/user_guide/` coding-agent page + `docs/changelog/v3.md` if
     they describe the coding prompt composition; `just docs-tests` passes.
   - Done when lint + strict docs build pass; plan doc set to Executed.

## Completion Test
1. `python -m pytest tests/application/agent -q` → all pass.
2. `python -m unittest discover -v -t . ./tests` (hermetic, placeholder key) → 0 failures.
3. `ruff check .` → clean.
4. Manual render check: in this repo,
   `python -c "from dandy.application.agent.cli.environment import environment_section; print(environment_section().to_str())"`
   shows OS/Python/project/git lines.

## Deviations
1. Fixed pre-existing broken imports in the un-staged working tree
    - What: `session_naming_bot.py` imported `session_name_prompt` from the
      package `__init__` (got the module, called it → `TypeError`);
      `cli_agent.py` / `test_init_bot.py` called `init_prompts(...)` which does
      not exist (the function is `init_prompt`); five prompt-module files used
      `from dandy import Prompt` inside the framework (forbidden root import).
      All now import the defining module's full path / correct function name.
    - Why: these made 9 hermetic tests fail before this work started (verified
      by stash/restore); the test suite had to be green to validate the
      environment section, and the import rules make the root imports a
      contract violation.
2. Dropped the manifest-detail lines (pyproject.toml / package.json)
    - What: removed `_python_manifest_info` / `_node_manifest_info` and their
      tests; the section now carries host env, top-level listing, build
      tooling, and git only. Changelog entry updated.
    - Why: user wanted the section to stay language-agnostic — early
      direction and project structure, not per-ecosystem manifest parsing.
