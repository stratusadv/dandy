from abc import ABC
from typing import Any

from typing_extensions import Union, List

from dandy.core.future import AsyncFuture
from dandy.llm.conf import llm_configs
from dandy.llm.processor.llm_processor import BaseLlmProcessor
from dandy.llm.prompt import Prompt
from dandy.llm.service.config.options import LlmConfigOptions
from dandy.map.intel import MapSelectedValuesIntel
from dandy.map.map import MapType, BaseMap


class BaseLlmMap(BaseLlmProcessor[MapSelectedValuesIntel], BaseMap, ABC):
    config: str = 'DEFAULT'
    config_options: LlmConfigOptions = LlmConfigOptions()
    instructions_prompt: Prompt = Prompt("You're a helpful assistant please follow the users instructions.")
    map: MapType

    def __new__(cls):
        print('hello')
        return super().__new__(cls)

    @classmethod
    def process(
            cls,
            prompt: Union[Prompt, str],
            choice_count: int = 1,
            map: MapType | None = None
    ) -> MapSelectedValuesIntel[Any]:
        map_selected_values_intel = MapSelectedValuesIntel()

        for value in cls.process_prompt_to_intel(prompt, choice_count, map):
            if value is BaseLlmMap:
                map_selected_values_intel.extend(
                    *value.process(prompt, choice_count, map)
                )
            else:
                map_selected_values_intel.append(cls.get_selected_value(value.value))

        return map_selected_values_intel

    @classmethod
    def process_prompt_to_intel(
            cls,
            prompt: Union[Prompt, str],
            choice_count: int = 1,
            map: MapType | None = None
    ) -> MapSelectedValuesIntel:

        system_prompt = (
            Prompt()
            .prompt(cls.instructions_prompt)
            .text(f'Please select {choice_count} of the following choices that best matches the intention of the user:')
            .list(cls.keyed_choices())
        )

        print(MapSelectedValuesIntel[cls.as_enum()].model_json_schema())

        if map:
            pass # We need to do something for a custom map ... maybe get rid of the BaseMap class

        return llm_configs[cls.config].generate_service(
            llm_options=cls.config_options
        ).process_prompt_to_intel(
            prompt=prompt if isinstance(prompt, Prompt) else Prompt(prompt),
            intel_class=MapSelectedValuesIntel[cls.as_enum()],
            system_prompt=system_prompt
        )

    @classmethod
    def process_to_future(cls, *args, **kwargs) -> AsyncFuture[MapSelectedValuesIntel]:
        return AsyncFuture[MapSelectedValuesIntel](cls.process, *args, **kwargs)
