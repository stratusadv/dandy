import sys
from pathlib import Path

from dandy.cli.utils import check_or_create_settings, load_environment_variables  # noqa: PLC0415
from dandy.cli.conf import config

def main():
    CWD_PATH = Path.cwd()

    sys.path.append(str(CWD_PATH))

    load_environment_variables(CWD_PATH)
    check_or_create_settings(CWD_PATH)

    config.project_base_path = CWD_PATH

    from dandy.conf import settings

    settings.reload_from_os()

    from dandy.cli.cli import DandyCli

    cli = DandyCli(
        current_working_directory=CWD_PATH
    )

    cli.run()

if __name__ == '__main__':
    sys.exit(main())
