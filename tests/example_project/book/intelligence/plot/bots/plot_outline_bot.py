from __future__ import annotations

from typing import TYPE_CHECKING

from dandy import Bot, Prompt, cache_to_sqlite
from tests.example_project.book.intelligence.plot.intel import PlotPointsIntel
from tests.example_project.book.intelligence.prompts import book_intel_prompt

if TYPE_CHECKING:
    from tests.example_project.book.intelligence.intel import BookIntel


class PlotOutlineBot(Bot):
    llm_config = 'THINKING'
    role = 'Plot Writer'
    task = 'You will be given a book title, overview, world and characters.'

    def process(
            self,
            book_intel: BookIntel,
            chapter_count: int,
    ) -> PlotPointsIntel:
        self.guidelines = (
            Prompt()
            .text('You will generate a plot using the classic heroes journey plot structure.')
            .text(f'Create {chapter_count} plot points based on the provided information')
        )

        print(self.guidelines)

        return self.llm.prompt_to_intel(
            prompt=book_intel_prompt(book_intel),
            intel_class=PlotPointsIntel,
            include_fields={'plot_points': {'outline'}}
        )
