from abc import ABC

from dandy.bot.service import BotService
from dandy.http.mixin import HttpProcessorMixin
from dandy.llm.mixin import LlmProcessorMixin
from dandy.core.processor.processor import BaseProcessor
from dandy.vision.mixin import VisionProcessorMixin


class BaseBot(
    BaseProcessor,
    ABC,
    LlmProcessorMixin,
    HttpProcessorMixin,
    VisionProcessorMixin,
):
    bot: BotService = BotService()

