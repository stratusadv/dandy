import json
import os
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from dandy.constants import (
    DANDY_HOME_CONFIG_DIRECTORY_NAME,
    DANDY_JSON_FILE_NAME,
    DANDY_LOCAL_DIRECTORY_NAME,
    DEFAULT_SETTINGS_MODULE,
)
from dandy.core.exceptions import DandyCriticalError


def get_settings_module_name() -> str:
    return os.getenv('DANDY_SETTINGS_MODULE', DEFAULT_SETTINGS_MODULE)


def get_settings_json_candidates(dandy_directory: str = DANDY_LOCAL_DIRECTORY_NAME) -> list[Path]:
    return [
        Path.cwd() / dandy_directory / DANDY_JSON_FILE_NAME,
        Path.home() / '.config' / DANDY_HOME_CONFIG_DIRECTORY_NAME / DANDY_JSON_FILE_NAME,
    ]


def find_settings_json_file(dandy_directory: str = DANDY_LOCAL_DIRECTORY_NAME) -> Path | None:
    for json_file_path in get_settings_json_candidates(dandy_directory):
        if json_file_path.is_file():
            return json_file_path

    return None


_PATH_SETTINGS_KEYS = ('BASE_PATH', 'CACHE_SQLITE_DATABASE_PATH')


def load_settings_from_json_file(json_file_path: Path) -> SimpleNamespace:
    try:
        with open(json_file_path, encoding='utf-8') as json_file:
            json_data = json.load(json_file)
    except (OSError, json.JSONDecodeError) as error:
        message = f'Failed to load settings from "{json_file_path}".'
        raise DandyCriticalError(message) from error

    if not isinstance(json_data, dict):
        message = (
            f'The settings file "{json_file_path}" must contain a JSON object of '
            'settings attributes.'
        )
        raise DandyCriticalError(message)

    normalized_data = _normalize_json_settings_keys(json_data)
    normalized_data.setdefault('BASE_PATH', Path.cwd())

    return SimpleNamespace(**normalized_data)


def _normalize_json_settings_keys(json_data: dict) -> dict:
    normalized = {}

    for key, value in json_data.items():
        normalized_key = key.upper()

        if normalized_key in _PATH_SETTINGS_KEYS and isinstance(value, (str, os.PathLike)):
            value = Path(value).expanduser().absolute()

        elif normalized_key == 'LLM_CONFIGS' and isinstance(value, dict):
            value = {
                config_key.upper(): _normalize_llm_config_settings(config)
                for config_key, config in value.items()
            }

        elif normalized_key == 'CLI_CONFIG' and isinstance(value, dict):
            value = {
                task_key.upper(): task_value.upper() if isinstance(task_value, str) else task_value
                for task_key, task_value in value.items()
            }

        normalized[normalized_key] = value

    return normalized


def _normalize_llm_config_settings(config: Any) -> Any:
    if not isinstance(config, dict):
        return config

    return {key.upper(): sub_value for key, sub_value in config.items()}
