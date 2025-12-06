import sys
from pathlib import Path

CWD_PATH = Path.cwd()

sys.path.append(str(CWD_PATH))


def main():
    from dandy.cli.utils import check_or_create_settings, load_environment_variables

    load_environment_variables(CWD_PATH)

    check_or_create_settings(CWD_PATH)



if __name__ == '__main__':
    print('Starting Dandy CLI...')

    sys.exit(main())
