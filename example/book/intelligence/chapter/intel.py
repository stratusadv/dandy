from typing import List

from pydantic import Field

from dandy.intel import BaseIntel, BaseIterableIntel


class SceneIntel(BaseIntel):
    summary: str    


class ChapterIntel(BaseIntel):
    title: str
    covered_plot_points: List[int]   
    scenes: List[SceneIntel] = Field(default_factory=list)
    content: str = ''
    
    
class ChaptersIntel(BaseIterableIntel[ChapterIntel]):
    pass