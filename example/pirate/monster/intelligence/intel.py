from typing import Union

from dandy.intel import Intel

from example.pirate.monster.enums import SeaMonsterType


class SeaMonsterIntel(Intel):
    name: Union[str, None] = None
    type: SeaMonsterType


class SeaMonsterNameStructureIntel(Intel):
    name: str
