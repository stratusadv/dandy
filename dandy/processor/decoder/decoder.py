from enum import Enum
from typing import Any, ClassVar

from dandy.core.future import AsyncFuture
from dandy.core.utils import generate_forwardable_kwargs_if_not_none
from dandy.llm.mixin import LlmServiceMixin
from dandy.llm.prompt.prompt import Prompt
from dandy.llm.prompt.typing import PromptOrStr
from dandy.llm.recorder import recorder_add_llm_failure_event
from dandy.processor.decoder.exceptions import (
    DecoderCriticalException,
    DecoderRecoverableException,
    DecoderNoKeysRecoverableException,
    DecoderToManyKeysRecoverableException,
)
from dandy.processor.decoder.intel import (
    DecoderKeysIntel,
    DecoderKeyIntel,
    DecoderValuesIntel,
)
from dandy.processor.decoder.intelligence.prompts import (
    decoder_no_key_error_prompt,
    decoder_max_key_count_error_prompt,
)
from dandy.processor.decoder.mixin import DecoderServiceMixin
from dandy.processor.decoder.recorder import (
    recorder_add_process_decoder_value_event,
    recorder_add_chosen_mappings_event,
)
from dandy.processor.decoder.service import DecoderService
from dandy.processor.processor import BaseProcessor


