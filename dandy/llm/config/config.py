from typing import List

from dandy.core.config.config import BaseConfig
from dandy.http.intelligence.intel import HttpRequestIntel, HttpResponseIntel
from dandy.http.url import Url
from dandy.llm.config.options import LlmConfigOptions
from dandy.llm.request.request import RequestBody


class LlmConfig(BaseConfig):
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

        self.http_request_intel.url.path_parameters = [
            'v1',
            'chat',
            'completions'
        ]

    def generate_request_body(
        self,
        max_input_tokens: int | None = None,
        max_output_tokens: int | None = None,
        seed: int | None = None,
        temperature: float | None = None,
    ) -> RequestBody:
        return RequestBody(
            model=self.model,
            max_completion_tokens=self.options.max_output_tokens
            if max_output_tokens is None
            else max_output_tokens,
            seed=self.options.seed if seed is None else seed,
            temperature=self.options.temperature
            if temperature is None
            else temperature,
            stream=False,
            response_format={
                'type': 'json_schema',
                'json_schema': {'name': 'response', 'strict': False, 'schema': ...},
            },
        )

    @staticmethod
    def get_response_content(response_intel: HttpResponseIntel) -> str:
        return response_intel.json_data['choices'][0]['message']['content']
