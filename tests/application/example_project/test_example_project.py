import logging
from unittest import TestCase

from dandy import Recorder
from tests.consts import live_llm_test
from tests.application.example_project.book.models import Book, Chapter
from tests.application.example_project.book.workflow import create_book

logger = logging.getLogger(__name__)

BOOK_USER_INPUT = (
    "It's 2035 and the dandy intelligence python library has changed the world for ever. "
    'In an effort to build awareness the people behind the library have created a working '
    'version of their lovable mascot the dandy robot. He has now been turned on and given '
    'the directive to let the world know about the dandy library and given full agency to '
    'do it ... what could go wrong!'
)


class TestExampleProject(TestCase):
    @live_llm_test
    def test_book_generation(self) -> None:
        Recorder.start_recording('book_generation')

        try:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
            )

            logger.info('Creating a Book')

            dandy_book = create_book(user_input=BOOK_USER_INPUT, chapter_count=2)

            dandy_book.to_markdown_file()

            logger.info('Complete')

        finally:
            Recorder.stop_recording('book_generation')
            Recorder.to_html_file('book_generation')

        self.assertIsInstance(dandy_book, Book)
        self.assertEqual(dandy_book.author, 'Dandy McAuthor')
        self.assertNotEqual(dandy_book.title, '')
        self.assertNotEqual(dandy_book.overview, '')
        self.assertEqual(len(dandy_book.chapters), 2)

        for chapter in dandy_book.chapters:
            self.assertIsInstance(chapter, Chapter)
            self.assertNotEqual(chapter.title, '')
            self.assertNotEqual(chapter.content, '')
