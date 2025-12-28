from typing import ClassVar

from dandy.core.service.mixin import BaseServiceMixin
from dandy.intel.intel import BaseIntel, DefaultIntel
from dandy.llm.conf import LlmConfigs
from dandy.llm.config.config import LlmConfig, LlmConfigOptions
from dandy.llm.prompt.typing import PromptOrStr, PromptOrStrOrNone
from dandy.llm.service import LlmService


class LlmServiceMixin(BaseServiceMixin):
    llm_config: str | LlmConfig = 'DEFAULT'
    llm_config_options: str | LlmConfigOptions = 'DEFAULT'
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
        super().__init__(**kwargs)

        llm_config: str | None = kwargs.get('llm_config')

        if llm_config is not None:
            self.llm_config = llm_config

        if isinstance(self.llm_config, str):
            self.llm_config = LlmConfigs()[self.llm_config]

        if isinstance(self.llm_config_options, str):
            self.llm_config_options = self.llm_config.options

        self.llm_intel_class = self.__class__.llm_intel_class

        self.llm.set_obj_service_instance(
            self,
            None,
        )


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
