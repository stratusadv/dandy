from unittest import TestCase

from dandy.core.utils import json_default

from example.pirate.ship.datasets import QUEEN_ANNES_REVENGE

class TestUtils(TestCase):
    def test_json_default_serializer(self):
        serialized_object = json_default(
            QUEEN_ANNES_REVENGE
        )

        self.assertEqual(serialized_object['name'], "Queen Annes Revenge")