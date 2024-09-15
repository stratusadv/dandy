from dataclasses import dataclass

from dandy.llm.service.settings import ServiceSettings


@dataclass(kw_only=True)
class OllamaSettings(ServiceSettings):
    pass