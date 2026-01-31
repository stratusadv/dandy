from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from dandy.core.service.service import BaseService
from dandy.llm.connector import LlmConnector
from dandy.llm.decoder.mixin import DecoderServiceMixin

if TYPE_CHECKING:
    from pydantic.main import IncEx
    from dandy.intel.typing import IntelType
    from dandy.llm.prompt.typing import PromptOrStr
    from dandy.llm.request.message import MessageHistory


class LlmService(
    BaseService['dandy.llm.mixin.LlmServiceMixin'],
    DecoderServiceMixin,
):
    def __post_init__(self):
        self._llm_connector: LlmConnector = LlmConnector(
            event_id=self.event_id,
            llm_service_mixin=self.obj
        )

    @property
    def messages(self) -> MessageHistory:
        return self._llm_connector.request_body.messages

    def prompt_to_intel(
            self,
            prompt: PromptOrStr,
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

    def reset_service(self):
        self._llm_connector.reset()

    def reset_messages(self):
        self._llm_connector.request_body.reset_messages()
