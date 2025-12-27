from typing import List, Any, Literal

from pydantic import BaseModel, Field

RoleLiteralStr = Literal['user', 'assistant', 'system']


class RequestMessage(BaseModel):
    role: RoleLiteralStr
    content: str | List[Any]
    images: List[str] |None = None

    def content_as_str(self) -> str:
        if self.content[0]['type'] == 'text':
            return self.content[0]['text']

        if self.content[0]['type'] == 'image_url':
            return self.content[0]['image_url']['url'].split(';base64,')[1]

        return self.content


class MessageHistory(BaseModel):
    messages: List[RequestMessage] = Field(default_factory=list)

    def add_message(
            self,
            role: RoleLiteralStr,
            content: str,
            images: List[str] | None = None
    ) -> None:
        self.messages.append(
            RequestMessage(
                role=role,
                content=content,
                images=images
            )
        )
