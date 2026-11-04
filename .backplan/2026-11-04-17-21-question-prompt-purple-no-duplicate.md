# question-prompt-purple-no-duplicate

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-04-17-21

## End State
When the agent asks a question mid-turn, the terminal shows the question exactly
once: an empty line, the `Asking` label in plain purple, a plain purple `↳` arrow
with the question in plain black to its right on the same line, plain purple
numbered choices, and plain purple dividers — with no story beat printed before
the prompt.

## Observable Concern
The beat suppression lives in `ToolService` (application) + `BaseTool` (domain):
the beat was the only other place the question text is displayed, so anything
relying on the question's beat silently loses it (verified: nothing besides the
beat emission references it). Second risk: once the beat is gone, the empty line
above the prompt depends on the render loop's `pause_at_fresh_line` leaving the
cursor at column zero — the prompt's leading `\n` must still produce exactly one
empty line in every pause shape (beats pending, no beats at all).

## Current State
Verified 2026-11-04, live tree (branch `v3/base`):
- Duplication mechanism (the "displaying broken" part, confirmed in the user's
  live paste): `ToolService._process_tool_call`
  (`dandy/application/tool/service.py:273-280`) emits a
  `StoryBeat(label=<action_label>, description=<action_output>, can_mutate_state=...)`
  for every executed tool call *before* `tool.handle()` runs. `QuestionTool.handle`
  then parks on `question_gate`, and `Printer.run_timed_task`'s render loop
  (`dandy/interfaces/cli/tui/printer.py:460-473`) settles the pending beats first
  (printing `Asking` / `↳ <question>` in bold skyblue), moves the cursor onto the
  leftover phrase line at column zero, and only then calls the question handler —
  where `Tui.get_user_input` prints a prompt that repeats the same label, arrow,
  and question. The paste shows each question twice; for questions 2 and 3 the
  beat prints a bare `↳ <question>` line (consecutive same-label beats share one
  heading), which is the most broken-looking case.
- Color: the prompt's label + arrow use
  `bold_orange if QuestionTool.can_mutate_state else bold_skyblue`
  (`dandy/interfaces/cli/tui/tui.py:32-34`); the user wants purple. The question
  block's theme color is plain purple (choices and both dividers are already
  plain `term.purple`).
- Empty-line inconsistency (same paste): the prompt's leading `\n` only yields a
  visible empty line when the cursor starts at column zero. With the question
  beat settling at the pause, question 1 had no empty line above the prompt and
  questions 2-3 did. With the question beat gone, the line before the prompt is
  always newline-terminated (a settled beat, a narration, or the task header), so
  the leading `\n` consistently yields one empty line.
- `BaseTool` class attrs (`dandy/domain/tool/tool.py:39-45`): `name`,
  `description`, `action_label`, `can_mutate_state`, `timeout_seconds`,
  `use_shell` — there is no existing per-tool opt-out for the execution beat.
- `QuestionTool.action_output` (`question_tool.py:30-32`) exists only to feed the
  beat's description (verified: referenced only by `service.py:275` and
  `tests/application/agent/test_question_tool.py:56-61`) — it is dead once the
  beat is suppressed. `action_label = 'Asking'` stays (the prompt reads it).
- Tests: `tests/application/tool/test_service.py` already captures beats via
  `progress_callback=progress_steps.append` and asserts exact `StoryBeat` lists
  (`:173-190`, `:206-223`, `:299-319`) — the new suppression test follows that
  pattern (fakes in `tests/application/tool/intelligence/`). The
  `run_timed_task` question tests in `tests/interfaces/cli/test_printer.py`
  (`:455-520`) call `gate.ask` directly from `work` (no question beat is pushed)
  and assert nothing about beat text — unaffected.
- Docs naming the beat or the prompt: `AGENTS.md` tool-calling bullet ("one beat
  is emitted as each tool actually executes", ~line 170) and CLI bullet (the
  question prompt clause, ~line 234); `docs/user_guide/tool_calling.md` (the
  `action_label` bullet ~line 31 and the `progress_callback` bullet ~line 72);
  the `BaseTool` member list in `docs/reference/domain.md:51-65`; the v3.1.0
  Changed changelog entry for the question prompt (lines 163-169, currently
  describing the bold skyblue label style).
- The tree carries the user's parallel WIP (divider renames, non-question prefix
  hunk in `tui.py`) — untouched by this plan.

## Plan
1. Beat suppression in the framework
   - `dandy/domain/tool/tool.py`: add `emits_story_beat: bool = True` next to
     `can_mutate_state`; one docstring sentence (a tool that renders its own
     story while it waits — like the question prompt — sets it `False`).
   - `dandy/application/tool/service.py:273`: the emission becomes
     `if progress_callback is not None and tool.emits_story_beat:`.
   - `dandy/application/agent/tools/question/question_tool.py`: set
     `emits_story_beat = False`; delete the now-dead `action_output` override.
   - Done when a new `ToolService` test shows no tool beat for such a tool
     (narration beats still emitted) and `QuestionTool.emits_story_beat is False`.
2. Purple prompt label + arrow in `tui.py`
   - Drop the `label_style` conditional; both events use `self.term.purple`
     (label line `\n{purple}Asking{normal}`, arrow line
     `{purple}↳{normal} {linkified question}`); the `QuestionTool` import stays
     for `action_label`.
   - Done when the TUI tests assert a plain purple label + arrow and plain black
     question text.
3. Tests
   - `test_tui.py` `TestTuiQuestionPrompt`: both tests re-pointed from
     `bold_skyblue` to `purple`; the color test asserts plain purple and the
     absence of `bold_purple` / `bold_skyblue` / `bold_orange` / `bold_grey` in
     the block.
   - `test_question_tool.py`: replace the `action_output` test with an
     `emits_story_beat is False` assertion.
   - `test_service.py`: new test — a tool with `emits_story_beat = False`
     executes with no tool beat.
   - Done when `just test-app` is green for all three files.
