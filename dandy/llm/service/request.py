from random import randint
from typing import List

from pydantic import BaseModel, Field

from dandy.llm.service.messages import ServiceMessage


class BaseRequest(BaseModel):
    model: str
    messages: List[ServiceMessage] = Field(default_factory=list)
    stream: bool = False
    format: str = 'json'
    temperature: float = 0.7
    seed: int = Field(default_factory=lambda: randint(0, 99999))

    def add_message(self, role: str, content: str) -> None:
        self.messages.append(ServiceMessage(role=role, content=content))
