from typing_extensions import List

from dandy.intel import Intel


class IslandIntel(Intel):
    name: str
    description: str
    size: int


class OceanIntel(Intel):
    name: str
    description: str
    size: int
    depth: int
    islands: List[IslandIntel]

