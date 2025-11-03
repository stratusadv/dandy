from __future__ import annotations

from typing import TYPE_CHECKING

from dandy.core.service.service import BaseService

if TYPE_CHECKING:
    from dandy.vision.mixin import VisionServiceMixin


class VisionService(BaseService['VisionProcessorMixin']):
    obj: VisionServiceMixin

    def image_to_intel(self):
        pass

    def reset_service(self):
        pass
