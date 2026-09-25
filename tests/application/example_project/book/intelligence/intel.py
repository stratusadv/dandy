from dandy.domain.intel.intel import BaseIntel
from tests.application.example_project.book.enums import BookTheme
from tests.application.example_project.book.intelligence.chapter.intel import ChaptersIntel
from tests.application.example_project.book.intelligence.character.intel import CharactersIntel
from tests.application.example_project.book.intelligence.plot.intel import PlotPointsIntel
from tests.application.example_project.book.intelligence.world.intel import WorldIntel


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
