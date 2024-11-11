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
            context_length: Union[int, None] = None,
            max_completion_tokens: Union[int, None] = None,
            seed: Union[int, None] = None,
            temperature: Union[float, None] = None,
    ) -> BaseRequestBody:

        return OllamaRequestBody(
            model=self.model,
            options=OllamaRequestOptions(
                num_ctx=self.context_length if context_length is None else context_length,
                num_predict=self.max_completion_tokens if max_completion_tokens is None else max_completion_tokens,
                seed=self.seed if seed is None else seed,
                temperature=self.temperature if temperature is None else temperature
            )
        )

    def get_response_content(self, response) -> str:
        return response['message']['content']


