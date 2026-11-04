# clickable-file-links-in-story-beats

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-03-18-40

## End State
Every file path a tool names in its story beat (the `description` of a labeled tool
beat — `read_file`/`write_file`/`edit_file`/`delete_file`/`create_directory`/
`list_directory`/`search_files`/`git_diff`/`run_command`) is rendered as a clickable
terminal hyperlink (OSC 8, `file://` URI resolved against the project root) in both the
animating and settled frames, so clicking it opens the file with the OS default handler
for that file type (the default editor for code files).

## Observable Concern
The link is emitted as a raw OSC 8 sequence — verified this session that blessed 1.52.0's
`term.hyperlink` is a terminfo-capability formatter that crashes (`Unknown terminal
capability, 'hyperlink'`), so blessed offers no usable helper. Terminals without OSC 8
support (rare today) would show raw escape garbage; all modern terminals (iTerm2, kitty,
WezTerm, Windows Terminal, VS Code, Alacritty) render it as a clickable link. Link
semantics are OS-level: `file://` opens the default app for the file type — the terminal
cannot pick a specific editor or a line number, so `read_file`'s "lines 1-10" suffix stays
plain text.

## Current State
Verified 2026-11-03, live tree (branch `v3/base`):
- `dandy/interfaces/cli/tui/printer.py` — `styled_beat` (label branch) is the one place
  every labeled beat's description is styled, for both `frame()` (animating, post-truncation
  `description_part`) and `settled_frame()` (full description); `session` is already
  imported at module level (banner lines).
- Blessed 1.52.0: `Terminal().hyperlink` exists but is a `ParameterizingString` terminfo
  formatter; calling it raises `TypeError: Unknown terminal capability, 'hyperlink'`.
  Raw OSC 8 (`ESC]8;;URI ESC\` + text + `ESC]8;; ESC\`) is the portable route.
- Beat description shapes (all whitespace-separated, paths unquoted, project-relative):
  `src/foo.py`, `src/foo.py lines 2-end`, `src/foo.py everywhere`, `nested/dir`,
  `.` / `src/` (+ ` recursively`), `for "query" in src`, `for src/foo.py`, and
  `run_command`'s raw command string.
- Non-path tokens present in descriptions that must NOT be linked: `lines`, `1-10`,
  `end`, `everywhere`, `recursively`, `-q`, `--short`, shell flags/assignments.
- Printer tests use `_StoryProgress(Terminal(force_styling='default'))` and assert raw
  escape strings in the frame output, so a raw-sequence helper is directly assertable.
- `tests/interfaces/cli/test_printer.py` already imports `TemporaryDirectory`/`Path` and
  the agent tool tests patch `session.project_base_path` (the same pattern applies).

## Plan
1. `linkify_file_paths` helper in `printer.py`
   - Module-level pure function: `linkify_file_paths(description: str) -> str`. Splits on
     whitespace; a word qualifies as a path if it uses only path-safe characters
     (`\w . / ~ -`), is not `.`/`..`/a leading-dash token, and either contains a `/` or
     ends in a dotted extension whose extension has at least one letter (so `1.0.5` and
     `v2.0` do not link, `foo.py` and `src/foo.py` do). Each qualifying word is wrapped in
     a raw OSC 8 sequence whose URI is `Path(token).expanduser()`, resolved against
     `session.project_base_path` when relative, as `Path.as_uri()`. Words that do not
     qualify (and everything between them) pass through byte-identical.
   - Done when a direct unit call links `src/foo.py` and leaves `pytest -q` /
     `lines 1-10` untouched.
2. Apply it in `styled_beat`
   - In the labeled branch, style the linkified description:
     `description = linkify_file_paths(description)` before building the styled string.
     Narration/system beats (no label) are untouched — the ask is tool calls.
   - Done when both `frame()` and `settled_frame()` output carry the OSC 8 sequence for a
     labeled beat and not for a description-only beat.
3. Docstrings
   - `_StoryProgress` docstring: one clause (file paths in a tool beat's description are
     emitted as clickable `file://` links).
   - Done when the class docstring matches the behavior.
4. Tests (`tests/interfaces/cli/test_printer.py`)
   - Helper unit tests: path linked (relative resolved against a patched
     `session.project_base_path` via `TemporaryDirectory`), extension-only file linked,
     non-path words untouched, `1-10`/`-q`/`.` untouched.
   - Frame tests: a labeled beat's settled and animating frames contain the OSC 8 open
     with the absolute `file://` URI, the close sequence, and the plain `lines 1-10`
     suffix; a description-only beat stays link-free.
   - Done when the file is green.
5. Docs
   - `AGENTS.md` story bullet (one sentence: tool-beat file paths render as clickable
     `file://` links via raw OSC 8, blessed's `hyperlink` capability is unusable);
     `docs/user_guide/tool_calling.md` beat bullet (same sentence);
     `docs/changelog/v3.md` v3.1.0 Added entry.
   - Done when `just docs-tests` strict build passes.
6. Gate
   - Targeted pytest (`tests/interfaces/cli/test_printer.py` + the agent tool suites that
     exercise beats); full suite
     (`DANDY_SETTINGS_MODULE=tests.dandy_settings PYTHONPATH=. .venv/bin/python -m pytest -q`);
     ruff mirror-path diff on touched files (no NEW findings); `just lint-imports`;
     `just docs-tests`.
   - Done when every gate is green.

## Completion Test
```bash
DANDY_SETTINGS_MODULE=tests.dandy_settings PYTHONPATH=. .venv/bin/python -m pytest \
  tests/interfaces/cli/test_printer.py tests/application/tool/test_service.py \
  tests/application/agent/test_file_tools.py tests/application/agent/test_agent_tools.py -q
```
all green, plus the full suite green, `just lint-imports` → `Contracts: 6 kept, 0 broken.`,
`just docs-tests` exit 0, and the ruff mirror diff on touched files empty.

## Assumptions (flagged)
- Scope is the tool-call story beats only; the model's narration and the final markdown
  answer are not linkified.
- Clicking opens the OS default handler for the file type (default editor for code
  files); a specific editor or line number cannot be selected from a terminal link.
- Tokens that are bare directory names without a slash (e.g. listing `.` or `build`)
  are indistinguishable from ordinary words and are not linked; slashed paths and
  extension-bearing files are.

## Deviations
none yet

## Observed Output
- Targeted pytest (`tests/interfaces/cli/test_printer.py`): `29 passed in 2.03s` (6 new tests)
- Full suite: `683 passed, 15 skipped, 49 subtests passed in 132.41s (0:02:12)`
- ruff mirror-path diff on the two touched Python files: NO NEW FINDINGS (after fixing one
  101-char line in the new absolute-path test)
- `just lint-imports`: `Contracts: 6 kept, 0 broken.`
- `just docs-tests`: exit 0 (strict mkdocs build)
