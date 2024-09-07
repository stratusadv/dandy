from typing import List

from pydantic import BaseModel, Field


class ServiceMessage(BaseModel):
    role: str
    content: str


class ServiceMessages(BaseModel):
    messages: List[ServiceMessage] = Field(default_factory=list)

    def add(self, role: str, content: str) -> None:
        self.messages.append(ServiceMessage(role=role, content=content))

    def model_dump_list(self) -> List[str]:
        return self.model_dump()['messages']