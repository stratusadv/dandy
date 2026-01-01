from typing import Literal

from dandy.conf import settings
from dandy.core.exceptions import DandyException
from dandy.core.utils import get_settings_module_name
from dandy.http.intelligence.intel import HttpRequestIntel
from dandy.http.url import Url


_DEFAULT_TRANSFER_KEYS = [
    'HOST',
    'PORT',
    'API_KEY',
]

class BaseConfig:
    type_: str

    def __init__(
            self,
            name: str,
    ):
        configs_name = f'{self.type_.upper()}_CONFIGS'
        settings_configs = getattr(settings, configs_name)

        if not isinstance(settings_configs, dict) or not settings_configs:
            message = f'Your "{configs_name}" in your "{get_settings_module_name()}" module is configured incorrectly.'
            raise DandyException(message)

        if 'DEFAULT' not in settings_configs:
            message = f'You need a "DEFAULT" in your "{configs_name}" in your "{get_settings_module_name()}" module.'
            raise DandyException(message)

        config = settings_configs.get(name)

        if not isinstance(config, dict):
            message = f'the "{configs_name}" in the settings are configured incorrectly.'
            raise DandyException(message)

        for key in _DEFAULT_TRANSFER_KEYS:
            if key in config:
                if config[key] is None or config[key] == '':
                    message = f'The "{key}" in "{configs_name}.{name}" in your "{get_settings_module_name()}" cannot be empty.'
                    raise DandyException(message)

            config[key] = config[key] if config.get(key) else settings_configs['DEFAULT'][key]

        self._settings_values = {
            key.lower(): val
            for key, val in config.items()
        }

        self.http_request_intel = HttpRequestIntel(
            method='POST',
            url=Url(
                host=self.get_settings_value('host', True),
                port=self.get_settings_value('port', True),
                path_parameters=self.get_settings_value('path_parameters'),
                query_parameters=self.get_settings_value('query_parameters'),
            ),
            headers=self.get_settings_value('headers') or {},
            bearer_token=self.get_settings_value('api_key') or self.get_settings_value('bearer_token'),
        )

        self.model = self.get_settings_value('model', True)

        self.__post_init__()

    def __post_init__(self):
        pass

    def get_settings_value(self, key: str, required: bool = False):
        value = self._settings_values.get(key)

        if required and value is None:
            message = f'The "{key}" was not found in your settings and is required by "{self.__class__.__name__}".'
            raise DandyException(message)

        return value

