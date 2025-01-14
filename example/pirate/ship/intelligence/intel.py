from typing_extensions import Union

from dandy.intel import Intel

from example.pirate.crew.intelligence.intel import CrewIntel


class ShipIntel(Intel):
    name: str
    description: str
    crew: Union[CrewIntel, None] = None