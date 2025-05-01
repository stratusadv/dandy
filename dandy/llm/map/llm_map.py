from abc import ABC
from typing import Any

from typing_extensions import Union

from dandy.core.future import AsyncFuture
from dandy.llm.conf import llm_configs
from dandy.llm.processor.llm_processor import BaseLlmProcessor
from dandy.llm.prompt import Prompt
from dandy.llm.service.config.options import LlmConfigOptions
from dandy.map.exceptions import MapCriticalException
from dandy.map.intel import MapValuesIntel
from dandy.map.map import Map


class BaseLlmMap(BaseLlmProcessor[MapValuesIntel], ABC):
    config: str = 'DEFAULT'
    config_options: LlmConfigOptions = LlmConfigOptions()
    instructions_prompt: Prompt = (
        Prompt()
        .text('You\'re a assistant that looks through sets of key value pairs.')
    )
    intel_class = MapValuesIntel
    map_keys_description: str
    map: Map

    def __init_subclass__(cls):
        super().__init_subclass__()

        if cls.map_keys_description is None:
            raise MapCriticalException(f'{cls.__name__} `map_keys_description` is not set.')

        if cls.map is None:
            raise MapCriticalException(f'{cls.__name__} `map` is not set.')

    @classmethod
    def process(
            cls,
            prompt: Union[Prompt, str],
            max_return_values: int | None = None,
    ) -> MapValuesIntel[Any]:
        return cls.process_map_to_intel(
            cls.map,
            prompt,
            max_return_values
        )

    @classmethod
    def process_map_to_intel(
            cls,
            map: Map,
            prompt: Union[Prompt, str],
            max_return_values: int | None = None
    ) -> MapValuesIntel[Any]:
        map_values_intel = MapValuesIntel()

        for map_enum in cls.process_prompt_to_intel(map, prompt, max_return_values):
            map_value = map.get_selected_value(map_enum.value)

            if isinstance(map_value, type):
                if issubclass(map_value, BaseLlmMap):
                    map_values_intel.extend(
                        map_value.process(
                            prompt,
                            max_return_values
                        ).items
                    )
                else:
                    map_values_intel.append(map_value)

            elif isinstance(map_value, Map):
                map_values_intel.extend(
                    cls.process_map_to_intel(
                        map_value,
                        prompt,
                        max_return_values
                    ).items
                )
            else:
                map_values_intel.append(map_value)

        return map_values_intel

    @classmethod
    def process_prompt_to_intel(
            cls,
            map: Map,
            prompt: Union[Prompt, str],
            max_return_values: int | None = None,
    ) -> MapValuesIntel:

        system_prompt = (
            Prompt()
            .prompt(cls.instructions_prompt)
            .text("Make sure you select at least one choice that is the most relevant to the users input.")
        )

        if max_return_values:
            system_prompt.text(f'Please select {max_return_values} of the following choices by number using the following rules.')

        system_prompt.line_break()
        system_prompt.sub_heading('Rules:')
        system_prompt.list([
            'Select the choice that best matches the users input.',
            'Return at least one choice by number.'
        ])
        system_prompt.line_break()
        system_prompt.sub_heading(f'{cls.map_keys_description}:')
        system_prompt.dict(map.keyed_choices_dict)

        return llm_configs[cls.config].generate_service(
            llm_options=cls.config_options
        ).process_prompt_to_intel(
            prompt=prompt if isinstance(prompt, Prompt) else Prompt(prompt),
            intel_class=MapValuesIntel[cls.map.as_enum()],
            system_prompt=system_prompt
        )

    @classmethod
    def process_to_future(cls, *args, **kwargs) -> AsyncFuture[MapValuesIntel]:
        return AsyncFuture[MapValuesIntel](cls.process, *args, **kwargs)