4. Docs
   - `docs/reference/domain.md`: add `emits_story_beat` to the `BaseTool` member
     list.
   - `docs/user_guide/tool_calling.md`: the `action_label` bullet names
     `emits_story_beat`; the `progress_callback` bullet says the per-tool beat is
     skipped for tools that set it.
   - `AGENTS.md`: tool-calling bullet gains the suppression clause (with the
     `question` tool as the reason); the CLI bullet's question clause describes
     the final display (empty line, plain purple label + arrow, black question,
     purple choices/dividers) and that the question tool emits no story beat.
   - Changelog v3.1.0: the question Changed entry is rewritten in place (plain
     purple label + arrow; `QuestionTool` sets the new
     `BaseTool.emits_story_beat = False` so the question appears exactly once).
   - Done when `just docs-tests` strict build passes.
5. Gate
   - `just test-app` for `test_tui.py`, `test_service.py`, `test_question_tool.py`
     (+ `test_cli.py` / `test_printer.py` as the neighbors), ruff check +
     `ruff format --check` on the touched files (no NEW findings), `just test`
     (full suite, backgrounded), `just lint-imports`, `just docs-tests`, plus a
     live `cat -v` smoke driving `get_user_input(question=..., choices=...)` to a
     double-escape with a forced-styling terminal, asserting the exact purple
     shape (no `\x1b[1m` anywhere in the block).
   - Done when every gate is green and the smoke shows the purple label/arrow.

## Completion Test
```bash
cd /home/nathanj/PycharmProjects/dandy
just test-app tests/interfaces/cli/test_tui.py
just test-app tests/application/tool/test_service.py
just test-app tests/application/agent/test_question_tool.py
.venv/bin/ruff check dandy/domain/tool/tool.py dandy/application/tool/service.py \
  dandy/application/agent/tools/question/question_tool.py dandy/interfaces/cli/tui/tui.py \
  tests/interfaces/cli/test_tui.py tests/application/tool/test_service.py \
  tests/application/agent/test_question_tool.py
.venv/bin/ruff format --check <same files>
just test
just lint-imports
just docs-tests
```
All green, plus the live smoke print of the question block showing: empty line,
`Asking` in plain purple (no `\x1b[1m`), a plain purple `↳` with the plain black
question to its right on the same line, purple choices, plain purple dividers —
and the unit-level proof that the question tool emits no story beat, so the
question appears exactly once.

## Assumptions (flagged)
- "They should be purple" is read as plain purple (`term.purple`), the question
  block's existing theme color (choices and dividers), not bold purple —
  consistent with the earlier "not bold_purple" feedback.
- "displaying broken" is the double display: the fix is to suppress the
  question's story beat (the prompt is the sole display of the question), not to
  remove the label/arrow from the prompt.
- `QuestionTool.action_output` is deleted as dead code (its only consumer was
  the suppressed beat); `action_label` stays because the prompt reads it.
- `emits_story_beat` is a general framework opt-out (default `True`); only
  `QuestionTool` sets it `False` today.

## Deviations
none yet

## Observed Output
Observed 2026-11-04, branch `v3/base` (all gates run after every step was complete):

Targeted tests:
```
.venv/bin/python -m pytest tests/interfaces/cli/test_tui.py tests/application/tool/test_service.py tests/application/agent/test_question_tool.py -q
51 passed in 0.35s
```

Lint/format (no NEW findings; every finding on the touched files is a pre-existing
convention, and the new test follows the file's unannotated-method pattern):
```
.venv/bin/ruff format --check <seven touched files>
7 files already formatted
```

Full suite (the first run failed
`tests/domain/decision/test_decision.py::TestDecision::test_big_user_decision` with
`DecisionNoChoicesRecoverableError: No Employee First and Last Names found` — an
unrelated decision flake; it passes in isolation and passed in the rerun below):
```
just test
758 passed, 81 skipped in 164.85s (0:02:44)
```

Contracts and docs:
```
just lint-imports
Contracts: 6 kept, 0 broken.

just docs-tests
Documentation built in 1.03 seconds
```

Live smoke (`DANDY_SETTINGS_MODULE=tests.dandy_settings .venv/bin/python
/tmp/smoke_question_purple.py | cat -v`; drives `get_user_input(question='Do you
have a cat?', choices=['yes', 'no'])` to a double-escape with a
`Terminal(force_styling='default')` injected, asserts the exact six-line sequence,
asserts no `\x1b[1m` (bold) and no `bold_skyblue` anywhere in the block, and
prints `SMOKE OK`):
```
^[[m
^[[38;2;160;32;240mAsking^[[m^[[m
^[[m^[[38;2;160;32;240mM-bM-^FM-3^[[m Do you have a cat?^[[m
^[[m^[[38;2;160;32;240m1)^[[m yes^[[m
^[[m^[[38;2;160;32;240m2)^[[m no^[[m
^[[38;2;160;32;240m<80 x M-bM-^TM-^@>^[[m
^[[38;2;160;32;240m<80 x M-bM-^TM-^@>^[[m
SMOKE OK
```
Reading: empty line, `Asking` in plain purple, the `↳` arrow in plain purple with
the plain black question to its right on the same line, plain purple choices, and
both dividers plain purple — no bold sequence anywhere in the block. The
one-display guarantee is unit-proven: `test_prompt_to_intel_skips_tool_beats_when_emits_story_beat_is_false`
asserts `progress_steps == []` for an `emits_story_beat = False` tool, and
`test_question_tool_does_not_emit_a_story_beat` asserts the attribute on
`QuestionTool`.
