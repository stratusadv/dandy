from __future__ import annotations

import http.client
import json
from time import sleep
from typing_extensions import Type, Union, TYPE_CHECKING

from pydantic import ValidationError

from dandy.core.type_vars import IntelType
from dandy.debug.debug import DebugRecorder
from dandy.debug.utils import generate_new_debug_event_id
from dandy.llm.exceptions import LlmException, LlmValidationException
from dandy.llm.service.debug import debug_record_llm_request, debug_record_llm_response, debug_record_llm_success, \
    debug_record_llm_validation_failure, debug_record_llm_retry
from dandy.llm.service.prompts import service_system_validation_error_prompt, service_user_prompt, \
    service_system_intel_prompt

if TYPE_CHECKING:
    from dandy.llm.prompt import Prompt
    from dandy.llm.config import BaseLlmConfig
    from dandy.llm.request.request import BaseRequestBody
    from dandy.llm.config.options import LlmConfigOptions


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

    def create_connection(self) -> Union[http.client.HTTPConnection, http.client.HTTPSConnection]:
        connection_kwargs = {
            'host': self._config.url.parsed_url.netloc,
            'port': self._config.port
        }

        if self._config.url.is_https:
            connection = http.client.HTTPSConnection(**connection_kwargs)
        else:
            connection = http.client.HTTPConnection(**connection_kwargs)

        return connection

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
            intel_class: Type[IntelType],
            prefix_system_prompt: Union[Prompt, None] = None
    ) -> IntelType:

        event_id = generate_new_debug_event_id()

        for attempt in range(self._config.options.prompt_retry_count + 1):

            request_body = self.get_request_body()

            request_body.add_message(
                role='system',
                content=service_system_intel_prompt(
                    intel_class=intel_class,
                    prefix_system_prompt=prefix_system_prompt
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
                intel = intel_class.model_validate_json(message_content)

                debug_record_llm_success(
                    'Validated response from prompt into intel object.',
                    event_id,
                    intel=intel
                )

                return intel

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

                    intel = intel_class.model_validate_json(message_content)

                    debug_record_llm_success(
                        'Validated response from validation errors prompt into intel object.',
                        event_id,
                        intel=intel
                    )

                    return intel

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

    def process_request(self, method, path, encoded_body: bytes = None) -> dict:
        response = None
        response_body = ''

        for _ in range(self._config.options.connection_retry_count):
            connection = self.create_connection()

            if encoded_body:
                connection.request(method, path, body=encoded_body, headers=self._config.headers)
            else:
                connection.request(method, path, headers=self._config.headers)

            response = connection.getresponse()

            response_body = response.read().decode("utf-8")

            if response.status == 200 or response.status == 201:
                json_data = json.loads(response_body)
                connection.close()
                break

            connection.close()
            sleep(0.1)

        else:
            raise LlmException(
                f'Llm service request failed with status code {response.status} and the following message "{response_body}" after {self._config.options.connection_retry_count} attempts')

        return json_data

    def post_request(self, body) -> dict:
        encoded_body = json.dumps(body).encode('utf-8')
        return self.process_request("POST", self._config.url.path, encoded_body)
