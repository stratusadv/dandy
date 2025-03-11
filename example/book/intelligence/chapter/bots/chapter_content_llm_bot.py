from __future__ import annotations

from pydantic.main import IncEx
from typing_extensions import TYPE_CHECKING, Union

from dandy.llm import BaseLlmBot, Prompt
from example.book.intelligence.chapter.intel import ChaptersIntel, ChapterIntel
from example.book.intelligence.chapter.prompts import chapter_intel_overview_prompt
from example.book.intelligence.prompts import book_intel_prompt

if TYPE_CHECKING:
    from example.book.intelligence.intel import BookIntel


class ChapterContentLlmBot(BaseLlmBot):
    config = 'ADVANCED'
    instructions_prompt = (
        Prompt()
        .text('You are a chapter writing bot that will use all the information provided to write the content for a new chapter.')
        # .text('Use the following rules to write the chapter:')
        # .list([
        #     'Use the same title from the current chapter.',
        #     'Use the same covered plot points from the current chapter.',
        #     'Use the same scenes as the current chapter.',
        #     'Write the `content` using the information provided for the current chapter.',
        # ])
    )

    @classmethod
    def process(
            cls,
            book_intel: BookIntel,
            chapter_intel: ChapterIntel,
    ) -> ChapterIntel:
        prompt = Prompt()

        prompt.prompt(book_intel_prompt(book_intel))

        prompt.line_break()

        prompt.heading('Current Chapter to Write Content For')
        prompt.prompt(chapter_intel_overview_prompt(chapter_intel))

        return cls.process_prompt_to_intel(
            prompt=prompt,
            intel_object=chapter_intel,
            include_fields={'content'},
        )
