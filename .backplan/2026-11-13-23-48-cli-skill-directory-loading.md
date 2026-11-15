# CLI Skill Directory Loading

Status: Executed

## Goal (locked)

Add skill loading to the dandy CLI: at process start, discover `SKILL.md` files from
the global (`~/.config/dandy/skills/`) and project (`<project>/.dandy/skills/`) skill
directories (project wins name collisions), register them as prompt-only `BaseSkill`
instances into the existing `SkillService`, and feed them to the interactive coding
agent only (no init pass, no new framework API). Passive skills keep the existing
`activate_skill` flow. Malformed skills print a notice and are skipped; they never
crash the CLI. Hermetic tests + docs.

User-locked choices (2026-11-13): format = `SKILL.md` (frontmatter + markdown body,
prompt-only, no typed tools); directories = both, project overrides global by name;
surface = CLI coding agent turns only; passive mode = yes.

## End State

Observable, no new framework API:

1. Drop `<project>/.dandy/skills/<name>/SKILL.md` -> the REPL welcome banner shows a
   `Skills` line counting it, and the coding agent's system prompt contains the skill
   prompt (active) or name+description (passive) in the existing skills section.
2. The same skill under `~/.config/dandy/skills/<name>/` is loaded when absent from
   the project dir; when both exist, the project one wins and the global one is
   dropped (an override, not an error).
3. A passive skill (frontmatter `active: false`) appears in the system prompt by
   name+description and its full prompt enters the conversation only after the model
   calls the existing `activate_skill` tool.
4. Malformed skill files (unreadable file, missing/unclosed frontmatter fence, passive
   skill with no description, empty name) print one notice line to the terminal and
   are skipped; every other skill loads and the CLI starts normally.
5. One-shot mode (`dandy "<request>"`) gets the same skills (it builds the same
   `CliAgent`). The init pass (`/init`, `dandy --init`) is untouched - `InitBot` runs
   without skills.
6. `pytest tests -q` passes (~870+, hermetic), `ruff check` / `ruff format --check` on
   changed files pass, `lint-imports` keeps 6/6 contracts, `mkdocs build --strict` is
   clean.

## Observable Concern

- **Hermeticity of the global dir**: the developer machine's real
  `~/.config/dandy/skills/` would leak into `DandyCli` tests and break system-prompt
  and tool-array assertions. Mitigation: every CLI wiring test patches
  `load_cli_skills` in `dandy.interfaces.cli.cli`; loader unit tests use temp dirs only.
- **No YAML dependency** (runtime deps stay pydantic/requests/blessed/python-dotenv):
  frontmatter is parsed dependency-free - `key: value` lines between `---` fences,
  unknown keys ignored, body is everything after the closing fence.
- **Resumed sessions**: a resumed session replays its saved system message (skills
  baked in at save time), so skills added or removed after the save do not apply until
  `/new`. Accepted and documented - same staleness as AGENTS.md in a resumed session.

## Current State (verified)

- `BaseSkill` (`dandy/domain/skill/skill.py`): plain class; attrs
  `name` / `description` / `prompt` / `active` / `tools`; `SkillType` and
  `to_skill_instances` live here too. A file skill is a `BaseSkill` instance with
  `tools=[]` and instance attrs set.
- `SkillService` (`dandy/application/skill/service.py`): `register()` validates
  (non-empty name; passive requires description; unique names; generated tool names
  must not collide or equal reserved `activate_skill`); `system_prompt_section()`
  renders active prompts + passive metadata; `active_tools()` feeds the per-round
  tool array in `ToolService` (`dandy/application/tool/service.py:56`) - passive
  activation works with zero loop changes.
- `Agent.__init__` (`dandy/application/agent/agent.py:50-71`): `skills=` param exists
  and registers + appends the section before the first request - the seam.
- `CliAgent.__init__` (`dandy/application/agent/cli/cli_agent.py:23`):
  `(self, ask_user=None)` only; no `skills` param yet.
- `DandyCli.__init__` (`dandy/interfaces/cli/cli.py:42-43`): `self.agent =
  CliAgent(ask_user=self._ask_user)`.
- Welcome banner: `Printer.welcome()` (`dandy/interfaces/cli/tui/printer.py:52-67`)
  prints label + line pairs; lines are self-contained disk readers in
  `dandy/interfaces/cli/tui/banner.py` (`agents_md_banner_line`,
  `session_banner_line`).
- Global config home precedent: `Path.home() / '.config' /
  DANDY_HOME_CONFIG_DIRECTORY_NAME / DANDY_JSON_FILE_NAME`
  (`dandy/shared/settings/load.py:75`).
- `dandy/shared/constants.py`: `DANDY_HOME_CONFIG_DIRECTORY_NAME = 'dandy'`,
  `DANDY_LOCAL_DIRECTORY_NAME = '.dandy'`; no skills constant yet. Note: the file
  already carries an uncommitted `__VERSION__ = '3.0.0a5'` bump (user) - preserve it.
- No spec convention to follow (`specs/` empty); this backplan doc is the planning
  artifact.
- Hermetic test style: `unittest.TestCase`, fakes under
  `tests/<layer>/<module>/intelligence/`, connector-boundary mocking.

## Plan

