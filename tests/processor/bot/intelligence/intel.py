
from dandy import BaseIntel
from dandy.intel.intel import BaseIntel


class GemIntel(BaseIntel):
    name: str
    value: float
    quality: str | None = None


class MoneyBagIntel(BaseIntel):
    coins: int
    bills: int | None = None
    gems: list[GemIntel] | None = None


class HappyIntel(BaseIntel):
    description: str
    happy_level: int


class SadIntel(BaseIntel):
    description: str
    sad_level: int
