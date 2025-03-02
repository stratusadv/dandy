from pydantic import Field
from typing_extensions import List

from dandy.intel import BaseIntel
from example.book.intelligence.character.enums import CharacterType, CharacterAlignment


class CharacterIntel(BaseIntel):
    first_name: str
    last_name: str
    age: int
    nickname: str
    description: str
    type: CharacterType
    alignment: CharacterAlignment
    gender: str
    
    
class CharactersIntel(BaseIntel):
    characters: List[CharacterIntel] = Field(default_factory=list)
    
    def add_character(self, character: CharacterIntel) -> None:
        self.characters.append(character)