from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

from pydantic import ValidationError

from dandy.core.service.service import BaseService
from dandy.core.utils import encode_file_to_base64
from dandy.http.connector import HttpConnector
from dandy.intel.factory import IntelFactory
from dandy.llm.conf import llm_configs
from dandy.llm.exceptions import LlmCriticalException, LlmRecoverableException
from dandy.llm.prompt.prompt import Prompt
from dandy.llm.intelligence.prompts import (
    service_system_validation_error_prompt,
    service_user_prompt,
    service_system_prompt,
)
from dandy.llm.recorder import (
    recorder_add_llm_request_event,
    recorder_add_llm_response_event,
    recorder_add_llm_success_event,
    recorder_add_llm_failure_event,
    recorder_add_llm_retry_event,
)
from dandy.recorder.utils import generate_new_recorder_event_id

if TYPE_CHECKING:
    from pathlib import Path
    from dandy.llm.prompt.typing import PromptOrStrOrNone
    from pydantic.main import IncEx
    from dandy.llm.prompt.typing import PromptOrStr
    from dandy.intel.typing import IntelType
    from dandy.llm.mixin import LlmServiceMixin
    from dandy.llm.request.message import MessageHistory, RoleLiteralStr, RequestMessage


class LlmService(BaseService['LlmServiceMixin']):
    obj: LlmServiceMixin

    def __post_init__(self):
        self._event_id = generate_new_recorder_event_id()

        if isinstance(self.obj.llm_config, str):
            self._llm_config = llm_configs[self.obj.llm_config]
        else:
            self._llm_config = self.obj.llm_config

        self._llm_options = self.obj.llm_config_options

        self._intel = None
        self._intel_json_schema = None

        self._request_body = self._llm_config.generate_request_body(
            max_input_tokens=self._llm_options.max_input_tokens,
            max_output_tokens=self._llm_options.max_output_tokens,
            seed=self._llm_options.seed,
            temperature=self._llm_options.temperature,
        )

        self._response_str = None
        self._retry_max_attempts = 0
        self._retry_attempt = 0

    @property
    def has_retry_attempts_available(self) -> bool:
        return self._retry_attempt < self._llm_config.options.prompt_retry_count

    @property
    def messages(self) -> list[RequestMessage]:
        return self._request_body.messages

    def add_message(
        self, role: RoleLiteralStr, content: str, images: list[str] | None = None
    ):
        self._request_body.add_message(role, content, images)

    def add_messages(
        self, messages: Sequence[tuple[RoleLiteralStr, str, list[str] | None]]
    ):
        for role, content, images in messages:
            self.add_message(role, content, images)

    def _prepend_system_message(self):
        self._request_body.add_message(
            role='system',
            content=service_system_prompt(
                role=self.obj.llm_role,
                task=self.obj.llm_task,
                guidelines=self.obj.llm_guidelines,
                system_override_prompt=self.obj.llm_system_override_prompt,
            ).to_str(),
            prepend=True,
        )

    def prompt_to_intel(
        self,
        prompt: PromptOrStrOrNone = None,
        intel_class: type[IntelType] | None = None,
        intel_object: IntelType | None = None,
        images: list[str] | None = None,
        image_files: list[str | Path] | None = None,
        include_fields: IncEx | None = None,
        exclude_fields: IncEx | None = None,
        message_history: MessageHistory | None = None,
    ) -> IntelType:
        if intel_class and intel_object:
            message = 'Cannot specify both intel_class and intel_object.'
            raise LlmCriticalException(message)

        if intel_class is None and intel_object is None:
            if self.obj_class.llm_intel_class:
                intel_class = self.obj_class.llm_intel_class
            else:
                message = 'Must specify either intel_class, intel_object or llm_intel_class on the processor.'
                raise LlmCriticalException(message)

        if image_files:
            images = [] if images is None else images

            for image_file in image_files:
                images.append(encode_file_to_base64(image_file))

        self._intel = intel_class or intel_object

        self._intel_json_schema = IntelFactory.intel_to_json_inc_ex_schema(
            intel=self._intel, include=include_fields, exclude=exclude_fields
        )

        if not self._request_body.has_system_message:
            self._prepend_system_message()

        self._request_body.set_format_to_json_schema(self._intel_json_schema)

        if message_history:
            for message in message_history.messages:
                self._request_body.add_message(
                    role=message.role, content=message.content, images=message.images
                )

        if prompt is not None:
            self._request_body.add_message(
                role='user',
                content=service_user_prompt(
                    prompt if isinstance(prompt, Prompt) else Prompt(prompt)
                ).to_str(),
                images=images,
            )

        if len(self._request_body.messages) <= 1:
            message = f'"{self.__class__.__name__}.llm.process_to_intel" method requires you to have a prompt or more than the system message.'
            raise LlmCriticalException(message)

        return self._request_to_intel()

    def _request_to_intel(
        self,
    ) -> IntelType:
        recorder_add_llm_request_event(
            self._request_body, self._intel_json_schema, self._event_id
        )

        http_connector = HttpConnector()

        http_request_intel = self._llm_config.http_request_intel
        http_request_intel.json_data = self._request_body.model_dump()

        self._response_str = self._llm_config.get_response_content(
            http_connector.request_to_response(request_intel=http_request_intel)
        )

        recorder_add_llm_response_event(
            message_content=self._response_str, event_id=self._event_id
        )

        try:
            intel_object = IntelFactory.json_str_to_intel_object(
                json_str=self._response_str, intel=self._intel
            )

            if intel_object is not None:
                recorder_add_llm_success_event(
                    description='Validated response from prompt into intel object.',
                    event_id=self._event_id,
                    intel=intel_object,
                )

                self._request_body.add_message(role='assistant', content=self._response_str)

                return intel_object

            message = 'Failed to validate response from prompt into intel object.'
            raise LlmRecoverableException(message)

        except ValidationError as error:
            recorder_add_llm_failure_event(error, self._event_id)

            return self.retry_request_to_intel(
                retry_event_description='Validation of response to intel object failed, retrying with validation errors prompt.',
                retry_user_prompt=service_system_validation_error_prompt(error),
            )

    def reset_service(self):
        self.reset_messages()
        self._prepend_system_message()

    def reset_messages(self):
        self._request_body.reset_messages()

    def retry_request_to_intel(
        self,
        retry_event_description: str,
        retry_user_prompt: PromptOrStr,
    ) -> IntelType:
        if self.has_retry_attempts_available:
            self._retry_attempt += 1

            recorder_add_llm_retry_event(
                retry_event_description,
                self._event_id,
                remaining_attempts=self._llm_config.options.prompt_retry_count
                - self._retry_attempt,
            )

            self._request_body.add_message(
                role='user', content=Prompt(retry_user_prompt).to_str()
            )

            return self._request_to_intel()

        message = f'Failed to get the correct response from the LlmService after {self._llm_config.options.prompt_retry_count} attempts.'
        raise LlmRecoverableException(message)
