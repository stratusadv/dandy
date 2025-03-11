from typing import Optional

from pydantic import Field
from typing_extensions import List, Generator, Union

from dandy.intel import BaseIntel, BaseListIntel


class PlotPointIntel(BaseIntel):
    outline: Optional[str] = None
    description: Optional[str] = None


class PlotIntel(BaseListIntel[PlotPointIntel]):
    pass
