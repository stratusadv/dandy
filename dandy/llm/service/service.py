from __future__ import annotations

from typing import List

from pydantic import ValidationError
from pydantic.main import IncEx
from typing_extensions import Type, Union, TYPE_CHECKING

from dandy.core.http.service import BaseHttpService
from dandy.recorder.recorder import Recorder
from dandy.recorder.utils import generate_new_recorder_event_id
from dandy.intel import BaseIntel
from dandy.intel.factory import IntelFactory
from dandy.intel.type_vars import IntelType
from dandy.llm.exceptions import LlmCriticalException, LlmValidationCriticalException, LlmRecoverableException
from dandy.llm.prompt import Prompt
from dandy.llm.service.recorder import recorder_add_llm_request_event, recorder_add_llm_response_event, \
    recorder_add_llm_success_event, \
    recorder_add_llm_failure_event, recorder_add_llm_retry_event
from dandy.llm.service.prompts import service_system_validation_error_prompt, service_user_prompt, \
    service_system_prompt

if TYPE_CHECKING:
    from dandy.llm.service.config import BaseLlmConfig
    from dandy.llm.service.request.request import BaseRequestBody
    from dandy.llm.service.config import LlmConfigOptions
    from dandy.llm.service.request.message import MessageHistory


class LlmService(BaseHttpService):
    def __init__(
            self,
            llm_config: BaseLlmConfig,
            llm_options: LlmConfigOptions,
    ):
        super().__init__(config=llm_config.http_config)

        self.event_id = generate_new_recorder_event_id()

        self._llm_config = llm_config
        self._llm_options = llm_options
        self._intel = None
        self._intel_json_schema = None
        self._request_body = self._llm_config.generate_request_body(
            max_input_tokens=self._llm_options.max_input_tokens,
            max_output_tokens=self._llm_options.max_output_tokens,
            seed=self._llm_options.seed,
            temperature=self._llm_options.temperature,
        )
        self._response_content = None
        self._retry_attempt = 0

    @property
    def has_retry_attempts_available(self) -> bool:
        return self._retry_attempt < self._llm_config.options.prompt_retry_count

    def process_prompt_to_intel(
            self,
            prompt: Prompt | str,
            intel_class: Union[Type[IntelType], None] = None,
            intel_object: Union[IntelType, None] = None,
            images: Union[List[str], None] = None,
            include_fields: Union[IncEx, None] = None,
            exclude_fields: Union[IncEx, None] = None,
            system_prompt: Union[Prompt, None] = None,
            message_history: Union[MessageHistory, None] = None,
    ) -> IntelType:

        if intel_class and intel_object:
            raise LlmCriticalException('Cannot specify both intel_class and intel_object.')

        if intel_class is None and intel_object is None:
            raise LlmCriticalException('Must specify either intel_class or intel_object.')

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
            content=service_system_prompt(
                system_prompt=system_prompt
            ).to_str()
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

        return self._process_request_to_intel()

    def _process_request_to_intel(
            self,
    ) -> IntelType:
        recorder_add_llm_request_event(self._request_body, self._intel_json_schema, self.event_id)

        self._response_content = self._llm_config.get_response_content(
            self.post_request(
                self._request_body.model_dump()
            )
        )

        recorder_add_llm_response_event(self._response_content, self.event_id)

        try:
            intel_object = IntelFactory.json_to_intel_object(
                self._response_content,
                self._intel
            )

            if intel_object is not None:
                recorder_add_llm_success_event(
                    'Validated response from prompt into intel object.',
                    self.event_id,
                    intel=intel_object
                )

                return intel_object

            else:
                raise LlmRecoverableException('Failed to validate response from prompt into intel object.')

        except ValidationError as error:
            recorder_add_llm_failure_event(error, self.event_id)

            return self.retry_process_request_to_intel(
                retry_event_description='Validation of response to intel object failed, retrying with validation errors prompt.',
                retry_user_prompt=service_system_validation_error_prompt(error)
            )

    def retry_process_request_to_intel(
            self,
            retry_event_description: str,
            retry_user_prompt: Prompt | str,
    ) -> IntelType:
        if self.has_retry_attempts_available:
            self._retry_attempt += 1

            recorder_add_llm_retry_event(
                retry_event_description,
                self.event_id,
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

            return self._process_request_to_intel(
            )

        else:
            raise LlmRecoverableException(
                f'Failed to get the correct response from the LlmService after {self._llm_config.options.prompt_retry_count} attempts.')
