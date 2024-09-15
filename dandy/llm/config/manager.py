from typing import Dict, Optional, Type, Union

from dandy.llm.exceptions import LlmException, LlmServiceNotFoundException
from dandy.llm.service import Service
from dandy.llm.service.settings import ServiceSettings


class LlmManager:
    def __init__(self):
        self._active_service_settings: Optional[str] = None
        self._service_settings: Dict[str, ServiceSettings] = {}

    @property
    def active_service_settings(self) -> ServiceSettings:
        if self._active_service_settings is None:
            raise LlmException('No LLM service is active')
        else:
            return self._service_settings[self._active_service_settings]

    def add_service_settings(
            self,
            name: str,
            url: str,
            port: Union[str, int],
            model: str,
    ):
        self._service_settings[name] = ServiceSettings(
            url=url,
            model=model,
            port=port,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            path_parameters=[
                'api',
                'chat',
            ],
            query_parameters=None
        )

        if self._active_service_settings is None:
            self.set_active_service_settings(name)

    def get_active_service(self) -> Service:
        return self.get_service(self._active_service_settings)

    def get_service(self, name: str) -> Service:
        if name not in self._service_settings:
            raise LlmServiceNotFoundException(name, list(self._service_settings.keys()))

        return Service(self.get_service_settings(name))

    def get_service_settings(self, name):
        if name not in self._service_settings:
            raise LlmServiceNotFoundException(name, list(self._service_settings.keys()))

        return self._service_settings[name]

    def set_active_service_settings(self, name):
        if name not in self._service_settings:
            raise LlmServiceNotFoundException(name, list(self._service_settings.keys()))

        self._active_service_settings = name