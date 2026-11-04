import importlib
import sys
from pathlib import Path

import dotenv

from dandy.shared.constants import DANDY_LOCAL_DIRECTORY_NAME


def check_or_create_settings(cwd_path: Path, system_exit_on_import_error: bool = True) -> None:
    from dandy.shared.settings.load import find_settings_json_file, get_settings_module_name

    settings_module_name = get_settings_module_name()

    try:
        importlib.import_module(settings_module_name)
    except ImportError:
        json_settings_path = find_settings_json_file()

        if json_settings_path is not None:
            print(f'Loaded settings from "{json_settings_path}".')
            return

        print(f'Could not find "{settings_module_name}" in your project.')

        settings_module_parts = settings_module_name.split('.')
        new_settings_module_file = f'{settings_module_parts[-1]}.py'
        new_settings_module_path = Path(cwd_path, *settings_module_parts[:-1])
        new_settings_module_file_path = Path(new_settings_module_path, new_settings_module_file)

        print(f'Creating "{new_settings_module_file_path}" from the default settings.')

        with open(
            Path(__file__).parent.parent.parent / 'shared' / 'settings' / 'default_settings.py', 'r'
        ) as default_settings:
            new_settings_module_path.mkdir(parents=True, exist_ok=True)

            with open(new_settings_module_file_path, 'w') as user_settings:
                user_settings.write(default_settings.read())

        print(
            f'You need to add "DANDY_SETTINGS_MODULE={settings_module_name}" to your environment variables.'
        )
        print(
            'Setup of "BASE_PATH" and "LLM_CONFIGS" are required in your new settings before proceeding.'
        )

        if system_exit_on_import_error:
            sys.exit(0)


def ensure_dandy_gitignore(project_base_path: Path) -> None:
    """Ensure a git project's .gitignore ignores dandy's local state directory.

    The .dandy directory holds per-project state (saved agent sessions,
    recordings, local settings) that should never be tracked, so a missing
    .dandy/ entry is appended to the project's .gitignore. Non-git
    directories are left untouched.
    """
    git_dir_path = Path(project_base_path, '.git')

    if not git_dir_path.is_dir() and not git_dir_path.is_file():
        return

    pattern = f'{DANDY_LOCAL_DIRECTORY_NAME}/'
    gitignore_path = Path(project_base_path, '.gitignore')
    existing_text = gitignore_path.read_text() if gitignore_path.is_file() else ''
    existing_lines = {line.strip() for line in existing_text.splitlines()}

    if pattern in existing_lines or f'/{DANDY_LOCAL_DIRECTORY_NAME}/' in existing_lines:
        return

    with open(gitignore_path, 'a') as gitignore_file:
        if existing_text and not existing_text.endswith('\n'):
            gitignore_file.write('\n')

        gitignore_file.write(f'{pattern}\n')
