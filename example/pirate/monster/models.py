from enum import Enum
from typing import Union

from pydantic import BaseModel


class SeaMonsterType(Enum):
    KRAKEN = "Kraken"
    SEA_SERPENT = "Sea Serpent"
    LEVIATHAN = "Leviathan"
    HYDRA = "Hydra"
    CTHULHU = "Cthulhu"

class SeaMonsterIntel(BaseModel):
    name: Union[str, None] = None
    type: SeaMonsterType


class SeaMonsterNameStructureIntel(BaseModel):
    name: str
