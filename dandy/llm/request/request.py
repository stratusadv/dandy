from abc import abstractmethod, ABC

from pydantic import BaseModel, Field

from dandy.llm.request.message import RequestMessage, RoleLiteralStr


class BaseRequestBody(BaseModel, ABC):
    model: str
    messages: list[RequestMessage] = Field(default_factory=list)

    @property
    def has_system_message(self) -> bool:
        return len(self.messages) > 0 and self.messages[0].role == 'system'

    @abstractmethod
    def add_message(
        self, role: RoleLiteralStr, content: str, images: list[str] | None = None, prepend: bool = False
    ): ...

    @abstractmethod
    def get_context_length(self) -> int: ...

    @abstractmethod
    def get_max_completion_tokens(self) -> int: ...

    @abstractmethod
    def get_seed(self) -> int: ...

    @abstractmethod
    def get_temperature(self) -> float: ...

    def reset_messages(self):
        self.messages = []

    @property
    @abstractmethod
    def token_usage(self) -> int:
        pass

    def get_total_context_length(self) -> int:
        return self.get_context_length() + self.get_max_completion_tokens()

    @abstractmethod
    def set_format_to_json_schema(self, json_schema: dict): ...

    @abstractmethod
    def set_format_to_text(self): ...

    @abstractmethod
    def to_dict(self): ...

