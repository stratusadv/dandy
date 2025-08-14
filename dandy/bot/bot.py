from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from dandy.bot.service import BotService
from dandy.http.mixin import HttpProcessorMixin
from dandy.processor.processor import BaseProcessor
from dandy.llm.mixin import LlmProcessorMixin
from dandy.llm.service.llm_service import LlmService


class BaseBot(
    BaseProcessor,
    ABC,
    LlmProcessorMixin,
    HttpProcessorMixin,
):
    services: BotService = BotService()

