import sys
from pathlib import Path

import dotenv
from blessed import Terminal

from dandy.cli.tui.printer import Printer
from dandy.cli.tui.tui import tui
from dandy.constants import __VERSION__

CWD_PATH = Path.cwd()

env_file_names = [
    'dandy.env',
    'development.env',
    'dev.env',
    '.env',
]

for env_file_name in env_file_names:
    env_file_path = Path(CWD_PATH, env_file_name)
    if env_file_path.exists():
        env_term = Terminal()
        # print(env_term.blue(f'\nLoading environment variables from "{env_file_path}"'))
        dotenv.load_dotenv(env_file_path)

sys.path.append(str(CWD_PATH))

from dandy.cli.session import session  # noqa: E402
from dandy.cli.utils import check_or_create_settings  # noqa: E402


USAGE = (
    '\n'
    'Usage:\n'
    '  dandy                         Start the interactive assistant (REPL)\n'
    '  dandy "<your request>"        Run one request then exit\n'
    '  dandy -h, --help              Show this help message\n'
    '  dandy -v, --version           Show the version\n'
    '\n'
    'With no request, dandy starts an interactive session and stays in an '
    'agentic loop: every message you type is sent to the coding agent. '
    'Start a line with /clear to reset the conversation or /quit to exit; '
    'pressing escape twice also exits the loop.\n'
)


def _print_usage() -> None:
    term = Terminal()
    print(term.bold_blue('\n Dandy') + term.normal + USAGE)


def main() -> None:
    sys.path.append(str(CWD_PATH))

    if len(sys.argv) > 1 and sys.argv[1] in {'-h', '--help'}:
        _print_usage()
        return

    if len(sys.argv) > 1 and sys.argv[1] in {'-v', '--version'}:
        arg_term = Terminal()
        print(arg_term.bold_blue(f'\nDandy {__VERSION__}'))
        return

    check_or_create_settings(CWD_PATH)

    from dandy.conf import settings  # noqa: PLC0415

    settings.reload_from_os()

    session.post_init(project_base_path=CWD_PATH)
    session.load()

    if not session.is_loaded:
        session.save()

    from dandy.cli.cli import DandyCli  # noqa: PLC0415

    cli = DandyCli()

    if len(sys.argv) > 1:
        user_input = ' '.join(sys.argv[1:])

        arg_term = Terminal()

        print()

        tui.printer.grey_divider()

        print(arg_term.bold_blue('\U0001F3A9 Dandy'))

        tui.printer.blue_divider()

        cli.process_user_input(
            user_input=user_input
        )

    else:
        cli.run()

    tui.printer.grey_divider()

    print()

if __name__ == '__main__':
    sys.exit(main())
