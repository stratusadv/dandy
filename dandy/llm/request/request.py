from abc import abstractmethod
from typing_extensions import List

from pydantic import BaseModel, Field

from dandy.llm.request.message import RequestMessage
from dandy.llm.utils import str_to_token_count


class BaseRequestBody(BaseModel):
    model: str
    messages: List[RequestMessage] = Field(default_factory=list)

    def add_message(self, role: str, content: str) -> None:
        self.messages.append(RequestMessage(role=role, content=content))

    @abstractmethod
    def get_temperature(self) -> float: ...

    @property
    def messages_estimated_tokens(self) -> int:
        return int(sum([str_to_token_count(message.content) for message in self.messages]))

    @abstractmethod
    def set_format_to_json(self): ...

    @abstractmethod
    def set_format_to_text(self): ...

