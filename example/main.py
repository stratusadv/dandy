from book.intelligence.workflow import GenerateBookWorkflow
from dandy.core.exceptions import DandyException
from dandy.debug import DebugRecorder

if __name__ == '__main__':
    try:
        DebugRecorder.start_recording('book_generation')
        
        dandy_book = GenerateBookWorkflow.process(
            title='Adventures of a Dandy Robot',
            author='Dandy McAuthor',
            overview="""It's 2035 and the dandy intelligence python library has changed the world for ever. In an effort
            to build awareness the people behind the library have created a working version of their lovable mascot the 
            dandy robot. He has now been turned on and given the directive to let the world know about the dandy library
            and given full agency to do it ... what could go wrong!""",
            chapter_count=4,
        )

    except DandyException:
        raise DandyException

    finally:
        DebugRecorder.stop_recording('book_generation')
        DebugRecorder.to_html_file('book_generation')
