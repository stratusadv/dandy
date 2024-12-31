from typing import Union

from pydantic import BaseModel

from example.pirate.monster.enums import SeaMonsterType


class SeaMonsterIntel(BaseModel):
    name: Union[str, None] = None
    type: SeaMonsterType


class SeaMonsterNameStructureIntel(BaseModel):
    name: str
