from __future__ import annotations

from typing import TYPE_CHECKING

from dandy import Bot, Prompt, cache_to_sqlite
from tests.example_project.book.intelligence.chapter.intel import ChapterIntel
from tests.example_project.book.intelligence.chapter.prompts import (
    chapter_intel_overview_prompt,
)
from tests.example_project.book.intelligence.prompts import book_intel_prompt

if TYPE_CHECKING:
    from tests.example_project.book.intelligence.intel import BookIntel


class SceneLlmBot(Bot):
    role = 'Book Scene Planner'
    task = 'You are a scene planning bot. You will be given information on a book that is being written.'
    guidelines = Prompt().list(
        [
            'For the current chapter you will create all the required scenes needed to cover the plot points in the chapter.',
        ]
    )

    @cache_to_sqlite('example')
    def process(
        self,
        book_intel: BookIntel,
        chapter_intel: ChapterIntel,
    ) -> ChapterIntel:
        prompt = Prompt()

        prompt.prompt(book_intel_prompt(book_intel))

        prompt.line_break()

        prompt.heading('Current Chapter Overview:')
        prompt.prompt(chapter_intel_overview_prompt(chapter_intel))

        return self.llm.prompt_to_intel(
            prompt=prompt, intel_object=chapter_intel, include_fields={'scenes'}
        )
