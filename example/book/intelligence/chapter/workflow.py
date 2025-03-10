from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from dandy.workflow import BaseWorkflow
from example.book.intelligence.chapter.intel import ChaptersIntel

from example.book.intelligence.chapter import bots

if TYPE_CHECKING:
    from example.book.intelligence.intel import BookIntel


class ChaptersWorkflow(BaseWorkflow):
    @classmethod
    def process(
            cls,
            book_intel: BookIntel,
            chapter_count: int
    ) -> ChaptersIntel:
        chapters_intel = bots.ChaptersStructureLlmBot.process(
            book_intel=book_intel,
            chapter_count=chapter_count,
        )

        for i, chapter_intel in enumerate(chapters_intel):
            chapters_intel[i] = bots.SceneLlmBot.process(
                book_intel=book_intel,
                chapter_intel=chapter_intel,
            )

        for i, chapter_intel in enumerate(chapters_intel):
            chapters_intel[i] = bots.ChapterContentLlmBot.process(
                book_intel=book_intel,
                chapter_intel=chapter_intel,
            )

        return chapters_intel
