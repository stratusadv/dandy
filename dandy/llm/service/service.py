from __future__ import annotations

import json
from time import sleep

from httpx import Response
from pydantic.main import IncEx
from typing_extensions import Type, Union, TYPE_CHECKING, Iterable

import httpx 
from pydantic import ValidationError

from dandy.conf import settings
from dandy.intel.type_vars import IntelType
from dandy.debug.debug import DebugRecorder
from dandy.debug.utils import generate_new_debug_event_id
from dandy.llm.exceptions import LlmException, LlmValidationException
from dandy.llm.service.debug import debug_record_llm_request, debug_record_llm_response, debug_record_llm_success, \
    debug_record_llm_validation_failure, debug_record_llm_retry
from dandy.llm.service.prompts import service_system_validation_error_prompt, service_user_prompt, \
    service_system_prompt

if TYPE_CHECKING:
    from dandy.llm.prompt import Prompt
    from dandy.llm.service.config import BaseLlmConfig
    from dandy.llm.service.request.request import BaseRequestBody
    from dandy.llm.service.config import LlmConfigOptions


class LlmService:
    def __init__(
            self,
            config: BaseLlmConfig,
            options: LlmConfigOptions,
    ):

        self._config = config
        self._options = options

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
        return self._config.generate_request_body(
            max_input_tokens=self._options.max_input_tokens,
            max_output_tokens=self._options.max_output_tokens,
            seed=self._options.seed,
            temperature=self._options.temperature,
        )

    def process_prompt_to_intel(
            self,
            prompt: Prompt,
            intel_class: Union[Type[IntelType], None] = None,
            intel_object: Union[IntelType, None] = None,
            include_fields: Union[IncEx, None] = None,
            exclude_fields: Union[IncEx, None] = None,
            system_prompt: Union[Prompt, None] = None
    ) -> IntelType:

        if intel_class and intel_object:
            raise LlmException('Cannot specify both intel_class and intel_object.')

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
            raise LlmException('Must specify either intel_class or intel_object.')  

        event_id = generate_new_debug_event_id()

        for attempt in range(self._config.options.prompt_retry_count + 1):

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
                content=service_user_prompt(prompt).to_str()
            )

            debug_record_llm_request(request_body, event_id)

            message_content = self._config.get_response_content(
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

                    message_content = self._config.get_response_content(
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

                if self._config.options.prompt_retry_count - 1:
                    debug_record_llm_retry(
                        'Response after validation errors prompt failed.\nRetrying with original prompt.',
                        event_id,
                        remaining_attempts=self._config.options.prompt_retry_count - attempt
                    )
        else:
            raise LlmValidationException

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

        message_content = self._config.get_response_content(
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

    def post_request(self, json_body_dict: dict) -> dict:
        response: Response = Response(status_code=0)

        for _ in range(self._config.options.connection_retry_count + 1):

            response = httpx.request(
                'POST', 
                self._config.url.to_str(), 
                headers=self._config.headers, 
                content=json.dumps(json_body_dict).encode('utf-8'),
                timeout=settings.DEFAULT_LLM_REQUEST_TIMEOUT
            )

            if response.status_code == 200 or response.status_code == 201:
                json_data = json.loads(response.text)
                return json_data

            sleep(0.1)

        else:
            if response.status_code != 0:
                raise LlmException(
                    f'Llm service request failed with status code {response.status_code} and the following message "{response.text}" after {self._config.options.connection_retry_count} attempts')
            else:
                raise LlmException(
                    f'Llm service request failed after {self._config.options.connection_retry_count} attempts for unknown reasons')
