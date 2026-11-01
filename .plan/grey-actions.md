# Plan: Render CLI action beats in grey

## Context
Action sentences (e.g. "Reading src/foo.py.", "Checking the git working tree status.", "Listing dandy recursively.") are produced by tool `action_sentence` methods, pushed via `progress_callback` in `dandy/application/tool/service.py` (`_process_tool_call`, line ~202), and rendered by `_StoryProgress` in `dandy/interfaces/cli/tui/printer.py`. Currently the animating beat is bold blue and settled beats are plain black. Goal: all action beats render in grey.

## Steps

1. `dandy/interfaces/cli/tui/printer.py` — `_StoryProgress.settled_frame` (line 71):
   - Change `{self.term.normal}` to `{self.term.grey}` so settled beats are grey.

2. `dandy/interfaces/cli/tui/printer.py` — `_StoryProgress.frame` (line 75):
   - Change the prefix `f'{self.term.bold_blue}{indent}↳ '` to `f'{self.term.grey}{indent}↳ '` so the currently animating beat (and its `↳` marker) is grey.

3. `dandy/interfaces/cli/tui/printer.py` — docstrings:
   - `_StoryProgress` docstring (lines 49-51): replace "prints settled beats in black and animates the newest one in blue with trailing dots" with wording that beats render in grey (newest animated with trailing dots).
   - `run_timed_task` docstring (lines 156-159): replace "settling as plain lines and the most recent beat rendered in blue" with the grey wording.

4. `tests/interfaces/cli/test_printer.py`:
   - `test_settled_frame_is_plain_text_without_duration` (line 37): add `self.assertIn(progress.term.grey, frame)` (optionally rename to `test_settled_frame_renders_beat_in_grey`).
   - `test_current_frame_renders_beat_in_blue` (line 44): rename to `test_current_frame_renders_beat_in_grey` and change the assertion on line 49 from `progress.term.bold_blue` to `progress.term.grey`.

5. Verify: run `python -m pytest tests/interfaces/cli/test_printer.py -v` (or `python -m unittest discover tests/interfaces/cli` per project convention). No other tests assert the blue color (only line 49 above).

## Notes
- Use `term.grey` (dim) for the beat text to match the existing secondary-text usage in `dandy/interfaces/cli/tui/markdown.py`; if it reads too faintly, `term.bold_grey` (as used by `grey_divider`) is the fallback.
- Out of scope (leave as-is): the blue "thinking phrase" line (`running_phrase`, line 135), the orange task header (`run_timed_task` header, line 167), the green completion sentence (line 209), and the debug verbose trace in `dandy/interfaces/cli/cli.py` (`_emit_verbose`).
