from __future__ import annotations

from typing import TYPE_CHECKING

from dandy import Bot, Prompt
from tests.example_project.book.intelligence.character.prompts import (
    characters_intel_prompt,
)
from tests.example_project.book.intelligence.world.intel import WorldIntel

if TYPE_CHECKING:
    from tests.example_project.book.intelligence.intel import BookIntel


class WorldCreationBot(Bot):
    role = 'World Creator'
    task = 'You will be given a book title, overview and characters to design your world around.'
    instructions_prompt = Prompt().list(
        ['You will generate a world with enough locations for the characters.']
    )

    def process(
        self,
        book_intel: BookIntel,
    ) -> WorldIntel:
        prompt = Prompt()
        prompt.title(f'Title: {book_intel.start.title}')
        prompt.heading(f'Overview: {book_intel.start.overview}')

        prompt.line_break()
        characters_intel_prompt(book_intel.characters)

        return self.llm.prompt_to_intel(prompt=prompt, intel_class=WorldIntel)
