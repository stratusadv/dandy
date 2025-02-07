from typing_extensions import Union

from dandy.intel import BaseIntel

from example.pirate.crew.intelligence.intel import CrewIntel


class ShipIntel(BaseIntel):
    name: str
    description: str
    crew: Union[CrewIntel, None] = None