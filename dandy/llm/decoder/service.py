from __future__ import annotations

from typing import TYPE_CHECKING, Any

from dandy.core.service.service import BaseService
from dandy.llm.decoder.decoder import Decoder
from dandy.llm.decoder.intel import DecoderValuesIntel
from dandy.llm.prompt.typing import PromptOrStr

if TYPE_CHECKING:
    from dandy.llm.connector import LlmConnector


class DecoderService(BaseService['dandy.llm.decoder.mixin.DecoderServiceMixin']):
    def prompt_to_values(
            self,
            prompt: PromptOrStr,
            keys_description: PromptOrStr,
            keys_values: dict[str, Any],
            max_return_values: int | None = None,
    ) -> DecoderValuesIntel:
        return Decoder(
            event_id=self.obj.event_id,
            llm_service_mixin=self.obj.obj,
            keys_description=keys_description,
            keys_values=keys_values,
        ).process(
            prompt=prompt,
            max_return_values=max_return_values
        )

    def reset_service(self):
        pass
