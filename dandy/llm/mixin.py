from typing import ClassVar

from dandy.intel.intel import BaseIntel
from dandy.core.service.mixin import BaseServiceMixin
from dandy.intel.intel import DefaultIntel
from dandy.llm.conf import llm_configs
from dandy.llm.config.config import LlmConfigOptions
from dandy.llm.config.ollama import OllamaLlmConfig
from dandy.llm.config.openai import OpenaiLlmConfig
from dandy.llm.prompt.typing import PromptOrStr, PromptOrStrOrNone
from dandy.llm.service import LlmService


class LlmServiceMixin(BaseServiceMixin):
    llm_config: str | OllamaLlmConfig | OpenaiLlmConfig = 'DEFAULT'
    llm_config_options: LlmConfigOptions = llm_configs['DEFAULT'].options
    llm_intel_class: type[BaseIntel] = DefaultIntel
    llm_role: PromptOrStr = 'Assistant'
    llm_task: PromptOrStrOrNone = 'Provide a response based users request, context or instructions.'
    llm_guidelines: PromptOrStrOrNone = None
    llm_system_override_prompt: PromptOrStrOrNone = None

    llm: ClassVar[LlmService] = LlmService()

    _LlmService_instance: LlmService | None = None

    _required_attrs: ClassVar[tuple[str, ...]] = (
        'llm_config',
        'llm_config_options',
        'llm_role',
    )

    def __init__(self, **kwargs):
        self.llm_intel_class = self.__class__.llm_intel_class
        self.llm.set_obj_service_instance(
            self,
            None,
        )
        super().__init__(**kwargs)

    @classmethod
    def get_llm_description(cls) -> str | None:
        if cls.llm_role:
            if cls.llm_task:
                return f'{cls.llm_role}: {cls.llm_task}'

            return f'{cls.llm_role}'

        return None

    def reset_services(self):
        super().reset_services()
        self.llm.reset_service()
