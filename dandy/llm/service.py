from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from dandy.core.service.service import BaseService
from dandy.intel.factory import IntelFactory
from dandy.llm.connector import LlmConnector
from dandy.llm.decoder.mixin import DecoderServiceMixin
from dandy.llm.exceptions import LlmCriticalException
from dandy.llm.intelligence.prompts import (
    service_system_prompt,
)
from dandy.llm.prompt.prompt import Prompt
from dandy.recorder.utils import generate_new_recorder_event_id

if TYPE_CHECKING:
    from pydantic.main import IncEx

    from dandy.intel.typing import IntelType
    # from dandy.llm.mixin import LlmServiceMixin
    from dandy.llm.prompt.typing import PromptOrStrOrNone
    from dandy.llm.request.message import MessageHistory


class LlmService(
    BaseService['dandy.llm.mixin.LlmServiceMixin'],
    DecoderServiceMixin,
):
    def __post_init__(self):
        self.event_id = generate_new_recorder_event_id()
        self._request_body = self.obj.get_llm_config().generate_request_body()

        self.connector = self.generate_connector()

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
        self._setup_request_body(
            intel_class=intel_class,
            intel_object=intel_object,
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

    def generate_connector(self) -> LlmConnector:
        return LlmConnector(
            event_id=self.event_id,
            prompt_retry_count=self.obj.get_llm_options().prompt_retry_count,
            http_request_intel=self.obj.get_llm_config().http_request_intel,
            request_body=self._request_body,
        )

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
            intel_class: type[IntelType] | None = None,
            intel_object: IntelType | None = None,
            include_fields: IncEx | None = None,
            exclude_fields: IncEx | None = None,
            prompt: PromptOrStrOrNone = None,
            message_history: MessageHistory | None = None,
            replace_message_history: bool = False,
    ):
        intel = self._generate_intel(intel_class, intel_object)

        self.connector.set_intel(intel)

        self._request_body.json_schema = IntelFactory.intel_to_json_inc_ex_schema(
            intel=intel,
            include=include_fields,
            exclude=exclude_fields
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


# class LlmService(BaseLlmService):
#     obj: LlmServiceMixin
#
#     def prompt_to_intel(
#             self,
#             prompt: PromptOrStrOrNone = None,
#             intel_class: type[IntelType] | None = None,
#             intel_object: IntelType | None = None,
#             include_fields: IncEx | None = None,
#             exclude_fields: IncEx | None = None,
#             message_history: MessageHistory | None = None,
#             replace_message_history: bool = False,
#     ) -> IntelType:
#         self._setup_request_body(
#             intel_class=intel_class,
#             intel_object=intel_object,
#             include_fields=include_fields,
#             exclude_fields=exclude_fields,
#             prompt=prompt,
#             message_history=message_history,
#             replace_message_history=replace_message_history,
#         )
#
#         return self.connector.request_to_intel()
