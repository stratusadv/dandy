from typing import List

from typing import Union

from dandy.intel.intel import BaseIntel, BaseListIntel


class SceneIntel(BaseIntel):
    summary: str


class ChapterIntel(BaseIntel):
    title: str = ''
    covered_plot_points: Union[List[int], None] = None
    scenes: Union[List[SceneIntel], None] = None
    content: Union[str, None] = None


class ChaptersIntel(BaseListIntel[ChapterIntel]):
    pass
