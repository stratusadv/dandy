from __future__ import annotations

from enum import Enum
from typing import Any, TYPE_CHECKING

from dandy.core.future.future import AsyncFuture
from dandy.llm.connector import LlmConnector
from dandy.llm.decoder.exceptions import (
    DecoderCriticalError,
    DecoderRecoverableError,
    DecoderNoKeysRecoverableError,
    DecoderToManyKeysRecoverableError,
)
from dandy.llm.decoder.intel import (
    DecoderKeysIntel,
    DecoderKeyIntel,
    DecoderValuesIntel,
)
from dandy.llm.decoder.intelligence.prompts import (
    decoder_no_key_error_prompt,
    decoder_max_key_count_error_prompt,
)
from dandy.llm.decoder.recorder import (
    recorder_add_process_decoder_value_event,
    recorder_add_chosen_values_event,
)
from dandy.llm.intelligence.prompts import service_system_prompt
from dandy.llm.prompt.prompt import Prompt
from dandy.llm.recorder import recorder_add_llm_failure_event

if TYPE_CHECKING:
    from dandy.llm.mixin import LlmServiceMixin


class Decoder:
    def __init__(
            self,
            event_id: str,
            llm_service_mixin: LlmServiceMixin,
    ):
        self._event_id = event_id
        self._llm_service_mixin = llm_service_mixin
        self.llm_config = self._llm_service_mixin.get_llm_config()
        self._llm_connector = None

        self.keys_description = None
        self.keys_values = None

    def __getitem__(self, item: str) -> Any:
        return self.keys_values[item]

    @property
    def _keyed_mapping_choices_dict(self) -> dict[str, str]:
        return {key: value[0] for key, value in self._keyed_mapping.items()}

    @property
    def _keyed_mapping(self) -> dict[str, tuple[str, ...]]:
        keyed_mapping = {}

        for i, (choice, value) in enumerate(self.keys_values.items(), start=1):
            key = str(i)
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

    def process(
            self,
            prompt: Prompt | str,
            keys_description: str,
            keys_values: dict[str, Any],
            max_return_values: int | None = None,
    ) -> DecoderValuesIntel:
        for key in keys_values:
            if not isinstance(key, str):
                message = f'all keys in `keys_values` must be strings to be decoded, found {key} ({type(key)}).'
                raise DecoderCriticalError(message)

        self.keys_description = keys_description
        self.keys_values = keys_values

        decoder_values_intel = DecoderValuesIntel()
        chosen_mappings = {}

        recorder_add_process_decoder_value_event(
            decoder=self,
            event_id=self._event_id,
        )

        for decoder_enum in self._process_decoder_prompt_to_intel(
                prompt, max_return_values
        ):
            decoder_value = self._get_selected_value(decoder_enum.value)

            decoder_values_intel.append(decoder_value)
            chosen_mappings[decoder_value] = str(
                self._get_selected_key(decoder_enum.value)
            )

        if chosen_mappings:
            recorder_add_chosen_values_event(
                chosen_values_keys=chosen_mappings,
                event_id=self._event_id,
            )

        return decoder_values_intel

    def _process_decoder_prompt_to_intel(
            self,
            prompt: Prompt | str,
            max_return_values: int | None = None,
    ) -> DecoderKeysIntel:
        if max_return_values is None or max_return_values > 1:
            intel_class = DecoderKeysIntel[self.as_enum()]
        else:
            intel_class = DecoderKeyIntel[self.as_enum()]

        self._llm_connector = LlmConnector(
            event_id=self._event_id,
            system_prompt=self._generate_service_system_prompt(max_return_values=max_return_values),
            llm_config=self.llm_config,
            intel_class=intel_class,
        )

        return_keys_intel = self._process_return_keys_intel(
            self._llm_connector.prompt_to_intel(
                prompt=prompt if isinstance(prompt, Prompt) else Prompt(prompt),
                intel_class=intel_class,
            )
        )

        while self._llm_connector.has_retry_attempts_available:
            try:
                self._validate_return_keys_intel(return_keys_intel, max_return_values)
                break

            except DecoderNoKeysRecoverableError as error:
                recorder_add_llm_failure_event(error, self._event_id)

                if self._llm_connector.has_retry_attempts_available:
                    return_keys_intel = self._llm_connector.retry_request_to_intel(
                        retry_event_description='Decoder keys intel object came back empty, retrying with no key(s) prompt.',
                        retry_user_prompt=decoder_no_key_error_prompt(),

                    )
                else:
                    raise

            except DecoderToManyKeysRecoverableError as error:
                recorder_add_llm_failure_event(error, self._event_id)

                if self._llm_connector.has_retry_attempts_available:
                    return_keys_intel = self._llm_connector.retry_request_to_intel(
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

        except DecoderRecoverableError as error:
            recorder_add_llm_failure_event(error, self._event_id)
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

    def _generate_service_system_prompt(self, max_return_values: int | None) -> Prompt:
        key_str = 'key' if max_return_values == 1 else 'keys'

        guidelines_prompt = Prompt()

        guidelines = [
            f'Read through all of the "{self.keys_description}" dict values and return the numbered {key_str} that matches the values with information relevant to the user\'s request.',
        ]

        if max_return_values is not None and max_return_values > 0:
            if max_return_values == 1:
                guidelines.append(
                    f'You must return exactly one numbered {key_str}.'
                )
            else:
                guidelines.append(
                    f'Return up to a maximum of {max_return_values} numbered {key_str}.'
                )
        else:
            guidelines.append(
                f"Return as many numbered {key_str} as you find that are relevant to the user's response."
            )

        guidelines.append(
            'Always return at least one numbered key closest to the user\'s request.'
        )

        guidelines_prompt.list(guidelines)

        guidelines_prompt.line_break()
        guidelines_prompt.heading(f'{self.keys_description} Dict')
        guidelines_prompt.line_break()

        guidelines_prompt.dict(self._keyed_mapping_choices_dict)

        return service_system_prompt(
            role=f'{self.keys_description} Relationship Identifier',
            task=f'Identify the "{self.keys_description}" that best matches the user provided information or request.',
            guidelines=guidelines_prompt,
        )

    def _validate_return_keys_intel(
            self,
            return_keys_intel: DecoderKeysIntel | DecoderKeyIntel,
            max_return_values: int | None = None,
    ) -> None:
        if len(return_keys_intel) == 0:
            message = f'No {self.keys_description} found.'
            raise DecoderNoKeysRecoverableError(message)

        if max_return_values is not None and len(return_keys_intel) > max_return_values:
            message = f'Too many {self.keys_description} found.'
            raise DecoderToManyKeysRecoverableError(message)

