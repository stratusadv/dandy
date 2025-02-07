from pydantic import BaseModel


class RequestMessage(BaseModel):
    role: str
    content: str