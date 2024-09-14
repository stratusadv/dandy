from typing import Dict

from dandy.llm.exceptions import LlmException
from dandy.llm.service.settings import ServiceSettings


class LlmManager:
    def __init__(self):
        self._llm_service_settings: Dict[str, ServiceSettings] = {}

    def add_llm(
            self,
            name,
            url,
            port,
            model,
    ):
        if name in self._llm_service_settings:
            raise LlmException(f'LLM Configuration "{name}" already exists')

        self._llm_service_settings[name] = ServiceSettings(
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

    def get_llm(self, name):
        if name not in self._llm_service_settings:
            raise LlmException(f'LLM Configuration "{name}" does not exist')

        return self._llm_service_settings[name]