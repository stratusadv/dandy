from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import ValidationError

from dandy.core.service.service import BaseService
from dandy.http.connector import HttpConnector
from dandy.intel.factory import IntelFactory
from dandy.llm.connector import LlmConnector
from dandy.llm.exceptions import LlmCriticalException, LlmRecoverableException
from dandy.llm.intelligence.prompts import (
    service_system_prompt,
    service_system_validation_error_prompt,
)
from dandy.llm.prompt.prompt import Prompt
from dandy.llm.recorder import (
    recorder_add_llm_failure_event,
    recorder_add_llm_request_event,
    recorder_add_llm_response_event,
    recorder_add_llm_retry_event,
    recorder_add_llm_success_event,
)
from dandy.recorder.utils import generate_new_recorder_event_id

if TYPE_CHECKING:
    from pydantic.main import IncEx

    from dandy.intel.typing import IntelType
    from dandy.llm.mixin import LlmServiceMixin
    from dandy.llm.prompt.typing import PromptOrStr, PromptOrStrOrNone
    from dandy.llm.request.message import MessageHistory


class LlmService(BaseService['LlmServiceMixin']):
    obj: LlmServiceMixin

    def __post_init__(self):
        self.event_id = generate_new_recorder_event_id()

        self._request_body = self.obj.llm_config.generate_request_body(
            max_completion_tokens=self.obj.llm_config_options.max_completion_tokens,
            seed=self.obj.llm_config_options.seed,
            temperature=self.obj.llm_config_options.temperature,
        )

        self.connector = LlmConnector(
            event_id=self.event_id,
            prompt_retry_count=self.obj.llm_config_options.prompt_retry_count,
            http_request_intel=self.obj.llm_config.http_request_intel,
            request_body=self._request_body,
        )

    @property
    def messages(self) -> MessageHistory:
        return self._request_body.messages

    def _prepend_system_message(self):
        self._request_body.messages.create_message(
            role='system',
            text=service_system_prompt(
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
            include_fields: IncEx | None = None,
            exclude_fields: IncEx | None = None,
            message_history: MessageHistory | None = None,
            replace_message_history: bool = False,
    ) -> IntelType:
        intel = self._generate_intel(intel_class, intel_object)

        self.connector.set_intel(intel)

        self._setup_request_body(
            intel=intel,
            include_fields=include_fields,
            exclude_fields=exclude_fields,
            prompt=prompt,
            message_history=message_history,
            replace_message_history=replace_message_history,
        )

        return self.connector.request_to_intel()

    def reset_service(self):
        self.reset_messages()
        self._prepend_system_message()

    def reset_messages(self):
        self._request_body.reset_messages()

    def _generate_intel(
            self,
            intel_class: type[IntelType] | None = None,
            intel_object: IntelType | None = None,
    ):
        if intel_class and intel_object:
            message = 'Cannot specify both intel_class and intel_object.'
            raise LlmCriticalException(message)

        if intel_class is None and intel_object is None:
            if self.obj_class.llm_intel_class:
                intel_class = self.obj_class.llm_intel_class
            else:
                message = 'Must specify either intel_class, intel_object or llm_intel_class on the processor.'
                raise LlmCriticalException(message)

        return intel_class or intel_object

    def _setup_request_body(
            self,
            intel: InterruptedError | type[IntelType],
            include_fields: IncEx | None = None,
            exclude_fields: IncEx | None = None,
            prompt: PromptOrStrOrNone = None,
            message_history: MessageHistory | None = None,
            replace_message_history: bool = False,
    ):
        self._request_body.json_schema = IntelFactory.intel_to_json_inc_ex_schema(
            intel=intel, include=include_fields, exclude=exclude_fields
        )

        if not self._request_body.messages.has_system_message:
            self._prepend_system_message()

        if message_history:
            if replace_message_history:
                self._request_body.messages = message_history
            else:
                self._request_body.messages.extend(
                    message_history.messages
                )

        if prompt is not None:
            self._request_body.messages.create_message(
                role='user',
                text=Prompt(prompt).to_str(),
            )

        if len(self._request_body.messages) <= 1:
            message = f'"{self.__class__.__name__}.llm.process_to_intel" method requires you to have a prompt or more than the system message.'
            raise LlmCriticalException(message)

