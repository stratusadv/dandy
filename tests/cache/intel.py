from dandy.intel.intel import BaseIntel


class WigIntel(BaseIntel):
    color: str


class ClownIntel(BaseIntel):
    name: str
    juggles: bool
    wig: WigIntel


class CandyNotIntel:
    def __init__(self, sweetness: int):
        self.sweetness = sweetness


