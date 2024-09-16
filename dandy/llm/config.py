from abc import abstractmethod
from typing import Optional, List

from dandy.core.url import Url
from dandy.llm.service import Service


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
            retry_count: int = 10,
    ):
        if headers is None:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

        if api_key is not None:
            headers["Authorization"] = f"Bearer {api_key}"

        self.url=Url(
            host=host,
            path_parameters=path_parameters,
            query_parameters=query_parameters,
        )
        self.port=port
        self.model=model
        self.headers=headers

        self.retry_count = retry_count

    @property
    def service(self):
        return Service(self)

    @abstractmethod
    def get_response_content(self, response) -> str:
        ...


class OllamaLlmConfig(LlmConfig):
    def __init__(
            self,
            host: str,
            port: int,
            model: str,
            api_key: Optional[str] = None,
    ):
        super().__init__(
            host=host,
            port=port,
            model=model,
            path_parameters=[
                'api',
                'chat',
            ],
            api_key=api_key,
        )

    def get_response_content(self, response) -> str:
        return response['message']['content']


class OpenaiLlmConfig(LlmConfig):
    def __init__(
            self,
            host: str,
            port: int,
            model: str,
            api_key: Optional[str] = None,
    ):
        super().__init__(
            host=host,
            port=port,
            model=model,
            path_parameters=[
                'v1',
                'chat',
                'completions',
            ],
            api_key=api_key,
        )

    def get_response_content(self, response) -> str:
        return response['choices'][0]['message']['content']


