from dandy.intel import BaseIntel

from example.book.intelligence.character.intel import CharactersIntel


class BookIntel(BaseIntel):
    characters_intel: CharactersIntel