import os
import importlib

from dandy.const import USER_SETTINGS_FILE_NAME
from dandy.core.exceptions import DandyException


class DandySettings:
    def __init__(self):
        from dandy import default_settings
        self.default_settings = default_settings

        DANDY_SETTINGS_MODULE = os.getenv('DANDY_SETTINGS_MODULE')

        if DANDY_SETTINGS_MODULE is not None:
            try:
                user_settings = importlib.import_module(DANDY_SETTINGS_MODULE)
                self.user_settings = user_settings
            except ImportError:
                raise DandyException(f'Failed to import settings module "{DANDY_SETTINGS_MODULE}", make sure it exists in your project or python path directory.')
        else:
            try:
                import dandy_settings as user_settings
                self.user_settings = user_settings
            except ImportError:
                raise DandyException(f'Failed to import settings file "{USER_SETTINGS_FILE_NAME}", make sure it exists in your project root directory or python path directory.')

        if self.default_settings.BASE_PATH is None and self.user_settings.BASE_PATH is None:
            raise DandyException(f'You need a BASE_PATH in your "{USER_SETTINGS_FILE_NAME}".')

        if self.default_settings.LLM_CONFIGS is None and self.user_settings.LLM_CONFIGS is None:
            raise DandyException(f'You need a "default" to the "LLM_CONFIG" in your "{USER_SETTINGS_FILE_NAME}".')

    def __getattr__(self, name):
        if hasattr(self.user_settings, name):
            return getattr(self.user_settings, name)

        if hasattr(self.default_settings, name):
            return getattr(self.default_settings, name)

        raise DandyException(f'No attribute "{name}" found in settings, check your "{USER_SETTINGS_FILE_NAME}" file.')


settings = DandySettings()


