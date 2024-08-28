from __future__ import annotations

from abc import ABCMeta
from typing import List, Any

from dandy.bot.bot import Bot


class Workflow(metaclass=ABCMeta):
    bots: List[Bot]

    def process(self, **kwargs: Any) -> Any:
        pass
