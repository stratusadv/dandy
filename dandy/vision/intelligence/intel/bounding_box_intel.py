# from pydantic import Field
#
# from dandy import BaseIntel, BaseListIntel
#
#
# class BoundingBoxIntel(BaseIntel):
#     rectangle_coordinates: list[int]
#     label: str
#
#
# class BoundingBoxesIntel(BaseListIntel[BoundingBoxIntel]):
#     bounding_boxes: list[BoundingBoxIntel] = Field(default_factory=list)
