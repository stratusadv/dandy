from abc import abstractmethod, ABCMeta
from typing import Any

from dandy.handler.handler import RunHandler


class Tool(RunHandler, metaclass=ABCMeta): ...
