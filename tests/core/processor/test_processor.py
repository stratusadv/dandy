from unittest import TestCase, mock

from dandy.core.future import AsyncFuture
from dandy.processor.processor import BaseProcessor


class TestProcessor(TestCase):
    def test_processor_import(self):
        from dandy.processor.processor import BaseProcessor
        self.assertTrue(type(BaseProcessor) is type(BaseProcessor))

    @mock.patch.multiple(BaseProcessor, __abstractmethods__=set())
    def test_processor_process(self):
        base_processor = BaseProcessor()

        with self.assertRaises(NotImplementedError):
            base_processor.process()

    @mock.patch.multiple(BaseProcessor, __abstractmethods__=set())
    def test_processor_process_to_future(self):
        base_processor = BaseProcessor()

        return_val = base_processor.process_to_future()

        self.assertTrue(isinstance(return_val, AsyncFuture))
