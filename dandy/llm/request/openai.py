from typing_extensions import Union

from dandy.llm.request.request import BaseRequestBody


_JSON_RESPONSE_FORMAT = {'type': 'json_object'}
_TEXT_RESPONSE_FORMAT = {'type': 'text'}


class OpenaiRequestBody(BaseRequestBody):
    stream: bool = False
    response_format: dict = _JSON_RESPONSE_FORMAT
    seed: Union[int, None] = None
    temperature: Union[float, None] = None

    def get_temperature(self) -> float:
        return self.temperature

    def set_format_to_json(self):
        self.response_format = _JSON_RESPONSE_FORMAT

    def set_format_to_text(self):
        self.response_format = _TEXT_RESPONSE_FORMAT