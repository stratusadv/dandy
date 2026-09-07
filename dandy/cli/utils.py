import importlib
import sys
from pathlib import Path

import dotenv

from dandy.conf import settings


def get_cli_llm_config(task: str) -> str:
    """Return the LLM config name for a CLI task, falling back to 'DEFAULT'."""
    cli_config = getattr(settings, 'CLI_CONFIG', None)

    if isinstance(cli_config, dict):
        config_name = cli_config.get(task)

        if isinstance(config_name, str) and config_name:
            return config_name

    return 'DEFAULT'


def check_or_create_settings(cwd_path: Path, system_exit_on_import_error: bool = True) -> None:
    from dandy.conf.utils import find_settings_json_file, get_settings_module_name

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
            Path(Path(__file__).parent.parent.resolve(), 'default_settings.py'), 'r'
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
