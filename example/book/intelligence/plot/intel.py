from pydantic import Field
from typing import Optional

from dandy.intel.intel import BaseIntel, BaseListIntel


class PlotPointIntel(BaseIntel):
    outline: Optional[str] = None
    description: Optional[str] = None


class PlotIntel(BaseListIntel[PlotPointIntel]):
    items: list[PlotPointIntel] = Field(default_factory=list)
