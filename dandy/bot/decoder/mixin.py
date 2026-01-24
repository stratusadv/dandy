from typing import ClassVar

from dandy.core.service.mixin import BaseServiceMixin
from dandy.processor.decoder.service import DecoderService


class DecoderServiceMixin(BaseServiceMixin):
    services: ClassVar[DecoderService] = DecoderService()
    _DecoderService_instance: DecoderService | None = None

    def reset_services(self):
        super().reset_services()
        self.services.reset_service()
