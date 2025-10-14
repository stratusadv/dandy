import importlib

from dandy.core.exceptions import DandyCriticalException
from dandy.core.utils import get_settings_module_name


class DandySettings:
    def __init__(self):
        from dandy import default_settings
        self._default_settings = default_settings

        self._settings_module_name = get_settings_module_name()

        if self._settings_module_name is not None:
            try:
                self._user_settings = importlib.import_module(self._settings_module_name)
            except ImportError as error:
                message = f'Failed to import settings module "{self._settings_module_name}", make sure it exists in your project or python path directory.'
                raise DandyCriticalException(message) from error
        else:
            try:
                from tests import dandy_settings as user_settings
                self._user_settings = user_settings
            except ImportError as error:
                message = f'Failed to import settings module "{self._settings_module_name}", make sure it exists in your project root directory or python path directory.'
                raise DandyCriticalException(message) from error

        if self._default_settings.BASE_PATH is None and self._user_settings.BASE_PATH is None:
            message = f'You need a BASE_PATH in your "{self._settings_module_name}".'
            raise DandyCriticalException(message)

        if self._default_settings.LLM_CONFIGS is None and self._user_settings.LLM_CONFIGS is None:
            message = f'You need a "default" to the "LLM_CONFIG" in your "{self._settings_module_name}".'
            raise DandyCriticalException(message)

    def __getattr__(self, name: str):
        if hasattr(self._user_settings, name):
            return getattr(self._user_settings, name)

        if hasattr(self._default_settings, name):
            return getattr(self._default_settings, name)

        message = f'No attribute "{name}" found in settings, check your "{self._settings_module_name}" file.'
        raise DandyCriticalException(message)


settings = DandySettings()


