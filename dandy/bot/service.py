from __future__ import annotations

from typing import TYPE_CHECKING

from dandy.service.llm.service import LlmService
from dandy.service.service import BaseService

if TYPE_CHECKING:
    from dandy.bot import BaseBot

class BotService(BaseService['BaseBot']):
    obj: BaseBot
    llm: LlmService = LlmService()