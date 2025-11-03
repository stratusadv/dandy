from __future__ import annotations

from typing import TYPE_CHECKING

from dandy.core.service.service import BaseService

if TYPE_CHECKING:
    from dandy.processor.decoder.decoder import Decoder

class DecoderService(BaseService['Decoder']):
    obj: Decoder

    def reset_service(self):
        pass
