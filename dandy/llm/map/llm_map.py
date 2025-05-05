from abc import ABC
from typing import Any

from typing_extensions import Union

from dandy.core.future import AsyncFuture
from dandy.llm.conf import llm_configs
from dandy.llm.processor.llm_processor import BaseLlmProcessor
from dandy.llm.prompt import Prompt
from dandy.llm.service.config.options import LlmConfigOptions
from dandy.map.exceptions import MapCriticalException, MapRecoverableException
from dandy.map.intel import MapValuesIntel, MapValueIntel
from dandy.map.map import Map


class BaseLlmMap(BaseLlmProcessor[MapValuesIntel], ABC):
    config: str = 'DEFAULT'
    config_options: LlmConfigOptions = LlmConfigOptions()
    instructions_prompt: Prompt = Prompt()
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

        if max_return_values is not None and max_return_values > 1:
            key_str = 'keys'
            intel_class = MapValuesIntel[cls.map.as_enum()]
        else:
            key_str = 'key'
            intel_class = MapValueIntel[cls.map.as_enum()]

        system_prompt = Prompt()
        system_prompt.prompt(cls.instructions_prompt)
        system_prompt.text(f'You\'re an "{cls.map_keys_description}" assistant')

        system_prompt.line_break()

        system_prompt.text(
            f'Read through all of the "{cls.map_keys_description}" and return the numbered {key_str} that match information relevant to the user\'s input.')

        system_prompt.line_break()

        if max_return_values is not None and max_return_values > 0:
            if max_return_values == 1:
                system_prompt.text(f'You must return exactly one numbered {key_str}.')
            else:
                system_prompt.text(f'Return up to a maximum of {max_return_values} numbered {key_str} and return at least one at a minimum.')
        else:
            system_prompt.text(f'Return the numbered {key_str} you find that are most relevant and return at least one.')

        system_prompt.line_break()
        system_prompt.heading(f'"{cls.map_keys_description}"')
        system_prompt.line_break()

        system_prompt.dict(map.keyed_choices_dict)

        return_values_intel = llm_configs[cls.config].generate_service(
            llm_options=cls.config_options
        ).process_prompt_to_intel(
            prompt=prompt if isinstance(prompt, Prompt) else Prompt(prompt),
            intel_class=intel_class,
            system_prompt=system_prompt
        )

        if isinstance(return_values_intel, MapValueIntel):
            return_values_intel = MapValuesIntel[cls.map.as_enum()](
                items=[return_values_intel.item.value]
            )

        if len(return_values_intel) == 0:
            raise MapRecoverableException(f'No {cls.map_keys_description} found.')

        if max_return_values is not None and len(return_values_intel) > max_return_values:
            raise MapRecoverableException(f'Too many {cls.map_keys_description} found.')

        return return_values_intel

    @classmethod
    def process_to_future(cls, *args, **kwargs) -> AsyncFuture[MapValuesIntel]:
        return AsyncFuture[MapValuesIntel](cls.process, *args, **kwargs)
