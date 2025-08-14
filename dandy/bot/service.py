from __future__ import annotations

from typing import TYPE_CHECKING

from dandy.core.service.service import BaseService

if TYPE_CHECKING:
    from dandy.bot import BaseBot

class BotService(BaseService['BaseBot']):
    obj: BaseBot
