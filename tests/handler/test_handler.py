from unittest import TestCase


class TestHandler(TestCase):
    def test_handler_import(self):
        from dandy.processor.processor import BaseProcessor
        self.assertTrue(type(BaseProcessor) is type(BaseProcessor))