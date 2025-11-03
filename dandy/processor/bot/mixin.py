from typing import ClassVar

from dandy.core.service.mixin import BaseServiceMixin
from dandy.processor.bot.service import BotService


class BotServiceMixin(BaseServiceMixin):
    services: ClassVar[BotService] = BotService()
    _BotService_instance: BotService | None = None

    def reset_services(self):
        super().reset_services()
        self.services.reset_service()
