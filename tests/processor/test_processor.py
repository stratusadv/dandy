from unittest import TestCase


class TestProcessor(TestCase):
    def test_processor_import(self):
        from dandy.processor.processor import BaseProcessor
        self.assertTrue(type(BaseProcessor) is type(BaseProcessor))