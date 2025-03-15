from pydantic import BaseModel
from typing_extensions import List, Union


class RequestMessage(BaseModel):
    role: str
    content: str
    images: Union[List[str], None] = None
