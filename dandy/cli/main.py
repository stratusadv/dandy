import sys
from pathlib import Path

from dandy.cli.cli import DandyCli

CWD_PATH = Path.cwd()

sys.path.append(str(CWD_PATH))


def main():
    from dandy.cli.utils import check_or_create_settings, load_environment_variables  # noqa: PLC0415

    load_environment_variables(CWD_PATH)
    check_or_create_settings(CWD_PATH)

    cli = DandyCli()

    cli.run()

if __name__ == '__main__':
    sys.exit(main())
