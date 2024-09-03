from abc import ABC, abstractmethod
from typing import Any

from dandy.handler.handler import Handler


class Bot(Handler, ABC):
    ...