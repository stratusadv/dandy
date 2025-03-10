from typing import List

from pydantic import Field
from typing_extensions import Union

from dandy.intel import BaseIntel, BaseListIntel


class SceneIntel(BaseIntel):
    summary: str


class ChapterIntel(BaseIntel):
    title: str = ''
    covered_plot_points: Union[List[int], None] = list
    scenes: Union[List[SceneIntel], None] = list
    content: str = ''


class ChaptersIntel(BaseListIntel[ChapterIntel]):
    pass
