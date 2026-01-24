from dandy.processor.bot.bot import Bot
from dandy.intel.intel import BaseIntel


class GenericTaskBot(Bot):
    def process(
            self,
            prompt: str,
    ) -> BaseIntel:
        return self.llm.prompt_to_intel(
            prompt=prompt,
        )
