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
from dandy.llm.service.recorder import recorder_add_llm_request_event, recorder_add_llm_response_event, recorder_add_llm_success_event, \
    recorder_add_llm_validation_failure_event, recorder_add_llm_retry_event
from dandy.llm.service.prompts import service_system_validation_error_prompt, service_user_prompt, \
    service_system_prompt

if TYPE_CHECKING:
    from dandy.llm.service.config import BaseLlmConfig
    from dandy.llm.service.request.request import BaseRequestBody
    from dandy.llm.service.config import LlmConfigOptions


class LlmService(BaseHttpService):
    def __init__(
            self,
            llm_config: BaseLlmConfig,
            llm_options: LlmConfigOptions,
    ):
        super().__init__(config=llm_config.http_config)

        self._llm_config = llm_config
        self._llm_options = llm_options

    def get_request_body(self) -> BaseRequestBody:
        return self._llm_config.generate_request_body(
            max_input_tokens=self._llm_options.max_input_tokens,
            max_output_tokens=self._llm_options.max_output_tokens,
            seed=self._llm_options.seed,
            temperature=self._llm_options.temperature,
        )

    def process_prompt_to_intel(
            self,
            prompt: Prompt | str,
            intel_class: Union[Type[IntelType], None] = None,
            intel_object: Union[IntelType, None] = None,
            images: Union[List[str], None] = None,
            include_fields: Union[IncEx, None] = None,
            exclude_fields: Union[IncEx, None] = None,
            system_prompt: Union[Prompt, None] = None,
    ) -> IntelType:

        if intel_class and intel_object:
            raise LlmCriticalException('Cannot specify both intel_class and intel_object.')

        if intel_class is None and intel_object is None:
            raise LlmCriticalException('Must specify either intel_class or intel_object.')

        intel_json_schema = IntelFactory.intel_to_json_inc_ex_schema(
            intel=intel_class or intel_object,
            include=include_fields,
            exclude=exclude_fields
        )

        event_id = generate_new_recorder_event_id()

        request_body = self.get_request_body()

        request_body.set_format_to_json_schema(
            intel_json_schema
        )

        request_body.add_message(
            role='system',
            content=service_system_prompt(
                system_prompt=system_prompt
            ).to_str()
        )

        request_body.add_message(
            role='user',
            content=service_user_prompt(
                prompt if isinstance(prompt, Prompt) else Prompt(prompt)
            ).to_str(),
            images=images,
        )

        return self._process_request_to_intel(
            request_body=request_body,
            intel_json_schema=intel_json_schema,
            event_id=event_id,
            intel=intel_class or intel_object
        )


    def _process_request_to_intel(
            self,
            request_body: BaseRequestBody,
            intel_json_schema: dict,
            event_id: str,
            intel: Union[BaseIntel, Type[BaseIntel]],
            retry_attempt: int = 0,
    ) -> IntelType:
        recorder_add_llm_request_event(request_body, intel_json_schema, event_id)

        message_content = self._llm_config.get_response_content(
            self.post_request(request_body.model_dump())
        )

        recorder_add_llm_response_event(message_content, event_id)

        try:
            intel_object = IntelFactory.json_to_intel_object(
                message_content,
                intel
            )

            if intel_object is not None:
                recorder_add_llm_success_event(
                    'Validated response from prompt into intel object.',
                    event_id,
                    intel=intel_object
                )

                return intel_object

            else:
                raise LlmRecoverableException('Failed to validate response from prompt into intel object.')

        # This validation error would be raised by pydantic if the IntelFactory failed to parse the JSON into an Intel object
        except ValidationError as e:
            recorder_add_llm_validation_failure_event(e, event_id)

            if retry_attempt < self._llm_config.options.prompt_retry_count:
                recorder_add_llm_retry_event(
                    'Validation of response to intel object failed retrying with validation errors prompt.',
                    event_id,
                    remaining_attempts = self._llm_config.options.prompt_retry_count - (retry_attempt + 1)
                )

                request_body.add_message(
                    role='system',
                    content=message_content
                )

                request_body.add_message(
                    role='user',
                    content=service_system_validation_error_prompt(e).to_str()
                )

                return self._process_request_to_intel(
                    request_body=request_body,
                    intel_json_schema=intel_json_schema,
                    event_id=event_id,
                    intel=intel,
                    retry_attempt=retry_attempt + 1
                )

            else:
                raise LlmRecoverableException(f'Failed to validate response from prompt into intel object after {self._llm_config.options.prompt_retry_count} attempts.')



