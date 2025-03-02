from __future__ import annotations

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
        book_start_intel = BookStartLlmBot.process(user_input)

        new_book = Book(
            title=book_start_intel.title,
            overview=book_start_intel.overview
        )

        characters_intel = CharactersWorkflow.process(new_book)

        world_intel = WorldLlmBot.process(
            book_start_intel=book_start_intel,
            characters_intel=characters_intel,
        )

        book_intel = BookIntel(
            characters_intel=characters_intel,
            world_intel=world_intel
        )

        print(new_book.model_dump_json(indent=4))
        print(book_intel.model_dump_json(indent=4))

        return new_book
