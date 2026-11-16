# Desktop notifications when the CLI completes a turn or parks a question

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-15-20-10
- Re-executed: 2026-11-15-20-35 (deviation 2, probe-based detection)

## End State
When `dandy` finishes a turn (or init pass) or the agent parks a question on
screen, the terminal is asked for a desktop notification via raw OSC
sequences (OSC 777 for xterm-family terminals, OSC 9 for tmux/iTerm2), so the
user is alerted even when the terminal window is not focused — covered by
hermetic unit tests, the docs (`docs/user_guide/cli_agent.md`,
`docs/changelog/v3.md`, `AGENTS.md`) are updated, and the hermetic suite
plus `ruff check` / `ruff format` pass.

## Observable Concern
The notification must be emitted from the main (UI) thread only, on the
success path of `Printer.run_timed_task` and the question branch of
`Tui.get_user_input`, and must be raw bytes written to stdout (the project's
established pattern for OSC 8 links — blessed has no notification
capability) that never raises and never adds a visible character or newline
to the output stream.

## Current State
- `dandy/interfaces/cli/tui/printer.py`: `Printer.run_timed_task` prints the
  `Request Completed in ...` event on the success path and re-raises worker
  errors (including `RunStoppedError`); it is the single shared run loop for
  agent turns and the init pass.
- `dandy/interfaces/cli/tui/tui.py`: `Tui.get_user_input(question=...,
  choices=...)` renders the agent question prompt on the main thread.
- `dandy/interfaces/cli/tui/text.py` sets the precedent: raw OSC sequences
  (`\x1b]8;;uri\x1b\\`) written directly because blessed lacks a capability
  for it.
- Tests: `tests/interfaces/cli/test_printer.py` mocks `sys.stdout.write` /
  `builtins.print` and exercises `run_timed_task`; `tests/interfaces/cli/test_tui.py`
  does the same for `get_user_input` (with `cbreak` patched).
- No existing bell/notify code anywhere in the repo.

## Plan
1. Add `dandy/interfaces/cli/tui/notify.py`
   - `notification_text(message)` — collapse whitespace, cap at 100 chars
     with a trailing ellipsis.
   - `notification_sequences(message)` — the raw OSC 777 + OSC 9 string,
     BEL-terminated.
   - `desktop_notify(message)` — best-effort stdout write + flush (swallows
     `OSError`).
   - Done when unit tests on the pure functions pass.
2. Fire the notification at the two moments
   - `Printer.run_timed_task`: on the success path, before the completion
     event.
   - `Tui.get_user_input`: in the `if question:` branch, before the prompt
     prints.
   - Done when `run_timed_task` and `get_user_input` tests assert the OSC
     bytes on stdout.
3. Hermetic tests
   - `tests/interfaces/cli/test_notify.py` (sequences, truncation, best-effort
     write).
   - New cases in `test_printer.py` (completion notifies) and `test_tui.py`
     (question notifies).
   - Done when `just test` (or targeted pytest) passes.
4. Docs
   - `docs/user_guide/cli_agent.md` TUI section, `docs/changelog/v3.md`
     Unreleased/Features, and the CLI bullet in `AGENTS.md`.
   - Done when `just docs-tests` passes.
5. Verification
   - `ruff check .` + `ruff format --check .` on the touched files,
     `just test`, `just docs-tests`.
   - Done when all three report clean.

## Completion Test
`just test` (full hermetic suite) passes with the new notify tests;
`ruff check .` and `ruff format . --check` are clean; `just docs-tests`
builds strict; the new unit tests show the exact OSC strings on the mocked
stdout for both the completion and the question path.

## Deviations
1. Konsole crash reported after execution
    - What: the raw OSC 777/OSC 9 write makes Konsole exit, so `notifications_enabled()` was added in `dandy/interfaces/cli/tui/notify.py` gating the write: Konsole (detected via the `KONSOLE_VERSION` env var it exports) is skipped, the new `DESKTOP_NOTIFICATIONS` setting (default `True`, added to `dandy/shared/settings/default_settings.py` and `tests/dandy_settings.py`) can turn notifications off, and the env override `DANDY_DESKTOP_NOTIFICATIONS` wins in either direction. Test env handling switched to `clear=True` because `mock.patch.dict` does not delete keys that are absent from the update dict.
    - Why: the user reported the notification crashed their Konsole; the fix keeps the feature on supporting terminals while making it safe everywhere and overridable.
2. Konsole still hard-crashed with the env-var guard in place (the guard is
   uncommitted and can be bypassed whenever the terminal's env vars do not
   reach the process).
   - What: probe-based detection replaces the env heuristic — the first
     notification (main thread only) asks the terminal the standard OSC 633
     `xterm-kitty` support query with a 0.25s non-blocking timeout; only a
     terminal that answers `ESC[?633;1C` ever receives OSC 777 / OSC 9.
     `DESKTOP_NOTIFICATIONS` now defaults to `False` (opt-in in
     `dandy_settings.py` or `DANDY_DESKTOP_NOTIFICATIONS=1`), so a terminal
     the probe cannot clear costs at most one short pause and never a
     sequence.
   - Why: env vars exported by a terminal are not a reliable crash guard
     (they can be unset for user-invoked processes), so the terminal itself
     must attest support; opt-in bounds the blast radius of any terminal the
     probe still cannot clear.
3. The feature is opt-out, not opt-in.
   - What: `DESKTOP_NOTIFICATIONS` defaults back to `True`
     (`dandy/shared/settings/default_settings.py`, `tests/dandy_settings.py`),
     the fallback in `notifications_enabled()` is `True`, and the docs
     (`cli_agent.md`, `docs/changelog/v3.md`, `AGENTS.md`) read opt-out.
   - Why: the user wants dandy opinionated about alerting them; the OSC 633
     probe already keeps crashing terminals safe, so the default is on and
     users opt out via the setting or `DANDY_DESKTOP_NOTIFICATIONS=0`.
