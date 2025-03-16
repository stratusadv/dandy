from pydantic import BaseModel
from typing_extensions import List, Union, Any


class RequestMessage(BaseModel):
    role: str
    content: Union[str, List[Any]]
    images: Union[List[str], None] = None
