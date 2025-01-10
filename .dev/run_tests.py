import argparse
import os
import subprocess
import sys

from pathlib import Path

def main() -> None:
    if sys.platform != 'win32':
        message = 'This script must run on Windows platform.'
        raise Exception(message)

    cwd = Path(__file__).parent.parent

    virtual_env = cwd / 'venv' / 'Scripts' / 'activate'
    virtual_env_alternate = cwd / '.venv' / 'Scripts' / 'activate'

    parser = argparse.ArgumentParser(description='Run coverage with tests.')

    apps_help = (
        'The specific app(s) to run testing on. '
        'The path should be relative to the project root. '
        'e.g., app/maintenance/work_order '
        'You can use a space-delimited list to include multiple apps '
        'e.g., app/maintenance/work_order/task app/maintenance/work_order/part'
    )

    parser.add_argument(
        '-a', '--apps',
        nargs='*',
        help=apps_help,
    )

    venv_help = (
        'The path to the activate file for the virtual environment. '
        'The path can be absolute or relative to the project root. '
        'e.g., C:/Users/User/code/django-skeleton/venv/Scripts/activate or '
        'venv/Scripts/activate'
    )

    parser.add_argument(
        '-v', '--venv',
        type=str,
        default=virtual_env,
        help=venv_help
    )

    args = parser.parse_args()

    if Path(args.venv).is_file():
        activate_virtualenv_cmd = virtual_env
    elif virtual_env_alternate.is_file():
        activate_virtualenv_cmd = virtual_env_alternate
    else:
        message = (
            f'Virtual environment "{virtual_env}" or '
            f'"{virtual_env_alternate}" not found.'
        )

        raise Exception(message)

    pip_install_coverage_cmd = 'pip install coverage'

    print('Running Testing ...\n')

    run_testing_cmd = [
        'python',
        '-m',
        'unittest',
        'discover',
        '-v',
        '-s',
        f'{cwd}',
        '-t',
        f'{cwd}',
    ]

    run_testing_cmd = ' '.join(run_testing_cmd)

    print(run_testing_cmd)

    cmd_call = (
        f'call {activate_virtualenv_cmd}'
        f' & {pip_install_coverage_cmd}'
        f' & cd..'
        f' & {run_testing_cmd}'
    )

    subprocess.run(cmd_call, check=True, shell=True)

    print('\nDone!')


if __name__ == '__main__':
    exit(main())