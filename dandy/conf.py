from dandy.constants import DANDY_SETTINGS_FILE_NAME
from dandy.core.exceptions import DandyException


class DandySettings:
    def __init__(self):
        from dandy import settings as default_settings
        self.default_settings = default_settings

        import dandy_settings as user_settings
        self.user_settings = user_settings

        if self.default_settings.BASE_PATH is None and self.user_settings.BASE_PATH is None:
            raise DandyException(f'You need a BASE_PATH in your "{DANDY_SETTINGS_FILE_NAME}".')

        if self.default_settings.LLM_CONFIGS is None and self.user_settings.LLM_CONFIGS is None:
            raise DandyException(f'You need a "default" to the "LLM_CONFIG" in your "{DANDY_SETTINGS_FILE_NAME}".')

    def __getattr__(self, name):
        if hasattr(self.user_settings, name):
            return getattr(self.user_settings, name)

        if hasattr(self.default_settings, name):
            return getattr(self.default_settings, name)

        raise f'No attribute {name} found in settings.'

settings = DandySettings()


