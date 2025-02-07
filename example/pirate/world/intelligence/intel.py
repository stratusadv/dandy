from typing_extensions import List

from dandy.intel import BaseIntel


class IslandIntel(BaseIntel):
    name: str
    description: str
    size: int


class OceanIntel(BaseIntel):
    name: str
    description: str
    size: int
    depth: int
    islands: List[IslandIntel]

