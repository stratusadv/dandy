from dataclasses import dataclass


@dataclass
class OllamaHandlerConfig:
    address: str
    port: int