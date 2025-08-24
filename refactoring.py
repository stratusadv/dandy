from typing import Literal

from dandy.bot import Bot
from dandy.intel import BaseIntel


class PoemIntel(BaseIntel):
    poem_title: str
    poem_body: str
    genre: Literal['happy', 'sad']


class AllanBot(Bot):
    def __post_init__(self):
        self.llm_instructions_prompt = self.llm.Prompt('You are a poetic assistant that writes poems for users. that always uses "pink" and "green" words in your poems.')

    def process(self, user_input: str = '') -> PoemIntel:
        poem_intel = self.llm.prompt_to_intel(
            prompt=self.llm.Prompt(user_input),
            intel_class=PoemIntel,
        )

        return poem_intel

allan_bot = AllanBot(
    llm_instructions_prompt='You are a poetic assistant that writes poems for users. make a dark and scary poem, using the word "black" all through out the poem'
)

print (allan_bot.llm_instructions_prompt)

print(allan_bot.process('There is a crab in my garden, also dance and I think he wants money!').poem_body)