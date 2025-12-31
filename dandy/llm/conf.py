from dandy.conf import settings
from dandy.core.exceptions import DandyException
from dandy.core.utils import get_settings_module_name
from dandy.llm.config.config import LlmConfig

_DEFAULT_KEY_LIST = [
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

            setattr(
                self,
                f'_{llm_config_name}',
                LlmConfig(
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

    def __getattr__(self, item: str) -> LlmConfig:
        llm_config = f'_{item}'
        if llm_config in self.__dict__ and isinstance(getattr(self, llm_config), LlmConfig):
                return getattr(self, llm_config)

        message = f'No llm config named "{item}" found in your settings, choices are {self.choices}.'
        raise DandyException(message)

    def __getitem__(self, item: str) -> LlmConfig:
        return getattr(self, item)
