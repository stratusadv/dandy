import importlib
from pathlib import Path

import dotenv

from dandy.const import CLI_DEFAULT_ENV_FILE_NAMES, DEFAULT_SETTINGS_FILE_NAME
from dandy.utils import get_settings_module_name


def check_or_create_settings(cwd_path: Path) -> None:
    dandy_settings_module_name = get_settings_module_name()
    try:
        importlib.import_module(dandy_settings_module_name)
        return
    except ImportError:
        print(f'Could not find "{dandy_settings_module_name}" in your current directory. Creating one for you...')

        with open(Path(Path(__file__).parent.parent.resolve(), 'default_settings.py'), 'r') as default_settings:
            with open(Path(cwd_path, DEFAULT_SETTINGS_FILE_NAME), 'w') as user_settings:
                user_settings.write(default_settings.read())

        print(f'Created "{dandy_settings_module_name}" in your current directory.')
        print(f'You need to configure the "BASE_PATH" and "LLM_CONFIGS".')

def load_environment_variables(cwd_path: Path) -> None:
    for env_file_name in CLI_DEFAULT_ENV_FILE_NAMES:
        env_file_path = Path(cwd_path, env_file_name)
        if env_file_path.exists():
            print(f'Loading environment variables from "{env_file_path}"')
            dotenv.load_dotenv(env_file_path)
