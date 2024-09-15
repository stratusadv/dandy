from typing import Optional, List

from dandy.core.url import Url
from dandy.llm.config.manager import LlmManager
from dandy.llm.service import Service
from dandy.llm.service.settings import ServiceSettings


class LlmConfig:
    def __init__(self):
        self._llm_manager = LlmManager()

    @property
    def active_service(self) -> Service:
        return self.get_active_service()

    def add_service(
            self,
            name: str,
            url_path: str,
            port: int,
            model: str,
            url_path_parameters: Optional[List[str]] = None,
            url_query_parameters: Optional[dict] = None,
            headers: Optional[dict] = None,
    ):

        if headers is None:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

        self._llm_manager.add_service_settings(
            name=name,
            settings=ServiceSettings(
                url=Url(
                    path=url_path,
                    path_parameters=url_path_parameters,
                    query_parameters=url_query_parameters,
                ),
                port=port,
                model=model,
                headers=headers
            )
        )

    def get_active_service(self) -> Service:
        return self._llm_manager.get_active_service()

    def get_service(self, name: str) -> Service:
        return self._llm_manager.get_service(name)

    def set_active_service(self, name: str):
        self._llm_manager.set_active_service_settings(name)