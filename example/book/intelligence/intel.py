from typing import Union

from dandy.intel import BaseIntel
from example.book.intelligence.chapter.intel import ChaptersIntel

from example.book.intelligence.character.intel import CharactersIntel
from example.book.intelligence.plot.intel import PlotIntel
from example.book.intelligence.world.intel import WorldIntel


class BookStartIntel(BaseIntel):
    title: str
    overview: str
    
    
class BookIntel(BaseIntel):
    user_input: str
    start: Union[BookStartIntel, None] = None
    characters: Union[CharactersIntel, None] = None
    plot: Union[PlotIntel, None] = None
    world: Union[WorldIntel, None] = None
    chapters: Union[ChaptersIntel, None] = None
