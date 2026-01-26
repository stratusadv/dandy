from typing import ClassVar

from dandy.core.service.mixin import BaseServiceMixin
from dandy.llm.decoder.service import DecoderService


class DecoderServiceMixin(BaseServiceMixin):
    @property
    def decoder(self) -> DecoderService:
        return self._get_service_instance(DecoderService)

    def reset_services(self):
        super().reset_services()
        self.decoder.reset_service()
