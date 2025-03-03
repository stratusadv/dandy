from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from dandy.llm import BaseLlmBot, Prompt
from example.book.intelligence.chapter.intel import ChaptersIntel
from example.book.intelligence.prompts import book_intel_prompt

if TYPE_CHECKING:
    from example.book.intelligence.intel import BookIntel


class ChaptersStructureLlmBot(BaseLlmBot):
    config = 'ADVANCED'
    instructions_prompt = (
        Prompt()
        .text('You are a chapter planning bot. You will be given information on a book that is being written.')
        .text('For each chapter create a title and which plot points will be covered in the chapter.')
        .text('Do not create any scenes or write content for the chapter.')
    )
   
    @classmethod    
    def process(
            cls,
            book_intel: BookIntel,
            chapter_count: int,
    ) -> ChaptersIntel:
        
        postfix_system_prompt = Prompt()
        postfix_system_prompt.text(f'Create {chapter_count} chapters.')
        
        return cls.process_prompt_to_intel(
            prompt=book_intel_prompt(book_intel),
            intel_class=ChaptersIntel,
            postfix_system_prompt=postfix_system_prompt
        )
        