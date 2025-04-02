from __future__ import annotations

import logging

from typing_extensions import TYPE_CHECKING

from dandy.workflow import BaseWorkflow
from example.book.intelligence.bots import BookStartLlmBot
from example.book.intelligence.chapter.workflow import ChaptersWorkflow
from example.book.intelligence.character.workflow import CharactersWorkflow
from example.book.intelligence.intel import BookIntel
from example.book.intelligence.maps import BookThemeLlmMap
from example.book.intelligence.plot.workflow import PlotWorkflow
from example.book.intelligence.world.bot import WorldLlmBot
from example.book.models import Book, Chapter

if TYPE_CHECKING:
    pass


class BookWorkflow(BaseWorkflow):
    @classmethod
    def process(
            cls,
            user_input: str,
    ) -> Book:
        book_intel = BookIntel(
            user_input=user_input,
            theme=BookThemeLlmMap.process(user_input)[0]
        )

        logging.info('Working on book title and overview')
        book_intel.start = BookStartLlmBot.process(user_input)

        logging.info('Creating "those" characters')
        book_intel.characters = CharactersWorkflow.process(book_intel)

        logging.info('Forging a world')
        book_intel.world = WorldLlmBot.process(book_intel)

        logging.info('Setting up the plot')
        book_intel.plot = PlotWorkflow.process(book_intel)

        logging.info('Writing the chapters for all to read')
        book_intel.chapters = ChaptersWorkflow.process(
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

        print(new_book.model_dump_json(indent=4))

        print(book_intel.model_dump_json(indent=4))

        return new_book
