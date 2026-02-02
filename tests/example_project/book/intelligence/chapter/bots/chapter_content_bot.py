from __future__ import annotations

from typing import TYPE_CHECKING

from dandy import Bot, Prompt
from tests.example_project.book.intelligence.chapter.prompts import (
    chapter_intel_overview_prompt,
)
from tests.example_project.book.intelligence.prompts import book_intel_prompt

if TYPE_CHECKING:
    from tests.example_project.book.intelligence.chapter.intel import ChapterIntel
    from tests.example_project.book.intelligence.intel import BookIntel


class ChapterContentLlmBot(Bot):
    role = 'Chapter Content Writer'
    task = 'You are a chapter writing bot that will use all the information provided to write the content for a new chapter.'
    guidelines = Prompt().list(
        [
            'Do not include a chapter titles, chapter numbers or scene information when you write the content.'
            'The content for a chapter should be at least 10 paragraphs long or longer including dialog.'
        ]
    )

    def process(
        self,
        book_intel: BookIntel,
        chapter_intel: ChapterIntel,
    ) -> ChapterIntel:
        prompt = Prompt()

        prompt.prompt(book_intel_prompt(book_intel))

        prompt.line_break()

        prompt.heading('Current Chapter to Write Content For:')

        prompt.prompt(chapter_intel_overview_prompt(chapter_intel))

        return self.llm.prompt_to_intel(
            prompt=prompt,
            intel_object=chapter_intel,
            include_fields={'content'},
        )
