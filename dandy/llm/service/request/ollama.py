from typing_extensions import Union

from pydantic import BaseModel

from dandy.llm.service.request.request import BaseRequestBody


class OllamaRequestOptions(BaseModel):
    num_ctx: Union[int, None] = None
    num_predict: Union[int, None] = None
    seed: Union[int, None] = None
    temperature: Union[float, None] = None


class OllamaRequestBody(BaseRequestBody):
    options: OllamaRequestOptions
    stream: bool = False
    format: Union[dict, None] = {}

    def get_context_length(self) -> int:
        return self.options.num_ctx

    def get_max_completion_tokens(self) -> int:
        return self.options.num_predict

    def get_seed(self):
        return self.options.seed

    def get_temperature(self):
        return self.options.temperature

    def set_format_to_json_schema(self, json_schema: dict):
        self.format = json_schema

    def set_format_to_text(self):
        self.format = None