from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Union, List

from pydantic import ValidationError
from pydantic.main import IncEx

from dandy.core.service.service import BaseService
from dandy.core.utils import encode_file_to_base64
from dandy.http.connector import HttpConnector
from dandy.intel.factory import IntelFactory
from dandy.intel.typing import IntelType
from dandy.llm.conf import llm_configs
from dandy.llm.exceptions import LlmCriticalException, LlmRecoverableException
from dandy.llm.prompt import Prompt
from dandy.llm.prompt.typing import PromptOrStr
from dandy.llm.prompt.typing import PromptOrStrOrNone
from dandy.llm.service.prompts import service_system_validation_error_prompt, service_user_prompt, \
    service_system_prompt
from dandy.llm.service.recorder import recorder_add_llm_request_event, recorder_add_llm_response_event, \
    recorder_add_llm_success_event, \
    recorder_add_llm_failure_event, recorder_add_llm_retry_event
from dandy.recorder.utils import generate_new_recorder_event_id

if TYPE_CHECKING:
    from dandy.llm.mixin import LlmProcessorMixin
    from dandy.llm.request.message import MessageHistory


class LlmService(BaseService['LlmProcessorMixin']):
    obj: LlmProcessorMixin
    Prompt: Prompt = Prompt

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
        self._response_content = None
        self._retry_max_attempts = 0
        self._retry_attempt = 0

    def _generate_system_prompt_str(
            self,
            postfix_system_prompt: PromptOrStrOrNone
    ) -> str:
        if self.obj.llm_system_override_prompt:
            system_override_prompt = self.Prompt()
            system_override_prompt.prompt(self.obj.llm_system_override_prompt)

            system_override_prompt.line_break()
            system_override_prompt.prompt(self.obj.llm_instructions_prompt)

            if postfix_system_prompt:
                system_override_prompt.line_break()
                system_override_prompt.prompt(postfix_system_prompt)

            system_prompt_str = system_override_prompt.to_str()

        else:
            system_prompt = Prompt()
            system_prompt.prompt(self.obj.llm_instructions_prompt)

            if postfix_system_prompt:
                system_prompt.line_break()
                system_prompt.prompt(postfix_system_prompt)

            system_prompt_str = service_system_prompt(
                system_prompt=system_prompt
            ).to_str()

        return system_prompt_str

    @property
    def has_retry_attempts_available(self) -> bool:
        return self._retry_attempt < self._llm_config.options.prompt_retry_count

    def prompt_to_intel(
            self,
            prompt: PromptOrStr,
            intel_class: type[IntelType] | None = None,
            intel_object: IntelType | None = None,
            images: list[str] | None = None,
            image_files: Union[List[str | Path], None] = None,
            include_fields: IncEx | None = None,
            exclude_fields: IncEx | None = None,
            postfix_system_prompt: PromptOrStrOrNone = None,
            message_history: MessageHistory | None = None,
    ) -> IntelType:

        if intel_class and intel_object:
            raise LlmCriticalException('Cannot specify both intel_class and intel_object.')

        if intel_class is None and intel_object is None:
            raise LlmCriticalException('Must specify either intel_class or intel_object.')

        if image_files:
            images = [] if images is None else images

            for image_file in image_files:
                images.append(encode_file_to_base64(image_file))

        self._intel = intel_class or intel_object

        self._intel_json_schema = IntelFactory.intel_to_json_inc_ex_schema(
            intel=self._intel,
            include=include_fields,
            exclude=exclude_fields
        )

        self._request_body.set_format_to_json_schema(
            self._intel_json_schema
        )

        self._request_body.add_message(
            role='system',
            content=self._generate_system_prompt_str(postfix_system_prompt)
        )

        if message_history:
            for message in message_history.messages:
                self._request_body.add_message(
                    role=message.role,
                    content=message.content,
                    images=message.images
                )

        self._request_body.add_message(
            role='user',
            content=service_user_prompt(
                prompt if isinstance(prompt, Prompt) else Prompt(prompt)
            ).to_str(),
            images=images,
        )

        return self._request_to_intel()

    def _request_to_intel(
            self,
    ) -> IntelType:
        recorder_add_llm_request_event(self._request_body, self._intel_json_schema, self._event_id)

        http_connector = HttpConnector(self._llm_config.http_config)

        self._response_content = self._llm_config.get_response_content(
            http_connector.post_request(
                self._request_body.model_dump()
            )
        )

        recorder_add_llm_response_event(self._response_content, self._event_id)

        try:
            intel_object = IntelFactory.json_to_intel_object(
                self._response_content,
                self._intel
            )

            if intel_object is not None:
                recorder_add_llm_success_event(
                    'Validated response from prompt into intel object.',
                    self._event_id,
                    intel=intel_object
                )

                return intel_object

            else:
                raise LlmRecoverableException('Failed to validate response from prompt into intel object.')

        except ValidationError as error:
            recorder_add_llm_failure_event(error, self._event_id)

            return self.retry_request_to_intel(
                retry_event_description='Validation of response to intel object failed, retrying with validation errors prompt.',
                retry_user_prompt=service_system_validation_error_prompt(error)
            )

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
                remaining_attempts=self._llm_config.options.prompt_retry_count - self._retry_attempt
            )

            self._request_body.add_message(
                role='assistant',
                content=self._response_content
            )

            self._request_body.add_message(
                role='user',
                content=Prompt(retry_user_prompt).to_str()
            )

            return self._request_to_intel(
            )

        else:
            raise LlmRecoverableException(
                f'Failed to get the correct response from the LlmService after {self._llm_config.options.prompt_retry_count} attempts.')
