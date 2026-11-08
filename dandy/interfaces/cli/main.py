import sys
from pathlib import Path
from typing import TYPE_CHECKING

import dotenv
from blessed import Terminal

from dandy.interfaces.cli.error_log import log_cli_error
from dandy.interfaces.cli.one_shot import OneShotPlan, parse_one_shot
from dandy.interfaces.cli.usage import print_banner, print_usage
from dandy.interfaces.cli.tui.tui import tui
from dandy.shared.constants import __VERSION__

if TYPE_CHECKING:
    from dandy.interfaces.cli.cli import DandyCli

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
from dandy.interfaces.cli.utils import check_or_create_settings, ensure_dandy_gitignore  # noqa: E402


def _dispatch_repl(cli: 'DandyCli', plan: OneShotPlan) -> int:
    if plan.command in {'sessions', 'resume'}:
        print_banner()

        name = plan.name

        if name is None or not cli.load_named_session(name):
            return 1

    if plan.command == 'new':
        cli.run(new_name=plan.name)
    else:
        cli.run()

    return 0


def _dispatch_one_shot(cli: 'DandyCli', plan: OneShotPlan) -> int:
    print_banner()

    if plan.continue_latest:
        succeeded = cli.continue_latest_session(plan.request)
        return 0 if succeeded else 1

    if plan.command is None:
        cli.process_user_input(user_input=plan.request)
        return 0 if cli.last_turn_succeeded else 1

    name = plan.name

    if plan.command == 'init':
        succeeded = cli.run_init()
    elif plan.command == 'sessions' and name is None:
        cli.run_sessions_list()
        return 0
    elif plan.command == 'new':
        succeeded = cli.run_new_one_shot(name, plan.request)
    elif name is None:
        print_usage()
        return 0
    elif plan.command in {'sessions', 'resume'}:
        succeeded = cli.run_in_session(name, plan.request)
    elif plan.command == 'delete':
        succeeded = cli.run_delete(name)

    return 0 if succeeded else 1


def _dispatch(cli: 'DandyCli', plan: OneShotPlan) -> int:
    if plan.repl:
        return _dispatch_repl(cli, plan)

    return _dispatch_one_shot(cli, plan)


def main() -> int:
    sys.path.append(str(CWD_PATH))

    if len(sys.argv) > 1 and sys.argv[1] in {'-h', '--help'}:
        print_usage()
        return 0

    if len(sys.argv) > 1 and sys.argv[1] in {'-v', '--version'}:
        arg_term = Terminal()
        print(arg_term.bold_blue(f'\nDandy {__VERSION__}'))
        return 0

    plan = parse_one_shot(sys.argv[1:]) if len(sys.argv) > 1 else OneShotPlan(repl=True)

    if plan is None:
        print_usage()
        return 0

    try:
        check_or_create_settings(CWD_PATH)

        from dandy.shared.settings import settings  # noqa: PLC0415

        settings.reload_from_os()

        session.post_init(project_base_path=CWD_PATH)

        ensure_dandy_gitignore(CWD_PATH)

        from dandy.interfaces.cli.cli import DandyCli  # noqa: PLC0415

        exit_code = _dispatch(DandyCli(), plan)
    except Exception as error:
        log_cli_error(CWD_PATH, 'cli', error)
        crash_term = Terminal()
        print()
        print(crash_term.red(f'Dandy failed: {error}'))
        return 1

    tui.printer.bold_grey_divider()

    print()

    return exit_code


if __name__ == '__main__':
    sys.exit(main())
