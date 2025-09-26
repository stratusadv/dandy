from dataclasses import dataclass
from typing import ClassVar

from dandy import BaseIntel
from dandy.core.service.mixin import BaseServiceMixin
from dandy.intel.intel import DefaultIntel
from dandy.llm.conf import llm_configs
from dandy.llm.config.config import LlmConfigOptions
from dandy.llm.config.ollama import OllamaLlmConfig
from dandy.llm.config.openai import OpenaiLlmConfig
from dandy.llm.prompt.typing import PromptOrStr, PromptOrStrOrNone
from dandy.llm.service.service import LlmService


@dataclass(kw_only=True)
class LlmServiceMixin(BaseServiceMixin):
    llm_config: str | OllamaLlmConfig | OpenaiLlmConfig = 'DEFAULT'
    llm_config_options: LlmConfigOptions = llm_configs['DEFAULT'].options
    llm_intel_class: type[BaseIntel] = DefaultIntel
    llm_role: PromptOrStr = 'You are a helpful assistant.'
    llm_task: PromptOrStrOrNone = None
    llm_guidelines: PromptOrStrOrNone = None
    llm_system_override_prompt: PromptOrStrOrNone = None

    llm: ClassVar[LlmService] = LlmService()

    _LlmService_instance: LlmService | None = None

    _required_attrs: ClassVar[tuple[str, ...]] = (
        'llm_config',
        'llm_config_options',
        'llm_role',
    )