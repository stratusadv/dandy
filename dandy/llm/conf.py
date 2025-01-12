from dandy.conf import settings
from dandy.const import USER_SETTINGS_FILE_NAME
from dandy.core.exceptions import DandyException
from dandy.llm.config import OllamaLlmConfig, OpenaiLlmConfig, BaseLlmConfig

_LLM_CONFIG_MAP = {
    'openai': OpenaiLlmConfig,
    'ollama': OllamaLlmConfig,
}


class LlmConfigs:
    def __init__(self):
        for llm_config_name, kwargs in settings.LLM_CONFIGS.items():
            if (not isinstance(llm_config_name, str) and
                    not isinstance(kwargs, dict)):
                raise DandyException('the "LLM_CONFIGS" in the settings are configured incorrectly.')

            if 'TYPE' not in kwargs:
                raise DandyException(f'All "LLM_CONFIGS" must have a "TYPE", choices are: {_LLM_CONFIG_MAP.keys()}.')

            if kwargs['TYPE'] not in _LLM_CONFIG_MAP:
                raise DandyException(f'TYPE "{kwargs["TYPE"]}" in "{llm_config_name}" is not a valid, choices are: {_LLM_CONFIG_MAP.keys()}.')

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
            raise DandyException(f'You need a "DEFAULT" in your "LLM_CONFIGS" in your "{USER_SETTINGS_FILE_NAME}".')

        self.choices = list(settings.LLM_CONFIGS.keys())



    def __getattr__(self, item) -> BaseLlmConfig:
        if hasattr(self, f'_{item}'):
            return getattr(self, f'_{item}')

        raise DandyException(f'No attribute "{item}" found in llm configs, check your "{USER_SETTINGS_FILE_NAME}" file.')

    def __getitem__(self, item) -> BaseLlmConfig:
        return getattr(self, item)

llm_configs = LlmConfigs()