from dandy import Decoder
from example.book.enums import BookTheme


class BookThemeDecoder(Decoder):
    mapping_keys_description = 'book themes'
    mapping = {
        'romance, love, kissing, feelings, emotions, sex': BookTheme.ROMANCE,
        'thriller, unknown, exciting, action, adventure': BookTheme.THRILLER,
        'science fiction, dystopian, space, technology, robots': BookTheme.SCIENCE_FICTION,
        'fantasy, magic, swords, dragons, elfs, wizards': BookTheme.FANTASY,
        'mystery, suspense, murder, crime, detective': BookTheme.MYSTERY,
        'violence, scary, horror, death, fear': BookTheme.HORROR,
    }
