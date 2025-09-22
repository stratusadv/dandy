from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, ClassVar

from dandy.core.future import AsyncFuture
from dandy.llm.mixin import LlmServiceMixin
from dandy.llm.prompt.prompt import Prompt
from dandy.llm.prompt.typing import PromptOrStr
from dandy.llm.service.recorder import recorder_add_llm_failure_event
from dandy.processor.map.exceptions import MapCriticalException, MapRecoverableException, MapNoKeysRecoverableException, \
    MapToManyKeysRecoverableException
from dandy.processor.map.intel import MapKeysIntel, MapKeyIntel, MapValuesIntel
from dandy.processor.map.intelligence.prompts import map_no_key_error_prompt, map_max_key_count_error_prompt
from dandy.processor.map.recorder import recorder_add_process_map_value_event, recorder_add_chosen_mappings_event
from dandy.processor.map.service import MapService
from dandy.processor.processor import BaseProcessor


@dataclass(kw_only=True)
class Map(
    BaseProcessor,
    LlmServiceMixin,
):
    mapping_keys_description: str = None
    mapping: Dict[str, Any] = None

    services: ClassVar[MapService] = MapService()
    _MapService_instance: MapService | None = None

    @property
    def _keyed_mapping_choices_dict(self) -> Dict[str, str]:
        return {key: value[0] for key, value in self._keyed_mapping.items()}

    @property
    def _keyed_mapping(self) -> Dict[str, tuple[str, ...]]:
        keyed_mapping = {}
        for i, (choice, value) in enumerate(self.mapping.items(), start=1):
            key = str(i)
            if isinstance(value, dict):
                keyed_mapping[key] = (
                    choice,
                    self.__class__(
                        mapping_keys_description=self.mapping_keys_description,
                        mapping=value
                    )
                )
            else:
                keyed_mapping[key] = (
                    choice,
                    value
                )
        return keyed_mapping

    def __init_subclass__(cls):
        super().__init_subclass__()

        if cls.mapping_keys_description is None:
            message = f'{cls.__name__} `mapping_keys_description` is not set.'
            raise MapCriticalException(message)

        if cls.mapping is None:
            message = f'{cls.__name__} `mapping` is not set.'
            raise MapCriticalException(message)

    def __post_init__(self):
        if self.mapping_keys_description is None:
            self.mapping_keys_description = self.__class__.mapping_keys_description

        if self.mapping is None:
            self.mapping = self.__class__.mapping

        for key in self.mapping.keys():
            if not isinstance(key, str):
                message = f'Mapping keys must be strings, found {key} ({type(key)}).'
                raise MapCriticalException(message)

    def __getitem__(self, item):
        return self.mapping[item]

    def as_enum(self) -> Enum:
        return Enum(
            f'{self.__class__.__name__}Enum',
            {
                value[0]: key
                for key, value in self._keyed_mapping.items()
            }
        )

    def _get_selected_key(self, choice_key: str) -> Any:
        return self._keyed_mapping[choice_key][0]

    def _get_selected_value(self, choice_key: str) -> Any:
        return self._keyed_mapping[choice_key][1]

    def process(
            self,
            prompt: PromptOrStr,
            max_return_values: int | None = None,
    ) -> MapValuesIntel:
        return self._process_map_to_intel(
            prompt,
            max_return_values
        )

    def _process_map_to_intel(
            self,
            prompt: PromptOrStr,
            max_return_values: int | None = None,
            mapping_name: str | None = None,
    ) -> MapValuesIntel:
        map_values_intel = MapValuesIntel()
        chosen_mappings = {}

        recorder_add_process_map_value_event(
            map=self,
            mapping_name=mapping_name,
            event_id=self._recorder_event_id,
        )

        for map_enum in self._process_map_prompt_to_intel(prompt, max_return_values):
            map_value = self._get_selected_value(map_enum.value)

            if isinstance(map_value, Map):
                map_values_intel.extend(
                    map_value._process_map_to_intel(
                        prompt,
                        max_return_values,
                        mapping_name=map_enum.name,
                    ).values
                )
            else:
                map_values_intel.append(map_value)
                chosen_mappings[map_value] = (
                    str(self._get_selected_key(map_enum.value))
                )

        if chosen_mappings:
            recorder_add_chosen_mappings_event(
                map=self,
                chosen_mappings=chosen_mappings,
                event_id=self._recorder_event_id,
            )

        return map_values_intel

    def _process_map_prompt_to_intel(
            self,
            prompt: PromptOrStr,
            max_return_values: int | None = None,
    ) -> MapKeysIntel:

        if max_return_values is not None and max_return_values > 1:
            key_str = 'keys'
            intel_class = MapKeysIntel[self.as_enum()]
        else:
            key_str = 'key'
            intel_class = MapKeyIntel[self.as_enum()]

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
                f'Return the numbered {key_str} you find that are relevant to the user\'s response and return at least one.')

        system_prompt.line_break()
        system_prompt.heading(f'"{self.mapping_keys_description}"')
        system_prompt.line_break()

        system_prompt.dict(self._keyed_mapping_choices_dict)

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
                recorder_add_llm_failure_event(error, self.llm._event_id)

                if self.llm.has_retry_attempts_available:
                    return_keys_intel = self.llm.retry_request_to_intel(
                        retry_event_description=f'Map keys intel object came back empty, retrying with no key(s) prompt.',
                        retry_user_prompt=map_no_key_error_prompt()
                    )
                else:
                    raise error

            except MapToManyKeysRecoverableException as error:
                recorder_add_llm_failure_event(error, self.llm._event_id)

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
            recorder_add_llm_failure_event(error, self.llm._event_id)
            raise error

        return return_keys_intel

    def _process_return_keys_intel(
            self,
            return_keys_intel: MapKeysIntel | MapKeyIntel
    ) -> MapKeysIntel:
        if isinstance(return_keys_intel, MapKeyIntel):
            return_keys_intel = MapKeysIntel[self.as_enum()](
                keys=[return_keys_intel.key.value]
            )

        return return_keys_intel

    def _validate_return_keys_intel(
            self,
            return_keys_intel: MapKeysIntel | MapKeyIntel,
            max_return_values: int | None = None,
    ) -> None:
        if len(return_keys_intel) == 0:
            message = f'No {self.mapping_keys_description} found.'
            raise MapNoKeysRecoverableException(message)

        if max_return_values is not None and len(return_keys_intel) > max_return_values:
            message = f'Too many {self.mapping_keys_description} found.'
            raise MapToManyKeysRecoverableException(message)

    def process_to_future(self, *args, **kwargs) -> AsyncFuture[MapValuesIntel]:
        return AsyncFuture[MapValuesIntel](self.process, *args, **kwargs)
