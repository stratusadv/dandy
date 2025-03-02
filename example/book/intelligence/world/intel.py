from typing_extensions import List

from dandy.intel import BaseIntel


class Location(BaseIntel):
    name: str
    description: str
    

class World(BaseIntel):
    name: str
    description: str
    locations: List[Location]