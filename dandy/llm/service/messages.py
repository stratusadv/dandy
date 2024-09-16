from pydantic import BaseModel


class ServiceMessage(BaseModel):
    role: str
    content: str