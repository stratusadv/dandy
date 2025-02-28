from typing_extensions import Union

from dandy.llm.service.request.request import BaseRequestBody


class OpenaiRequestBody(BaseRequestBody):
    stream: bool = False
    response_format: dict = { type: 'json_schema', 'json_schema': {'strict': True, 'schema': ...} }
    max_completion_tokens: Union[int, None] = None
    seed: Union[int, None] = None
    temperature: Union[float, None] = None

    def get_context_length(self) -> int:
        return 0

    def get_max_completion_tokens(self) -> int:
        return self.max_completion_tokens

    def get_seed(self) -> int:
        return self.seed

    def get_temperature(self) -> float:
        return self.temperature

    def set_format_to_json_schema(self, json_schema: dict):
        self.response_format['json_schema']['schema'] = json_schema

    def set_format_to_text(self):
        self.response_format = {'type': 'text'}