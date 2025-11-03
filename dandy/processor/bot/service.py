from __future__ import annotations

from typing import TYPE_CHECKING

from dandy.core.service.service import BaseService

if TYPE_CHECKING:
    from dandy.processor.bot.bot import Bot

class BotService(BaseService['Bot']):
    obj: Bot

    def reset_service(self):
        pass
