# Make the bullet the default for non-tool story beats

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-02-12-11

## End State

Every CLI story beat line without an explicit `ascii_char` — the opening
thinking phrase, the model's narration, 'Planning', and compaction notices —
is prefixed with `•` instead of `.`, and the tests and docs describe the
bullet fallback.

## Observable Concern

The user is live-editing the CLI/test files concurrently (`test_printer.py`
already gained an `agents_md_banner_line` import and the `agents_md` tests
this session) — re-View immediately before each edit and expect
"modified since last read" failures. The `•` is a single codepoint, so the
`frame()` width math (`len(prefix)`) is unaffected.

## Current State

- `dandy/interfaces/cli/tui/printer.py:91` — `char = beat.ascii_char or '.'`
  (settled frame); `:96` — `prefix = f'{self.term.normal}{beat.ascii_char or
  "."} '` (animating frame); `:57` — docstring "prefixed with the beat's ascii
  character (a dot when the beat carries none)".
- `dandy/domain/tool/beat.py:23` — `ascii_char: str = ''`; docstring lines
  14-16: "an empty value means the renderer falls back to its default dot".
  The renderer owns the fallback; the dataclass default stays `''`
  (= "unspecified").
- Non-tool beat construction sites (all rely on the fallback, none set
  `ascii_char`): `printer.py:62` (THINKING_PHRASE opening beat),
  `dandy/application/agent/agent.py:256` (system notice),
  `dandy/application/agent/coding_agent.py:59` ('Planning'),
  `dandy/application/tool/service.py:157` (narration), `service.py:219`
  (compaction notice). Tool beats set `ascii_char=tool.action_ascii_char`
  (`service.py:270`), default `'•'`, overridable per tool (`'>'` on
  RunCommandTool) — unchanged.
- Tests asserting the dot for char-less beats
  (`tests/interfaces/cli/test_printer.py`): `:82`
  `assertIn('. Reading the test file.', frame)`, `:90` `assertIn('. Checking
  the forecast now.', frame)`, `:103` and `:116`
  `startswith(f'\r{progress.term.normal}. ')`.
- Docs describing the dot fallback: `AGENTS.md:168` ("with narration and
  system beats falling back to a dot"),
  `docs/user_guide/tool_calling.md:79` ("or a dot when the beat carries
  none"), `docs/changelog/v3.md:162` ("falling back to the same dot").
  `dandy/domain/tool/tool.py` docstring ("without one, a bullet is used")
  already says bullet for tools — unchanged.

## Plan

1. Renderer fallback to bullet
   - `printer.py:91` `or '.'` → `or '•'`; `printer.py:96` `or "."` →
     `or '•'`; `printer.py:57` docstring "a dot when the beat carries none" →
     "a bullet when the beat carries none"; `beat.py:16` "falls back to its
     default dot" → "falls back to its default bullet".
   - Done when the four dot assertions in `test_printer.py` fail (proof of
     behavior change), then pass after step 2.

2. Adapt the four dot assertions
   - `:82` → `'• Reading the test file.'`; `:90` → `'• Checking the forecast
     now.'`; `:103` and `:116` →
     `f'\r{progress.term.normal}• '`.
   - Done when `pytest tests/interfaces/cli -q` is green.

3. Docs
   - `AGENTS.md:168` → "falling back to a bullet";
     `docs/user_guide/tool_calling.md:79` → "or a bullet when the beat
     carries none"; `docs/changelog/v3.md:162` → "falling back to the same
     bullet".
   - Done when `just docs-tests` exits 0.

4. Gate
   - Full suite, ruff check/format on touched files, `just lint-imports`.
   - Done when every command in the Completion Test passes with output
     quoted.

## Completion Test

- `DANDY_SETTINGS_MODULE=tests.dandy_settings PYTHONPATH=. .venv/bin/python -m
  pytest tests -q` → whole suite passes.
- `.venv/bin/ruff check <touched files>` + `grep -E 'E501|F[0-9]{3}|W[0-9]{3}'`
  empty; `.venv/bin/ruff format --check <touched files>` clean.
- `just lint-imports` → all 6 contracts kept.
- `just docs-tests` → mkdocs strict build exits 0.
- Smoke: `python -c` rendering one char-less `StoryBeat` through
  `_StoryProgress.settled_frame` → line prefixed `• `.

### Observed

- Step-1 proof: after the renderer change, `pytest tests/interfaces/cli -q`
  → `4 failed, 102 passed` — exactly the four dot-assertion tests.
- `pytest tests/interfaces/cli tests/application/tool tests/domain/tool -q`
  → `156 passed`.
- `pytest tests -q` (full) → `650 passed, 49 subtests passed in 243.01s` (zero
  failures; the earlier in-flight `reload_agents_md` and live-LLM book failures
  were both green in this run).
- `ruff check` on the three touched .py files + `grep -E 'E501|F[0-9]{3}|W[0-9]{3}'`
  → empty; `ruff format --check` → `3 files already formatted`.
- `just lint-imports` → `Contracts: 6 kept, 0 broken.`
- `just docs-tests` → `Documentation built in 0.99 seconds` (exit 0).
- Smoke: `settled_frame(StoryBeat(description='Planning'))` →
  `'\r\x1b[m• Planning\x1b[K\n'`.

## Deviations

1. **AGENTS.md + changelog re-read after user live-edits** — the doc-step
   edits to `AGENTS.md` and `docs/changelog/v3.md` initially failed with
   "modified since last read" (user edited other parts of both files mid-run).
   - What: re-located the target strings (both still intact), re-Viewed the
     exact lines, re-applied the same one-word edits unchanged.
   - Why: the anticipated concurrent-editing hazard from the Observable Concern
     materialized; mechanism only, no plan content changed.
