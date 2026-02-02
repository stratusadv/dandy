from __future__ import annotations

from typing import TYPE_CHECKING

from dandy import Bot, Prompt, cache_to_sqlite
from tests.example_project.book.intelligence.chapter.intel import ChaptersIntel
from tests.example_project.book.intelligence.prompts import book_intel_prompt

if TYPE_CHECKING:
    from tests.example_project.book.intelligence.intel import BookIntel


class ChaptersLlmBot(Bot):
    role = 'Book Chapter Planner'
    task = 'You are a chapter planner. You will be given information on a book that is being written.'
    guidelines = Prompt().list(
        [
            'For each chapter create a title and which plot points will be covered in the chapter.',
            'You will select a randomly sized set of plot points to cover',
        ]
    )

    def process(
        self,
        book_intel: BookIntel,
        chapter_count: int,
    ) -> ChaptersIntel:
        prompt = Prompt()
        prompt.prompt(book_intel_prompt(book_intel))
        prompt.line_break()
        prompt.text(f'Create {chapter_count} chapters.')

        return self.llm.prompt_to_intel(
            prompt=prompt,
            intel_class=ChaptersIntel,
            include_fields={
                'items': {'title': True, 'covered_plot_points': True},
            },
        )
