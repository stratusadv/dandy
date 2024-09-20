from time import time
from typing import List

from pydantic import BaseModel, Field


class Event(BaseModel):
    actor: str
    action: str
    data: dict
    time: float = Field(default_factory=time)
