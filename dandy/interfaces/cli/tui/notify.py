import sys

# The longest message a desktop notification carries before it is cut off.
NOTIFICATION_MAX_LENGTH = 100


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
    """The raw OSC sequences asking the terminal for a desktop notification.

    OSC 777 is the xterm-family form (kitty, alacritty, xterm; GNOME and KDE
    terminals forward it to a native notification) and OSC 9 covers tmux and
    iTerm2. Each is BEL-terminated. Terminals that ignore both are harmless.
    """
    text = notification_text(message)

    return f'\x1b]777;notify\x07Dandy\x07{text}\x07\x1b]9;{text}\x07'


def desktop_notify(message: str) -> None:
    """Ask the terminal for a desktop notification (best-effort, never raises).

    Written directly to stdout the way the OSC 8 file links are, because
    blessed exposes no notification capability; the sequences carry no
    visible character and no newline, so the output stream is untouched.
    """
    try:
        sys.stdout.write(notification_sequences(message))
        sys.stdout.flush()
    except OSError:
        pass
