from typing import ClassVar

from dandy.core.service.mixin import BaseServiceMixin
from dandy.intel.intel import BaseIntel, DefaultIntel
from dandy.llm.config import LlmConfig
from dandy.llm.prompt.prompt import Prompt
from dandy.llm.service import LlmService


class LlmServiceMixin(BaseServiceMixin):
    llm_config: str = 'DEFAULT'
    intel_class: type[BaseIntel] = DefaultIntel
    role: Prompt | str = 'Assistant'
    task: Prompt | str | None = (
        'Provide a response based on the users request, context or instructions.'
    )
    guidelines: Prompt | str | None = None
    system_override_prompt: Prompt | str | None = None

    _required_attrs: ClassVar[tuple[str, ...]] = (
        'llm_config',
        'role',
        'task',
    )

    def __init__(
        self,
        llm_config: str | None = None,
        llm_temperature: float | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        if isinstance(llm_config, str):
            self.llm_config = llm_config

        if isinstance(llm_temperature, float):
            self.llm.options.temperature = llm_temperature

    def get_llm_config(self) -> LlmConfig:
        return LlmConfig(self.llm_config)

    @property
    def llm(self) -> LlmService:
        return self._get_service_instance(LlmService)

    def reset(self):
        super().reset()
        self.llm.reset()
