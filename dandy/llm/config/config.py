from abc import abstractmethod, ABC
from typing import List

from dandy.core.config.config import BaseConfig
from dandy.http.intelligence.intel import HttpRequestIntel, HttpResponseIntel
from dandy.http.url import Url
from dandy.llm.config.options import LlmConfigOptions
from dandy.llm.request.request import BaseRequestBody


class BaseLlmConfig(BaseConfig, ABC):
    def __init__(
            self,
            host: str,
            port: int,
            model: str,
            path_parameters: List[str] | None = None,
            query_parameters: dict | None = None,
            headers: dict | None = None,
            api_key: str | None = None,
            seed: int | None = None,
            randomize_seed: bool | None = None,
            max_input_tokens: int | None = None,
            max_output_tokens: int | None = None,
            temperature: float | None = None,
            prompt_retry_count: int | None = None,
    ):

        self.http_request_intel = HttpRequestIntel(
            method='POST',
            url=Url(
                host=host,
                port=port,
                path_parameters=path_parameters,
                query_parameters=query_parameters,
            ),
            headers=headers,
            bearer_token=api_key,
        )

        self.model = model

        self.options = LlmConfigOptions(
            prompt_retry_count=prompt_retry_count,
            max_input_tokens=max_input_tokens,
            max_output_tokens=max_output_tokens,
            seed=seed,
            randomize_seed=randomize_seed,
            temperature=temperature,
        )

        self.register_settings(
            'host',
            'port',
            'model',
            'path_parameters',
            'query_parameters',
            'headers',
            'api_key',
            'seed',
            'randomize_seed',
            'max_input_tokens',
            'max_output_tokens',
            'temperature',
            'prompt_retry_count',
        )

        self.__llm_config_post_init__()

    @abstractmethod
    def __llm_config_post_init__(self):
        ...

    @staticmethod
    @abstractmethod
    def get_response_content(response_intel: HttpResponseIntel) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_request_body(
            self,
            max_input_tokens: int | None = None,
            max_output_tokens: int | None = None,
            seed: int | None = None,
            temperature: float | None = None,
    ) -> BaseRequestBody:
        ...
