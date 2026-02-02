from dandy.bot.bot import Bot


class FunDecoderBot(Bot):
    def process(self, prompt: str, max_return_values: int):
        return self.llm.decoder.prompt_to_values(
            prompt=prompt,
            keys_description='Descriptions of People',
            keys_values={
                'Would be glad to get a free puppy': 391,
                'Needs a laugh and needs clowns': 113,
                'Interested in seeing animals': 782,
                'Looking for something more technical': 927,
            },
            max_return_values=max_return_values
        )
