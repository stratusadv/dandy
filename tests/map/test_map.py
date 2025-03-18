from unittest import TestCase

from dandy.core.processor.processor import BaseProcessor
from dandy.map import BaseMap


class TestMap(TestCase):
    def test_map_import(self):
        self.assertTrue(type(BaseMap) is type(BaseProcessor))