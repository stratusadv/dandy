import sys
from pathlib import Path

from dandy.cli.session import session
from dandy.cli.utils import (
    check_or_create_settings,
    load_environment_variables,
)


def main():
    CWD_PATH = Path.cwd()

    sys.path.append(str(CWD_PATH))

    load_environment_variables(CWD_PATH)
    check_or_create_settings(CWD_PATH)

    session.post_init(project_base_path=CWD_PATH)
    session.load()
    print(session)

    if not session.is_loaded:
        session.save()

    from dandy.conf import settings

    settings.reload_from_os()

    from dandy.cli.cli import DandyCli

    cli = DandyCli()

    cli.run()


if __name__ == '__main__':
    sys.exit(main())
