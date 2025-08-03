from abc import ABC

from dandy.bot.service import BotService
from dandy.processor.processor import BaseProcessor


class BaseBot(BaseProcessor, ABC):
    services: BotService = BotService()

