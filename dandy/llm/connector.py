from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import ValidationError
from pydantic.main import IncEx

from dandy.core.connector.connector import BaseConnector
from dandy.http.connector import HttpConnector
from dandy.intel.factory import IntelFactory
from dandy.intel.typing import IntelType
from dandy.llm.exceptions import LlmRecoverableException, LlmCriticalException
from dandy.llm.intelligence.prompts import service_system_validation_error_prompt, service_system_prompt
from dandy.llm.prompt.prompt import Prompt
from dandy.llm.prompt.typing import PromptOrStr
from dandy.llm.recorder import recorder_add_llm_request_event, recorder_add_llm_response_event, \
    recorder_add_llm_success_event, recorder_add_llm_failure_event, recorder_add_llm_retry_event
from dandy.llm.request.message import MessageHistory
from dandy.llm.request.request import LlmRequestBody

if TYPE_CHECKING:
    from dandy.llm.mixin import LlmServiceMixin


class LlmConnector(BaseConnector):
    def __init__(
            self,
            event_id: str,
            llm_service_mixin: LlmServiceMixin,
    ):
        self.intel = None
        self.llm_service_mixin = llm_service_mixin
        self._event_id = event_id
        self.prompt_retry_attempt = 0
        self.prompt_retry_count = self.llm_service_mixin.llm_options.prompt_retry_count

        self.http_request_intel = self.llm_service_mixin.get_llm_config().http_request_intel

        self.request_body: LlmRequestBody = llm_service_mixin.get_llm_config().generate_request_body()

        self.response_str = None


    @property
    def has_retry_attempts_available(self) -> bool:
        return self.prompt_retry_attempt < self.prompt_retry_count

    def _prepend_system_message(self):
        self.request_body.messages.create_message(
            role='system',
            text=service_system_prompt(
                role=self.llm_service_mixin.llm_role,
                task=self.llm_service_mixin.llm_task,
                guidelines=self.llm_service_mixin.llm_guidelines,
                system_override_prompt=self.llm_service_mixin.llm_system_override_prompt,
            ).to_str(),
            prepend=True,
        )

    def prompt_to_intel(
            self,
            prompt: PromptOrStr,
            intel_class: type[IntelType] | None = None,
            intel_object: IntelType | None = None,
            image_urls: list[str] | None = None,
            image_file_paths: list[str | Path] | None = None,
            image_base64_strings: list[str] | None = None,
            include_fields: IncEx | None = None,
            exclude_fields: IncEx | None = None,
            message_history: MessageHistory | None = None,
            replace_message_history: bool = False,
    ) -> IntelType:
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

        if image_urls or image_file_paths or image_base64_strings:
            self.request_body.messages.create_message(
                role='user',
                image_urls=image_urls,
                image_file_paths=image_file_paths,
                image_base64_strings=image_base64_strings,
            )

        return self._request_to_intel()

    def _reset_prompt_retry_attempt(self):
        self.prompt_retry_attempt = 0

    def reset(self):
        self.request_body.reset_messages()
        self._prepend_system_message()

    def _request_to_intel(
            self,
    ) -> IntelType:
        recorder_add_llm_request_event(
            self.request_body, self._event_id
        )

        http_connector = HttpConnector()

        self.http_request_intel.json_data = self.request_body.model_dump()

        self.response_str = http_connector.request_to_response(
            request_intel=self.http_request_intel
        ).json_data['choices'][0]['message']['content']

        recorder_add_llm_response_event(
            message_content=self.response_str, event_id=self._event_id
        )

        try:
            intel_object = IntelFactory.json_str_to_intel_object(
                json_str=self.response_str, intel=self.intel
            )

            if intel_object is not None:
                recorder_add_llm_success_event(
                    description='Validated response from prompt into intel object.',
                    event_id=self._event_id,
                    intel=intel_object,
                )

                self.request_body.messages.create_message(
                    role='assistant',
                    text=self.response_str
                )

                return intel_object

            message = 'Failed to validate response from prompt into intel object.'
            raise LlmRecoverableException(message)

        except ValidationError as error:
            recorder_add_llm_failure_event(error, self._event_id)

            return self.retry_request_to_intel(
                retry_event_description='Validation of response to intel object failed, retrying with validation errors prompt.',
                retry_user_prompt=service_system_validation_error_prompt(error),
            )

    def retry_request_to_intel(
            self,
            retry_event_description: str,
            retry_user_prompt: PromptOrStr,
    ) -> IntelType:
        if self.has_retry_attempts_available:
            self.prompt_retry_attempt += 1

            recorder_add_llm_retry_event(
                retry_event_description,
                self._event_id,
                remaining_attempts=self.prompt_retry_count - self.prompt_retry_attempt,
            )

            self.request_body.messages.create_message(
                role='user',
                text=Prompt(retry_user_prompt).to_str()
            )

            return self._request_to_intel()

        message = f'Failed to get the correct response from the LlmService after {self.prompt_retry_count} attempts.'
        raise LlmRecoverableException(message)

    def _set_intel(
            self,
            intel_class: type[IntelType] | None = None,
            intel_object: IntelType | None = None,
    ):
        if intel_class and intel_object:
            message = 'Cannot specify both intel_class and intel_object.'
            raise LlmCriticalException(message)

        if intel_class is None and intel_object is None:
            if self.llm_service_mixin.llm_intel_class:
                intel_class = self.llm_service_mixin.llm_intel_class
            else:
                message = 'Must specify either intel_class, intel_object or llm_intel_class on the processor.'
                raise LlmCriticalException(message)

        self.intel = intel_class or intel_object
