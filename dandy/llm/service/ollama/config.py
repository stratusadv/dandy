from dataclasses import dataclass


@dataclass
class OllamaServiceConfig:
    url: str
    port: int

