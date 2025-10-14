
from dandy.http.intelligence.intel import HttpResponseIntel
from dandy.llm.config.config import BaseLlmConfig
from dandy.llm.request.ollama import OllamaRequestBody, OllamaRequestOptions
from dandy.llm.request.request import BaseRequestBody


class OllamaLlmConfig(BaseLlmConfig):
    def __llm_config_post_init__(self):
        self.http_request_intel.url.path_parameters = [
            'api',
            'chat',
        ]

    def generate_request_body(
        self,
        max_input_tokens: int | None = None,
        max_output_tokens: int | None = None,
        seed: int | None = None,
        temperature: float | None = None,
    ) -> BaseRequestBody:
        return OllamaRequestBody(
            model=self.model,
            options=OllamaRequestOptions(
                num_ctx=self.options.max_input_tokens
                if max_input_tokens is None
                else max_input_tokens,
                num_predict=self.options.max_output_tokens
                if max_output_tokens is None
                else max_output_tokens,
                seed=self.options.seed if seed is None else seed,
                temperature=self.options.temperature
                if temperature is None
                else temperature,
            ),
        )

    @staticmethod
    def get_response_content(response_intel: HttpResponseIntel) -> str:
        return response_intel.json_data['message']['content']


