from typing import Type

from dandy.llm.handler import Handler
from dandy.llm.handler.ollama.config import OllamaHandlerConfig
from dandy.llm.enums import LlmService


class Config:
    _ollama_handler_config: OllamaHandlerConfig
    _instance = None
    _active_llm_service: LlmService
    _active_llm_model: str

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    @property
    def active_llm_handler(self) -> Type[Handler]:
        if self._active_llm_service == LlmService.OLLAMA:
            from dandy.llm.handler.ollama.handler import OllamaHandler
            return OllamaHandler
        else:
            raise Exception('Unknown LLM service')

    @property
    def ollama(self) -> OllamaHandlerConfig:
        return self._ollama_handler_config

    def setup_ollama(self, url: str, port: int):
        self._ollama_handler_config = OllamaHandlerConfig(
            url=url,
            port=port
        )

        self._active_llm_service = LlmService.OLLAMA

    def set_llm(
            self,
            service: str = None,
            model: str = None,
    ):
        if isinstance(service, LlmService):
            self._active_llm_service = service
        elif isinstance(service, str):
            self._active_llm_service = LlmService(service)
        else:
            raise Exception('Unknown LLM service')

        if isinstance(model, str):
            self._active_llm_model = model
        else:
            raise Exception('Unknown LLM model')