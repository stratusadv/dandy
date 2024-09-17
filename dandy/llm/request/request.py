from abc import abstractmethod
from random import randint
from typing import List

from pydantic import BaseModel, Field

from dandy.llm.request.message import RequestMessage


class BaseRequestBody(BaseModel):
    model: str
    messages: List[RequestMessage] = Field(default_factory=list)

    def add_message(self, role: str, content: str) -> None:
        self.messages.append(RequestMessage(role=role, content=content))

    @abstractmethod
    def set_format_to_json(self): ...

    @abstractmethod
    def set_format_to_text(self): ...