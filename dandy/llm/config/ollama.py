from dandy.llm.config import BaseLlmConfig
from dandy.llm.request.ollama import OllamaRequestBody, OllamaRequestOptions


class OllamaLlmConfig(BaseLlmConfig):
    def __llm_config_post_init__(self):
        self.url.path_parameters = [
            'api',
            'chat',
        ]

        self.request_body = OllamaRequestBody(
            model=self.model,
            options=OllamaRequestOptions(
                seed=self.seed,
                temperature=self.temperature
            )
        )

    def get_response_content(self, response) -> str:
        return response['message']['content']


