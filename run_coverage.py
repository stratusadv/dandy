import argparse
import subprocess
import sys

from pathlib import Path


OMITS = (
    # Directories
    '*/system/*',
    '*/tests/*',
    '*/migrations/*',
    '*/static/*',
    '*/venv/*',
    '*/.venv/*',

    # Files
    'apps.py',
    '__init__.py',
    'manage.py',
    'automation.py',
    'run_coverage.py'
)


def main() -> None:
    # Do not ever rename this file to coverage.py as it creates an infinite
    # loop. This script must run from the root of your project.

    if sys.platform != 'win32':
        message = 'This script must run on Windows platform.'
        raise Exception(message)

    cwd = Path(__file__).parent
    virtual_env = cwd / 'venv' / 'Scripts' / 'activate'
    virtual_env_alternate = cwd / '.venv' / 'Scripts' / 'activate'

    parser = argparse.ArgumentParser(description='Run coverage with Django tests.')

    apps_help = (
        'The specific app(s) to run coverage on. '
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

    settings_help = (
        'The Django settings module. '
        'This is a Python module path that is relative to the project root. '
        'e.g., system.testing.settings'
    )

    parser.add_argument(
        '-s', '--settings',
        type=str,
        default='system.testing.settings',
        help=settings_help
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

    no_browser_help = (
        'Do not open the browser window to show the coverage results.'
    )

    parser.add_argument(
        '-nb', '--nobrowser',
        action='store_true',
        help=no_browser_help
    )

    no_erase_help = (
        'Do not erase the coverage results.'
    )

    parser.add_argument(
        '-ne', '--noerase',
        action='store_true',
        help=no_erase_help
    )

    no_html_help = 'Do not write the coverage results to HTML.'

    parser.add_argument(
        '-nh', '--nohtml',
        action='store_true',
        help=no_html_help
    )

    args = parser.parse_args()

    django_app_paths = ' '.join(args.apps) if args.apps else ''

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

    django_settings = args.settings

    django_settings_path = cwd.joinpath(
        *django_settings.split('.')[:-1],
        f'{django_settings.split(".")[-1]}.py'
    )

    if not django_settings_path.is_file():
        message = f'Django test settings "{django_settings_path}" not found.'
        raise Exception(message)

    print('Running coverage with django tests ...\n')

    omits = ','.join(OMITS)

    coverage_run_cmd = [
        'coverage',
        'run',
        '--branch',
        '--source=.',
        f'--omit={omits}',
        'manage.py',
        'test',
        f'{django_app_paths}',
        f'--settings={django_settings}',
        '--noinput'
    ]

    coverage_run_cmd = ' '.join(coverage_run_cmd)

    cmd_call = (
        f'call {activate_virtualenv_cmd}'
        f' & {pip_install_coverage_cmd}'
        f' & {coverage_run_cmd}'
    )

    html_directory = '.coverage_html_report'

    if not args.nohtml:
        coverage_html_cmd = f'coverage html --directory={html_directory}'
        cmd_call += f' & {coverage_html_cmd}'

    if not args.noerase:
        coverage_erase_cmd = f'coverage erase'
        cmd_call += f' & {coverage_erase_cmd}'

    if not args.nobrowser:
        open_browser_cmd = f'start "" "{cwd / html_directory / "index.html"}"'
        cmd_call += f' & {open_browser_cmd}'

    subprocess.run(cmd_call, check=True, shell=True)

    print('\nDone!')


if __name__ == '__main__':
    main()