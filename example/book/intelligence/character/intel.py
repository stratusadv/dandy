from pydantic import Field
from typing_extensions import List, Generator

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
    
    
class CharactersIntel(BaseIntel):
    characters: List[CharacterIntel] = Field(default_factory=list)

    def __iter__(self) -> Generator[CharacterIntel]:
        for character in self.characters:
            yield character    
    
    def add_character(self, character: CharacterIntel) -> None:
        self.characters.append(character)