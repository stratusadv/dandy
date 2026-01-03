from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from pydantic.main import IncEx

from dandy.intel.typing import IntelType
from dandy.llm.prompt.typing import PromptOrStrOrNone
from dandy.llm.request.message import MessageHistory
from dandy.llm.service import BaseLlmService

if TYPE_CHECKING:
    from dandy.vision.mixin import VisionServiceMixin


class VisionService(BaseLlmService):
    obj: VisionServiceMixin

    def image_prompt_to_intel(
            self,
            prompt: PromptOrStrOrNone = None,
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
        self._setup_request_body(
            intel_class=intel_class,
            intel_object=intel_object,
            include_fields=include_fields,
            exclude_fields=exclude_fields,
            prompt=prompt,
            message_history=message_history,
            replace_message_history=replace_message_history,
        )

        self._request_body.messages.create_message(
            role='user',
            image_urls=image_urls,
            image_file_paths=image_file_paths,
            image_base64_strings=image_base64_strings,
        )

        return self.connector.request_to_intel()
