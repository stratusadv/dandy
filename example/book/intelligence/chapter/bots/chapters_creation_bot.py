from __future__ import annotations

from typing import TYPE_CHECKING

from dandy import Bot
from example.book.intelligence.chapter.intel import ChaptersIntel

from example.book.intelligence.chapter import bots

if TYPE_CHECKING:
    from example.book.intelligence.intel import BookIntel


class ChaptersCreationBot(Bot):
    def process(
            self,
            book_intel: BookIntel,
            chapter_count: int
    ) -> ChaptersIntel:
        chapters_intel = bots.ChaptersLlmBot().process(
            book_intel=book_intel,
            chapter_count=chapter_count,
        )

        for i, chapter_intel in enumerate(chapters_intel):
            chapters_intel[i] = bots.SceneLlmBot().process(
                book_intel=book_intel,
                chapter_intel=chapter_intel,
            )

        for i, chapter_intel in enumerate(chapters_intel):
            chapters_intel[i] = bots.ChapterContentLlmBot().process(
                book_intel=book_intel,
                chapter_intel=chapter_intel,
            )

        return chapters_intel
