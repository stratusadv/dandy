from dataclasses import dataclass
from typing import ClassVar

from dandy.core.service.mixin import BaseServiceMixin
from dandy.vision.service.service import VisionService


@dataclass(kw_only=True)
class VisionProcessorMixin(BaseServiceMixin):
    vision_config: str = 'DEFAULT'

    vision: ClassVar[VisionService] = VisionService()
    _VisionService_instance: VisionService | None = None
