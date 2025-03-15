from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from dandy.core.cache import cache_to_sqlite
from dandy.llm import BaseLlmBot, Prompt
from example.book.intelligence.chapter.intel import ChapterIntel
from example.book.intelligence.chapter.prompts import chapter_intel_overview_prompt
from example.book.intelligence.prompts import book_intel_prompt

if TYPE_CHECKING:
    from example.book.intelligence.intel import BookIntel


class ChapterContentLlmBot(BaseLlmBot):
    config = 'ADVANCED'
    instructions_prompt = (
        Prompt()
        .text('You are a chapter writing bot that will use all the information provided to write the content for a new chapter.')
        .text('You will not include a chapter title or number in your response.')
    )

    @classmethod
    @cache_to_sqlite('example')
    def process(
            cls,
            book_intel: BookIntel,
            chapter_intel: ChapterIntel,
    ) -> ChapterIntel:
        prompt = Prompt()

        prompt.prompt(book_intel_prompt(book_intel))

        prompt.line_break()

        prompt.heading('Current Chapter to Write Content For:')
        prompt.prompt(chapter_intel_overview_prompt(chapter_intel))

        return cls.process_prompt_to_intel(
            prompt=prompt,
            intel_object=chapter_intel,
            include_fields={'content'},
        )
