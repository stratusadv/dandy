from abc import ABC
from enum import Enum
from typing import Any

from typing_extensions import Union

from dandy.core.future import AsyncFuture
from dandy.llm.conf import llm_configs
from dandy.llm.map.prompts import map_no_key_error_prompt, map_max_key_count_error_prompt
from dandy.llm.processor.llm_processor import BaseLlmProcessor
from dandy.llm.prompt import Prompt
from dandy.llm.service.config.options import LlmConfigOptions
from dandy.llm.service.recorder import recorder_add_llm_failure_event
from dandy.map.exceptions import MapCriticalException, MapRecoverableException, MapNoKeysRecoverableException, \
    MapToManyKeysRecoverableException
from dandy.map.intel import MapKeysIntel, MapKeyIntel, MapValuesIntel
from dandy.map.map import Map


class BaseLlmMap(BaseLlmProcessor[MapKeysIntel], ABC):
    config: str = 'DEFAULT'
    config_options: LlmConfigOptions = LlmConfigOptions()
    instructions_prompt: Prompt = Prompt()
    intel_class = MapKeysIntel
    map_keys_description: str
    map: Map
    _map_enum: Enum | None = None

    def __init_subclass__(cls):
        super().__init_subclass__()

        if cls.map_keys_description is None:
            raise MapCriticalException(f'{cls.__name__} `map_keys_description` is not set.')

        if cls.map is None:
            raise MapCriticalException(f'{cls.__name__} `map` is not set.')

        if cls._map_enum is None:
            cls._map_enum = cls.map.as_enum()

    @classmethod
    def process(
            cls,
            prompt: Union[Prompt, str],
            max_return_values: int | None = None,
    ) -> MapValuesIntel:
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
    ) -> MapValuesIntel:
        map_values_intel = MapValuesIntel()

        for map_enum in cls.process_prompt_to_intel(map, prompt, max_return_values):
            map_value = map.get_selected_value(map_enum.value)

            if isinstance(map_value, type):
                if issubclass(map_value, BaseLlmMap):
                    map_values_intel.extend(
                        map_value.process(
                            prompt,
                            max_return_values
                        ).values
                    )
                else:
                    map_values_intel.append(map_value)

            elif isinstance(map_value, Map):
                map_values_intel.extend(
                    cls.process_map_to_intel(
                        map_value,
                        prompt,
                        max_return_values
                    ).values
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
    ) -> MapKeysIntel:

        if max_return_values is not None and max_return_values > 1:
            key_str = 'keys'
            intel_class = MapKeysIntel[list[cls._map_enum]]
        else:
            key_str = 'key'
            intel_class = MapKeyIntel[cls._map_enum]

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
                system_prompt.text(
                    f'Return up to a maximum of {max_return_values} numbered {key_str} and return at least one at a minimum.')
        else:
            system_prompt.text(
                f'Return the numbered {key_str} you find that are most relevant and return at least one.')

        system_prompt.line_break()
        system_prompt.heading(f'"{cls.map_keys_description}"')
        system_prompt.line_break()

        system_prompt.dict(map.keyed_choices_dict)

        llm_service = llm_configs[cls.config].generate_service(
            llm_options=cls.config_options
        )

        return_keys_intel = cls._process_return_keys_intel(
            llm_service.process_prompt_to_intel(
                prompt=prompt if isinstance(prompt, Prompt) else Prompt(prompt),
                intel_class=intel_class,
                system_prompt=system_prompt
            )
        )

        while llm_service.has_retry_attempts_available:
            try:
                cls._validate_return_keys_intel(return_keys_intel, max_return_values)
                break

            except MapNoKeysRecoverableException as error:
                recorder_add_llm_failure_event(error, llm_service.event_id)

                if llm_service.has_retry_attempts_available:
                    return_keys_intel = llm_service.retry_process_request_to_intel(
                        retry_event_description=f'Map keys intel object came back empty, retrying with no keys prompt.',
                        retry_user_prompt=map_no_key_error_prompt()
                    )
                else:
                    raise error

            except MapToManyKeysRecoverableException as error:
                recorder_add_llm_failure_event(error, llm_service.event_id)

                if llm_service.has_retry_attempts_available:
                    return_keys_intel = llm_service.retry_process_request_to_intel(
                        retry_event_description=f'Map keys intel object came back with to many keys, retrying with to many keys prompt.',
                        retry_user_prompt=map_max_key_count_error_prompt(
                            returned_count=len(return_keys_intel),
                            max_count=max_return_values if max_return_values is not None else 0,
                        )
                    )

                else:
                    raise error

        try:
            cls._validate_return_keys_intel(return_keys_intel, max_return_values)

        except MapRecoverableException as error:
            recorder_add_llm_failure_event(error, llm_service.event_id)
            raise error

        return return_keys_intel

    @classmethod
    def _process_return_keys_intel(
            cls,
            return_keys_intel: MapKeysIntel | MapKeyIntel
    ) -> MapKeysIntel:
        if isinstance(return_keys_intel, MapKeyIntel):
            return_keys_intel = MapKeysIntel[list[cls._map_enum]](
                keys=[return_keys_intel.key.value]
            )

        return return_keys_intel

    @classmethod
    def _validate_return_keys_intel(
            cls,
            return_keys_intel: MapKeysIntel | MapKeyIntel,
            max_return_values: int | None = None,
    ) -> None:
        if len(return_keys_intel) == 0:
            raise MapNoKeysRecoverableException(f'No {cls.map_keys_description} found.')

        if max_return_values is not None and len(return_keys_intel) > max_return_values:
            raise MapToManyKeysRecoverableException(f'Too many {cls.map_keys_description} found.')

    @classmethod
    def process_to_future(cls, *args, **kwargs) -> AsyncFuture[MapValuesIntel]:
        return AsyncFuture[MapValuesIntel](cls.process, *args, **kwargs)
