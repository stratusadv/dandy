from unittest import TestCase

from dandy.llm.map.llm_map import BaseLlmMap


class FunLlmMap(BaseLlmMap):
    map = {
        'clowns': ('if someone needs a laugh then they need clowns', 1),
        'lions': ('someone is interested in seeing animals', 2),
        'jugglers': ('someone looking for something more technical', 3),
    }


class TestMap(TestCase):
    def test_map_validator(self):
