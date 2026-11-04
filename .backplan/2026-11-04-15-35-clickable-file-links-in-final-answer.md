# clickable-file-links-in-final-answer

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-04-15-35

## End State
Every file path the agent names in its final rendered answer (paragraphs, headings, list
items, blockquotes, table cells, and inline code spans) is a clickable OSC 8 `file://`
link (relative paths resolved against the project root) in the CLI, while fenced code
blocks, URLs, and non-path tokens are left untouched and the rendered layout (wrap,
table column widths/padding) is unchanged; covered by hermetic tests.

## Observable Concern
The markdown renderer measures and wraps with blessed `term.length` / `term.wrap`, so
those must be OSC 8-aware or the links would corrupt the layout. Verified 2026-11-04
against the venv's blessed: `term.length` on a linked `src/foo.py` equals the plain
length (10 == 10), and `term.wrap` on a link-dense line wraps only between links
(every wrapped line has balanced OSC opens/closes, URIs intact). Residual risk:
`_INLINE_PATTERN` matching on text that already contains OSC bytes (a bold span around
a link, `**src/foo.py**`) — the match still succeeds and `_style_inline` wraps the
already-linked inner text in styling, which modern terminals render correctly; the
tests assert exactly that case.

## Current State
Verified 2026-11-04, live tree (branch `v3/base`):
- `linkify_file_paths` (+ `_is_path_token`, `_PATH_WORD_RE`, `_FILE_EXTENSION_RE`)
  lives in `dandy/interfaces/cli/tui/printer.py:51-89`; used only by
  `_StoryProgress._styled_description` (:169, labeled tool beats, animating + settled
  frames) and `Printer.edited_files` (:598). The Nov 3 backplan
  `2026-11-03-18-40-clickable-file-links-in-story-beats.md` (Status: Executed) covers
  those two surfaces; the final answer is the one remaining surface
  (its backplan's flagged assumption: "the model's narration and the final markdown
  answer are not linkified").
- Final-answer pipeline: `DandyCli.process_agent_input` → `Printer.output`
  (printer.py:578) → `MarkdownRenderer.render` (markdown.py:51) → per-block renderers.
  Every prose element (heading, paragraph, blockquote, list item, table cell) funnels
  through `_apply_inline` (markdown.py:372), which unescapes then runs
  `_INLINE_PATTERN.sub(_style_inline)`; blessed styling wraps each span's plain inner
  text. Fenced code blocks (`_render_code_block`, :227) do NOT go through
  `_apply_inline`.
- `dandy/interfaces/cli/tui/text.py` already exists (small text-utils module with
  `wrap_text_with_indentation`; `tests/interfaces/cli/test_text.py` covers it) — the
  natural home for the shared helper without a new module.
- Import direction: printer.py imports markdown.py (printer.py:15), so markdown.py
  cannot import from printer.py (circular) — the helper must move before markdown.py
  can use it. `tests/interfaces/cli/test_printer.py:17` imports
  `linkify_file_paths` from printer.py and must follow it.
- Markdown link rendering (`_styled_link`, markdown.py:402) prints
  `underline(label) dim(url)`; URLs contain `:`, which `_PATH_WORD_RE` excludes, so
  they are untouched by linkification.
- Test style: `test_markdown.py` builds `MarkdownRenderer(Terminal(), width=40)` and
  asserts on rendered text; the printer's linkify tests patch
  `session.project_base_path` onto a `TemporaryDirectory` (same pattern applies).
- blessed OSC 8 verification (venv, 2026-11-04): `term.length(linked) == term.length(plain)`;
  `term.wrap` on a line of 12 links at width 40 produced 4 lines, each with balanced
  OSC open/close counts and all 12 URIs intact.

## Plan
1. Move the linkify helper to `dandy/interfaces/cli/tui/text.py`
   - Move `_PATH_WORD_RE`, `_FILE_EXTENSION_RE`, `_is_path_token`,
     `linkify_file_paths` (docstring unchanged) verbatim; printer.py imports
     `linkify_file_paths` from text.py (its two call sites unchanged); update the
     `test_printer.py` import to the new module.
   - Done when all 47 `test_printer.py` tests pass unchanged in behavior (6 linkify
     tests now import from text.py) and `test_text.py` still passes.
2. Apply it in `MarkdownRenderer._apply_inline`
   - Linkify the unescaped plain text before `_INLINE_PATTERN.sub`, so prose tokens,
     inline code spans (`` `src/foo.py` `` — the model's most common file reference),
     and span-wrapped paths all link; fenced code blocks stay untouched (they never
     call `_apply_inline`). No changes to the block renderers: blessed
     length/wrap are verified OSC-aware.
   - Done when `render('I edited src/foo.py')` carries the OSC 8 URI and
     `render('**src/foo.py**')` / `render('`src/foo.py`')` do too, with styling intact.
3. Tests (`tests/interfaces/cli/test_markdown.py`)
   - With `session.project_base_path` patched to a `TemporaryDirectory`: paragraph
     path linked (absolute `file://` URI), inline code span linked, list item linked,
     table cell linked, heading linked; a `https://example.com/x` URL untouched; a
     fenced code block's `src/foo.py` untouched; a link-dense paragraph wrapped at
     width 40 has every line OSC-balanced with URIs intact.
   - Done when the file is green.
4. Docs
   - `AGENTS.md` CLI bullet: one clause on the `Printer.output` / `MarkdownRenderer`
     sentence (final-answer file paths are clickable `file://` links; fenced code
     blocks excluded); `docs/user_guide/coding_agent.md` final-answer paragraph
     (same, one sentence); `docs/changelog/v3.md` v3.1.0 Added entry.
   - Done when `just docs-tests` strict build passes.
5. Gate
   - Targeted pytest (`tests/interfaces/cli/`), full suite, ruff on touched files
     (no NEW findings; branch has pre-existing violations on HEAD), `just lint-imports`.
   - Done when every gate is green.

## Completion Test
```bash
cd /home/nathanj/PycharmProjects/dandy
just test-app tests/interfaces/cli/
just test
.venv/bin/ruff check dandy/interfaces/cli/tui/text.py dandy/interfaces/cli/tui/markdown.py \
  dandy/interfaces/cli/tui/printer.py tests/interfaces/cli/test_markdown.py \
  tests/interfaces/cli/test_printer.py tests/interfaces/cli/test_text.py
just lint-imports
just docs-tests
```
All green, plus a live smoke render:
```bash
DANDY_SETTINGS_MODULE=tests.dandy_settings PYTHONPATH=. .venv/bin/python -c "
from blessed import Terminal
from dandy.interfaces.cli.tui.markdown import MarkdownRenderer
print(MarkdownRenderer(Terminal(force_styling='default')).render('Edited src/foo.py and `src/bar.py`').splitlines()[0])
"
```
shows raw OSC 8 open/close sequences around both paths.

## Assumptions (flagged)
- Fenced code blocks are NOT linkified: they are code samples, where the path-like
  token heuristic false-positives (dotted module names such as `os.path` or
  `src.stockroom.ops` would link to nonexistent files). Prose, bullets, headings,
  tables, blockquotes, and inline code spans ARE linkified. Redirect if code blocks
  should link too.
- Schemeless domain paths (`www.example.com/bar`) would link as local files — same
  known limitation as the existing beat behavior; scheme-carrying URLs never link.
- Relative paths resolve against `session.project_base_path` exactly as the story
  beats do (the CLI sets it at startup); a link to a file that does not exist still
  opens (or errors) in the OS default handler, same as today's beats.

## Deviations
1. One whole-text linkify pass in `_apply_inline` was not enough for span-wrapped paths
    - What: besides linkifying the unescaped text before `_INLINE_PATTERN.sub`, each span
      branch of `_style_inline` (code/bold/strikethrough/italic) and `_styled_link`'s
      label now linkifies the span's inner text before styling.
    - Why: the whole-text pass sees `` `src/foo.py` `` / `**src/foo.py**` as one word
      containing backticks/asterisks, which `_is_path_token` rejects, so span-wrapped
      paths (the model's most common file-reference forms) never linked until the span
      branches linkified their inner text. Already-linked words self-protect against
      double-linking (the OSC bytes fail the path-safe character match).

## Observed Output
- `tests/interfaces/cli/` (pytest): `169 passed in 3.05s` (9 new tests in test_markdown.py)
- Full suite: `751 passed, 1 failed, 81 skipped in 236.42s` — the single failure is
  `tests/infrastructure/http/test_http_connector.py::test_late_connection_error_keeps_the_last_response_in_the_error`
  (StopIteration in a mock side_effect), which passes in isolation (2/2) and is in a layer
  this change does not touch: pre-existing flake, not caused by this work.
- ruff on the six touched files: 25 findings, all pre-existing (missing ANN201 on printer
  divider methods, ARG001/TRY003/EM101 on pre-existing test lines); zero on the new code
  in text.py / markdown.py / the new tests; `ruff format --check` clean.
- `just lint-imports`: `Contracts: 6 kept, 0 broken.`
- `just docs-tests`: `Documentation built in 1.02 seconds` (strict build, exit 0)
- Smoke render (cat -v): `Edited ^[]8;;file:///.../src/foo.py^[\src/foo.py^[]8;;^[\ and
  ^[[33m^[]8;;file:///.../src/bar.py^[\src/bar.py^[]8;;^[\^[[m` — raw OSC 8 around both a
  plain path and an inline-code path, the latter styled yellow around the link.
