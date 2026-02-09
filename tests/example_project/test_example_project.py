import logging
from unittest import TestCase

from dandy import Recorder
from tests.example_project.book.workflow import create_book


class TestExampleProject(TestCase):
    def test_book_generation(self):
        dandy_book = None

        try:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
            )

            Recorder.start_recording('book_generation')

            logging.info('Creating a Book')

            dandy_book = create_book(
                user_input="""It's 2035 and the dandy intelligence python library has changed the world for ever. In an effort
                to build awareness the people behind the library have created a working version of their lovable mascot the 
                dandy robot. He has now been turned on and given the directive to let the world know about the dandy library
                and given full agency to do it ... what could go wrong!""",
                chapter_count=2,
            )

            dandy_book.to_markdown_file()

            logging.info('Complete')

        finally:
            Recorder.stop_recording('book_generation')
            Recorder.to_html_file('book_generation')

            self.assertTrue(dandy_book)
