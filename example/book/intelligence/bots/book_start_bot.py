from dandy import cache_to_sqlite, Bot, Prompt
from example.book.intelligence.intel import BookStartIntel


class BookStartLlmBot(Bot):
    instructions_prompt = (
        Prompt()
        .text('You are a book starting bot. You will be given an idea by the user.')
        .text('you will generate a book title and overview.')
    )

    @cache_to_sqlite('example')
    def process(
            self,
            user_input: str,
    ) -> BookStartIntel:

        return self.llm.prompt_to_intel(
            prompt=Prompt(user_input),
            intel_class=BookStartIntel
        )
