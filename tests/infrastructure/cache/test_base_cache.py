from unittest import TestCase

from dandy.infrastructure.cache.cache import BaseCache


class TestBaseCache(TestCase):
    def test_base_cache_is_abstract(self) -> None:
        with self.assertRaises(TypeError):
            BaseCache(cache_name='test', limit=10)
