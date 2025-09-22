from __future__ import annotations

from typing import TYPE_CHECKING

from dandy import Bot
from example.book.intelligence.character.bots import CharacterGeneratorBot
from example.book.intelligence.character.enums import CharacterType
from example.book.intelligence.character.intel import CharactersIntel

if TYPE_CHECKING:
    from example.book.intelligence.intel import BookIntel


class CharactersCreationBot(Bot):
    def process(
            self,
            book_intel: BookIntel
    ) -> CharactersIntel:
        self.characters_intel = CharactersIntel()
        self.book_intel = book_intel

        self.create_character(CharacterType.PROTAGONIST)
        self.create_character(CharacterType.ANTAGONIST)
        self.create_character(CharacterType.CONFIDANT)
        self.create_character(CharacterType.FOIL)
        self.create_character(CharacterType.EXTRA)
        self.create_character(CharacterType.EXTRA)

        return self.characters_intel

    def create_character(
            self,
            character_type: CharacterType,
    ):
        self.characters_intel.append(
            CharacterGeneratorBot().process(
                self.book_intel,
                character_type,
                self.characters_intel
            )
        )
