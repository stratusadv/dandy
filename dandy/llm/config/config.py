from dandy.core.config.config import BaseConfig
from dandy.http.intelligence.intel import HttpResponseIntel
from dandy.llm.options.options import LlmOptions
from dandy.llm.request.request import LlmRequestBody


class LlmConfig(BaseConfig):
    type_: str = 'LLM'

    def __post_init__(self):
        self.options = LlmOptions(
            prompt_retry_count=self.get_settings_value('prompt_retry_count'),
            max_completion_tokens=self.get_settings_value('max_completion_tokens'),
            seed=self.get_settings_value('seed'),
            randomize_seed=self.get_settings_value('randomize_seed'),
            temperature=self.get_settings_value('temperature'),
        )

        self.http_request_intel.url.path_parameters = [
            'v1',
            'chat',
            'completions'
        ]

    def generate_request_body(
        self,
    ) -> LlmRequestBody:
        return LlmRequestBody(
            model=self.model,
            max_completion_tokens=self.options.max_completion_tokens,
            seed=self.options.seed,
            temperature=self.options.temperature,
            stream=False,
        )

    @staticmethod
    def get_response_content(response_intel: HttpResponseIntel) -> str:
        return response_intel.json_data['choices'][0]['message']['content']
