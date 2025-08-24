from typing import Union, List

from dandy.intel import BaseIntel


class GemIntel(BaseIntel):
    name: str
    value: float
    quality: str | None = None


class MoneyBagIntel(BaseIntel):
    coins: int
    bills: int | None = None
    gems: List[GemIntel] | None = None