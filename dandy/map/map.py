from abc import ABC
from dataclasses import dataclass, Field, field
from enum import Enum
from typing import Dict, Any

from dandy.core.future import AsyncFuture
from dandy.core.processor.processor import BaseProcessor
from dandy.llm.conf import llm_configs
from dandy.llm.mixin import LlmProcessorMixin
from dandy.map.prompts import map_no_key_error_prompt, map_max_key_count_error_prompt
from dandy.llm.prompt import Prompt
from dandy.llm.prompt.typing import PromptOrStr
from dandy.llm.service.recorder import recorder_add_llm_failure_event
from dandy.map.exceptions import MapCriticalException, MapRecoverableException, MapNoKeysRecoverableException, \
    MapToManyKeysRecoverableException
from dandy.map.intel import MapKeysIntel, MapKeyIntel, MapValuesIntel
from dandy.map.service import MapService


@dataclass(kw_only=True)
class Map(
    BaseProcessor,
    LlmProcessorMixin,
):
    # These are set to None to fix an init issue with class variables
    mapping_keys_description: str | None = None
    mapping: Dict[str, Any] | None = None
    # End

    _keyed_mapping: Dict[str, tuple[str, Any]] = field(default_factory=dict)
    _map_enum: Enum | None = None

    services: MapService = MapService()

    def __post_init__(self):
        if self.mapping_keys_description is None:
            self.mapping_keys_description = self.__class__.mapping_keys_description

        if self.mapping is None:
            self.mapping = self.__class__.mapping

        for key in self.mapping.keys():
            if not isinstance(key, str):
                raise MapCriticalException(f'Mapping keys must be strings, found {key} ({type(key)}).')

        self._process_mapping_to_keyed()

        if self._map_enum is None:
            self._map_enum = self.as_enum()

    def __init_subclass__(cls):
        super().__init_subclass__()

        if cls.mapping_keys_description is None:
            raise MapCriticalException(f'{cls.__name__} `mapping_keys_description` is not set.')

        if cls.mapping is None:
            raise MapCriticalException(f'{cls.__name__} `mapping` is not set.')


    def __getitem__(self, item):
        return self.mapping[item]

    def as_enum(self) -> Enum:
        enum_choices = {}
        for key, value in self._keyed_mapping.items():
            enum_choices[value[0]] = key

        return Enum(f'{self.__class__.__name__}Enum', enum_choices)

    @property
    def keyed_mapping_choices(self) -> list[str]:
        return [f'{key}. {value[0]}\n' for key, value in self._keyed_mapping.items()]

    @property
    def keyed_mapping_choices_dict(self) -> Dict[str, str]:
        return {key: value[0] for key, value in self._keyed_mapping.items()}

    @property
    def keyed_mapping_choices_str(self) -> str:
        return ''.join(self.keyed_mapping_choices)

    def _get_selected_value(self, choice_key: str) -> Any:
        return self._keyed_mapping[choice_key][1]

    def _process_mapping_to_keyed(self):
        for i, (choice, value) in enumerate(self.mapping.items(), start=1):
            key = str(i)
            if isinstance(value, dict):
                self._keyed_mapping[key] = (choice, self._process_mapping_to_keyed())
            else:
                self._keyed_mapping[key] = (choice, value)

    def process(
            self,
            prompt: PromptOrStr,
            max_return_values: int | None = None,
    ) -> MapValuesIntel:
        return self.process_map_to_intel(
            prompt,
            max_return_values
        )

    def process_map_to_intel(
            self,
            # map: Mapping,
            prompt: PromptOrStr,
            max_return_values: int | None = None
    ) -> MapValuesIntel:
        map_values_intel = MapValuesIntel()

        for map_enum in self.process_prompt_to_intel(prompt, max_return_values):
            map_value = self._get_selected_value(map_enum.value)

            if isinstance(map_value, Map):
                map_values_intel.extend(
                    map_value.process(
                        prompt,
                        max_return_values
                    ).values
                )
            else:
                map_values_intel.append(map_value)

        return map_values_intel

    def process_prompt_to_intel(
            self,
            prompt: PromptOrStr,
            max_return_values: int | None = None,
    ) -> MapKeysIntel:

        if max_return_values is not None and max_return_values > 1:
            key_str = 'keys'
            intel_class = MapKeysIntel[list[self._map_enum]]
        else:
            key_str = 'key'
            intel_class = MapKeyIntel[self._map_enum]

        system_prompt = Prompt()
        system_prompt.prompt(self.llm_instructions_prompt)
        system_prompt.text(f'You\'re an "{self.mapping_keys_description}" assistant')

        system_prompt.line_break()

        system_prompt.text(
            f'Read through all of the "{self.mapping_keys_description}" and return the numbered {key_str} that match information relevant to the user\'s input.')

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
        system_prompt.heading(f'"{self.mapping_keys_description}"')
        system_prompt.line_break()

        system_prompt.dict(self.keyed_mapping_choices_dict)

        # llm_service = llm_configs[self.llm_config].generate_service(
        #     llm_options=self.config_options
        # )

        return_keys_intel = self._process_return_keys_intel(
            self.llm.prompt_to_intel(
                prompt=prompt if isinstance(prompt, Prompt) else Prompt(prompt),
                intel_class=intel_class,
                postfix_system_prompt=system_prompt
            )
        )

        while self.llm.has_retry_attempts_available:
            try:
                self._validate_return_keys_intel(return_keys_intel, max_return_values)
                break

            except MapNoKeysRecoverableException as error:
                recorder_add_llm_failure_event(error, self.llm.event_id)

                if self.llm.has_retry_attempts_available:
                    return_keys_intel = self.llm.retry_request_to_intel(
                        retry_event_description=f'Map keys intel object came back empty, retrying with no key(s) prompt.',
                        retry_user_prompt=map_no_key_error_prompt()
                    )
                else:
                    raise error

            except MapToManyKeysRecoverableException as error:
                recorder_add_llm_failure_event(error, self.llm.event_id)

                if self.llm.has_retry_attempts_available:
                    return_keys_intel = self.llm.retry_request_to_intel(
                        retry_event_description=f'Map keys intel object came back with to many keys, retrying with to many key(s) prompt.',
                        retry_user_prompt=map_max_key_count_error_prompt(
                            returned_count=len(return_keys_intel),
                            max_count=max_return_values if max_return_values is not None else 0,
                        )
                    )

                else:
                    raise error

        try:
            self._validate_return_keys_intel(return_keys_intel, max_return_values)

        except MapRecoverableException as error:
            recorder_add_llm_failure_event(error, self.llm.event_id)
            raise error

        return return_keys_intel

    def _process_return_keys_intel(
            self,
            return_keys_intel: MapKeysIntel | MapKeyIntel
    ) -> MapKeysIntel:
        if isinstance(return_keys_intel, MapKeyIntel):
            return_keys_intel = MapKeysIntel[list[self._map_enum]](
                keys=[return_keys_intel.key.value]
            )

        return return_keys_intel

    def _validate_return_keys_intel(
            self,
            return_keys_intel: MapKeysIntel | MapKeyIntel,
            max_return_values: int | None = None,
    ) -> None:
        if len(return_keys_intel) == 0:
            raise MapNoKeysRecoverableException(f'No {self.mapping_keys_description} found.')

        if max_return_values is not None and len(return_keys_intel) > max_return_values:
            raise MapToManyKeysRecoverableException(f'Too many {self.mapping_keys_description} found.')

    def process_to_future(self, *args, **kwargs) -> AsyncFuture[MapValuesIntel]:
        return AsyncFuture[MapValuesIntel](self.process, *args, **kwargs)
