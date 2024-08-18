from dandy.config.handlers import OllamaHandlerConfig


class Config:
    _ollama_handler_config: OllamaHandlerConfig
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    @property
    def ollama(self) -> OllamaHandlerConfig:
        return self._ollama_handler_config

    def setup_ollama(self, url: str, port: int):
        self._ollama_handler_config = OllamaHandlerConfig(
            url=url,
            port=port
        )
