from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from dandy.llm.request.message import Message

if TYPE_CHECKING:
    from dandy.llm.connector import LlmConnector


class BaseDiligence(ABC):
    requires_new_llm_request: bool = False

    def __init__(self):
        self.is_activated = False

    def activate(self) -> None:
        self.is_activated = True

    def deactivate(self) -> None:
        self.is_activated = False

    @classmethod
    def _prepend_system_instruction(cls, llm_connector: LlmConnector, instruction: str) -> None:
        # Some OpenAI-compatible endpoints reject more than one system message
        # (vLLM raises "System message must be at the beginning."), so merge into
        # the leading system message instead of adding a second one.
        messages = llm_connector.request_body.messages

        first_message = messages[0] if len(messages) else None

        if isinstance(first_message, Message) and first_message.role == 'system':
            first_message.add_content_from_text(instruction)
        else:
            messages.add_message(role='system', text=instruction, prepend=True)

    @abstractmethod
    def apply(self, llm_connector: LlmConnector) -> None:
        raise NotImplementedError
