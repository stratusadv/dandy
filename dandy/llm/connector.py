from pydantic import ValidationError

from dandy.core.connector.connector import BaseConnector
from dandy.llm.prompt.prompt import Prompt
from dandy.http.connector import HttpConnector
from dandy.http.intelligence.intel import HttpRequestIntel
from dandy.intel.factory import IntelFactory
from dandy.intel.typing import IntelType
from dandy.llm.exceptions import LlmRecoverableException
from dandy.llm.intelligence.prompts import service_system_validation_error_prompt
from dandy.llm.prompt.typing import PromptOrStr
from dandy.llm.recorder import recorder_add_llm_request_event, recorder_add_llm_response_event, \
    recorder_add_llm_success_event, recorder_add_llm_failure_event, recorder_add_llm_retry_event
from dandy.llm.request.request import LlmRequestBody


class LlmConnector(BaseConnector):
    def __init__(
            self,
            event_id: str,
            prompt_retry_count: int,
            http_request_intel: HttpRequestIntel,
            request_body: LlmRequestBody,
    ):
        self._event_id = event_id
        self.prompt_retry_attempt = 0
        self.prompt_retry_count = prompt_retry_count

        self.http_request_intel = http_request_intel
        self.request_body = request_body
        self.intel = None

        self.response_str = None

    @property
    def has_retry_attempts_available(self) -> bool:
        return self.prompt_retry_attempt < self.prompt_retry_count

    def _reset_prompt_retry_attempt(self):
        self.prompt_retry_attempt = 0

    def request_to_intel(
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

            return self.request_to_intel()

        message = f'Failed to get the correct response from the LlmService after {self.prompt_retry_count} attempts.'
        raise LlmRecoverableException(message)

    def set_intel(self, intel: IntelType | type[IntelType]):
        self.intel = intel
