from dandy.llm import BaseLlmMap, Map
from example.book.enums import BookTheme


class BookThemeLlmMap(BaseLlmMap):
    map = Map({
        'romance, love, kissing, feelings, emotions, sex': BookTheme.ROMANCE,
        'thriller, unknown, exciting, action, adventure': BookTheme.THRILLER,
        'science fiction, dystopian, space, technology, robots': BookTheme.SCIENCE_FICTION,
        'fantasy, magic, swords, dragons, elfs, wizards': BookTheme.FANTASY,
        'mystery, suspense, murder, crime, detective': BookTheme.MYSTERY,
        'violence, scary, horror, death, fear': BookTheme.HORROR,
    })