from __future__ import annotations

from typing import TYPE_CHECKING

from dandy.core.service.service import BaseService


if TYPE_CHECKING:
    from dandy.processor.processor import BaseProcessor


class VisionService(BaseService['BaseProcessor']):
    obj: BaseProcessor

    def image_to_intel(self):
        pass