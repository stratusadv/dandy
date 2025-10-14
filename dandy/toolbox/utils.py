import importlib
import sys
from pathlib import Path

import dotenv

from dandy.consts import TOOLBOX_DEFAULT_ENV_FILE_NAMES
from dandy.core.utils import get_settings_module_name


def check_or_create_settings(cwd_path: Path, system_exit_on_import_error: bool = True) -> None:
    settings_module_name = get_settings_module_name()

    try:
        importlib.import_module(settings_module_name)
    except ImportError:
        print(f'Could not find "{settings_module_name}" in your project.')

        settings_module_parts = settings_module_name.split('.')
        new_settings_module_file = f'{settings_module_parts[-1]}.py'
        new_settings_module_path = Path(cwd_path, *settings_module_parts[:-1])
        new_settings_module_file_path = Path(new_settings_module_path, new_settings_module_file)

        print(f'Creating "{new_settings_module_file_path}" from the default settings.')

        with open(Path(Path(__file__).parent.parent.resolve(), 'default_settings.py'), 'r') as default_settings:

            new_settings_module_path.mkdir(parents=True, exist_ok=True)

            with open(new_settings_module_file_path, 'w') as user_settings:
                user_settings.write(default_settings.read())

        print(f'You need to add "DANDY_SETTINGS_MODULE={settings_module_name}" to your environment variables.')
        print('Setup of "BASE_PATH" and "LLM_CONFIGS" are required in your new settings before proceeding.')

        if system_exit_on_import_error:
            sys.exit(0)

def load_environment_variables(cwd_path: Path) -> None:
    for env_file_name in TOOLBOX_DEFAULT_ENV_FILE_NAMES:
        env_file_path = Path(cwd_path, env_file_name)
        if env_file_path.exists():
            print(f'Loading environment variables from "{env_file_path}"')
            dotenv.load_dotenv(env_file_path)
