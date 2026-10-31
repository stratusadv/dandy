from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from dandy.infrastructure.future.process import process_to_future
from dandy.shared.service.service import BaseService
from dandy.infrastructure.llm.connector import LlmConnector
from dandy.application.decision.mixin import DecisionServiceMixin
from dandy.application.diligence.mixin import DiligenceServiceMixin
from dandy.domain.request.prompts import service_system_prompt
from dandy.application.tool.mixin import ToolServiceMixin
from dandy.application.skill.mixin import SkillServiceMixin

if TYPE_CHECKING:
    from pydantic.main import IncEx

    from dandy.infrastructure.future.future import AsyncFuture
    from dandy.domain.intel.typing import IntelType
    from dandy.infrastructure.llm.config import LlmConfig
    from dandy.domain.request.options import LlmOptions
    from dandy.domain.prompt.prompt import Prompt
    from dandy.domain.message.message import MessageHistory
    from dandy.domain.tool.tool import ToolType


class LlmService(
    BaseService['dandy.application.llm.mixin.LlmServiceMixin'],
    DecisionServiceMixin,
    DiligenceServiceMixin,
    ToolServiceMixin,
    SkillServiceMixin,
):
    def __post_init__(self):
        self.skills.register(self.obj.skills)

        system_prompt = service_system_prompt(
            role=self.obj.role,
            task=self.obj.task,
            guidelines=self.obj.guidelines,
            system_override_prompt=self.obj.system_override_prompt,
        ).to_str()

        skill_section = self.skills.system_prompt_section()

        if skill_section:
            system_prompt = f'{system_prompt}\n\n{skill_section}'

        self._llm_connector: LlmConnector = LlmConnector(
            recorder_event_id=self.recorder_event_id,
            system_prompt=system_prompt,
            llm_config=self.obj.get_llm_config(),
            intel_class=self.obj.intel_class,
            post_diligence_handler=self.diligence.post_handler,
            pre_diligence_handler=self.diligence.pre_handler,
        )

    @property
    def messages(self) -> MessageHistory:
        return self._llm_connector.request_body.messages

    @property
    def config(self) -> LlmConfig:
        return self._llm_connector.llm_config

    @property
    def options(self) -> LlmOptions:
        return self._llm_connector.llm_config.options

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
        return self._llm_connector.prompt_to_intel(
            prompt=prompt,
            intel_class=intel_class,
            intel_object=intel_object,
            audio_urls=audio_urls,
            audio_file_paths=audio_file_paths,
            audio_base64_strings=audio_base64_strings,
            image_urls=image_urls,
            image_file_paths=image_file_paths,
            image_base64_strings=image_base64_strings,
            include_fields=include_fields,
            exclude_fields=exclude_fields,
            tools=tools,
            tool_choice=tool_choice,
            message_history=message_history,
            replace_message_history=replace_message_history,
        )

    def prompt_to_intel_future(self, **kwargs) -> AsyncFuture:
        return process_to_future(self.prompt_to_intel, **kwargs)

    def append_system_prompt(self, section: str) -> None:
        """Append a section to the system message for the rest of the conversation.

        Used when skills are registered after the LlmService was built (for
        example by an Agent wrapping the bot). Must be called before the
        first request of the conversation.
        """
        if section:
            self._llm_connector.system_prompt_str = (
                f'{self._llm_connector.system_prompt_str}\n\n{section}'
            )

    def reset(self):
        self._llm_connector.reset()
        self.reset_messages()
        self.skills.reset()

    def reset_messages(self):
        self._llm_connector.request_body.reset_messages()
