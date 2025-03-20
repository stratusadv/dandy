import time
from unittest import TestCase

from typing_extensions import Callable

from dandy.core.cache import cache_to_memory
from dandy.core.cache import cache_to_sqlite
from dandy.core.cache.cache import BaseCache
from tests.core.cache.caches import sql_lite_cache, memory_cache


class TestCache(TestCase):
    @classmethod
    def tearDownClass(cls):
        sql_lite_cache.destroy()
        memory_cache.destroy()

    # def run_test_cache_with_llm_bot(self, cache: BaseCache, cache_decorator: Callable):
    #     cache.clear()
    #
    #     start = time.perf_counter()
    #
    #     # run uncached
    #
    #     self.assertGreater(time.perf_counter() - start, 0.5)
    #
    #     cached_start = time.perf_counter()
    #
    #     # run cached
    #
    #     self.assertLess(time.perf_counter() - cached_start, 0.1)
    #
    #     self.assertEqual(clown, cached_clown)
    #
    # def test_memory_cache(self):
    #     self.run_test_cache(memory_cache, cache_to_memory)
    #
    # def test_sqlite_cache(self):
    #     self.run_test_cache(sql_lite_cache, cache_to_sqlite)

