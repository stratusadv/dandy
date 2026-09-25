from typing import Optional

from pydantic import Field

from dandy import BaseIntel, BaseListIntel


class PlotPointIntel(BaseIntel):
    outline: str | None = None
    description: str | None = None


class PlotPointsIntel(BaseListIntel[PlotPointIntel]):
    plot_points: list[PlotPointIntel] = Field(default_factory=list)
