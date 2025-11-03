from typing import ClassVar

from dandy.core.service.mixin import BaseServiceMixin
from dandy.vision.service import VisionService


class VisionServiceMixin(BaseServiceMixin):
    vision_config: str = 'DEFAULT'

    vision: ClassVar[VisionService] = VisionService()
    _VisionService_instance: VisionService | None = None

    def reset_services(self):
        super().reset_services()
