from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import ValidationError
from pydantic.main import IncEx

from dandy.core.connector.connector import BaseConnector
from dandy.http.connector import HttpConnector
from dandy.intel.factory import IntelFactory
from dandy.intel.intel import DefaultIntel
from dandy.intel.typing import IntelType
from dandy.llm.config import LlmConfig
from dandy.llm.exceptions import LlmCriticalError, LlmRecoverableError
from dandy.llm.intelligence.prompts import service_system_validation_error_prompt
from dandy.llm.prompt.prompt import Prompt
from dandy.llm.recorder import (
    recorder_add_llm_failure_event,
    recorder_add_llm_request_event,
    recorder_add_llm_response_event,
    recorder_add_llm_retry_event,
    recorder_add_llm_success_event,
)
from dandy.llm.request.message import MessageHistory
from dandy.llm.tool.intel import LlmToolCallIntel, LlmToolCallsIntel
from dandy.llm.tool.recorder import recorder_add_tool_call_event
from dandy.tool.tool import ToolType, to_tool_instances

if TYPE_CHECKING:
    from dandy.llm.diligence.handler import DiligenceHandler


class LlmConnector(BaseConnector):
    def __init__(
        self,
        recorder_event_id: str,
        llm_config: LlmConfig,
        intel_class: type[IntelType] | None,
        system_prompt: Prompt | str,
        post_diligence_handler: DiligenceHandler | None = None,
        pre_diligence_handler: DiligenceHandler | None = None,
    ):
        self.recorder_event_id = recorder_event_id

        self.llm_config = llm_config

        self.intel = None
        self.intel_class = intel_class

        self.prompt_retry_attempt = 0

        self.request_body = self.llm_config.generate_request_body()
        self.response_str = None
        self.tool_calls = None

        self.system_prompt_str = str(system_prompt)

        self.post_diligence_handler = post_diligence_handler
        self.pre_diligence_handler = pre_diligence_handler

    @property
    def has_retry_attempts_available(self) -> bool:
        return self.prompt_retry_attempt < self.llm_config.options.prompt_retry_count

    def _http_request_to_response_str(self) -> None:
        http_connector = HttpConnector()

        self.llm_config.http_request_intel.json_data = self.request_body.model_dump()

        response_message = http_connector.request_to_response(
            request_intel=self.llm_config.http_request_intel
        ).json_data['choices'][0]['message']

        self.response_str = response_message.get('content') or ''
        self.tool_calls = response_message.get('tool_calls') or None

    def _prepend_system_message(self):
        self.request_body.messages.add_message(
            role='system', text=self.system_prompt_str, prepend=True
        )

    def prompt_to_intel(
        self,
        prompt: Prompt | str | None = None,
        intel_class: type[IntelType] | None = None,
        intel_object: IntelType | None = None,
        audio_urls: list[str] | None = None,
        audio_file_paths: list[str | Path] | None = None,
        audio_base64_strings: list[str] | None = None,
        image_urls: list[str] | None = None,
        image_file_paths: list[str | Path] | None = None,
        image_base64_strings: list[str] | None = None,
        include_fields: IncEx | None = None,
        exclude_fields: IncEx | None = None,
        tools: list[ToolType] | None = None,
        tool_choice: str | dict | None = None,
        message_history: MessageHistory | None = None,
        replace_message_history: bool = False,
    ) -> IntelType:
        self._update_request_body()

        self._set_intel(intel_class=intel_class, intel_object=intel_object)

        self.request_body.json_schema = IntelFactory.intel_to_json_inc_ex_schema(
            intel=self.intel, include=include_fields, exclude=exclude_fields
        )

        self._update_request_body_options(
            tools=tools,
            tool_choice=tool_choice,
            message_history=message_history,
            replace_message_history=replace_message_history,
            prompt=prompt,
            audio_urls=audio_urls,
            audio_file_paths=audio_file_paths,
            audio_base64_strings=audio_base64_strings,
            image_urls=image_urls,
            image_file_paths=image_file_paths,
            image_base64_strings=image_base64_strings,
        )

        if len(self.request_body.messages) <= 1:
            message = (
                'You cannot prompt the LlmService without at least one system and one user message.'
            )
            raise LlmCriticalError(message)

        if self.pre_diligence_handler is not None:
            self.pre_diligence_handler.apply(llm_connector=self)

        response_intel_object = self._request_to_intel()

        if self.post_diligence_handler is not None:
            self.post_diligence_handler.apply(llm_connector=self)

            if self.post_diligence_handler.requires_new_llm_request:
                response_intel_object = self._request_to_intel()

        return response_intel_object

    def _update_request_body_options(
        self,
        tools: list[ToolType] | None,
        tool_choice: str | dict | None,
        message_history: MessageHistory | None,
        replace_message_history: bool,
        prompt: Prompt | str | None,
        audio_urls: list[str] | None,
        audio_file_paths: list[str | Path] | None,
        audio_base64_strings: list[str] | None,
        image_urls: list[str] | None,
        image_file_paths: list[str | Path] | None,
        image_base64_strings: list[str] | None,
    ) -> None:
        if tools is not None:
            self.request_body.tools = [tool.to_function_dict() for tool in to_tool_instances(tools)]
            self.request_body.response_format = None
            self.request_body.tool_choice = tool_choice
        else:
            self.request_body.tools = None
            self.request_body.tool_choice = None

        if message_history is not None:
            if replace_message_history:
                self.request_body.messages = message_history
            else:
                self.request_body.messages.extend(message_history.messages)

        if not self.request_body.messages.has_system_message:
            self._prepend_system_message()

        if prompt is not None:
            self.request_body.messages.add_message(role='user', text=Prompt(prompt).to_str())

        if audio_urls or audio_file_paths or audio_base64_strings:
            self.request_body.messages.add_message(
                role='user',
                audio_urls=audio_urls,
                audio_file_paths=audio_file_paths,
                audio_base64_strings=audio_base64_strings,
            )

        if image_urls or image_file_paths or image_base64_strings:
            self.request_body.messages.add_message(
                role='user',
                image_urls=image_urls,
                image_file_paths=image_file_paths,
                image_base64_strings=image_base64_strings,
            )

    def _reset_prompt_retry_attempt(self):
        self.prompt_retry_attempt = 0

    def reset(self):
        self.llm_config.reset()
        self.request_body = self.llm_config.generate_request_body()

    def _request_to_intel(self) -> IntelType:
        recorder_add_llm_request_event(self.request_body, self.recorder_event_id)

        self._http_request_to_response_str()

        recorder_add_llm_response_event(
            message_content=self.response_str, event_id=self.recorder_event_id
        )

        if self.tool_calls:
            self.request_body.messages.add_message(role='assistant', tool_calls=self.tool_calls)

            return self._parse_tool_calls_to_intel()

        try:
            intel_object = IntelFactory.json_str_to_intel_object(
                json_str=self.response_str, intel=self.intel
            )

            if intel_object is not None:
                recorder_add_llm_success_event(
                    description='Validated response from prompt into intel object.',
                    event_id=self.recorder_event_id,
                    intel=intel_object,
                )

                self.request_body.messages.add_message(role='assistant', text=self.response_str)

                return intel_object

            message = 'Failed to validate response from prompt into intel object.'
            raise LlmRecoverableError(message)

        except ValidationError as error:
            if self._should_fallback_to_default_text(error):
                recorder_add_llm_success_event(
                    description='Response was plain text; stored it in DefaultIntel.',
                    event_id=self.recorder_event_id,
                    intel=DefaultIntel(text=self.response_str),
                )

                self.request_body.messages.add_message(role='assistant', text=self.response_str)

                return DefaultIntel(text=self.response_str)

            recorder_add_llm_failure_event(error, self.recorder_event_id)

            return self.retry_request_to_intel(
                retry_event_description='Validation of response to intel object failed, retrying with validation errors prompt.',
                retry_user_prompt=service_system_validation_error_prompt(error),
            )

    def _should_fallback_to_default_text(self, error: ValidationError) -> bool:
        if not self.response_str:
            return False

        if not isinstance(self.intel, DefaultIntel) and self.intel is not DefaultIntel:
            return False

        return {entry['type'] for entry in error.errors()} == {'json_invalid'}

    def _parse_tool_calls_to_intel(self) -> LlmToolCallsIntel:
        tool_calls_intel = LlmToolCallsIntel(summary=(self.response_str or '').strip())

        for tool_call in self.tool_calls or []:
            tool_calls_intel.append(
                LlmToolCallIntel(
                    id=tool_call.get('id'),
                    name=tool_call['function']['name'],
                    arguments=tool_call['function'].get('arguments') or '',
                )
            )

        recorder_add_tool_call_event(tool_calls_intel, self.recorder_event_id)

        return tool_calls_intel

    def retry_request_to_intel(
        self, retry_event_description: str, retry_user_prompt: Prompt | str
    ) -> IntelType:
        if self.has_retry_attempts_available:
            self.prompt_retry_attempt += 1

            recorder_add_llm_retry_event(
                retry_event_description,
                self.recorder_event_id,
                remaining_attempts=self.llm_config.options.prompt_retry_count
                - self.prompt_retry_attempt,
            )

            self.request_body.messages.add_message(
                role='user', text=Prompt(retry_user_prompt).to_str()
            )

            return self._request_to_intel()

        message = f'Failed to get the correct response from the LlmService after {self.llm_config.options.prompt_retry_count} attempts.'
        raise LlmRecoverableError(message)

    def _set_intel(
        self, intel_class: type[IntelType] | None = None, intel_object: IntelType | None = None
    ):
        if intel_class and intel_object:
            message = 'Cannot specify both intel_class and intel_object.'
            raise LlmCriticalError(message)

        if intel_class is None and intel_object is None:
            if self.intel_class:
                intel_class = self.intel_class
            else:
                message = 'Must specify either intel_class, intel_object or llm_intel_class on the processor.'
                raise LlmCriticalError(message)

        self.intel = intel_class or intel_object

    def _update_request_body(self):
        for key, value in self.llm_config.options.model_dump(exclude_none=True).items():
            setattr(self.request_body, key, value)
