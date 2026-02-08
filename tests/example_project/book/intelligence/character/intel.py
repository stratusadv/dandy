from typing import List

from pydantic import Field

from dandy import BaseIntel, BaseListIntel
from tests.example_project.book.intelligence.character.enums import (
    CharacterAlignment,
    CharacterType,
)


class CharacterIntel(BaseIntel):
    first_name: str
    last_name: str
    age: int
    nickname: str
    description: str
    type: CharacterType
    alignment: CharacterAlignment


class CharactersIntel(BaseListIntel[CharacterIntel]):
    characters: List[CharacterIntel] = Field(default_factory=list)
