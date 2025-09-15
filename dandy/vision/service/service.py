from __future__ import annotations

from typing import TYPE_CHECKING

from dandy.core.service.service import BaseService

if TYPE_CHECKING:
    from dandy.vision.mixin import VisionProcessorMixin


class VisionService(BaseService['VisionProcessorMixin']):
    obj: VisionProcessorMixin

    def image_to_intel(self):
        pass