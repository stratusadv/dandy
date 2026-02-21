import importlib

from dandy.core.exceptions import DandyCriticalError
from dandy.core.utils import get_settings_module_name


class DandySettings:
    def __init__(self):
        self._has_loaded_user_settings = False
        from dandy import default_settings  # noqa: PLC0415

        self._settings_module_name = ...
        self._user_settings = ...

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
                self._user_settings = importlib.import_module(
                    self._settings_module_name
                )

                self._has_loaded_user_settings = True

                if (
                    self._default_settings.BASE_PATH is None
                    and self._user_settings.BASE_PATH is None
                ):
                    message = (
                        f'You need a BASE_PATH in your "{self._settings_module_name}".'
                    )
                    raise DandyCriticalError(message)

            except ImportError:
                pass

    def reload_from_os(self):
        self._default_settings = importlib.reload(self._default_settings)
        self.load_user_settings()


settings = DandySettings()
