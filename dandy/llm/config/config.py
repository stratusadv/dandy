from typing import Type

from dandy.llm.config.manager import LlmManager
from dandy.llm.exceptions import LlmException
from dandy.llm.service import Service


class LlmConfig:
    def __init__(self):
        self._llm_manager = LlmManager()

    @property
    def active_service(self) -> Service:
        return self.get_active_service()

    def add_service(
            self,
            name: str,
            url: str,
            port: int,
            model: str
    ):

        self._llm_manager.add_service_settings(
            name,
            url,
            port,
            model
        )

    def get_active_service(self) -> Service:
        return self._llm_manager.get_active_service()

    def get_service(self, name: str) -> Service:
        return self._llm_manager.get_service(name)

    def set_active_service(self, name: str):
        self._llm_manager.set_active_service_settings(name)