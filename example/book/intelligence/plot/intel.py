from typing_extensions import List

from dandy.intel import BaseIntel


class PlotStructureIntel(BaseIntel):
    steps: List[str]
    descriptions: List[str]