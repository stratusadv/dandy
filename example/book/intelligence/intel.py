from dandy.intel import BaseIntel

from example.book.intelligence.character.intel import CharactersIntel
from example.book.intelligence.world.intel import WorldIntel


class BookStartIntel(BaseIntel):
    title: str
    overview: str
    
    
class BookIntel(BaseIntel):
    characters_intel: CharactersIntel
    world_intel: WorldIntel