from dandy import Bot
from tests.example_project.book.enums import BookTheme


class BookThemeDecoderBot(Bot):
    def process(self, prompt: str) -> BookTheme:
        return self.llm.decoder.prompt_to_value(
            prompt=prompt,
            keys_description='book themes',
            keys_values={
                'romance, love, kissing, feelings, emotions, sex': BookTheme.ROMANCE,
                'thriller, unknown, exciting, action, adventure': BookTheme.THRILLER,
                'science fiction, dystopian, space, technology, robots': BookTheme.SCIENCE_FICTION,
                'fantasy, magic, swords, dragons, elfs, wizards': BookTheme.FANTASY,
                'mystery, suspense, murder, crime, detective': BookTheme.MYSTERY,
                'violence, scary, horror, death, fear': BookTheme.HORROR,
            },
        )
