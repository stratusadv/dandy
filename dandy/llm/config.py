from dandy.conf import settings
from dandy.core.exceptions import DandyError

from dandy.core.utils import get_settings_module_name
from dandy.http.intelligence.intel import HttpResponseIntel, HttpRequestIntel
from dandy.http.url import Url
from dandy.llm.options import LlmOptions
from dandy.llm.request.request import LlmRequestBody

_DEFAULT_TRANSFER_KEYS = [
    'HOST',
    'PORT',
    'API_KEY',
]

_CONFIGS_NAME = 'LLM_CONFIGS'

class LlmConfig:
    def __init__(
            self,
            name: str,
    ):
        self.name = name

        settings_configs = getattr(settings, _CONFIGS_NAME)

        if not isinstance(settings_configs, dict) or not settings_configs:
            message = f'Your "{_CONFIGS_NAME}" in your "{get_settings_module_name()}" module is configured incorrectly.'
            raise DandyError(message)

        if 'DEFAULT' not in settings_configs:
            message = f'You need a "DEFAULT" in your "{_CONFIGS_NAME}" in your "{get_settings_module_name()}" module.'
            raise DandyError(message)

        config = settings_configs.get(name)

        if not isinstance(config, dict):
            message = f'the "{_CONFIGS_NAME}" in the settings are configured incorrectly.'
            raise DandyError(message)

        for key in _DEFAULT_TRANSFER_KEYS:
            if key in config:
                if config[key] is None or config[key] == '':
                    message = f'The "{key}" in "{_CONFIGS_NAME}.{name}" in your "{get_settings_module_name()}" cannot be empty.'
                    raise DandyError(message)

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

        self.options = LlmOptions()

        self._set_options_from_config()

        self.http_request_intel.url.path_parameters = [
            'v1',
            'chat',
            'completions'
        ]

    def generate_request_body(
        self,
    ) -> LlmRequestBody:
        return LlmRequestBody(
            model=self.model,
            **self.options.model_dump(exclude_none=True),
            stream=False,
        )

    @staticmethod
    def get_response_content(response_intel: HttpResponseIntel) -> str:
        return response_intel.json_data['choices'][0]['message']['content']

    def get_settings_value(self, key: str, required: bool = False):
        value = self._settings_values.get(key)

        if required and value is None:
            message = f'The "{key}" was not found in your settings and is required by "{self.__class__.__name__}".'
            raise DandyError(message)

        return value

    def reset(self):
        self._set_options_from_config()

    def _set_options_from_config(self):
        options = self._settings_values.get('options', None)

        if isinstance(options, dict):
            self.options = LlmOptions(
                **options
            )



