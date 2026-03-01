import sys
from pathlib import Path

import dotenv
from blessed import Terminal

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
        print(env_term.blue(f'\nLoading environment variables from "{env_file_path}"'))
        dotenv.load_dotenv(env_file_path)

sys.path.append(str(CWD_PATH))

from dandy.cli.session import session
from dandy.cli.utils import check_or_create_settings


def main():
    sys.path.append(str(CWD_PATH))

    check_or_create_settings(CWD_PATH)

    from dandy.conf import settings

    settings.reload_from_os()

    session.post_init(project_base_path=CWD_PATH)
    session.load()

    if not session.is_loaded:
        session.save()

    from dandy.cli.cli import DandyCli

    cli = DandyCli()

    if len(sys.argv) > 1:
        user_input = ' '.join(sys.argv[1:])

        if user_input[0] == '-':
            user_input = '/' + user_input[1:]

        if user_input[0] != '/':
            user_input = '/' + user_input

        arg_term = Terminal()

        print(arg_term.bold_blue(f'\nDandy'))

        cli.process_user_input(
            user_input=user_input
        )

    else:
        cli.run()

    print('')


if __name__ == '__main__':
    sys.exit(main())
