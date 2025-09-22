from __future__ import annotations

from typing import TYPE_CHECKING

from dandy import cache_to_sqlite, Bot, Prompt
from example.book.intelligence.chapter.intel import ChapterIntel
from example.book.intelligence.chapter.prompts import chapter_intel_overview_prompt
from example.book.intelligence.prompts import book_intel_prompt

if TYPE_CHECKING:
    from example.book.intelligence.intel import BookIntel


class ChapterContentLlmBot(Bot):
    config = 'ADVANCED'
    instructions_prompt = (
        Prompt()
        .text('You are a chapter writing bot that will use all the information provided to write the content for a new chapter.')
        .text('Do not include a chapter titles, chapter numbers or scene information in when you write the content.')
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

        prompt.heading('Current Chapter to Write Content For:')
        prompt.prompt(chapter_intel_overview_prompt(chapter_intel))

        return self.llm.prompt_to_intel(
            prompt=prompt,
            intel_object=chapter_intel,
            include_fields={'content'},
        )
