from typing import ClassVar

from dandy.core.service.mixin import BaseServiceMixin
from dandy.intel.intel import BaseIntel, DefaultIntel
from dandy.llm.config.config import LlmConfig, LlmOptions
from dandy.llm.prompt.typing import PromptOrStr, PromptOrStrOrNone
from dandy.llm.service import LlmService


class LlmServiceMixin(BaseServiceMixin):
    llm_config: str | LlmConfig = 'DEFAULT'
    llm_options: str | LlmOptions = 'DEFAULT'
    llm_intel_class: type[BaseIntel] = DefaultIntel
    llm_role: PromptOrStr = 'Assistant'
    llm_task: PromptOrStrOrNone = 'Provide a response based users request, context or instructions.'
    llm_guidelines: PromptOrStrOrNone = None
    llm_system_override_prompt: PromptOrStrOrNone = None

    _required_attrs: ClassVar[tuple[str, ...]] = (
        'llm_config',
        'llm_options',
        'llm_role',
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        llm_config: str | None = kwargs.get('llm_config')

        if llm_config is not None:
            self.llm_config = llm_config

        # self.llm_intel_class = self.__class__.llm_intel_class

        # self.llm.set_obj_service_instance(
        #     self,
        #     None,
        # )

    def get_llm_config(self) -> LlmConfig:
        if isinstance(self.llm_config, str):
            return LlmConfig(self.llm_config)

        else:
            return self.llm_config

    def get_llm_options(self) -> LlmOptions:
        if isinstance(self.llm_options, str):
            return self.get_llm_config().options

        else:
            return self.llm_options

    @classmethod
    def get_llm_description(cls) -> str | None:
        if cls.llm_role:
            if cls.llm_task:
                return f'{cls.llm_role}: {cls.llm_task}'

            return f'{cls.llm_role}'

        return None

    @property
    def llm(self) -> LlmService:
        return self._get_service_instance(LlmService)

    def reset_services(self):
        super().reset_services()
        self.llm.reset_service()
