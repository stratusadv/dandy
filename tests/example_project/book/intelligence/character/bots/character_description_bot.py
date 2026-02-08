from __future__ import annotations

from typing import TYPE_CHECKING

from dandy import Bot, Prompt
from tests.example_project.book.intelligence.character.intel import CharacterIntel
from tests.example_project.book.intelligence.character.prompts import (
    characters_intel_prompt,
)

if TYPE_CHECKING:
    from tests.example_project.book.intelligence.character.enums import CharacterType
    from tests.example_project.book.intelligence.character.intel import CharactersIntel
    from tests.example_project.book.intelligence.intel import BookIntel


class CharacterGeneratorBot(Bot):
    role = 'Character Generator'
    task = 'You are a character generating bot, please create a character based on the provided input.'

    def process(
            self,
            book_intel: BookIntel,
            character_type: CharacterType,
            characters_intel: CharactersIntel | None = None,
    ) -> CharacterIntel:
        prompt = Prompt()

        prompt.line_break()

        prompt.heading('Book Title')

        prompt.text(book_intel.start.title)
        prompt.line_break()

        prompt.sub_heading('Overview')
        prompt.text(book_intel.start.overview)

        if characters_intel:
            prompt.line_break()

            prompt.prompt(characters_intel_prompt(characters_intel))

        prompt.sub_heading('New Character Type')
        prompt.text(character_type.value)

        return self.llm.prompt_to_intel(
            prompt=prompt,
            intel_class=CharacterIntel,
        )
