from dandy import BaseIntel


class ImageIntel(BaseIntel):
    people_count: int


class ImageCompareIntel(BaseIntel):
    description: str
    changes: str