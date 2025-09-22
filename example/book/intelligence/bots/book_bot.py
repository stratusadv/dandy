from __future__ import annotations

import logging

from typing import TYPE_CHECKING


from dandy import Bot
from example.book.intelligence.bots import BookStartLlmBot
from example.book.intelligence.chapter.bots.chapters_creation_bot import ChaptersCreationBot
from example.book.intelligence.character.bots.characters_creation_bot import CharactersCreationBot
from example.book.intelligence.intel import BookIntel
from example.book.intelligence.maps import BookThemeMap
from example.book.intelligence.plot.bots.plot_creation_bot import PlotCreationBot
from example.book.intelligence.world.bots import WorldCreationBot
from example.book.models import Book, Chapter

if TYPE_CHECKING:
    pass


class BookBot(Bot):
    def process(
            self,
            user_input: str,
    ) -> Book:
        book_intel = BookIntel(
            user_input=user_input,
            theme=BookThemeMap().process(user_input)[0]
        )

        logging.info('Working on book title and overview')
        book_intel.start = BookStartLlmBot().process(user_input)

        logging.info('Creating "those" characters')
        book_intel.characters = CharactersCreationBot().process(book_intel)

        logging.info('Forging a world')
        book_intel.world = WorldCreationBot().process(book_intel)

        logging.info('Setting up the plot')
        book_intel.plot = PlotCreationBot().process(book_intel)

        logging.info('Writing the chapters for all to read')
        book_intel.chapters = ChaptersCreationBot().process(
            book_intel=book_intel,
            chapter_count=4
        )

        new_book = Book(
            title=book_intel.start.title,
            author='Dandy McAuthor',
            theme=book_intel.theme,
            overview=book_intel.start.overview,
            chapters=[
                Chapter(title=chapter_intel.title, content=chapter_intel.content)
                for chapter_intel in book_intel.chapters
            ]
        )

        return new_book
