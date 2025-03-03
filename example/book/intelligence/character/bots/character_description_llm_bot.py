from __future__ import annotations

from typing import Union

from typing_extensions import TYPE_CHECKING

from dandy.llm import BaseLlmBot, Prompt
from example.book.intelligence.character.enums import CharacterType
from example.book.intelligence.character.intel import CharacterIntel

if TYPE_CHECKING:
    from example.book.intelligence.intel import BookIntel
    from example.book.intelligence.character.intel import CharactersIntel


class CharacterGeneratorLlmBot(BaseLlmBot):
    config = 'ADVANCED'
    
    @classmethod
    def process(
            cls,
            book_intel: BookIntel,
            character_type: CharacterType,
            characters_intel: Union[CharactersIntel, None] = None,
    ) -> CharacterIntel:
        prompt = Prompt()
        
        prompt.text(f'Generate a {character_type.value} Character for the following book.')
        
        prompt.line_break()
        
        prompt.text(f'Title: {book_intel.start.title}')
        prompt.text(f'Overview: {book_intel.start.overview}')
        
        if characters_intel:
            prompt.line_break()
            
            prompt.text('Other Characters:')
            
            for character in characters_intel.characters:
                prompt.line_break()
                
                prompt.text(f'Name: {character.first_name} {character.last_name}')
                prompt.text(f'Age: {character.age}')
                prompt.text(f'Nickname: {character.nickname}')
                prompt.text(f'Description: {character.description}')
                prompt.text(f'Type: {character.type.value}')
                prompt.text(f'Alignment: {character.alignment.value}')
    
        return cls.process_prompt_to_intel(
            prompt=prompt, 
            intel_class=CharacterIntel,
            postfix_system_prompt=Prompt().text(f'Set the Character Type to: {character_type.value}')
        )