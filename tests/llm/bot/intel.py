from typing_extensions import Union, List

from dandy.intel import BaseIntel


class GemIntel(BaseIntel):
    name: str
    value: float
    quality: str | None = None


class MoneyBagIntel(BaseIntel):
    coins: int
    bills: int | None = None
    gems: Union[List[GemIntel], None] = None