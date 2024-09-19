from typing import List, Optional

from pydantic import BaseModel

from dandy.llm.request.request import BaseRequestBody


_JSON_FORMAT = 'json'
_TEXT_FORMAT = 'text'


class OllamaRequestOptions(BaseModel):
    seed: Optional[int] = None
    temperature: Optional[float] = None


class OllamaRequestBody(BaseRequestBody):
    options: OllamaRequestOptions
    stream: bool = False
    format: str = _JSON_FORMAT


    def set_format_to_json(self):
        self.format = _JSON_FORMAT

    def set_format_to_text(self):
        self.format = _TEXT_FORMAT