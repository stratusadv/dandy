from __future__ import annotations

from typing import TYPE_CHECKING

from dandy import cache_to_sqlite, Bot, Prompt
from example.book.intelligence.character.prompts import characters_intel_prompt
from example.book.intelligence.world.intel import WorldIntel

if TYPE_CHECKING:
    from example.book.intelligence.intel import BookIntel


class WorldCreationBot(Bot):
    config = 'ADVANCED'
    instructions_prompt = (
        Prompt()
        .text('You are a world creation bot. You will be given a book title, overview and characters.')
        .text('You will generate a world with enough locations for the characters.')
    )

    @cache_to_sqlite('example')
    def process(
            self,
            book_intel: BookIntel,
    ) -> WorldIntel:
        prompt = Prompt()
        prompt.title(f'Title: {book_intel.start.title}')
        prompt.heading(f'Overview: {book_intel.start.overview}')

        prompt.line_break()
        characters_intel_prompt(book_intel.characters)

        return self.llm.prompt_to_intel(
            prompt=prompt,
            intel_class=WorldIntel
        )
