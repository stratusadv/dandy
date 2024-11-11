from typing_extensions import List, Union

from pydantic import BaseModel

from dandy.llm.request.request import BaseRequestBody


_JSON_FORMAT = 'json'
_TEXT_FORMAT = 'text'


class OllamaRequestOptions(BaseModel):
    num_ctx: Union[int, None] = None
    num_predict: Union[int, None] = None
    seed: Union[int, None] = None
    temperature: Union[float, None] = None


class OllamaRequestBody(BaseRequestBody):
    options: OllamaRequestOptions
    stream: bool = False
    format: str = _JSON_FORMAT

    def get_context_length(self) -> int:
        return self.options.num_ctx

    def get_max_completion_tokens(self) -> int:
        return self.options.num_predict

    def get_temperature(self):
        return self.options.temperature

    def set_format_to_json(self):
        self.format = _JSON_FORMAT

    def set_format_to_text(self):
        self.format = _TEXT_FORMAT