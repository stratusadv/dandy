from __future__ import annotations

import importlib
import types
from typing import TYPE_CHECKING, Any

from dandy.shared.settings.load import (
    check_default_llm_config,
    get_settings_json_candidates,
    get_settings_module_name,
    load_settings_from_json_file,
)
from dandy.shared.exceptions import DandyCriticalError

if TYPE_CHECKING:
    from pathlib import Path


class DandySettings:
    def __init__(self) -> None:
        self._has_loaded_user_settings = False
        from dandy.shared.settings import default_settings  # noqa: PLC0415

        self._settings_module_name = ...
        self._user_settings = ...
        self._json_settings_path: Path | None = None

        self._default_settings = default_settings

        self.load_user_settings()

    def __getattr__(self, name: str) -> Any:
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

    def load_user_settings(self) -> None:
        self._settings_module_name = get_settings_module_name()

        module_settings = self._import_settings_module()

        if module_settings is None:
            self._user_settings = ...
            self._json_settings_path = None

            if self._load_user_settings_from_json():
                self._has_loaded_user_settings = True
            return

        unusable_reason = check_default_llm_config(module_settings)

        if unusable_reason is not None:
            # A module that imports but cannot resolve a default LLM config
            # (e.g. MODEL read from an unset environment variable) is unusable,
            # so the dandy.json fallback gets a chance before the CLI scaffolds
            # a new .py on top of it.
            self._user_settings = ...
            self._json_settings_path = None

            if self._load_user_settings_from_json():
                self._has_loaded_user_settings = True
            return

        self._user_settings = module_settings
        self._has_loaded_user_settings = True

        if self._default_settings.BASE_PATH is None and module_settings.BASE_PATH is None:
            message = f'You need a BASE_PATH in your "{self._settings_module_name}".'
            raise DandyCriticalError(message)

    def _import_settings_module(self) -> types.ModuleType | None:
        try:
            if self._user_settings is not ... and isinstance(self._user_settings, types.ModuleType):
                return importlib.reload(self._user_settings)

            return importlib.import_module(self._settings_module_name)

        except ImportError:
            return None

    def _load_user_settings_from_json(self) -> bool:
        for json_file_path in get_settings_json_candidates():
            if json_file_path.is_file():
                self._user_settings = load_settings_from_json_file(json_file_path)
                self._json_settings_path = json_file_path
                return True

        return False

    def reload_from_os(self) -> None:
        self._default_settings = importlib.reload(self._default_settings)
        self.load_user_settings()


settings = DandySettings()
