from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from dandy.infrastructure.future.process import process_to_future
from dandy.shared.service.service import BaseService
from dandy.infrastructure.llm.connector import LlmConnector
from dandy.infrastructure.llm.config import LlmConfig
from dandy.application.decision.mixin import DecisionServiceMixin
from dandy.application.diligence.mixin import DiligenceServiceMixin
from dandy.domain.request.exceptions import LlmCriticalError
from dandy.domain.request.options import LlmOptions
from dandy.domain.request.prompts import service_system_prompt
from dandy.application.tool.mixin import ToolServiceMixin
from dandy.application.skill.mixin import SkillServiceMixin

if TYPE_CHECKING:
    from pydantic.main import IncEx

    from dandy.infrastructure.future.future import AsyncFuture
    from dandy.domain.intel.typing import IntelType
    from dandy.domain.prompt.prompt import Prompt
    from dandy.domain.message.message import MessageHistory
    from dandy.domain.tool.tool import ToolType


_CONFIG_IDENTITY_OVERRIDE_TYPES = {
    'model': str,
    'host': str,
    'port': int,
    'api_key': str,
    'context_size': int,
    'prompt_retry_count': int,
}


class LlmService(
    BaseService['dandy.application.llm.mixin.LlmServiceMixin'],
    DecisionServiceMixin,
    DiligenceServiceMixin,
    ToolServiceMixin,
    SkillServiceMixin,
):
    def __post_init__(self) -> None:
        self.skills.register(self.obj.skills)

        self._llm_connector: LlmConnector = LlmConnector(
            recorder_event_id=self.recorder_event_id,
            system_prompt=self.build_system_prompt(),
            llm_config=self.obj.get_llm_config(),
            intel_class=self.obj.intel_class,
            post_diligence_handler=self.diligence.post_handler,
            pre_diligence_handler=self.diligence.pre_handler,
        )

    def build_system_prompt(self) -> str:
        system_prompt = service_system_prompt(
            role=self.obj.role,
            task=self.obj.task,
            guidelines=self.obj.guidelines,
            system_override_prompt=self.obj.system_override_prompt,
        ).to_str()

        skill_section = self.skills.system_prompt_section()

        if skill_section:
            system_prompt = f'{system_prompt}\n\n{skill_section}'

        return system_prompt

    @property
    def messages(self) -> MessageHistory:
        return self._llm_connector.request_body.messages

    @property
    def config(self) -> LlmConfig:
        return self._llm_connector.llm_config

    @config.setter
    def config(self, llm_config: LlmConfig) -> None:
        if not isinstance(llm_config, LlmConfig):
            message = f'config expects an LlmConfig instance, got {type(llm_config).__name__}.'
            raise LlmCriticalError(message)

        self._llm_connector.set_llm_config(llm_config)
        self.obj.llm_config = llm_config.name

    def set_config(self, name: str, **overrides: Any) -> LlmConfig:
        """Swap this bot's LLM config mid-conversation, keeping the history.

        `name` selects a settings `LLM_CONFIGS` entry; keyword overrides set
        individual fields on the resolved config (model, host, port, api_key,
        context_size, prompt_retry_count, or any LlmOptions field). The new
        config applies to the next request and survives `reset()`.
        """
        identity_overrides: dict[str, Any] = {}
        option_overrides: dict[str, Any] = {}

        for key, value in overrides.items():
            expected_type = _CONFIG_IDENTITY_OVERRIDE_TYPES.get(key)

            if expected_type is not None:
                if isinstance(value, bool) or not isinstance(value, expected_type):
                    message = f'Invalid override for "{key}": expected {expected_type.__name__}.'
                    raise LlmCriticalError(message)

                identity_overrides[key] = value

            elif key in LlmOptions.model_fields:
                option_overrides[key] = value

            else:
                message = (
                    f'Unknown LLM config override "{key}". Use model, host, port, api_key, '
                    'context_size, prompt_retry_count or an LlmOptions field.'
                )
                raise LlmCriticalError(message)

        llm_config = LlmConfig(name)

        for key, value in identity_overrides.items():
            setattr(llm_config, key, value)

        if option_overrides:
            base_options = llm_config._settings_values.get('options') or {}
            merged_options = {**base_options, **option_overrides}
            llm_config.options = LlmOptions(**merged_options)
            llm_config._settings_values['options'] = merged_options

        self._llm_connector.set_llm_config(llm_config)
        self.obj.llm_config = name

        return llm_config

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

    def rebuild_system_prompt(self) -> str:
        """Rebuild the system message text from the bot's current prompt attributes.

        Used when the bot's prompt content changes mid-conversation (for
        example when the project's AGENTS.md is regenerated). This only
        updates the connector; any conversation that already carries a
        system message keeps its own copy until the caller syncs it.
        """
        self._llm_connector.system_prompt_str = self.build_system_prompt()

        return self._llm_connector.system_prompt_str

    def reset(self) -> None:
        self._llm_connector.reset()
        self.reset_messages()
        self.skills.reset()

    def reset_messages(self) -> None:
        self._llm_connector.request_body.reset_messages()
