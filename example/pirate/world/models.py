from typing_extensions import List

from pydantic import BaseModel


class Island(BaseModel):
    name: str
    description: str
    size: int


class Ocean(BaseModel):
    name: str
    description: str
    size: int
    depth: int
    islands: List[Island]

