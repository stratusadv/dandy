import sys
from pathlib import Path

import dotenv

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
        print(f'Loading environment variables from "{env_file_path}"')
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

    cli.run()


if __name__ == '__main__':
    sys.exit(main())
