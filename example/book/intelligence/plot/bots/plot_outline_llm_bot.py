from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from dandy.llm import BaseLlmBot, Prompt
from example.book.intelligence.plot.intel import PlotIntel
from example.book.intelligence.prompts import book_intel_prompt

if TYPE_CHECKING:
    from example.book.intelligence.intel import BookIntel


class PlotOutlineLlmBot(BaseLlmBot):
    config = 'COMPLEX'
    instructions_prompt = (
        Prompt()
        .text('You are a plot bot. You will be given a book title, overview, world and characters.')
        .text('You will generate a plot using the classic heroes journey plot structure.')
        .text('Create 10 plot points with only an outline (do not number them) and no description.')
    )
   
    @classmethod    
    def process(
            cls,
            book_intel: BookIntel
    ) -> PlotIntel:
        return cls.process_prompt_to_intel(
            prompt=book_intel_prompt(book_intel),
            intel_class=PlotIntel
        )
        