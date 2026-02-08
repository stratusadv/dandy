from __future__ import annotations

import logging

from tests.example_project.book.intelligence.bots import BookStartLlmBot
from tests.example_project.book.intelligence.chapter.workflow import (
    chapters_creation,
)
from tests.example_project.book.intelligence.character.workflow import (
    characters_creation,
)
from tests.example_project.book.intelligence.decoders import BookThemeDecoderBot
from tests.example_project.book.intelligence.intel import BookIntel
from tests.example_project.book.intelligence.plot.workflow import plot_creation
from tests.example_project.book.intelligence.world.bots import WorldCreationBot
from tests.example_project.book.models import Book, Chapter


def create_book(user_input: str, chapter_count: int = 10) -> Book:
    book_intel = BookIntel(
        user_input=user_input,
        theme=BookThemeDecoderBot().process(user_input),
    )

    logging.info('Working on book title and overview')
    book_intel.start = BookStartLlmBot().process(user_input)

    logging.info('Creating "those" characters')
    book_intel.characters = characters_creation(book_intel)

    logging.info('Forging a world')
    book_intel.world = WorldCreationBot().process(book_intel)

    logging.info('Setting up the plot')
    book_intel.plot = plot_creation(book_intel)

    logging.info('Writing the chapters for all to read')
    book_intel.chapters = chapters_creation(
        book_intel=book_intel,
        chapter_count=chapter_count,
    )

    new_book = Book(
        title=book_intel.start.title,
        author='Dandy McAuthor',
        theme=book_intel.theme,
        overview=book_intel.start.overview,
        chapters=[
            Chapter(title=chapter_intel.title, content=chapter_intel.content)
            for chapter_intel in book_intel.chapters
        ],
    )

    return new_book
