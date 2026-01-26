from __future__ import annotations

from typing import TYPE_CHECKING, Any

from dandy.core.service.service import BaseService
from dandy.llm.decoder.intel import DecoderValuesIntel
from dandy.llm.prompt.typing import PromptOrStr

from dandy.llm.decoder.bot import DecoderBot

if TYPE_CHECKING:
    from dandy.llm.connector import LlmConnector


class DecoderService(BaseService['dandy.llm.decoder.mixin.DecoderServiceMixin']):
    def __post_init__(self):
        self._llm_connector: LlmConnector = self.obj.generate_connector()

    def prompt_to_values(
            self,
            prompt: PromptOrStr,
            keys_description: PromptOrStr,
            keys_values: dict[str, Any],
            max_return_values: int | None = None,
    ) -> DecoderValuesIntel:
        return DecoderBot(
            mapping=keys_values,
            mapping_keys_description=keys_description,
        ).process(
            prompt=prompt,
            max_return_values=max_return_values
        )

    def reset_service(self):
        pass
