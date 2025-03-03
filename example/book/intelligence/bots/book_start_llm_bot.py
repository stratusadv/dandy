from typing import Any

from dandy.llm import BaseLlmBot, Prompt
from example.book.intelligence.intel import BookStartIntel

class BookStartLlmBot(BaseLlmBot):
    instructions_prompt = (
            Prompt()
        .text('You are a book starting bot. You will be given an idea by the user.')
        .text('you will generate a book title and overview.')
    )
    
    @classmethod
    def process(
            cls,
            user_input: str,
    ) -> BookStartIntel:
        
        return cls.process_prompt_to_intel(
            prompt=Prompt(user_input),
            intel_class=BookStartIntel
        )
        
        