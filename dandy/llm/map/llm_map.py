from abc import ABC
from typing import Any, Type

from typing_extensions import Union, List

from dandy.core.future import AsyncFuture
from dandy.llm.conf import llm_configs
from dandy.llm.processor.llm_processor import BaseLlmProcessor
from dandy.llm.prompt import Prompt
from dandy.llm.service.config.options import LlmConfigOptions
from dandy.map.exceptions import MapCriticalException
from dandy.map.intel import MapSelectedValuesIntel
from dandy.map.map import MapType, Map


class BaseLlmMap(BaseLlmProcessor[MapSelectedValuesIntel], ABC):
    config: str = 'DEFAULT'
    config_options: LlmConfigOptions = LlmConfigOptions()
    instructions_prompt: Prompt = (
        Prompt()
        .text("Your job is to select a choice for the provided list of choices.")
        .text("Make sure you select at least one choice that is the most relevant to the users input.")
    )
    intel_class = MapSelectedValuesIntel
    map: MapType
    _map: Map

    def __init_subclass__(cls):
        super().__init_subclass__()

        if cls.map is None:
            raise MapCriticalException(f'{cls.__name__} map is not set.')

        cls._map = Map(valid_map=cls.map)

    @classmethod
    def process(
            cls,
            prompt: Union[Prompt, str],
            choice_count: int = 1,
    ) -> MapSelectedValuesIntel[Any]:
        map_selected_values_intel = MapSelectedValuesIntel()

        for map_enum in cls.process_prompt_to_intel(prompt, choice_count):
            map_value = cls._map.get_selected_value(map_enum.value)

            if isinstance(map_value, type):
                if issubclass(map_value, BaseLlmMap):
                    map_selected_values_intel.extend(
                        map_value.process(prompt, choice_count).items
                    )
                else:
                    map_selected_values_intel.append(map_value)
            else:
                map_selected_values_intel.append(map_value)

        return map_selected_values_intel

    @classmethod
    def process_prompt_to_intel(
            cls,
            prompt: Union[Prompt, str],
            choice_count: int = 1,
    ) -> MapSelectedValuesIntel:

        system_prompt = (
            Prompt()
            .prompt(cls.instructions_prompt)
            .text(f'Please select {choice_count} of the following choices by number using the following rules.')
            .line_break()
            .sub_heading('Rules:')
            .list([
                'Select the choice that best matches the users input.',
                'Return at least one choice by number.'
            ])
            .line_break()
            .sub_heading('Choices:')
            .text(cls._map.keyed_choices_str())
        )

        print(MapSelectedValuesIntel[cls._map.as_enum()].model_json_schema())

        return llm_configs[cls.config].generate_service(
            llm_options=cls.config_options
        ).process_prompt_to_intel(
            prompt=prompt if isinstance(prompt, Prompt) else Prompt(prompt),
            intel_class=MapSelectedValuesIntel[cls._map.as_enum()],
            system_prompt=system_prompt
        )

    @classmethod
    def process_to_future(cls, *args, **kwargs) -> AsyncFuture[MapSelectedValuesIntel]:
        return AsyncFuture[MapSelectedValuesIntel](cls.process, *args, **kwargs)


class LlmMap(BaseLlmMap):
    map = {}

    @classmethod
    def process(
            cls,
            prompt: Union[Prompt, str],
            choice_count: int = 1,
            map: MapType | None = None,
    ) -> MapSelectedValuesIntel[Any]: