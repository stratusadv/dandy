from dandy.llm.config import BaseLlmConfig
from dandy.llm.request.openai import OpenaiRequestBody


class OpenaiLlmConfig(BaseLlmConfig):
    def __llm_config_post_init__(self):
        self.url.path_parameters = [
            'v1',
            'chat',
            'completions',
        ]

        self.request_body = OpenaiRequestBody(
            model=self.model,
            seed=self.seed,
            temperature=self.temperature
        )

    def get_response_content(self, response) -> str:
        return response['choices'][0]['message']['content']