import importlib
import os
import sys
from pathlib import Path


CWD_PATH = Path.cwd()

sys.path.append(str(CWD_PATH))


def main():
    from dandy.cli.utils import check_or_create_settings, load_environment_variables  # noqa: PLC0415

    load_environment_variables(CWD_PATH)
    check_or_create_settings(CWD_PATH)

    from dandy.conf import settings

    settings.reload()

    from dandy.cli.cli import DandyCli

    cli = DandyCli()

    cli.run()

if __name__ == '__main__':
    sys.exit(main())
