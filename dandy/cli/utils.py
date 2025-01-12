from pathlib import Path

import dotenv

from dandy.const import USER_SETTINGS_FILE_NAME, CLI_DEFAULT_ENV_FILE_NAMES


def check_or_create_settings(cwd_path: Path) -> None:
    if Path(cwd_path, USER_SETTINGS_FILE_NAME).exists():
        return

    print(f'Could not find "{USER_SETTINGS_FILE_NAME}" in your current directory. Creating one for you...')

    with open(Path(Path(__file__).parent.parent.resolve(), 'default_settings.py'), 'r') as default_settings:
        with open(Path(cwd_path, 'dandy_settings.py'), 'w') as user_settings:
            user_settings.write(default_settings.read())

    print(f'Created "{USER_SETTINGS_FILE_NAME}" in your current directory.')
    print(f'You need to configure the "BASE_PATH" and "LLM_CONFIGS".')

def load_environment_variables(cwd_path: Path) -> None:
    for env_file_name in CLI_DEFAULT_ENV_FILE_NAMES:
        env_file_path = Path(cwd_path, env_file_name)
        if env_file_path.exists():
            print(f'Loading environment variables from "{env_file_path}"')
            dotenv.load_dotenv(env_file_path)
