from dandy.conf import settings
from dandy.core.exceptions import DandyException
from dandy.llm.config.config import BaseLlmConfig
from dandy.llm.config.openai import OpenaiLlmConfig
from dandy.llm.config.ollama import OllamaLlmConfig
from dandy.core.utils import get_settings_module_name

_LLM_CONFIG_MAP = {
    'openai': OpenaiLlmConfig,
    'ollama': OllamaLlmConfig,
}

_DEFAULT_KEY_LIST = [
    'TYPE',
    'HOST',
    'PORT',
    'API_KEY',
]

class LlmConfigs:
    def __init__(self):
        if not isinstance(settings.LLM_CONFIGS, dict) or not settings.LLM_CONFIGS:
            message = f'Your "LLM_CONFIGS" in your "{get_settings_module_name()}" module is configured incorrectly.'
            raise DandyException(message)

        if 'DEFAULT' not in settings.LLM_CONFIGS:
            message = f'You need a "DEFAULT" in your "LLM_CONFIGS" in your "{get_settings_module_name()}" module.'
            raise DandyException(message)

        for llm_config_name, kwargs in settings.LLM_CONFIGS.items():
            if (not isinstance(llm_config_name, str) and
                    not isinstance(kwargs, dict)):
                message = 'the "LLM_CONFIGS" in the settings are configured incorrectly.'
                raise DandyException(message)

            for key in _DEFAULT_KEY_LIST:
                if key in kwargs:
                    if kwargs[key] is None or kwargs[key] == '':
                        message = f'The "{key}" in "LLM_CONFIGS.{llm_config_name}" in your "{get_settings_module_name()}" cannot be empty.'
                        raise DandyException(message)

                kwargs[key] = kwargs[key] if kwargs.get(key) else settings.LLM_CONFIGS['DEFAULT'][key]

            if 'TYPE' not in kwargs:
                message = f'All "LLM_CONFIGS" must have a "TYPE", choices are: {_LLM_CONFIG_MAP.keys()}.'
                raise DandyException(message)

            if kwargs['TYPE'] not in _LLM_CONFIG_MAP:
                message = f'TYPE "{kwargs["TYPE"]}" in "{llm_config_name}" is not a valid, choices are: {_LLM_CONFIG_MAP.keys()}.'
                raise DandyException(message)


            setattr(
                self,
                f'_{llm_config_name}',
                _LLM_CONFIG_MAP[kwargs['TYPE']](
                    **{
                        key.lower(): value
                        for key, value in kwargs.items()
                        if key != 'TYPE'
                    }
                )
            )

        if not hasattr(self, 'DEFAULT'):
            message = f'You need a "DEFAULT" in your "LLM_CONFIGS" in your "{get_settings_module_name()}" module.'
            raise DandyException(message)

        self.choices = list(settings.LLM_CONFIGS.keys())

    def __getattr__(self, item: str) -> BaseLlmConfig:
        llm_config = f'_{item}'
        if llm_config in self.__dict__ and isinstance(getattr(self, llm_config), BaseLlmConfig):
                return getattr(self, llm_config)

        message = f'No llm config named "{item}" found in your settings, choices are {self.choices}.'
        raise DandyException(message)

    def __getitem__(self, item: str) -> BaseLlmConfig:
        return getattr(self, item)


llm_configs = LlmConfigs()
