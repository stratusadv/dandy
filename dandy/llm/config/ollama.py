from typing_extensions import Union

from dandy.llm.config import BaseLlmConfig
from dandy.llm.request.ollama import OllamaRequestBody, OllamaRequestOptions
from dandy.llm.request.request import BaseRequestBody


class OllamaLlmConfig(BaseLlmConfig):
    def __llm_config_post_init__(self):
        self.url.path_parameters = [
            'api',
            'chat',
        ]

    def generate_request_body(
            self,
            max_input_tokens: Union[int, None] = None,
            max_output_tokens: Union[int, None] = None,
            seed: Union[int, None] = None,
            temperature: Union[float, None] = None,
    ) -> BaseRequestBody:

        return OllamaRequestBody(
            model=self.model,
            options=OllamaRequestOptions(
                num_ctx=self.max_input_tokens if max_input_tokens is None else max_input_tokens,
                num_predict=self.max_output_tokens if max_output_tokens is None else max_output_tokens,
                seed=self.seed if seed is None else seed,
                temperature=self.temperature if temperature is None else temperature
            )
        )

    def get_response_content(self, response) -> str:
        return response['message']['content']


