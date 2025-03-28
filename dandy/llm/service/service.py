from __future__ import annotations

from typing import List

from pydantic import ValidationError
from pydantic.main import IncEx
from typing_extensions import Type, Union, TYPE_CHECKING

from dandy.core.http.service import BaseHttpService
from dandy.debug.debug import DebugRecorder
from dandy.debug.utils import generate_new_debug_event_id
from dandy.intel.type_vars import IntelType
from dandy.llm.exceptions import LlmCriticalException, LlmValidationCriticalException
from dandy.llm.prompt import Prompt
from dandy.llm.service.debug import debug_record_llm_request, debug_record_llm_response, debug_record_llm_success, \
    debug_record_llm_validation_failure, debug_record_llm_retry
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

        inc_ex_kwargs = {'include': include_fields, 'exclude': exclude_fields}

        if intel_class:
            intel_json_schema = intel_class.model_inc_ex_class_copy(
                **inc_ex_kwargs,
                intel_object=None
            ).model_json_schema()

        elif intel_object:
            intel_json_schema = intel_object.model_inc_ex_class_copy(
                **inc_ex_kwargs,
                intel_object=intel_object
            ).model_json_schema()

        else:
            raise LlmCriticalException('Must specify either intel_class or intel_object.')

        event_id = generate_new_debug_event_id()

        for attempt in range(self._llm_config.options.prompt_retry_count):

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

            debug_record_llm_request(request_body, intel_json_schema, event_id)

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
                        debug_record_llm_request(request_body, intel_json_schema, event_id)

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

                if self._llm_config.options.prompt_retry_count:
                    debug_record_llm_retry(
                        'Response after validation errors prompt failed.\nRetrying with original prompt.',
                        event_id,
                        remaining_attempts=self._llm_config.options.prompt_retry_count + 1 - attempt
                    )
        else:
            raise LlmValidationCriticalException
