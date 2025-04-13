from pydantic import BaseModel, Field
from typing_extensions import List, Union, Any, Literal

RoleLiteralStr = Literal['user', 'assistant', 'system']

class RequestMessage(BaseModel):
    role: RoleLiteralStr
    content: Union[str, List[Any]]
    images: Union[List[str], None] = None


class MessageHistory(BaseModel):
    messages: List[RequestMessage] = Field(default_factory=list)

    def add_message(
            self,
            role: RoleLiteralStr,
            content: str,
            images: Union[List[str], None] = None
    ) -> None:
        self.messages.append(
            RequestMessage(
                role=role,
                content=content,
                images=images
            )
        )