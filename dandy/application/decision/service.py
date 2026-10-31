from typing import Any

from dandy.infrastructure.future.future import AsyncFuture
from dandy.infrastructure.future.process import process_to_future
from dandy.shared.service.service import BaseService
from dandy.application.decision.decision import Decision
from dandy.domain.decision.intel import DecisionValuesIntel
from dandy.domain.prompt.prompt import Prompt


class DecisionService(BaseService['dandy.application.decision.mixin.DecisionServiceMixin']):
    def __post_init__(self):
        self.decision = Decision(
            recorder_event_id=self.obj.recorder_event_id, llm_service_mixin=self.obj.obj
        )

    def prompt_to_value(
        self, prompt: Prompt | str, keys_description: Prompt | str, keys_values: dict[str, Any]
    ) -> Any:
        return self.prompt_to_values(prompt, keys_description, keys_values, max_return_values=1)[0]

    @property
    def options(self):
        return self.decision.llm_config.options

    def prompt_to_value_future(self, **kwargs) -> AsyncFuture:
        return process_to_future(self.prompt_to_value, **kwargs)

    def prompt_to_values(
        self,
        prompt: Prompt | str,
        keys_description: Prompt | str,
        keys_values: dict[str, Any],
        max_return_values: int | None = None,
    ) -> DecisionValuesIntel:
        return self.decision.process(
            prompt=prompt,
            keys_description=keys_description,
            keys_values=keys_values,
            max_return_values=max_return_values,
        )

    def prompt_to_values_future(self, **kwargs) -> AsyncFuture:
        return process_to_future(self.prompt_to_values, **kwargs)

    def reset(self):
        pass
