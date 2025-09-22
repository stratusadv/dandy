from __future__ import annotations

from typing import TYPE_CHECKING

from dandy import cache_to_sqlite, Bot, Prompt
from example.book.intelligence.character.enums import CharacterType
from example.book.intelligence.character.intel import CharacterIntel
from example.book.intelligence.character.prompts import characters_intel_prompt

if TYPE_CHECKING:
    from example.book.intelligence.intel import BookIntel
    from example.book.intelligence.character.intel import CharactersIntel


class CharacterGeneratorBot(Bot):
    config = 'ADVANCED'
    instructions_prompt = (
        Prompt()
        .text('You are a character generating bot, please create a character based on the provided input.')
    )

    @cache_to_sqlite('example')
    def process(
            self,
            book_intel: BookIntel,
            character_type: CharacterType,
            characters_intel: CharactersIntel | None = None,
    ) -> CharacterIntel:
        prompt = Prompt()

        prompt.line_break()

        prompt.title(f'Book Title: {book_intel.start.title}')
        prompt.heading(f'Overview: {book_intel.start.overview}')

        if characters_intel:
            prompt.line_break()

            prompt.prompt(characters_intel_prompt(characters_intel))

        return self.llm.prompt_to_intel(
            prompt=prompt,
            intel_class=CharacterIntel,
            postfix_system_prompt=Prompt().text(label='Set the Character Type to', text=character_type.value)
        )
