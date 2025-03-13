from typing_extensions import Union

from dandy.llm.service.config import BaseLlmConfig
from dandy.llm.service.request.openai import OpenaiRequestBody
from dandy.llm.service.request.request import BaseRequestBody


class OpenaiLlmConfig(BaseLlmConfig):
    def __llm_config_post_init__(self):
        self.http_config.url.path_parameters = [
            'v1',
            'chat',
            'completions',
        ]

    def generate_request_body(
            self,
            max_input_tokens: Union[int, None] = None,
            max_output_tokens: Union[int, None] = None,
            seed: Union[int, None] = None,
            temperature: Union[float, None] = None,
    ) -> BaseRequestBody:

        return OpenaiRequestBody(
            model=self.model,
            max_completion_tokens=self.options.max_output_tokens if max_output_tokens is None else max_output_tokens,
            seed=self.options.seed if seed is None else seed,
            temperature=self.options.temperature if temperature is None else temperature,
        )

    def get_response_content(self, response) -> str:
        return response['choices'][0]['message']['content']