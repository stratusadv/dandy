from dandy.core.service.mixin import BaseServiceMixin
from dandy.llm.decoder.service import DecoderService


class DecoderServiceMixin(BaseServiceMixin):
    @property
    def decoder(self) -> DecoderService:
        return self._get_service_instance(DecoderService)

    def reset(self):
        super().reset()
        self.decoder.reset()
