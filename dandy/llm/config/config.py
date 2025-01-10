from abc import abstractmethod
from base64 import b64encode

from typing_extensions import List, Union

from dandy.core.url import Url
from dandy.llm.config.options import LlmConfigOptions
from dandy.llm.exceptions import LlmException
from dandy.llm.request.request import BaseRequestBody
from dandy.llm.service import LlmService


class BaseLlmConfig:
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
            connection_retry_count: Union[int, None] = None,
            prompt_retry_count: Union[int, None] = None,
    ):
        if headers is None:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

        if api_key is not None:
            headers["Authorization"] = f'Basic {b64encode(f"Bearer:{api_key}".encode()).decode()}'

        self.url = Url(
            host=host,
            path_parameters=path_parameters,
            query_parameters=query_parameters,
        )

        self.port = port
        self.model = model
        self.headers = headers

        self.options = LlmConfigOptions(
            connection_retry_count=connection_retry_count,
            prompt_retry_count=prompt_retry_count,
            max_input_tokens=max_input_tokens,
            max_output_tokens=max_output_tokens,
            seed=seed,
            randomize_seed=randomize_seed,
            temperature=temperature,
        )

        self.__llm_config_post_init__()

    @abstractmethod
    def __llm_config_post_init__(self):
        ...

    def assistant_str_prompt_to_str(self, user_prompt_str: str) -> str:
        return self.service.assistant_str_prompt_to_str(user_prompt_str=user_prompt_str)

    @abstractmethod
    def get_response_content(self, response) -> str:
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

    def generate_service(
            self,
            llm_options: Union[LlmConfigOptions, None] = None,
    ):
        return LlmService(
            self,
            options=llm_options.merge_to_copy(self.options) if llm_options is not None else self.options,
        )

    @property
    def service(self) -> LlmService:
        return self.generate_service()

    def validate_value(self, value: Union[str, int], value_name: str, value_type: type):
        exception_postfix = f'{self.__class__.__name__}: {value_name}'
        if not isinstance(value, value_type):
            raise LlmException(f'"{exception_postfix}" must be type {value_type}')
        elif value is None:
            raise LlmException(f'"{exception_postfix}" cannot be None')
        elif value == '' or value == 0:
            raise LlmException(f'"{exception_postfix}" cannot be empty')