class Decoder(
    BaseProcessor,
    DecoderServiceMixin,
    LlmServiceMixin,
):
    mapping: dict[str, Any] = None
    mapping_keys_description: str = None

    services: ClassVar[DecoderService] = DecoderService()
    _DecoderService_instance: DecoderService | None = None

    def __init__(
            self,
            llm_randomize_seed: bool | None = None,
            llm_seed: int | None = None,
            llm_temperature: float | None = None,
            mapping: dict[str, Any] | None = None,
            mapping_keys_description: str | None = None,
            **kwargs
    ):
        super().__init__(
            **generate_forwardable_kwargs_if_not_none(
                mapping=mapping,
                mapping_keys_description=mapping_keys_description,
            ),
            **kwargs
        )

        self.llm_config_options.update_values(
            randomize_seed=llm_randomize_seed,
            seed=llm_seed,
            temperature=llm_temperature,
        )

    def __init_subclass__(cls):
        super().__init_subclass__()

        if cls.mapping_keys_description is None:
            message = f'{cls.__name__} `mapping_keys_description` is not set.'
            raise DecoderCriticalException(message)

        if cls.mapping is None:
            message = f'{cls.__name__} `mapping` is not set.'
            raise DecoderCriticalException(message)

    def __post_init__(self):
        if self.mapping_keys_description is None:
            self.mapping_keys_description = self.__class__.mapping_keys_description

        if self.mapping is None:
            self.mapping = self.__class__.mapping

        for key in self.mapping:
            if not isinstance(key, str):
                message = f'Decoder keys must be strings, found {key} ({type(key)}).'
                raise DecoderCriticalException(message)

    def __getitem__(self, item: str) -> Any:
        return self.mapping[item]

    @property
    def _keyed_mapping_choices_dict(self) -> dict[str, str]:
        return {key: value[0] for key, value in self._keyed_mapping.items()}

    @property
    def _keyed_mapping(self) -> dict[str, tuple[str, ...]]:
        keyed_mapping = {}
        for i, (choice, value) in enumerate(self.mapping.items(), start=1):
            key = str(i)
            if isinstance(value, dict):
                keyed_mapping[key] = (
                    choice,
                    self.__class__(
                        mapping_keys_description=self.mapping_keys_description,
                        mapping=value,
                    ),
                )
            else:
                keyed_mapping[key] = (choice, value)
        return keyed_mapping

    def as_enum(self) -> Enum:
        return Enum(
            f'{self.__class__.__name__}Enum',
            {value[0]: key for key, value in self._keyed_mapping.items()},
        )

    def _get_selected_key(self, choice_key: str) -> Any:
        return self._keyed_mapping[choice_key][0]

    def _get_selected_value(self, choice_key: str) -> Any:
        return self._keyed_mapping[choice_key][1]

    @classmethod
    def get_description(cls) -> str | None:
        if cls.description is not None:
            return cls.description

        return cls.get_llm_description()

    def process(
        self,
        prompt: PromptOrStr,
        max_return_values: int | None = None,
    ) -> DecoderValuesIntel:
        return self._process_decoder_to_intel(prompt, max_return_values)

    def _process_decoder_to_intel(
        self,
        prompt: PromptOrStr,
        max_return_values: int | None = None,
        mapping_name: str | None = None,
    ) -> DecoderValuesIntel:
        decoder_values_intel = DecoderValuesIntel()
        chosen_mappings = {}

        recorder_add_process_decoder_value_event(
            decoder=self,
            mapping_name=mapping_name,
            event_id=self._recorder_event_id,
        )

        for decoder_enum in self._process_decoder_prompt_to_intel(
            prompt, max_return_values
        ):
            decoder_value = self._get_selected_value(decoder_enum.value)

            if isinstance(decoder_value, Decoder):
                decoder_values_intel.extend(
                    decoder_value._process_decoder_to_intel(
                        prompt,
                        max_return_values,
                        mapping_name=decoder_enum.name,
                    ).values
                )
            else:
                decoder_values_intel.append(decoder_value)
                chosen_mappings[decoder_value] = str(
                    self._get_selected_key(decoder_enum.value)
                )

        if chosen_mappings:
            recorder_add_chosen_mappings_event(
                decoder=self,
                chosen_mappings=chosen_mappings,
                event_id=self._recorder_event_id,
            )

        return decoder_values_intel

    def _process_decoder_prompt_to_intel(
        self,
        prompt: PromptOrStr,
        max_return_values: int | None = None,
    ) -> DecoderKeysIntel:
        if max_return_values is not None and max_return_values > 1:
            intel_class = DecoderKeysIntel[self.as_enum()]
        else:
            intel_class = DecoderKeyIntel[self.as_enum()]

        self._set_llm_role_task_guidelines(max_return_values=max_return_values)

        return_keys_intel = self._process_return_keys_intel(
            self.llm.prompt_to_intel(
                prompt=prompt if isinstance(prompt, Prompt) else Prompt(prompt),
                intel_class=intel_class,
            )
        )

        while self.llm.has_retry_attempts_available:
            try:
                self._validate_return_keys_intel(return_keys_intel, max_return_values)
                break

            except DecoderNoKeysRecoverableException as error:
                recorder_add_llm_failure_event(error, self.llm._event_id)

                if self.llm.has_retry_attempts_available:
                    return_keys_intel = self.llm.retry_request_to_intel(
                        retry_event_description='Decoder keys intel object came back empty, retrying with no key(s) prompt.',
                        retry_user_prompt=decoder_no_key_error_prompt(),
                    )
                else:
                    raise

            except DecoderToManyKeysRecoverableException as error:
                recorder_add_llm_failure_event(error, self.llm._event_id)

                if self.llm.has_retry_attempts_available:
                    return_keys_intel = self.llm.retry_request_to_intel(
                        retry_event_description='Decoder keys intel object came back with to many keys, retrying with to many key(s) prompt.',
                        retry_user_prompt=decoder_max_key_count_error_prompt(
                            returned_count=len(return_keys_intel),
                            max_count=max_return_values
                            if max_return_values is not None
                            else 0,
                        ),
                    )

                else:
                    raise

        try:
            self._validate_return_keys_intel(return_keys_intel, max_return_values)

        except DecoderRecoverableException as error:
            recorder_add_llm_failure_event(error, self.llm._event_id)
            raise

        return return_keys_intel

    def _process_return_keys_intel(
        self, return_keys_intel: DecoderKeysIntel | DecoderKeyIntel
    ) -> DecoderKeysIntel:
        if isinstance(return_keys_intel, DecoderKeyIntel):
            return_keys_intel = DecoderKeysIntel[self.as_enum()](
                keys=[return_keys_intel.key.value]
            )

        return return_keys_intel

    def _set_llm_role_task_guidelines(self, max_return_values: int | None):
        self.llm_role: str = f'{self.mapping_keys_description} Relationship Identifier'
        self.llm_task: str = f'Identify the "{self.mapping_keys_description}" that best matches the user provided information or request.'

        key_str = 'key' if max_return_values == 1 else 'keys'

        guidelines_prompt = Prompt()

        guidelines = [
            f'Read through all of the "{self.mapping_keys_description}" and return the numbered {key_str} (as integers) that match information relevant to the user\'s input.',
            'Include matches even if the input is misspelled or abbreviated, but only if context strongly suggests it.'
        ]

        if max_return_values is not None and max_return_values > 0:
            if max_return_values == 1:
                guidelines.append(
                    f'You must return exactly one numbered {key_str}.'
                )
            else:
                guidelines.append(
                    f'Return up to a maximum of {max_return_values} numbered {key_str} and return at least one at a minimum.'
                )
        else:
            guidelines.append(
                f"Return any numbered {key_str} you find that are relevant to the user's response and make sure to return at least one."
            )

        guidelines_prompt.list(guidelines)

        guidelines_prompt.line_break()
        guidelines_prompt.heading(f'"{self.mapping_keys_description}"')
        guidelines_prompt.line_break()

        guidelines_prompt.dict(self._keyed_mapping_choices_dict)

        self.llm_guidelines = guidelines_prompt

    def _validate_return_keys_intel(
        self,
        return_keys_intel: DecoderKeysIntel | DecoderKeyIntel,
        max_return_values: int | None = None,
    ) -> None:
        if len(return_keys_intel) == 0:
            message = f'No {self.mapping_keys_description} found.'
            raise DecoderNoKeysRecoverableException(message)

        if max_return_values is not None and len(return_keys_intel) > max_return_values:
            message = f'Too many {self.mapping_keys_description} found.'
            raise DecoderToManyKeysRecoverableException(message)

    def process_to_future(self, *args, **kwargs) -> AsyncFuture[DecoderValuesIntel]:
        return AsyncFuture[DecoderValuesIntel](self.process, *args, **kwargs)
