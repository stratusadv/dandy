from typing import Type

from dandy.llm.service import Service
from dandy.llm.service.ollama.config import OllamaServiceConfig
from dandy.llm.service.enums import ServiceType


class Config:
    ollama_service_config: OllamaServiceConfig
    _instance = None
    _active_llm_service: ServiceType
    _active_llm_model: str

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    @property
    def active_llm_service(self) -> Type[Service]:
        if self._active_llm_service == ServiceType.OLLAMA:
            from dandy.llm.service.ollama.service import OllamaHandler
            return OllamaHandler
        else:
            raise Exception('Unknown LLM service')

    def setup_ollama(self, url: str, port: int, model: str = None):
        self.ollama_service_config = OllamaServiceConfig(
            url=url,
            port=port
        )

        if model is not None:
            self.set_llm(model=model)

        self._active_llm_service = ServiceType.OLLAMA

    def set_llm(
            self,
            service: str = None,
            model: str = None,
    ):
        if isinstance(service, ServiceType):
            self._active_llm_service = service
        elif isinstance(service, str):
            self._active_llm_service = ServiceType(service)
        else:
            raise Exception('Unknown LLM service')

        if isinstance(model, str):
            self._active_llm_model = model
        else:
            raise Exception('Unknown LLM model')