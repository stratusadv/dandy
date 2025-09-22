from typing import List

from pydantic import Field

from dandy import BaseIntel, BaseListIntel
from example.book.intelligence.character.enums import CharacterType, CharacterAlignment


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
