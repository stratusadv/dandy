from abc import abstractmethod
from base64 import b64encode
from typing_extensions import List, Union, TYPE_CHECKING

from pydantic import BaseModel, Field, field_validator

from dandy.core.url import Url
from dandy.llm.exceptions import LlmException
from dandy.llm.service import Service
from dandy.llm.request.request import BaseRequestBody

_DEFAULT_CONTEXT_LENGTH = 4096
_DEFAULT_MAX_COMPLETION_TOKENS = 1024
_DEFAULT_SEED = 77
_DEFAULT_TEMPERATURE = 0.7
_DEFAULT_CONNECTION_RETRY_COUNT = 10
_DEFAULT_PROMPT_RETRY_COUNT = 2


class BaseLlmConfig(BaseModel):
    url: Url
    port: int
    model: str
    headers: Union[dict, None] = None,
    api_key: Union[str, None] = None,
    seed: Union[int, None] = _DEFAULT_SEED,
    max_input_tokens: int = Field(_DEFAULT_CONTEXT_LENGTH, ge=0, le=128_000)
    max_output_tokens: int = Field(_DEFAULT_MAX_COMPLETION_TOKENS, ge=0, le=128_000)
    temperature: float = Field(_DEFAULT_TEMPERATURE, ge=0.0, le=1.0)
    connection_retry_count: int = Field(_DEFAULT_CONNECTION_RETRY_COUNT, ge=1, le=100)
    prompt_retry_count: int = Field(_DEFAULT_PROMPT_RETRY_COUNT, ge=1, le=10)

    def __init__(
            self,
            host: str,
            port: int,
            model: str,
            path_parameters: Union[List[str], None] = None,
            query_parameters: Union[dict, None] = None,
            headers: Union[dict, None] = None,
            api_key: Union[str, None] = None,
            max_input_tokens: int = _DEFAULT_CONTEXT_LENGTH,
            max_output_tokens: int = _DEFAULT_MAX_COMPLETION_TOKENS,
            seed: Union[int, None] = _DEFAULT_SEED,
            temperature: float = _DEFAULT_TEMPERATURE,
            connection_retry_count: int = _DEFAULT_CONNECTION_RETRY_COUNT,
            prompt_retry_count: int = _DEFAULT_PROMPT_RETRY_COUNT,
            request_body: Union[BaseRequestBody, None] = None,
    ):
        if headers is None:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

        if api_key is not None:
            headers["Authorization"] = f'Basic {b64encode(f"Bearer:{api_key}".encode()).decode()}'

        self.validate_value(host, 'host', str)
        self.validate_value(port, 'port', int)
        self.validate_value(model, 'model', str)

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
            max_input_tokens=max_input_tokens,
            max_output_tokens=max_output_tokens,
            seed=seed,
            temperature=temperature,
            request_body=request_body,
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
            max_input_tokens: Union[int, None] = None,
            max_output_tokens: Union[int, None] = None,
            seed: Union[int, None] = None,
            temperature: Union[float, None] = None,
    ) -> Service:

        return Service(
            self,
            max_input_tokens=max_input_tokens,
            max_output_tokens=max_output_tokens,
            seed=seed,
            temperature=temperature,
        )

    @property
    def service(self) -> Service:
        return self.generate_service()

    def validate_value(self, value: Union[str, int], value_name: str, value_type: type):
        exception_postfix = f'{self.__class__.__name__}: {value_name}'
        if not isinstance(value, value_type):
            raise LlmException(f'"{exception_postfix}" must be type {value_type}')
        elif value is None:
            raise LlmException(f'"{exception_postfix}" cannot be None')
        elif value == '' or value == 0:
            raise LlmException(f'"{exception_postfix}" cannot be empty')
