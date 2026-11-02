# Blue model narration beats

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-02-10-10

## End State

Story beats written by the model (its narration sentences) render in bold blue
in the CLI story, while tool action beats keep the grey label + plain
description and non-model description-only beats (opening thinking phrase,
'Planning', compaction notice) stay plain black — with tests and docs updated
and the gates green.

## Observable Concern

Narration beats are currently indistinguishable from the other
description-only beats (`StoryBeat(description=...)`): the opening thinking
phrase, 'Planning', and the compaction notice all use the same shape. The
change hangs on adding a `kind` marker that only the model-narration site
sets; missing or extra `kind='narration'` at any of the five emitter sites
mis-colors system text or leaves the model's voice plain.

## Current State

- `StoryBeat` (`dandy/domain/tool/beat.py`): `label: str = ''`,
  `description: str = ''`; no voice/kind marker.
- Emitters:
  - `ToolService.prompt_to_intel` (summary): `StoryBeat(description=intel.summary)` —
    the model narration (the one to mark).
  - `ToolService._compact_history_before_next_round`: `StoryBeat(description=...)` —
    system.
  - `Agent._compact_history_for_next_message`: `StoryBeat(description=...)` — system.
  - `CodingAgent._create_plan`: `StoryBeat(description='Planning')` — system.
  - `_StoryProgress.__init__` (seed thinking phrase): `StoryBeat(description=...)` —
    system.
- Renderer `_StoryProgress.styled_beat(label, description)`
  (`dandy/interfaces/cli/tui/printer.py`): label → `bold_grey`, description
  plain; used by both `settled_frame` and `frame` (frame truncates the plain
  text first, so styling is applied after truncation).
- Tests asserting beat equality: `tests/application/tool/test_service.py`
  (`test_prompt_to_intel_reports_summary_sentences`,
  `test_prompt_to_intel_reports_summary_and_tool_sentence`); printer tests in
  `tests/interfaces/cli/test_printer.py` (description-only beat stays plain).

## Plan

1. Mark narration beats
   - `StoryBeat` gains `kind: str = 'system'` ('system' | 'narration'); docstring
     updated; the summary emitter in `ToolService` sets `kind='narration'`. No
     other emitter changes.
   - Done when `StoryBeat(description='x', kind='narration')` compares distinct
     from the default-kind beat.
2. Render narration in bold blue
   - `_StoryProgress.styled_beat` takes the kind: no label + kind 'narration' →
     `bold_blue` description; everything else unchanged (label grey + detail
     plain; system beats plain). `settled_frame` / `frame` pass `beat.kind`
     through (after the plain-text truncation, so no mid-escape cuts).
   - Done when a new printer test shows `term.bold_blue` in both the animating
     and settled frames of a narration beat, and the existing plain-beat test
     still passes.
3. Update tests and docs
   - `test_service.py`: the two summary assertions gain `kind='narration'` on the
     narration beats (tool beats keep the default kind).
   - Docs: `AGENTS.md` execute-and-loop paragraph, `docs/user_guide/tool_calling.md`
     progress_callback bullet, and the v3.1.0 'Tool story beats are structured'
     changelog entry all mention the `kind='narration'` beat and its bold-blue
     rendering.
   - Done when the affected test files pass and `just docs-tests` exits 0.
4. Run the gate
   - `pytest tests -q`, `ruff check` + `ruff format --check` on touched files,
     `just lint-imports`, `just docs-tests`, and the `run_timed_task` smoke run
     showing a bold-blue narration line.
   - Done when every command is green and the smoke output shows the blue beat.

## Completion Test

1. `pytest tests -q` → full suite passes.
2. `ruff check` / `ruff format --check` on touched files → no new findings/diffs.
3. `just lint-imports` → all contracts kept.
4. `just docs-tests` → exit 0.
5. Smoke: `run_timed_task` with a fake `work` pushing one
   `StoryBeat(description=..., kind='narration')`, one tool beat, and one
   system beat; captured stdout shows the narration line wrapped in
   `bold_blue`, the tool line in `bold_grey` label + plain detail, the system
   line plain.

## Deviations

none — executed as planned.

## Completion Test Results (observed 2026-11-02)

- `pytest tests -q` → `621 passed, 49 subtests passed in 114.51s` (the +1 is the
  new `test_narration_beat_renders_bold_blue`).
- `ruff check` on the five touched files → no E501/F/W findings (the 87 reported
  are the branch-wide pre-existing ANN/TRY/EM style findings); `ruff format
  --check` → `5 files already formatted`.
- `just lint-imports` → `Contracts: 6 kept, 0 broken.`
- `just docs-tests` → exit 0.
- Smoke: `run_timed_task` with a narration beat (`kind='narration'`), a tool beat,
  and a compaction beat; captured stdout shows the narration line wrapped in
  `\x1b[1m\x1b[34m` (bold blue), the tool line in the `bold_grey` label + plain
  detail, and the compaction line plain.
