from dandy.http.intelligence.intel import HttpResponseIntel
from dandy.llm.config.config import BaseLlmConfig
from dandy.llm.request.openai import OpenaiRequestBody
from dandy.llm.request.request import BaseRequestBody


class OpenaiLlmConfig(BaseLlmConfig):
    def __llm_config_post_init__(self):
        self.http_request_intel.url.path_parameters = [
            'v1',
            'chat',
            'completions',
        ]

    def generate_request_body(
        self,
        max_input_tokens: int | None = None,
        max_output_tokens: int | None = None,
        seed: int | None = None,
        temperature: float | None = None,
    ) -> BaseRequestBody:
        return OpenaiRequestBody(
            model=self.model,
            max_completion_tokens=self.options.max_output_tokens
            if max_output_tokens is None
            else max_output_tokens,
            seed=self.options.seed if seed is None else seed,
            temperature=self.options.temperature
            if temperature is None
            else temperature,
        )

    @staticmethod
    def get_response_content(response_intel: HttpResponseIntel) -> str:
        return response_intel.json_data['choices'][0]['message']['content']
