from blessed import Terminal

from dandy.interfaces.cli.commands import CLI_COMMANDS, flag_usage
from dandy.interfaces.cli.tui.tui import tui


def _usage_line(forms: str, description: str) -> str:
    return f'  dandy {forms:<29}{description}'


def _usage_text() -> str:
    lines = [
        '\n',
        'Usage:',
        _usage_line('', 'Start the interactive assistant (REPL)'),
        _usage_line('"<your request>"', 'Run one request then exit'),
        _usage_line('--continue "<request>"', 'Run one request inside the latest saved session'),
    ]

    for command in CLI_COMMANDS:
        forms = flag_usage(command)
        if forms is not None:
            lines.append(_usage_line(forms, command.description))

    lines += [
        _usage_line('-h, --help', 'Show this help message'),
        _usage_line('-v, --version', 'Show the version'),
        '\n',
        (
            'With no request, dandy starts an interactive session and stays in an '
            'agentic loop: every message you type is sent to the coding agent. '
            'Conversations are saved automatically; use /init (or /i) to create or '
            'refresh the project AGENTS.md, /new (or /n) to start over, /sessions '
            '(or /s) to list saved conversations, /resume (or /r) to continue one, '
            'and /quit (or /q) to exit. Pressing escape twice stops a running turn; '
            'at the prompt, pressing escape twice exits the loop.\n'
        ),
    ]

    return '\n'.join(lines)


_USAGE = _usage_text()


def print_usage() -> None:
    term = Terminal()
    print(term.bold_blue('\n Dandy') + term.normal + _USAGE)


def print_banner() -> None:
    arg_term = Terminal()

    print()

    tui.printer.bold_grey_divider()

    print(arg_term.bold_blue('\U0001f3a9 Dandy'))

    tui.printer.bold_blue_divider()
