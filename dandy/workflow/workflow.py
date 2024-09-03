from __future__ import annotations

from abc import ABC
from typing import List, Any

from dandy.bot.bot import Bot
from dandy.handler.handler import Handler


class Workflow(Handler, ABC):
    ...
