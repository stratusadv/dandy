from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from dandy import Bot
from tests.example_project.book.intelligence.character.bots import CharacterGeneratorBot
from tests.example_project.book.intelligence.character.enums import CharacterType
from tests.example_project.book.intelligence.character.intel import CharactersIntel

if TYPE_CHECKING:
    from tests.example_project.book.intelligence.intel import BookIntel


CHARACTER_TYPES = [
    CharacterType.PROTAGONIST,
    CharacterType.ANTAGONIST,
    CharacterType.CONFIDANT,
    CharacterType.FOIL,
    CharacterType.EXTRA,
    CharacterType.EXTRA,
]


def characters_creation(book_intel: BookIntel) -> CharactersIntel:
    characters_intel = CharactersIntel()

    for character_type in CHARACTER_TYPES:
        logging.info(f'Adding {character_type} Character')
        characters_intel.append(
            CharacterGeneratorBot().process(
                book_intel, character_type, characters_intel
            )
        )

    return characters_intel
