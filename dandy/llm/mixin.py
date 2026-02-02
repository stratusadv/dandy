from typing import ClassVar

from dandy.llm.prompt.prompt import Prompt

from dandy.core.service.mixin import BaseServiceMixin
from dandy.intel.intel import BaseIntel, DefaultIntel
from dandy.llm.config import LlmConfig, LlmOptions
from dandy.llm.service import LlmService


class LlmServiceMixin(BaseServiceMixin):
    llm_config: str | LlmConfig = 'DEFAULT'
    llm_intel_class: type[BaseIntel] = DefaultIntel
    llm_role: Prompt | str = 'Assistant'
    llm_task: Prompt | str | None = 'Provide a response based on the users request, context or instructions.'
    llm_guidelines: Prompt | str | None = None
    llm_system_override_prompt: Prompt | str | None = None

    _required_attrs: ClassVar[tuple[str, ...]] = (
        'llm_config',
        'llm_role',
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        llm_config: str | None = kwargs.get('llm_config', None)

        if llm_config is not None:
            self.llm_config = llm_config

    def get_llm_config(self) -> LlmConfig:
        if isinstance(self.llm_config, str):
            return LlmConfig(self.llm_config)

        else:
            return self.llm_config

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

    def reset(self):
        super().reset()
        self.llm.reset()
