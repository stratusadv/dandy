from unittest import TestCase


class TestProcessor(TestCase):
    def test_processor_import(self):
        from dandy.core.processor.processor import BaseProcessor
        self.assertTrue(type(BaseProcessor) is type(BaseProcessor))