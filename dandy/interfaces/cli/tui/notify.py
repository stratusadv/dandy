import os
import sys
import threading
import time

from blessed import Terminal

from dandy.application.agent.session import session
from dandy.shared.notifications import os_desktop_notify
from dandy.shared.settings import settings

# The longest message a desktop notification carries before it is cut off.
NOTIFICATION_MAX_LENGTH = 100

# How long the support probe waits for the terminal's answer before giving up.
PROBE_TIMEOUT_SECONDS = 0.25

# The standard OSC 633 (`xterm-kitty`) query asking the terminal whether it
# implements shell-integration notification support; the terminal answers with
# an ESC[?633;1C (yes) or ESC[?633;0C (no) DSR reply.
PROBE_QUERY = '\x1b]633;P;notify=?\x1b\\'

_lock = threading.Lock()
_support: dict[str, bool | None] = {}


def notification_text(message: str) -> str:
    """Collapse the message to one line, capped at 100 characters.

    Whitespace runs fold to single spaces so a multi-line answer still fits on
    one notification line; anything longer is cut at the cap with an ellipsis.
    """
    text = ' '.join(message.split())

    if len(text) > NOTIFICATION_MAX_LENGTH:
        text = f'{text[: NOTIFICATION_MAX_LENGTH - 1]}…'

    return text


def notification_sequences(message: str) -> str:
    """The raw OSC 9 sequence asking the terminal for a desktop notification.

    OSC 9 is understood by tmux and iTerm2 and, on Wayland, forwarded to the
    notification daemon by KDE. OSC 777 (the xterm-family form) is deliberately
    never emitted: Konsole hard-crashes on it. Terminals that answer the OSC 633
    probe no, or stay silent, fall back to the OS-level notification instead.
    """
    text = notification_text(message)

    return f'\x1b]9;{text}\x07'


def notifications_enabled() -> bool:
    """Whether the user has desktop notifications switched on.

    Off when the setting `DESKTOP_NOTIFICATIONS` is false; the env override
    `DANDY_DESKTOP_NOTIFICATIONS` wins in either direction. The setting is on
    by default; dandy is opinionated about alerting you.
    """
    env_override = os.getenv('DANDY_DESKTOP_NOTIFICATIONS')

    if env_override is not None:
        return env_override.strip().lower() not in {'0', 'false', 'no', 'off', ''}

    return bool(getattr(settings, 'DESKTOP_NOTIFICATIONS', True))


def _terminal_supports_notifications(term: Terminal) -> bool:
    with _lock:
        if 'result' not in _support:
            _support['result'] = _probe_terminal_support(term)

        return _support['result']


def _probe_terminal_support(term: Terminal) -> bool:
    """Ask the terminal itself once (main thread only) if it can notify.

    Sends the OSC 633 query, then drains up to 250ms of input looking for the
    DSR reply; anything that does not answer — or answers no — falls back to
    the OS-level notification instead of receiving terminal sequences.
    """
    try:
        sys.stdout.write(PROBE_QUERY)
        sys.stdout.flush()
    except OSError:
        return False

    reply = ''
    deadline = time.perf_counter() + PROBE_TIMEOUT_SECONDS

    try:
        with term.cbreak():
            while time.perf_counter() < deadline:
                key = term.inkey(timeout=0.02)

                if not key:
                    continue

                reply += str(key)

                if '633;1' in reply:
                    return True

                if '633;0' in reply:
                    return False
    except OSError:
        return False

    return False


def desktop_notify(message: str, term: Terminal) -> None:
    """Ask for a desktop notification (best-effort, never raises).

    Skips silently when `notifications_enabled()` is false. Otherwise the
    terminal-native OSC 9 goes to stdout when the terminal answered the OSC 633
    probe yes, and the OS-level notification (`notify-send` / `osascript`) is
    the fallback for every terminal that did not — which is what actually
    alerts Konsole. The message is prefixed with the project's directory name
    ("dandy — Request Completed in 4.2 seconds") so a popup identifies which
    project sent it; the prefix is dropped when the name is empty.
    """
    if not notifications_enabled():
        return

    project = session.project_base_path.name

    if project:
        message = f'{project} — {message}'

    sent = False

    if _terminal_supports_notifications(term):
        try:
            sys.stdout.write(notification_sequences(message))
            sys.stdout.flush()
            sent = True
        except OSError:
            pass

    if not sent:
        os_desktop_notify(notification_text(message))
