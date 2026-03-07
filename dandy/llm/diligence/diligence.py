from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

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

    @abstractmethod
    def apply(self, llm_connector: LlmConnector) -> None:
        raise NotImplementedError
