from __future__ import annotations

import logging

from typing_extensions import TYPE_CHECKING

from dandy.workflow import BaseWorkflow
from example.book.intelligence.bots.book_start_llm_bot import BookStartLlmBot
from example.book.intelligence.character.workflow import CharactersWorkflow
from example.book.intelligence.intel import BookIntel
from example.book.intelligence.world.bot import WorldLlmBot
from example.book.models import Book

if TYPE_CHECKING:
    from example.book.intelligence.character.intel import CharactersIntel


class BookWorkflow(BaseWorkflow):
    @classmethod
    def process(
            cls,
            user_input: str,
    ) -> Book:
        book_intel = BookIntel()
        
        logging.info('Working on book title and overview')
        book_intel.start = BookStartLlmBot.process(user_input)

        logging.info('Creating "those" characters')
        book_intel.characters = CharactersWorkflow.process(book_intel)

        logging.info('Forging a world')
        book_intel.world = WorldLlmBot.process(
            book_intel=book_intel,
        )

        new_book = Book(
            title=book_intel.start.title,
            overview=book_intel.start.overview
        )

        print(new_book.model_dump_json(indent=4))

        print(book_intel.model_dump_json(indent=4))

        return new_book
