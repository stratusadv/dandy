from __future__ import annotations

from typing import TYPE_CHECKING

from dandy.llm import BaseLlmBot, Prompt
from example.book.intelligence.world.intel import WorldIntel

if TYPE_CHECKING:
    from example.book.intelligence.intel import BookStartIntel
    from example.book.intelligence.character.intel import CharactersIntel


class WorldLlmBot(BaseLlmBot):
    config = 'ADVANCED'
    instructions_prompt = (
        Prompt()
        .text('You are a world bot. You will be given a book title, overview and characters. ')
        .text('You will generate a world with enough locations for the characters. ')
    )

    @classmethod
    def process(
            cls,
            book_start_intel: BookStartIntel,
            characters_intel: CharactersIntel
    ) -> WorldIntel:
        prompt = Prompt()
        prompt.text(f'Title: {book_start_intel.title} ')
        prompt.text(f'Overview: {book_start_intel.overview} ')
        
        for character in characters_intel.characters:
            prompt.line_break()
            
            prompt.text(f'Name: {character.first_name} {character.last_name} ')
            prompt.text(f'Age: {character.age} ')
            prompt.text(f'Nickname: {character.nickname} ')
            prompt.text(f'Description: {character.description} ')
            prompt.text(f'Type: {character.type.value} ')
            prompt.text(f'Alignment: {character.alignment.value} ')

        return cls.process_prompt_to_intel(
            prompt=prompt,
            intel_class=WorldIntel
        )
