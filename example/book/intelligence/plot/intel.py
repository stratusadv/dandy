from pydantic import Field
from typing_extensions import List, Generator, Union

from dandy.intel import BaseIntel, BaseListIntel


class PlotPointIntel(BaseIntel):
    outline: str
    description: str = ''


class PlotIntel(BaseListIntel[PlotPointIntel]):
    pass