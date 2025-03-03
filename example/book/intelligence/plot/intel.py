from pydantic import Field
from typing_extensions import List, Generator

from dandy.intel import BaseIntel


class PlotPoint(BaseIntel):
    outline: str
    description: str = ''


class PlotIntel(BaseIntel):
    points: List[PlotPoint]
    
    def __iter__(self) -> Generator[PlotPoint]:
        for point in self.points:
            yield point
    
    def add_point(self, point: PlotPoint):
        self.points.append(point)
