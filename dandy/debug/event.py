from time import time
from typing import List

from pydantic import BaseModel


class Event(BaseModel):
    actor: str
    action: str
    time: float
    data: dict
