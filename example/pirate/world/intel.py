from typing_extensions import List

from pydantic import BaseModel


class IslandIntel(BaseModel):
    name: str
    description: str
    size: int


class OceanIntel(BaseModel):
    name: str
    description: str
    size: int
    depth: int
    islands: List[IslandIntel]

