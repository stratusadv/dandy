from abc import abstractmethod
from typing import List, Union

from dandy.core.config.config import BaseConfig
from dandy.http.config import HttpConnectorConfig
from dandy.http.url import Url
from dandy.llm.config.options import LlmConfigOptions
from dandy.llm.request.request import BaseRequestBody


class BaseLlmConfig(BaseConfig):
    def __init__(
            self,
            host: str,
            port: int,
            model: str,
            path_parameters: Union[List[str], None] = None,
            query_parameters: Union[dict, None] = None,
            headers: Union[dict, None] = None,
            api_key: Union[str, None] = None,
            seed: Union[int, None] = None,
            randomize_seed: Union[bool, None] = None,
            max_input_tokens: Union[int, None] = None,
            max_output_tokens: Union[int, None] = None,
            temperature: Union[float, None] = None,
            prompt_retry_count: Union[int, None] = None,
    ):

        self.http_config = HttpConnectorConfig(
            url=Url(
                host=host,
                port=port,
                path_parameters=path_parameters,
                query_parameters=query_parameters,
            ),
            headers=headers,
            basic_auth=api_key,
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
    def get_response_content(response) -> str:
        ...

    @abstractmethod
    def generate_request_body(
            self,
            max_input_tokens: Union[int, None] = None,
            max_output_tokens: Union[int, None] = None,
            seed: Union[int, None] = None,
            temperature: Union[float, None] = None,
    ) -> BaseRequestBody:
        ...