from __future__ import annotations

from typing import TYPE_CHECKING

from dandy import cache_to_sqlite, Bot, Prompt
from example.book.intelligence.plot.intel import PlotIntel
from example.book.intelligence.prompts import book_intel_prompt

if TYPE_CHECKING:
    from example.book.intelligence.intel import BookIntel


class PlotOutlineBot(Bot):
    config = 'COMPLEX'
    instructions_prompt = (
        Prompt()
        .text('You are a plot bot. You will be given a book title, overview, world and characters.')
        .text('You will generate a plot using the classic heroes journey plot structure.')
        .text('Create 10 unnumbered outlines for plot points')
    )

    @cache_to_sqlite('example')
    def process(
            self,
            book_intel: BookIntel,
    ) -> PlotIntel:
        return self.llm.prompt_to_intel(
            prompt=book_intel_prompt(book_intel),
            intel_class=PlotIntel,
            include_fields={'items': {'outline'}}
        )
