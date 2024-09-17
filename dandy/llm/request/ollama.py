from typing import List, Optional

from pydantic import BaseModel

from dandy.llm.request.request import BaseRequestBody


_JSON_FORMAT = 'json'
_TEXT_FORMAT = 'text'


class OllamaRequestOptions(BaseModel):
    numkeep: Optional[int] = None
    seed: Optional[int] = None
    numpredict: Optional[int] = None
    topk: Optional[int] = None
    topp: Optional[float] = None
    minp: Optional[int] = None
    tfsz: Optional[float] = None
    typicalp: Optional[float] = None
    repeatlastn: Optional[int] = None
    temperature: Optional[float] = None
    repeatpenalty: Optional[float] = None
    presencepenalty: Optional[float] = None
    frequencypenalty: Optional[int] = None
    mirostat: Optional[int] = None
    mirostattau: Optional[float] = None
    mirostateta: Optional[float] = None
    penalizenewline: Optional[bool] = None
    stop: Optional[List[str]] = None
    numa: Optional[bool] = None
    numctx: Optional[int] = None
    numbatch: Optional[int] = None
    numgpu: Optional[int] = None
    maingpu: Optional[int] = None
    lowvram: Optional[bool] = None
    f16kv: Optional[bool] = None
    vocabonly: Optional[bool] = None
    usemmap: Optional[bool] = None
    usemlock: Optional[bool] = None
    numthread: Optional[int] = None


class OllamaRequestBody(BaseRequestBody):
    options: OllamaRequestOptions
    stream: bool = False
    format: str = _JSON_FORMAT


    def set_format_to_json(self):
        self.format = _JSON_FORMAT

    def set_format_to_text(self):
        self.format = _TEXT_FORMAT