from __future__ import annotations

from pydantic.main import IncEx
from typing_extensions import TYPE_CHECKING, Union

from dandy.llm import BaseLlmBot, Prompt
from example.book.intelligence.chapter.intel import ChaptersIntel, ChapterIntel
from example.book.intelligence.chapter.prompts import chapter_intel_overview_prompt
from example.book.intelligence.prompts import book_intel_prompt

if TYPE_CHECKING:
    from example.book.intelligence.intel import BookIntel


class SceneLlmBot(BaseLlmBot):
    config = 'ADVANCED'
    instructions_prompt = (
        Prompt()
        .text('You are a scene planning bot. You will be given information on a book that is being written.')
        .text('For the current chapter you will create all the required scenes needed to cover the plot points in the chapter.')
        # .text('Use the following rules to add the scenes to the chapter:')
        # .list([
        #     'Do not change the title or covered plot points of the chapter.',
        #     'Do not write the content for the chapter.',
        #     'Only create scenes for the current chapter.',
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

        prompt.text('Current Chapter Overview:')
        prompt.prompt(chapter_intel_overview_prompt(chapter_intel))

        return cls.process_prompt_to_intel(
            prompt=prompt,
            intel_class=ChapterIntel,
        )
