from abc import abstractmethod
from typing import Optional, List

from pydantic import BaseModel, Field

from dandy.core.url import Url
from dandy.llm.service import Service
from dandy.llm.request.request import BaseRequestBody

_DEFAULT_SEED = 77
_DEFAULT_TEMPERATURE = 0.7
_DEFAULT_CONNECTION_RETRY_COUNT = 10
_DEFAULT_PROMPT_RETRY_COUNT = 2


class BaseLlmConfig(BaseModel):
    url: Url
    port: int
    model: str
    headers: Optional[dict] = None,
    api_key: Optional[str] = None,
    seed: Optional[int] = _DEFAULT_SEED,
    temperature: float = Field(_DEFAULT_TEMPERATURE, ge=0.0, le=1.0),
    connection_retry_count: int = Field(_DEFAULT_CONNECTION_RETRY_COUNT, ge=1, le=100),
    prompt_retry_count: int = Field(_DEFAULT_PROMPT_RETRY_COUNT, ge=1, le=10),
    request_body: Optional[BaseRequestBody] = None,

    def __init__(
            self,
            host: str,
            port: int,
            model: str,
            path_parameters: Optional[List[str]] = None,
            query_parameters: Optional[dict] = None,
            headers: Optional[dict] = None,
            api_key: Optional[str] = None,
            seed: Optional[int] = _DEFAULT_SEED,
            temperature: float = _DEFAULT_TEMPERATURE,
            connection_retry_count: int = _DEFAULT_CONNECTION_RETRY_COUNT,
            prompt_retry_count: int = _DEFAULT_PROMPT_RETRY_COUNT,
            request_body: Optional[BaseRequestBody] = None,
    ):
        if headers is None:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

        if api_key is not None:
            headers["Authorization"] = f"Bearer {api_key}"

        super().__init__(
            url=Url(
                host=host,
                path_parameters=path_parameters,
                query_parameters=query_parameters,
            ),
            port=port,
            model=model,
            headers=headers,
            connection_retry_count=connection_retry_count,
            prompt_retry_count=prompt_retry_count,
            seed=seed,
            temperature=temperature,
            request_body=request_body,
        )

        self.__llm_config_post_init__()

    @abstractmethod
    def __llm_config_post_init__(self):
        ...

    @property
    def service(self):
        return Service(self)

    @abstractmethod
    def get_response_content(self, response) -> str:
        ...


