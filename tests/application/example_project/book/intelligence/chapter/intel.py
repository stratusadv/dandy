from pydantic import Field

from dandy.domain.intel.intel import BaseIntel, BaseListIntel


class SceneIntel(BaseIntel):
    summary: str


class ChapterIntel(BaseIntel):
    title: str = ''
    covered_plot_points: list[int] | None = None
    scenes: list[SceneIntel] | None = None
    content: str | None = None


class ChaptersIntel(BaseListIntel[ChapterIntel]):
    items: list[ChapterIntel] = Field(default_factory=list)
