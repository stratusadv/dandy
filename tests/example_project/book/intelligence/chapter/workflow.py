from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from tests.example_project.book.intelligence.chapter import bots
from tests.example_project.book.intelligence.chapter.intel import ChaptersIntel

if TYPE_CHECKING:
    from tests.example_project.book.intelligence.intel import BookIntel


def chapters_creation(book_intel: BookIntel, chapter_count: int) -> ChaptersIntel:
    chapters_intel = bots.ChaptersLlmBot().process(
        book_intel=book_intel,
        chapter_count=chapter_count,
    )

    for i, chapter_intel in enumerate(chapters_intel):
        logging.info(f'Planning Scenes for Chapter {i + 1}')

        chapters_intel[i] = bots.SceneLlmBot().process(
            book_intel=book_intel,
            chapter_intel=chapter_intel,
        )

    for i, chapter_intel in enumerate(chapters_intel):
        logging.info(f'Building Chapter {i + 1} Content')

        chapters_intel[i] = bots.ChapterContentLlmBot().process(
            book_intel=book_intel,
            chapter_intel=chapter_intel,
        )

    return chapters_intel
