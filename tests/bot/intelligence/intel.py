
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
    sentence: str
    happy_level: int


class SadIntel(BaseIntel):
    sentence: str
    sad_level: int
