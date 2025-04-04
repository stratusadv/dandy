import logging
import os

from book.intelligence.workflow import BookWorkflow
from dandy.cache import SqliteCache
from dandy.core.exceptions import DandyException
from dandy.recorder import Recorder

if __name__ == '__main__':
    try:
        # if os.getenv('DEBUG'):
        #     SqliteCache.clear('example')

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )

        Recorder.start_recording('book_generation')

        logging.info('Creating a Book')

        dandy_book = BookWorkflow.process(
            user_input="""It's 2035 and the dandy intelligence python library has changed the world for ever. In an effort
            to build awareness the people behind the library have created a working version of their lovable mascot the 
            dandy robot. He has now been turned on and given the directive to let the world know about the dandy library
            and given full agency to do it ... what could go wrong!""",
        )

        dandy_book.to_markdown_file()

        logging.info('Complete')

    except DandyException:
        raise DandyException

    finally:
        Recorder.stop_recording('book_generation')
        Recorder.to_html_file('book_generation')
