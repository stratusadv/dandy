from dataclasses import dataclass


@dataclass
class OllamaHandlerConfig:
    url: str
    port: int


@dataclass
class GroqHandlerConfig:
    url: str
    port: int