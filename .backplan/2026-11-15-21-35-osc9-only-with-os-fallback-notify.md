# OSC 9 only + OS-level notification fallback

- Developer: Nathan Johnson (nathanj@stratusadv.com)
- Status: Executed
- Date: 2026-11-15-21-35

## End State
Desktop notifications actually pop up in Konsole (via `notify-send` on Linux,
`osascript` on macOS), OSC 777 is never emitted by dandy again (Konsole hard
crashes on it — verified live this session), and terminals that answer the
OSC 633 support query still get the terminal-native OSC 9 form. The hermetic
suite, ruff, and the strict docs build all pass.

## Observable Concern
The OS fallback spawns a subprocess from the main thread: it must be fully
fire-and-forget (no blocking `communicate()` — a hung `notify-send` with no
session bus would stall the render loop), time-boxed, and never raise, so a
machine without a notification daemon costs nothing but a skipped notify.

## Current State
Verified live on the user's machine (Konsole, Wayland, `notify-send 0.8.8`
installed at `/usr/bin/notify-send`, no `terminal-notifier`):

- Konsole **crashes** when written `\x1b]777;notify\x07...\x07` (step
  `osc777` of `scripts/diagnose_notify.py`).
- Konsole survives the OSC 633 probe (`probe` step) and OSC 9 (`osc9` step),
  and emits **no** desktop notification for either — Konsole neither answers
  the probe yes nor forwards OSC 9.
- `dandy/interfaces/cli/tui/notify.py`: `notifications_enabled` gates on the
  `DESKTOP_NOTIFICATIONS` setting (default `True`), the env override
  `DANDY_DESKTOP_NOTIFICATIONS`, and the OSC 633 probe (yes-only, cached in
  the module-global `_support`). `desktop_notify` writes OSC 777 + OSC 9 to
  stdout.
- Call sites: `Printer.run_timed_task` (turn complete) and
  `Tui.get_user_input` (question parked) — both on the main thread, unchanged.
- `dandy/shared/subprocess.py::run_subprocess` is a blocking, polling helper
  designed for tool output (returns strings) — not suitable for fire-and-forget
  here, so the fallback uses plain `subprocess.Popen` with `DEVNULL`.
- Tests: `tests/interfaces/cli/test_notify.py` asserts the exact combined
  OSC 777 + OSC 9 string in three places; `test_printer.py` / `test_tui.py`
  assert the OSC 777 prefix on stdout.
- The previous plan doc (`2026-11-15-20-10-desktop-notifications-for-cli.md`)
  carries the deviation history (Konsole crash → env guard → probe → opt-out).

## Plan
1. Strip OSC 777 from dandy
   - `dandy/interfaces/cli/tui/notify.py`: `notification_sequences` emits OSC 9
     only; docstrings updated.
   - Update the exact-string assertions in `test_notify.py`, `test_printer.py`,
     `test_tui.py` to the OSC 9-only form.
   - Done when no `777` remains anywhere under `dandy/` or `tests/`.
2. Add the OS-level fallback
   - New `dandy/shared/notifications.py`: `os_desktop_notify(message)` —
     Linux: `subprocess.Popen(['notify-send', 'Dandy', message], stdout/err =
     DEVNULL, start_new_session=True)`; macOS: `Popen(['osascript', '-e',
     'display notification ... with title "Dandy"'])` with the message
     escaped; anything else (Windows, missing binary, spawn failure): no-op.
     Caches a "daemon available" decision so the probe costs at most one
     spawn per process. Never raises.
   - `notify.py`: `desktop_notify` sends the OSC 9 sequences when the probe
     says the terminal supports them, and otherwise falls back to the OS
     notification — so Konsole (probe silent) gets exactly one native
     `notify-send` popup, and a terminal that answers yes (Kitty) gets only
     its own native form, never a double notification. `notifications_enabled`
     shrinks to the setting/env gate; the probe moves into `desktop_notify`'s
     dispatch.
   - Done when unit tests cover: Linux path spawns `notify-send` with
     (title, message), macOS path spawns `osascript`, no-binary no-op,
     never-raises, and the OSC-vs-fallback split in `desktop_notify`.
3. Diagnostic script
   - `scripts/diagnose_notify.py`: drop the `osc777` step (documented crash
     on Konsole); `probe` / `osc9` / `bell` steps stay as-is.
4. Docs
   - `docs/user_guide/cli_agent.md`, `docs/changelog/v3.md`, and the CLI
     bullet in `AGENTS.md`: OSC 777 gone, OSC 9 + OS fallback described.
   - Done when `just docs-tests` passes.
5. Verification
   - `just test`, `ruff check .`, `ruff format . --check`, `just lint-imports`,
     `just docs-tests`.
   - Done when all report clean.
   - Manual: user runs dandy in Konsole and a `notify-send` popup appears on
     completion and on a parked question.

## Completion Test
`just test` (full hermetic suite) passes; `ruff check .` + `ruff format
--check .` clean; `just docs-tests` builds strict; `grep -r '777' dandy/
tests/` shows no notification usage; and the user confirms a desktop
notification pops up in Konsole on a real dandy turn.

## Deviations
1. Project-name prefix added to the notification message after user feedback
    - What: `desktop_notify` now prefixes the message with the project's directory name (`session.project_base_path.name`, e.g. "dandy — Request Completed in 4.2 seconds") before folding/capping, so a popup identifies which project sent it; the prefix is dropped when the name is empty (e.g. project base is `/`). Tests updated to stub `dandy.interfaces.cli.tui.notify.session`; docs updated.
    - Why: the user confirmed the notifications work but the popups only said "Dandy …" and asked for a short description of which project is running.
2. Linux `notify-send` call gained the `--urgency=low` hint; focus suppression was investigated and shelved
    - What: the Linux path spawns `notify-send --urgency=low Dandy <message>` (test updated to match). The follow-up request "don't notify while my window is focused" was investigated on the user's Konsole/KWin Wayland box: Plasma ignores `--urgency=low` for foreign app names, the KWin `queryWindowInfo` D-Bus call is refused with `UserCancel` from any client, and the X11 fallback reads only an empty Wayland shim — so no reliable focus check exists there. The user chose to leave the behavior as-is for now.
    - Why: `--urgency=low` is the standard hint and will auto-suppress on desktops that honor it (harmless no-op on those that don't); a focus check without a working active-window query would be guesswork.
