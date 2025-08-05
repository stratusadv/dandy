from typing import Literal

from dandy.bot import BaseBot
from dandy.intel import BaseIntel


class PoemIntel(BaseIntel):
    poem: str
    genre: Literal['happy', 'sad']


class Bot(BaseBot):
    def process(self):
        self.services.llm.prompt_to_intel(
            prompt='Write me a random poem',
            intel_class=PoemIntel,
        )

print(Bot().process())