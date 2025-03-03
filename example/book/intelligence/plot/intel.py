from pydantic import Field
from typing_extensions import List, Generator, Union

from dandy.intel import BaseIntel, BaseIterableIntel


class PlotPointIntel(BaseIntel):
    outline: str
    description: str = ''


class PlotIntel(BaseIterableIntel[PlotPointIntel]):
    pass