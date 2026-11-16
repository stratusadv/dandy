"""Best-effort OS-level desktop notifications, independent of the terminal.

Linux uses `notify-send` (libnotify) and macOS uses `osascript`; every other
platform, or a machine without the binary, is a silent no-op. The spawn is
fire-and-forget — `DEVNULL` streams in a new session — so a missing daemon or
a hung binary can never block the calling (UI) thread.
"""

import subprocess
import sys

# Process-lifetime flags: 'missing' is set once the first spawn found no
# notification binary (or the platform has no known form).
_flags: dict[str, bool] = {}


def os_desktop_notify(message: str) -> None:
    """Raise a native desktop notification titled `Dandy` (never raises).

    Caches a missing binary per process so a machine without a notification
    daemon pays at most one failed spawn.
    """
    if _flags.get('missing'):
        return

    if sys.platform == 'linux':
        # `--urgency=low` is the best-effort hint for desktops that suppress
        # low-urgency popups while the app's own window has focus; Plasma does
        # not implement it for foreign app names (verified live), so treat it
        # as a no-op elsewhere and never block on it.
        command = ['notify-send', '--urgency=low', 'Dandy', message]
    elif sys.platform == 'darwin':
        escaped = message.replace('\\', '\\\\').replace('"', '\\"')
        command = ['osascript', '-e', f'display notification "{escaped}" with title "Dandy"']
    else:
        _flags['missing'] = True
        return

    try:
        subprocess.Popen(
            command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True
        )
    except FileNotFoundError:
        _flags['missing'] = True
    except OSError:
        pass
