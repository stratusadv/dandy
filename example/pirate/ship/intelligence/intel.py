from pydantic import BaseModel
from typing_extensions import Union

from example.pirate.crew.intelligence.intel import CrewIntel


class ShipIntel(BaseModel):
    name: str
    description: str
    crew: Union[CrewIntel, None] = None