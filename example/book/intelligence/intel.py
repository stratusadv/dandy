from dandy.intel.intel import BaseIntel
from example.book.enums import BookTheme
from example.book.intelligence.chapter.intel import ChaptersIntel

from example.book.intelligence.character.intel import CharactersIntel
from example.book.intelligence.plot.intel import PlotIntel
from example.book.intelligence.world.intel import WorldIntel


class BookStartIntel(BaseIntel):
    title: str
    overview: str
    
    
class BookIntel(BaseIntel):
    user_input: str
    theme: BookTheme
    start: BookStartIntel | None = None
    characters: CharactersIntel | None = None
    plot: PlotIntel | None = None
    world: WorldIntel | None = None
    chapters: ChaptersIntel | None = None
