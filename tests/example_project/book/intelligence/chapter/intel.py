from typing import List

from pydantic import Field

from dandy.intel.intel import BaseIntel, BaseListIntel


class SceneIntel(BaseIntel):
    summary: str


class ChapterIntel(BaseIntel):
    title: str = ''
    covered_plot_points: List[int] | None = None
    scenes: List[SceneIntel] | None = None
    content: str | None = None


class ChaptersIntel(BaseListIntel[ChapterIntel]):
    items: List[ChapterIntel] = Field(default_factory=list)
