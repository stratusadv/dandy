from typing import Optional, List

from dandy.core.url import Url
from dandy.llm.service import Service
from dandy.llm.service.settings import ServiceSettings


class LlmConfig:
    def __init__(
            self,
            host: str,
            port: int,
            model: str,
            path_parameters: Optional[List[str]] = None,
            query_parameters: Optional[dict] = None,
            headers: Optional[dict] = None,
            api_key: Optional[str] = None,
    ):
        if headers is None:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

        if api_key is not None:
            headers["Authorization"] = f"Bearer {api_key}"

        self.settings = ServiceSettings(
            url=Url(
                host=host,
                path_parameters=path_parameters,
                query_parameters=query_parameters,
            ),
            port=port,
            model=model,
            headers=headers,
        )

    @property
    def service(self):
        return Service(self.settings)
