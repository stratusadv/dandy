from dandy import Bot, Prompt, cache_to_sqlite
from tests.example_project.book.intelligence.intel import BookStartIntel


class BookStartLlmBot(Bot):
    role = 'Book Overview Writer'
    task = 'Take the idea provide by the user and create a title and overview for a new book.'
    guidelines = Prompt().list([
        'Read through the user input and create a title and overview for a new book.',
        'The title should be catchy and attention-grabbing.',
        'The overview should provide a brief summary of the book and its main themes.',
    ])
    intel_class = BookStartIntel