1. **Constant** - add `SKILLS_DIRECTORY_NAME = 'skills'` to
   `dandy/shared/constants.py` (next to `SESSIONS_DIRECTORY_NAME`), preserving the
   uncommitted a5 version bump.
   *Done when:* constant importable; `git diff dandy/shared/constants.py` shows only
   the version bump + the new line.

2. **Loader** - new `dandy/application/skill/loader.py` (application layer; imports
   domain `BaseSkill` / `SkillType` + shared constants only - no interfaces, no
   infrastructure):
   - `parse_skill_file(text: str) -> (frontmatter dict, body str)` - dependency-free
     frontmatter parse; missing/unclosed `---` fence -> issue, not exception.
   - `load_skill_files(directories: list[Path]) -> (list[BaseSkill], list[str])` - each
     `<dir>/<skill-name>/SKILL.md` becomes a prompt-only `BaseSkill` (`tools=[]`,
     `name` from frontmatter defaulting to the dir name, `description`, `active`
     defaulting to true, `prompt` = body); later directories override earlier ones by
     final name; every failure becomes an `issues` string (path + reason), never
     raises.
   - `load_cli_skills(project_base_path: Path) -> (list[BaseSkill], list[str])` - calls
     the above with `[global_dir, project_dir]` (global first, project wins).
   *Done when:* `tests/application/skill/test_loader.py` passes (temp dirs: minimal
   skill, name default, passive, project-over-global, malformed frontmatter, passive
   without description, empty dir, missing dir, override keeps project body, never
   raises).

3. **CliAgent seam** - `dandy/application/agent/cli/cli_agent.py:23`: add
   `skills: list[SkillType] | None = None` to `CliAgent.__init__`, forward to
   `super().__init__` (registration + system-prompt section happen in
   `Agent.__init__`).
   *Done when:* `CliAgent(skills=[...])` registers with `bot.llm.skills` (asserted in
   a wiring test); `CliAgent()` behavior unchanged (existing tests still pass).

4. **Wiring** - `dandy/interfaces/cli/cli.py:42-43`: `DandyCli.__init__` calls
   `load_cli_skills(session.project_base_path)`, passes the skills into
   `CliAgent(ask_user=..., skills=...)`, and prints one notice line per loader issue
   (printing is interfaces; loading stays application).
   *Done when:* with patched loader (temp-dir skills) a `DandyCli` starts with them
   registered, project wins a collision, malformed ones print a notice; the existing
   `test_cli.py` suite stays hermetic by patching `load_cli_skills` in
   `dandy.interfaces.cli.cli`.

5. **Banner** - `dandy/interfaces/cli/tui/banner.py`: `skills_banner_line(project_base_
   path: Path)` (re-runs `load_cli_skills`, matching the self-contained style of the
   other two lines): none -> 'none found - drop SKILL.md folders in .dandy/skills/';
   some -> 'N loaded (A active, P passive)'. Printed in `Printer.welcome()` after the
   Sessions line.
   *Done when:* a test asserts the line text for 0, active-only, and mixed cases.

6. **Docs** - `docs/user_guide/cli_agent.md` (new "Skills" section: locations, format,
   precedence, passive, resume staleness), `docs/getting_started/cli.md` (short
   pointer), `docs/changelog/v3.md` (new `## v3.0.0a5` / Added entry - the version
   bump to a5 is already in the tree), `docs/reference/application.md` (loader symbols,
   if that page lists the skill service), `AGENTS.md` (Skill section + CLI bullet:
   loader module, directories, precedence, banner line, hermetic mocking rule).
   *Done when:* `mkdocs build --strict` clean; AGENTS.md fragments match the code.

## Completion Test

```
cd /home/nathanj/PycharmProjects/dandy
PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings AI_API_KEY=placeholder \
  .venv/bin/python -m pytest tests -q
.venv/bin/ruff check <changed files>
.venv/bin/ruff format --check <changed files>
.venv/bin/lint-imports
PYTHONPATH=. DANDY_SETTINGS_MODULE=tests.dandy_settings \
  .venv/bin/python -m mkdocs build --strict
```

Pass = all green, no new failures vs the 869-passed baseline, plus the step-2 loader
temp-dir checks.

## Deviations

1. **What:** also added `SKILL_FILE_NAME = 'SKILL.md'` alongside
   `SKILLS_DIRECTORY_NAME` in `dandy/shared/constants.py`.
   **Why:** keeps the filename out of string literals in loader and docs.
2. **What:** `parse_skill_file` returns a 3-tuple `(frontmatter, body, issues)`
   instead of the planned 2-tuple, and strips matching quotes from values.
   **Why:** per-file parse issues need to be attributed to the file's path for the
   skip notices, and quoted frontmatter values (`name: ""`) are a realistic case.
3. **What:** the loader also rejects an empty markdown body and an unparseable
   `active` value as issue cases (beyond the four named in the End State).
   **Why:** both are malformed-file cases the "never crash" contract covers; each
   has a dedicated test.
4. **What:** the changelog entry lives under a new `## v3.0.0a5` section rather
   than the existing v3.0.0a4 section.
   **Why:** `__VERSION__` was already bumped to 3.0.0a5 (uncommitted user change)
   and no a5 section existed; this feature is the a5 release content.
