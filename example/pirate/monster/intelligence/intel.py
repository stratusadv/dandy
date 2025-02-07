from typing_extensions import Union

from dandy.intel import BaseIntel

from example.pirate.monster.enums import SeaMonsterType


class SeaMonsterIntel(BaseIntel):
    name: Union[str, None] = None
    type: SeaMonsterType


class SeaMonsterNameIntel(BaseIntel):
    name: str
