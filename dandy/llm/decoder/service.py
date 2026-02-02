from typing import Any

from dandy.core.future.future import AsyncFuture
from dandy.core.future.tools import process_to_future
from dandy.core.service.service import BaseService
from dandy.llm.decoder.decoder import Decoder
from dandy.llm.decoder.intel import DecoderValuesIntel
from dandy.llm.prompt.prompt import Prompt


class DecoderService(BaseService['dandy.llm.decoder.mixin.DecoderServiceMixin']):
    def __post_init__(self):
        self.decoder = Decoder(
            event_id=self.obj.event_id,
            llm_service_mixin=self.obj.obj,
        )

    def prompt_to_value(
            self,
            prompt: Prompt | str,
            keys_description: Prompt | str,
            keys_values: dict[str, Any],
    ) -> Any:
        return self.prompt_to_values(
            prompt,
            keys_description,
            keys_values,
            max_return_values=1
        )[0]

    @property
    def options(self):
        return self.decoder.llm_config.options

    def prompt_to_value_future(self, **kwargs) -> AsyncFuture:
        return process_to_future(self.prompt_to_value, **kwargs)

    def prompt_to_values(
            self,
            prompt: Prompt | str,
            keys_description: Prompt | str,
            keys_values: dict[str, Any],
            max_return_values: int | None = None,
    ) -> DecoderValuesIntel:
        return self.decoder.process(
            prompt=prompt,
            keys_description=keys_description,
            keys_values=keys_values,
            max_return_values=max_return_values
        )

    def prompt_to_values_future(self, **kwargs) -> AsyncFuture:
        return process_to_future(self.prompt_to_values, **kwargs)

    def reset(self):
        pass
