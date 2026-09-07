from dandy.conf import settings
from dandy.conf.utils import get_settings_module_name
from dandy.core.exceptions import DandyError
from dandy.http.intelligence.intel import HttpResponseIntel, HttpRequestIntel
from dandy.http.url import Url
from dandy.llm.options import LlmOptions
from dandy.llm.request.request import LlmRequestBody

_DEFAULT_TRANSFER_KEYS = ['HOST', 'PORT', 'API_KEY']

# The share of the context window reserved for the model's output. The other
# half (0.75) is the agent's compaction target in dandy/cli/agent/coding_agent.py.

LLM_OUTPUT_TOKEN_RATIO = 0.25

_CONFIGS_NAME = 'LLM_CONFIGS'


class LlmConfig:
    def __init__(self, name: str) -> None:
        self.name = name

        settings_configs = getattr(settings, _CONFIGS_NAME)

        if not isinstance(settings_configs, dict) or not settings_configs:
            message = f'Your "{_CONFIGS_NAME}" in your "{get_settings_module_name()}" module is configured incorrectly.'
            raise DandyError(message)

        if 'DEFAULT' not in settings_configs:
            message = f'You need a "DEFAULT" in your "{_CONFIGS_NAME}" in your "{get_settings_module_name()}" module.'
            raise DandyError(message)

        config = settings_configs.get(name)

        if config is None:
            message = f'The "{name}" in "{_CONFIGS_NAME}" in your "{get_settings_module_name()}" module is not configured.'
            raise DandyError(message)

        if not isinstance(config, dict):
            message = f'the "{_CONFIGS_NAME}" in the "{get_settings_module_name()}" module are configured incorrectly.'
            raise DandyError(message)

        for key in _DEFAULT_TRANSFER_KEYS:
            if key in config:
                if config[key] is None or config[key] == '':
                    message = f'The "{key}" in "{_CONFIGS_NAME}.{name}" in your "{get_settings_module_name()}" cannot be empty.'
                    raise DandyError(message)

            config[key] = config[key] if config.get(key) else settings_configs['DEFAULT'][key]

        if config.get('CONTEXT_SIZE') is None:
            config['CONTEXT_SIZE'] = (settings_configs['DEFAULT'] or {}).get('CONTEXT_SIZE')

        self._settings_values = {key.lower(): val for key, val in config.items()}

        self.http_request_intel = HttpRequestIntel(
            method='POST',
            url=Url(
                host=self.get_settings_value('host', True),
                port=self.get_settings_value('port', True),
                path_parameters=self.get_settings_value('path_parameters'),
                query_parameters=self.get_settings_value('query_parameters'),
            ),
            headers=self.get_settings_value('headers') or {},
            bearer_token=self.get_settings_value('api_key')
            or self.get_settings_value('bearer_token'),
        )

        self.model = self.get_settings_value('model', True)

        context_size_value = self.get_settings_value('context_size')

        try:
            self.context_size = int(context_size_value) if context_size_value else 0
        except (TypeError, ValueError):
            self.context_size = 0

        self.max_completion_tokens = (
            int(self.context_size * LLM_OUTPUT_TOKEN_RATIO) if self.context_size else None
        )

        self.options = LlmOptions()

        self._set_options_from_config()

        self.http_request_intel.url.path_parameters = ['v1', 'chat', 'completions']

    def generate_request_body(self) -> LlmRequestBody:
        request_body_kwargs = self.options.model_dump(exclude_none=True)

        if self.max_completion_tokens is not None:
            request_body_kwargs['max_completion_tokens'] = self.max_completion_tokens

        return LlmRequestBody(model=self.model, **request_body_kwargs, stream=False)

    @staticmethod
    def get_response_content(response_intel: HttpResponseIntel) -> str:
        return response_intel.json_data['choices'][0]['message']['content']

    def get_settings_value(self, key: str, required: bool = False):
        value = self._settings_values.get(key)

        if required and value is None:
            message = f'The "{key.upper()}" was not found in your settings and is required by "{self.__class__.__name__}".'
            raise DandyError(message)

        return value

    def reset(self):
        self._set_options_from_config()

    def _set_options_from_config(self):
        options = self._settings_values.get('options', None)

        if isinstance(options, dict):
            self.options = LlmOptions(**options)
