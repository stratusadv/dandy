from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from dandy.llm.options import LlmOptions
from dandy.core.future.tools import process_to_future
from dandy.core.future.future import AsyncFuture
from dandy.llm.prompt.prompt import Prompt

from dandy.core.service.service import BaseService
from dandy.llm.connector import LlmConnector
from dandy.llm.decoder.mixin import DecoderServiceMixin
from dandy.llm.intelligence.prompts import service_system_prompt

if TYPE_CHECKING:
    from pydantic.main import IncEx
    from dandy.intel.typing import IntelType
    from dandy.llm.request.message import MessageHistory


class LlmService(
    BaseService['dandy.llm.mixin.LlmServiceMixin'],
    DecoderServiceMixin,
):
    def __post_init__(self):
        self._llm_connector: LlmConnector = LlmConnector(
            event_id=self.recorder_event_id,
            system_prompt=service_system_prompt(
                role=self.obj.llm_role,
                task=self.obj.llm_task,
                guidelines=self.obj.llm_guidelines,
                system_override_prompt=self.obj.llm_system_override_prompt,
            ).to_str(),
            llm_config=self.obj.get_llm_config(),
            intel_class=self.obj.llm_intel_class,
        )

    @property
    def messages(self) -> MessageHistory:
        return self._llm_connector.request_body.messages

    @property
    def options(self) -> LlmOptions:
        return self._llm_connector.llm_config.options

    def prompt_to_intel(
            self,
            prompt: Prompt | str | None = None,
            intel_class: type[IntelType] | None = None,
            intel_object: IntelType | None = None,
            image_urls: list[str] | None = None,
            image_file_paths: list[str | Path] | None = None,
            image_base64_strings: list[str] | None = None,
            include_fields: IncEx | None = None,
            exclude_fields: IncEx | None = None,
            message_history: MessageHistory | None = None,
            replace_message_history: bool = False,
    ) -> IntelType:
        return self._llm_connector.prompt_to_intel(
            prompt=prompt,
            intel_class=intel_class,
            intel_object=intel_object,
            image_urls=image_urls,
            image_file_paths=image_file_paths,
            image_base64_strings=image_base64_strings,
            include_fields=include_fields,
            exclude_fields=exclude_fields,
            message_history=message_history,
            replace_message_history=replace_message_history,
        )

    def prompt_to_intel_future(self, **kwargs) -> AsyncFuture:
        return process_to_future(self.prompt_to_intel, **kwargs)

    def reset(self):
        self._llm_connector.reset()
        self.reset_messages()

    def reset_messages(self):
        self._llm_connector.request_body.reset_messages()
