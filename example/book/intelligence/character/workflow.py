from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from dandy.workflow import BaseWorkflow
from example.book.intelligence.character.bots.character_description_llm_bot import CharacterGeneratorLlmBot
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

        characters_intel = CharactersIntel()

        characters_intel.add_character(
            CharacterGeneratorLlmBot.process(book_intel, CharacterType.PROTAGONIST)
        )

        characters_intel.add_character(
            CharacterGeneratorLlmBot.process(book_intel, CharacterType.ANTAGONIST, characters_intel)
        )

        characters_intel.add_character(
            CharacterGeneratorLlmBot.process(book_intel, CharacterType.FOIL, characters_intel)
        )

        characters_intel.add_character(
            CharacterGeneratorLlmBot.process(book_intel, CharacterType.CONFIDANT, characters_intel)
        )

        characters_intel.add_character(
            CharacterGeneratorLlmBot.process(book_intel, CharacterType.EXTRA, characters_intel)
        )

        characters_intel.add_character(
            CharacterGeneratorLlmBot.process(book_intel, CharacterType.EXTRA, characters_intel)
        )

        return characters_intel
