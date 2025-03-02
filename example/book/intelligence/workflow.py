from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from dandy.workflow import BaseWorkflow
from example.book.intelligence.character.workflow import GenerateCharactersIntelWorkflow
from example.book.intelligence.intel import BookIntel
from example.book.models import Book

if TYPE_CHECKING:
    from example.book.intelligence.character.intel import CharactersIntel


class GenerateBookWorkflow(BaseWorkflow):
    @classmethod
    def process(
            cls,
            title: str,
            author: str,
            overview: str,
            chapter_count: int,
    ) -> Book:
        
        new_book = Book(
            title=title,
            author=author,
            overview=overview
        )
        
        characters_intel = GenerateCharactersIntelWorkflow.process(new_book)
        
        book_intel = BookIntel(
            characters_intel=characters_intel
        )

        print(new_book.model_dump_json(indent=4))
        print(book_intel.model_dump_json(indent=4))
        
        return new_book