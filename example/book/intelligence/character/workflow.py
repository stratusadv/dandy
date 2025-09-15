from __future__ import annotations

from typing import TYPE_CHECKING

from dandy.workflow import BaseWorkflow
from example.book.intelligence.character.bots import CharacterGeneratorLlmBot
from example.book.intelligence.character.enums import CharacterType
from example.book.intelligence.character.intel import CharactersIntel

if TYPE_CHECKING:
    from example.book.intelligence.intel import BookIntel


class CharactersWorkflow(BaseWorkflow):
    @classmethod
    def process(
            cls,
            book_intel: BookIntel
    ) -> CharactersIntel:
        cls.characters_intel = CharactersIntel()
        cls.book_intel = book_intel

        cls.create_character(CharacterType.PROTAGONIST)
        cls.create_character(CharacterType.ANTAGONIST)
        cls.create_character(CharacterType.CONFIDANT)
        cls.create_character(CharacterType.FOIL)
        cls.create_character(CharacterType.EXTRA)
        cls.create_character(CharacterType.EXTRA)

        return cls.characters_intel

    @classmethod
    def create_character(
            cls,
            character_type: CharacterType,
    ):
        cls.characters_intel.add_character(
            CharacterGeneratorLlmBot.process(
                cls.book_intel,
                character_type,
                cls.characters_intel
            )
        )
