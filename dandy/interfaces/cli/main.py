import sys
from pathlib import Path

import dotenv
from blessed import Terminal

from dandy.interfaces.cli.tui.tui import tui
from dandy.shared.constants import __VERSION__

CWD_PATH = Path.cwd()

env_file_names = ['dandy.env', 'development.env', 'dev.env', '.env']

for env_file_name in env_file_names:
    env_file_path = Path(CWD_PATH, env_file_name)
    if env_file_path.exists():
        env_term = Terminal()
        # print(env_term.blue(f'\nLoading environment variables from "{env_file_path}"'))
        dotenv.load_dotenv(env_file_path)

sys.path.append(str(CWD_PATH))

from dandy.application.agent.session import session  # noqa: E402
from dandy.interfaces.cli.utils import check_or_create_settings  # noqa: E402


USAGE = (
    '\n'
    'Usage:\n'
    '  dandy                         Start the interactive assistant (REPL)\n'
    '  dandy "<your request>"        Run one request then exit\n'
    '  dandy --continue "<request>"  Run one request inside the latest saved session\n'
    '  dandy -h, --help              Show this help message\n'
    '  dandy -v, --version           Show the version\n'
    '\n'
    'With no request, dandy starts an interactive session and stays in an '
    'agentic loop: every message you type is sent to the coding agent. '
    'Conversations are saved automatically; use /new to start over, '
    '/sessions to list saved conversations, /resume <name> to continue one, '
    'and /quit to exit. Pressing escape twice also exits the loop.\n'
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

    if len(sys.argv) > 1:
        one_shot_arguments = [arg for arg in sys.argv[1:] if arg != '--continue']

        if not one_shot_arguments:
            _print_usage()
            return

    check_or_create_settings(CWD_PATH)

    from dandy.shared.settings import settings  # noqa: PLC0415

    settings.reload_from_os()

    session.post_init(project_base_path=CWD_PATH)

    from dandy.interfaces.cli.cli import DandyCli  # noqa: PLC0415

    cli = DandyCli()

    if len(sys.argv) > 1:
        user_input = ' '.join(one_shot_arguments)

        arg_term = Terminal()

        print()

        tui.printer.grey_divider()

        print(arg_term.bold_blue('\U0001f3a9 Dandy'))

        tui.printer.blue_divider()

        if '--continue' in sys.argv[1:]:
            cli.continue_latest_session(user_input)
        else:
            cli.process_user_input(user_input=user_input, save_session=False)

    else:
        cli.run()

    tui.printer.grey_divider()

    print()


if __name__ == '__main__':
    sys.exit(main())
