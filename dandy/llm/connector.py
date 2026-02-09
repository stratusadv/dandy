from pathlib import Path

from pydantic import ValidationError
from pydantic.main import IncEx

from dandy.core.connector.connector import BaseConnector
from dandy.http.connector import HttpConnector
from dandy.intel.factory import IntelFactory
from dandy.intel.typing import IntelType
from dandy.llm.config import LlmConfig
from dandy.llm.exceptions import LlmCriticalError, LlmRecoverableError
from dandy.llm.intelligence.prompts import service_system_validation_error_prompt
from dandy.llm.prompt.prompt import Prompt
from dandy.llm.recorder import (
    recorder_add_llm_failure_event,
    recorder_add_llm_request_event,
    recorder_add_llm_response_event,
    recorder_add_llm_retry_event,
    recorder_add_llm_success_event,
)
from dandy.llm.request.message import MessageHistory


class LlmConnector(BaseConnector):
    def __init__(
            self,
            recorder_event_id: str,
            llm_config: LlmConfig,
            intel_class: type[IntelType] | None,
            system_prompt: Prompt | str,
    ):
        self.recorder_event_id = recorder_event_id

        self.llm_config = llm_config

        self.intel = None
        self.intel_class = intel_class

        self.prompt_retry_attempt = 0

        self.request_body = self.llm_config.generate_request_body()
        self.response_str = None

        self.system_prompt_str = str(system_prompt)

    @property
    def has_retry_attempts_available(self) -> bool:
        return self.prompt_retry_attempt < self.llm_config.options.prompt_retry_count

    def _prepend_system_message(self):
        self.request_body.messages.create_message(
            role='system',
            text=self.system_prompt_str,
            prepend=True,
        )

    def prompt_to_intel(
            self,
            prompt: Prompt | str | None = None,
            intel_class: type[IntelType] | None = None,
            intel_object: IntelType | None = None,
            audio_urls: list[str] | None = None,
            audio_file_paths: list[str | Path] | None = None,
            audio_base64_strings: list[str] | None = None,
            image_urls: list[str] | None = None,
            image_file_paths: list[str | Path] | None = None,
            image_base64_strings: list[str] | None = None,
            include_fields: IncEx | None = None,
            exclude_fields: IncEx | None = None,
            message_history: MessageHistory | None = None,
            replace_message_history: bool = False,
    ) -> IntelType:
        self._update_request_body()

        self._set_intel(intel_class=intel_class, intel_object=intel_object)

        self.request_body.json_schema = IntelFactory.intel_to_json_inc_ex_schema(
            intel=self.intel,
            include=include_fields,
            exclude=exclude_fields
        )

        if not self.request_body.messages.has_system_message:
            self._prepend_system_message()

        if message_history:
            if replace_message_history:
                self.request_body.messages = message_history
            else:
                self.request_body.messages.extend(
                    message_history.messages
                )

        if prompt is not None:
            self.request_body.messages.create_message(
                role='user',
                text=Prompt(prompt).to_str(),
            )

        if audio_urls or audio_file_paths or audio_base64_strings:
            self.request_body.messages.create_message(
                role='user',
                audio_urls=audio_urls,
                audio_file_paths=audio_file_paths,
                audio_base64_strings=audio_base64_strings
            )

        if image_urls or image_file_paths or image_base64_strings:
            self.request_body.messages.create_message(
                role='user',
                image_urls=image_urls,
                image_file_paths=image_file_paths,
                image_base64_strings=image_base64_strings,
            )

        if len(self.request_body.messages) <= 1:
            message = 'You cannot prompt the LlmService without at least one system and one user message.'
            raise LlmCriticalError(message)

        return self._request_to_intel()

    def _reset_prompt_retry_attempt(self):
        self.prompt_retry_attempt = 0

    def reset(self):
        self.llm_config.reset()
        self.request_body = self.llm_config.generate_request_body()

    def _request_to_intel(
            self,
    ) -> IntelType:
        recorder_add_llm_request_event(
            self.request_body, self.recorder_event_id
        )

        http_connector = HttpConnector()

        self.llm_config.http_request_intel.json_data = self.request_body.model_dump()

        self.response_str = http_connector.request_to_response(
            request_intel=self.llm_config.http_request_intel
        ).json_data['choices'][0]['message']['content']

        recorder_add_llm_response_event(
            message_content=self.response_str, event_id=self.recorder_event_id
        )

        try:
            intel_object = IntelFactory.json_str_to_intel_object(
                json_str=self.response_str, intel=self.intel
            )

            if intel_object is not None:
                recorder_add_llm_success_event(
                    description='Validated response from prompt into intel object.',
                    event_id=self.recorder_event_id,
                    intel=intel_object,
                )

                self.request_body.messages.create_message(
                    role='assistant',
                    text=self.response_str
                )

                return intel_object

            message = 'Failed to validate response from prompt into intel object.'
            raise LlmRecoverableError(message)

        except ValidationError as error:
            recorder_add_llm_failure_event(error, self.recorder_event_id)

            return self.retry_request_to_intel(
                retry_event_description='Validation of response to intel object failed, retrying with validation errors prompt.',
                retry_user_prompt=service_system_validation_error_prompt(error),
            )

    def retry_request_to_intel(
            self,
            retry_event_description: str,
            retry_user_prompt: Prompt | str,
    ) -> IntelType:
        if self.has_retry_attempts_available:
            self.prompt_retry_attempt += 1

            recorder_add_llm_retry_event(
                retry_event_description,
                self.recorder_event_id,
                remaining_attempts=self.llm_config.options.prompt_retry_count - self.prompt_retry_attempt,
            )

            self.request_body.messages.create_message(
                role='user',
                text=Prompt(retry_user_prompt).to_str()
            )

            return self._request_to_intel()

        message = f'Failed to get the correct response from the LlmService after {self.llm_config.options.prompt_retry_count} attempts.'
        raise LlmRecoverableError(message)

    def _set_intel(
            self,
            intel_class: type[IntelType] | None = None,
            intel_object: IntelType | None = None,
    ):
        if intel_class and intel_object:
            message = 'Cannot specify both intel_class and intel_object.'
            raise LlmCriticalError(message)

        if intel_class is None and intel_object is None:
            if self.intel_class:
                intel_class = self.intel_class
            else:
                message = 'Must specify either intel_class, intel_object or llm_intel_class on the processor.'
                raise LlmCriticalError(message)

        self.intel = intel_class or intel_object

    def _update_request_body(self):
        for key, value in self.llm_config.options.model_dump(exclude_none=True).items():
            setattr(self.request_body, key, value)
