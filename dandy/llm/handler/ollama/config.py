from dataclasses import dataclass


@dataclass
class OllamaHandlerConfig:
    url: str
    port: int

