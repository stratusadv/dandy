from __future__ import annotations

import importlib
import types
from typing import TYPE_CHECKING

from dandy.conf.utils import (
    get_settings_json_candidates,
    get_settings_module_name,
    load_settings_from_json_file,
)
from dandy.core.exceptions import DandyCriticalError

if TYPE_CHECKING:
    from pathlib import Path


class DandySettings:
    def __init__(self):
        self._has_loaded_user_settings = False
        from dandy import default_settings  # noqa: PLC0415

        self._settings_module_name = ...
        self._user_settings = ...
        self._json_settings_path: Path | None = None

        self._default_settings = default_settings

        self.load_user_settings()

    def __getattr__(self, name: str):
        if self._has_loaded_user_settings:
            if hasattr(self._user_settings, name):
                return getattr(self._user_settings, name)

            if hasattr(self._default_settings, name):
                return getattr(self._default_settings, name)

        else:
            message = f'Failed to import settings module "{self._settings_module_name}", make sure it exists in your project or python path directory.'
            raise DandyCriticalError(message)

        message = f'No attribute "{name}" found in settings, check your "{self._settings_module_name}" file.'
        raise DandyCriticalError(message)

    def load_user_settings(self):
        self._settings_module_name = get_settings_module_name()

        if self._settings_module_name is not None:
            try:
                if self._user_settings is not ... and isinstance(
                    self._user_settings, types.ModuleType
                ):
                    self._user_settings = importlib.reload(self._user_settings)
                else:
                    self._user_settings = importlib.import_module(self._settings_module_name)

                self._has_loaded_user_settings = True

                if (
                    self._default_settings.BASE_PATH is None
                    and self._user_settings.BASE_PATH is None
                ):
                    message = f'You need a BASE_PATH in your "{self._settings_module_name}".'
                    raise DandyCriticalError(message)

            except ImportError:
                self._user_settings = ...
                self._json_settings_path = None

                if self._load_user_settings_from_json():
                    self._has_loaded_user_settings = True

    def _load_user_settings_from_json(self) -> bool:
        for json_file_path in get_settings_json_candidates():
            if json_file_path.is_file():
                self._user_settings = load_settings_from_json_file(json_file_path)
                self._json_settings_path = json_file_path
                return True

        return False

    def reload_from_os(self):
        self._default_settings = importlib.reload(self._default_settings)
        self.load_user_settings()


settings = DandySettings()
