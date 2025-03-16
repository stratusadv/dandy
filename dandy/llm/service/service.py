from __future__ import annotations

import json
from time import sleep
from typing import List

import httpx
from httpx import Response
from pydantic import ValidationError
from pydantic.main import IncEx
from typing_extensions import Type, Union, TYPE_CHECKING

from dandy.conf import settings
from dandy.core.http.service import BaseHttpService
from dandy.debug.debug import DebugRecorder
from dandy.debug.utils import generate_new_debug_event_id
from dandy.intel.type_vars import IntelType
from dandy.llm.exceptions import LlmCriticalException, LlmValidationCriticalException
from dandy.llm.service.debug import debug_record_llm_request, debug_record_llm_response, debug_record_llm_success, \
    debug_record_llm_validation_failure, debug_record_llm_retry
from dandy.llm.service.prompts import service_system_validation_error_prompt, service_user_prompt, \
    service_system_prompt

if TYPE_CHECKING:
    from dandy.llm.prompt import Prompt
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

    def assistant_str_prompt_to_str(
            self,
            user_prompt_str: str,
    ) -> str:
        return self.process_str_to_str(
            system_prompt_str='You are a helpful assistant.',
            user_prompt_str=user_prompt_str,
            llm_success_message='Assistant properly returned a response.'
        )

    def get_request_body(self) -> BaseRequestBody:
        return self._llm_config.generate_request_body(
            max_input_tokens=self._llm_options.max_input_tokens,
            max_output_tokens=self._llm_options.max_output_tokens,
            seed=self._llm_options.seed,
            temperature=self._llm_options.temperature,
        )

    def process_prompt_to_intel(
            self,
            prompt: Prompt,
            intel_class: Union[Type[IntelType], None] = None,
            intel_object: Union[IntelType, None] = None,
            images: Union[List[str], None] = None,
            include_fields: Union[IncEx, None] = None,
            exclude_fields: Union[IncEx, None] = None,
            system_prompt: Union[Prompt, None] = None,
    ) -> IntelType:

        if intel_class and intel_object:
            raise LlmCriticalException('Cannot specify both intel_class and intel_object.')

        def intel_inc_ex_json_schema(intel_: Union[Type[IntelType], IntelType]) -> dict:
            return intel_.model_inc_ex_class_copy(
                include=include_fields, 
                exclude=exclude_fields
            ).model_json_schema()
        
        if intel_class:
            intel_json_schema = intel_inc_ex_json_schema(intel_class)

        elif intel_object:
            intel_json_schema = intel_inc_ex_json_schema(intel_object)
          
        else:
            raise LlmCriticalException('Must specify either intel_class or intel_object.')

        event_id = generate_new_debug_event_id()

        for attempt in range(self._llm_config.options.prompt_retry_count + 1):

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
                content=service_user_prompt(prompt).to_str(),
                images=images,
            )

            debug_record_llm_request(request_body, event_id)

            message_content = self._llm_config.get_response_content(
                self.post_request(request_body.model_dump())
            )

            debug_record_llm_response(message_content, event_id)

            try:
                intel_ = None

                if intel_class:
                    intel_ = intel_class.model_validate_json(message_content)
                elif intel_object:
                    intel_ = intel_object.model_validate_json_and_copy(message_content)

                if intel_ is not None:
                    debug_record_llm_success(
                        'Validated response from prompt into intel object.',
                        event_id,
                        intel=intel_
                    )

                    return intel_

                else:
                    raise ValueError('Failed to validate response from prompt into intel object.')

            except ValidationError as e:
                debug_record_llm_validation_failure(e, event_id)
                debug_record_llm_retry(
                    'Validation of response to intel object failed retrying with validation errors prompt.',
                    event_id
                )

                try:
                    request_body.add_message(
                        role='system',
                        content=message_content
                    )
                    request_body.add_message(
                        role='user',
                        content=service_system_validation_error_prompt(e).to_str()
                    )

                    if DebugRecorder.is_recording:
                        debug_record_llm_request(request_body, event_id)

                    message_content = self._llm_config.get_response_content(
                        self.post_request(request_body.model_dump())
                    )

                    if DebugRecorder.is_recording:
                        debug_record_llm_response(message_content, event_id)

                    intel_ = None

                    if intel_class:
                        intel_ = intel_class.model_validate_json(message_content)
                    elif intel_object:
                        intel_ = intel_object.model_validate_json_and_copy(message_content)

                    if intel_ is not None:
                        debug_record_llm_success(
                            'Validated response from validation errors prompt into intel object.',
                            event_id,
                            intel=intel_
                        )

                        return intel_

                    else:
                        raise ValueError('Failed to validate response from prompt into intel object.')

                except ValidationError as e:
                    debug_record_llm_validation_failure(e, event_id)

                if self._llm_config.options.prompt_retry_count - 1:
                    debug_record_llm_retry(
                        'Response after validation errors prompt failed.\nRetrying with original prompt.',
                        event_id,
                        remaining_attempts=self._llm_config.options.prompt_retry_count - attempt
                    )
        else:
            raise LlmValidationCriticalException

    def process_str_to_str(self, system_prompt_str: str, user_prompt_str: str, llm_success_message: str) -> str:
        event_id = generate_new_debug_event_id()

        request_body: BaseRequestBody = self.get_request_body()

        request_body.set_format_to_text()

        request_body.add_message(
            role='system',
            content=system_prompt_str
        )

        request_body.add_message(
            role='user',
            content=user_prompt_str
        )

        debug_record_llm_request(request_body, event_id)

        message_content = self._llm_config.get_response_content(
            self.post_request(request_body.model_dump())
        )

        debug_record_llm_response(message_content, event_id)
        debug_record_llm_success(llm_success_message, event_id)

        return message_content

    def process_prompts_to_str(self, system_prompt: Prompt, user_prompt: Prompt) -> str:
        return self.process_str_to_str(
            system_prompt_str=system_prompt.to_str(),
            user_prompt_str=user_prompt.to_str(),
            llm_success_message='Prompt properly returned a response.'
        )