from __future__ import annotations

from typing import TYPE_CHECKING

from dandy import cache_to_sqlite, Bot, Prompt
from example.book.intelligence.chapter.intel import ChaptersIntel
from example.book.intelligence.prompts import book_intel_prompt

if TYPE_CHECKING:
    from example.book.intelligence.intel import BookIntel


class ChaptersLlmBot(Bot):
    config = 'ADVANCED'
    instructions_prompt = (
        Prompt()
        .text('You are a chapter planning bot. You will be given information on a book that is being written.')
        .text('For each chapter create a title and which plot points will be covered in the chapter.')
        .text('You will select a randomly sized set of plot points to cover')
    )

    @cache_to_sqlite('example')
    def process(
            self,
            book_intel: BookIntel,
            chapter_count: int,
    ) -> ChaptersIntel:

        postfix_system_prompt = Prompt()
        postfix_system_prompt.text(f'Create {chapter_count} chapters.')

        return self.llm.prompt_to_intel(
            prompt=book_intel_prompt(book_intel),
            intel_class=ChaptersIntel,
            include_fields={
                'items': {
                    'title': True,
                    'covered_plot_points': True
                },
            },
            postfix_system_prompt=postfix_system_prompt,
        )
