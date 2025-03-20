from unittest import TestCase

from dandy.core.processor.processor import BaseProcessor
from dandy.map.map import Map


class TestMap(TestCase):
    def test_map_import(self):
        self.assertTrue(type(Map) is type(BaseProcessor))