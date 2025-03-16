from abc import abstractmethod

from pydantic import BaseModel, Field
from typing_extensions import List, Union, Any

from dandy.llm.service.request.message import RequestMessage
from dandy.llm.tokens.utils import get_estimated_token_count_for_string


class BaseRequestBody(BaseModel):
    model: str
    messages: List[RequestMessage] = Field(default_factory=list)

    @abstractmethod
    def add_message(
            self,
            role: str,
            content: str,
            images: Union[List[str], None] = None
    ): ...

    @abstractmethod
    def get_context_length(self) -> int: ...

    @abstractmethod
    def get_max_completion_tokens(self) -> int: ...

    @abstractmethod
    def get_seed(self) -> int: ...

    @abstractmethod
    def get_temperature(self) -> float: ...

    @property
    def messages_estimated_tokens(self) -> int:
        return int(sum([get_estimated_token_count_for_string(message.content) for message in self.messages]))

    @abstractmethod
    def set_format_to_json_schema(self, json_schema: dict): ...

    @abstractmethod
    def set_format_to_text(self): ...

