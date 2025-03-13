from __future__ import annotations

from typing import Union

from typing_extensions import TYPE_CHECKING

from dandy.core.cache import cache_to_sqlite
from dandy.llm import BaseLlmBot, Prompt
from example.book.intelligence.character.enums import CharacterType
from example.book.intelligence.character.intel import CharacterIntel
from example.book.intelligence.character.prompts import characters_intel_prompt

if TYPE_CHECKING:
    from example.book.intelligence.intel import BookIntel
    from example.book.intelligence.character.intel import CharactersIntel


class CharacterGeneratorLlmBot(BaseLlmBot):
    config = 'ADVANCED'
    instructions_prompt = (
        Prompt()
        .text('You are a character generating bot, please create a character based on the provided input.')
    )

    @classmethod
    @cache_to_sqlite('book')
    def process(
            cls,
            book_intel: BookIntel,
            character_type: CharacterType,
            characters_intel: Union[CharactersIntel, None] = None,
    ) -> CharacterIntel:
        prompt = Prompt()

        prompt.line_break()

        prompt.title(f'Book Title: {book_intel.start.title}')
        prompt.heading(f'Overview: {book_intel.start.overview}')

        if characters_intel:
            prompt.line_break()

            prompt.prompt(characters_intel_prompt(characters_intel))

        return cls.process_prompt_to_intel(
            prompt=prompt,
            intel_class=CharacterIntel,
            postfix_system_prompt=Prompt().text(label='Set the Character Type to', text=character_type.value)
        )
