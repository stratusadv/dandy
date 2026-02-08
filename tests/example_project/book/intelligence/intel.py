from dandy.intel.intel import BaseIntel
from tests.example_project.book.enums import BookTheme
from tests.example_project.book.intelligence.chapter.intel import ChaptersIntel
from tests.example_project.book.intelligence.character.intel import CharactersIntel
from tests.example_project.book.intelligence.plot.intel import PlotPointsIntel
from tests.example_project.book.intelligence.world.intel import WorldIntel


class BookStartIntel(BaseIntel):
    title: str
    overview: str


class BookIntel(BaseIntel):
    user_input: str
    theme: BookTheme
    start: BookStartIntel | None = None
    characters: CharactersIntel | None = None
    plot: PlotPointsIntel | None = None
    world: WorldIntel | None = None
    chapters: ChaptersIntel | None = None
