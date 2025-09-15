from typing import List

from dandy.intel.intel import BaseIntel


class LocationIntel(BaseIntel):
    name: str
    description: str
    

class WorldIntel(BaseIntel):
    name: str
    description: str
    locations: List[LocationIntel]